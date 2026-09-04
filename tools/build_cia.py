"""Build a patched Puyo Puyo Tetris CIA.

    python build_cia.py <shell.cia> <decrypted.cci> <new.romfs> <out.cia> [major.minor.micro]

The shipped .cia carries NCCH-encrypted contents, so a plaintext romfs cannot be
spliced into it. The matching -decrypted.cci holds the same three partitions with
NoCrypto set, and they map to the CIA's three contents byte-for-byte by size, so
all three are sourced from the CCI and content 0 gets the new romfs.

Reuses the TGAA pipeline:
  ncch.splice  - swap the romfs inside partition 0 and repair the NCCH hash chain
  cia.Cia      - rewrite the CIA, recomputing every TMD hash and re-verifying
"""
import sys, os, struct
sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
import ncch
from cia import Cia

shell, cci_path, romfs_path, out = sys.argv[1:5]
VERSION = tuple(int(x) for x in sys.argv[5].split('.')) if len(sys.argv) > 5 else (1, 0, 0)

# --- NCSD partition table ---------------------------------------------------
MU = 0x200
cci = open(cci_path, 'rb')
head = cci.read(0x200)
assert head[0x100:0x104] == b'NCSD', 'not an NCSD/CCI'
parts = []
for i in range(8):
    off, ln = struct.unpack_from('<II', head, 0x120 + i * 8)
    if ln:
        parts.append((off * MU, ln * MU))
print('CCI partitions:')
for i, (o, n) in enumerate(parts):
    print('  %d  offset 0x%08X  %d bytes' % (i, o, n))

print('reading shell CIA ...')
c = Cia(shell)
print('  %d contents, version %d.%d.%d' % ((c.count,) + c.version()))
assert c.count == len(parts), 'CIA has %d contents, CCI has %d partitions' % (c.count, len(parts))
for i, (o, n) in enumerate(parts):
    assert n == len(c.contents[i]), \
        'partition %d is %d bytes, CIA content %d is %d' % (i, n, i, len(c.contents[i]))
print('  partition sizes match CIA content sizes')

blobs = []
for o, n in parts:
    cci.seek(o)
    blobs.append(cci.read(n))

ok, f = ncch.verify(blobs[0])
print('decrypted partition 0 superblock hash reproduces:', ok)
assert ok, 'source CXI failed its own null test - stop'
assert f['nocrypto'], 'partition 0 is still encrypted - stop'

new_romfs = open(romfs_path, 'rb').read()
print('splicing romfs: %d -> %d bytes (%+d)'
      % (f['romfs_size'] * MU, len(new_romfs), len(new_romfs) - f['romfs_size'] * MU))
blobs[0] = ncch.splice(blobs[0], new_romfs)

ok2, _ = ncch.verify(blobs[0])
print('patched partition 0 superblock hash reproduces:', ok2)
assert ok2, 'splice produced an NCCH that fails its own hash - stop'

print('writing %s ...' % out)
chk = Cia(shell).write(out, replace=dict(enumerate(blobs)), version=VERSION)
print('done: %d contents, %.1f MB' % (chk.count, sum(len(b) for b in chk.contents) / 1048576))
