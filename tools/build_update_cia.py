"""Build the English patch as an UPDATE title (0004000E) instead of a full base.

    python build_update_cia.py <update-decrypted.cia> <romfs source> <out.cia> [major.minor.micro]

<romfs source> is either a raw romfs file or a patched base CIA, in which case
the romfs is lifted out of its content 0 exactly as shipped (so the update and
the base build carry the same bytes, provably).

The official v1.2.0 update is code only: its CXI has an exheader and an ExeFS
and no romfs. When an update title carries a romfs the 3DS uses it in place of
the base game's, so appending our patched romfs to Sega's own update code gives
a package that installs over the official update, leaves the user's untouched
Japanese base in place, and needs no base CIA at all - the shape TGAA shipped.

Never rebuild a CXI with `3dstool -c -t cxi` (see ncch.py). This appends the
romfs region in place and repairs exactly the fields that describe it:

    NCCH 0x104  content size (media units)
         0x18D  flags[5] content type: set bit 0 (Data) as the base has it
         0x18F  flags[7]: clear bit 1 (NoMountRomFs)
         0x1B0  romfs offset = ExeFS end aligned up to 0x1000, in media units
         0x1B4  romfs size (media units)
         0x1B8  romfs hash-region size = align(IVFC header 0x60 + master hash, 0x200)
         0x1E0  sha256 over that leading region
         0x160  sha256 over the exheader, because
    exheader ACI +0x4F  Storage Info "other attributes": clear bit 0 (Not use RomFS).
                        Sega's code-only update sets it; the base does not. The
                        access descriptor's copy of the ACI already has it clear.

Null test (run with `--selftest`): strip the romfs off the base CXI with the
inverse of the above, add it back, and require the result to be byte-identical
to the base partition. If the alignment or hash-region rules were wrong that
comparison would fail.
"""
import hashlib
import os
import struct
import sys

sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
import ncch
from cia import Cia

MU = 0x200
ROMFS_ALIGN = 0x1000


def u32(d, o):
    return struct.unpack_from('<I', d, o)[0]


def exefs_end(d):
    return (u32(d, 0x1A0) + u32(d, 0x1A4)) * MU


def add_romfs(cxi, romfs):
    """Return cxi with romfs appended as its RomFS region, header and exheader repaired."""
    d = bytearray(cxi)
    if d[0x100:0x104] != b'NCCH':
        raise SystemExit('not an NCCH')
    if not d[0x18F] & 0x04:
        raise SystemExit('CXI is encrypted; use the decrypted update CIA')
    if u32(d, 0x1B0):
        raise SystemExit('this CXI already has a romfs; use ncch.splice')
    if romfs[:4] != b'IVFC':
        raise SystemExit('romfs does not start with IVFC')

    end = exefs_end(d)
    if len(d) < end:
        raise SystemExit('CXI is shorter than its ExeFS')
    d = d[:end]                                  # drop anything after the ExeFS
    start = (end + ROMFS_ALIGN - 1) // ROMFS_ALIGN * ROMFS_ALIGN
    d += b'\0' * (start - end)

    body = bytearray(romfs)
    if len(body) % MU:
        body += b'\0' * (MU - len(body) % MU)
    d += body

    master_hash = u32(body, 8)
    hreg = (0x60 + master_hash + MU - 1) // MU
    struct.pack_into('<I', d, 0x1B0, start // MU)
    struct.pack_into('<I', d, 0x1B4, len(body) // MU)
    struct.pack_into('<I', d, 0x1B8, hreg)
    d[0x1E0:0x200] = hashlib.sha256(bytes(body[:hreg * MU])).digest()
    struct.pack_into('<I', d, 0x104, len(d) // MU)
    d[0x18D] |= 0x01                              # content type: Data
    d[0x18F] &= ~0x02                             # mount the romfs

    aci = 0x200 + 0x200                           # exheader starts at 0x200, ACI at +0x200
    d[aci + 0x4F] &= ~0x01                        # use RomFS
    d[0x160:0x180] = hashlib.sha256(bytes(d[0x200:0x600])).digest()

    ok, f = ncch.verify(bytes(d))
    if not ok:
        raise SystemExit('result fails its own superblock hash')
    return bytes(d)


def strip_romfs(cxi):
    """Inverse of add_romfs, for the null test only."""
    d = bytearray(cxi[:exefs_end(cxi)])
    for o in (0x1B0, 0x1B4, 0x1B8):
        struct.pack_into('<I', d, o, 0)
    d[0x1E0:0x200] = b'\0' * 32
    struct.pack_into('<I', d, 0x104, len(d) // MU)
    d[0x18D] &= ~0x01
    d[0x18F] |= 0x02
    d[0x400 + 0x4F] |= 0x01
    d[0x160:0x180] = hashlib.sha256(bytes(d[0x200:0x600])).digest()
    return bytes(d)


def romfs_of(cxi):
    f = ncch.fields(cxi)
    s = f['romfs_off'] * MU
    return cxi[s:s + f['romfs_size'] * MU]


def selftest(cci_path):
    cci = open(cci_path, 'rb')
    head = cci.read(MU)
    off, ln = struct.unpack_from('<II', head, 0x120)
    cci.seek(off * MU)
    base = cci.read(ln * MU)
    romfs = romfs_of(base)
    rebuilt = add_romfs(strip_romfs(base), romfs)
    same = rebuilt == base
    print('null test: strip + add_romfs reproduces the base CXI byte-for-byte:', same)
    if not same:
        for o in range(0x100, 0x200, 4):
            if rebuilt[o:o + 4] != base[o:o + 4]:
                print('   header differs at 0x%03X: %s vs %s' % (o, rebuilt[o:o + 4].hex(), base[o:o + 4].hex()))
        raise SystemExit('null test failed')


def raw_content0(path):
    """Content 0 of a CIA, without cia.py's hash gate (the decrypted update passes it anyway)."""
    c = Cia(path)
    if c.count != 1:
        raise SystemExit('update shell has %d contents' % c.count)
    return c, c.contents[0]


def main():
    if sys.argv[1:2] == ['--selftest']:
        selftest(sys.argv[2])
        return
    shell, src, out = sys.argv[1:4]
    version = tuple(int(x) for x in sys.argv[4].split('.')) if len(sys.argv) > 4 else (1, 3, 0)

    c, upd = raw_content0(shell)
    print('shell: %s' % os.path.basename(shell))
    print('   TMD version %d.%d.%d, content 0 = %d bytes, flags %s' % (c.version() + (len(upd), upd[0x188:0x190].hex())))

    if src.lower().endswith('.cia'):
        b = Cia(src)
        romfs = romfs_of(b.contents[0])
        print('romfs lifted from %s content 0: %d bytes' % (os.path.basename(src), len(romfs)))
    else:
        romfs = open(src, 'rb').read()
        print('romfs from %s: %d bytes' % (src, len(romfs)))
    print('   romfs sha256 %s' % hashlib.sha256(romfs).hexdigest()[:16])

    cxi = add_romfs(upd, romfs)
    f = ncch.fields(cxi)
    print('update CXI: %d bytes; romfs at 0x%X, %d MU, hash region %d MU; flags %s; exheader other_attr %d'
          % (len(cxi), f['romfs_off'] * MU, f['romfs_size'], f['hash_region'], cxi[0x188:0x190].hex(), cxi[0x400 + 0x4F]))
    assert romfs_of(cxi)[:len(romfs)] == romfs, 'romfs did not survive the append'

    chk = c.write(out, replace={0: cxi}, version=version)
    print('wrote %s: TMD version %d.%d.%d, %d content, %.1f MB' % ((out,) + chk.version() + (chk.count, len(chk.contents[0]) / 1048576)))
    assert chk.contents[0] == cxi, 'CIA content does not match the CXI'


if __name__ == '__main__':
    main()
