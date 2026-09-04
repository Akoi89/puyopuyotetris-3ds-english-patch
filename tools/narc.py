"""Read and rebuild a NARC archive.

    NARC  feff 0001 | filesize u32 | headersize u16 (0x10) | sections u16
    BTAF  size u32 | count u32 | (start,end) u32 pairs, relative to GMIF data
    BTNF  size u32 | name table, kept verbatim
    GMIF  size u32 | the member data, laid out back to back
"""
import struct


def read(path_or_bytes):
    d = path_or_bytes if isinstance(path_or_bytes, bytes) else open(path_or_bytes, 'rb').read()
    assert d[:4] == b'NARC', 'not a NARC'
    hs, nsec = struct.unpack_from('<HH', d, 12)
    off, files, btnf, img = hs, [], None, None
    while off < len(d):
        m = d[off:off + 4]
        size = struct.unpack_from('<I', d, off + 4)[0]
        if size == 0:
            break
        if m == b'BTAF':
            n = struct.unpack_from('<I', d, off + 8)[0]
            files = [struct.unpack_from('<II', d, off + 12 + 8 * i) for i in range(n)]
        elif m == b'BTNF':
            btnf = bytes(d[off:off + size])
        elif m == b'GMIF':
            img = off + 8
        off += size
    return dict(raw=d, btnf=btnf, nsec=nsec,
                members=[bytes(d[img + a:img + b]) for a, b in files])


def build(orig, members):
    """Rebuild, keeping the original name table and section count."""
    btnf = orig['btnf']
    data = bytearray()
    spans = []
    for m in members:
        spans.append((len(data), len(data) + len(m)))
        data += m
    btaf = bytearray(b'BTAF')
    btaf += struct.pack('<II', 12 + 8 * len(members), len(members))
    for a, b in spans:
        btaf += struct.pack('<II', a, b)
    gmif = b'GMIF' + struct.pack('<I', 8 + len(data)) + bytes(data)
    out = bytearray(b'NARC\xfe\xff\x00\x01')
    out += struct.pack('<I', 0)                 # filesize, patched below
    out += struct.pack('<HH', 0x10, orig['nsec'])
    out += btaf + btnf + gmif
    struct.pack_into('<I', out, 8, len(out))
    return bytes(out)


if __name__ == '__main__':
    import os, sys
    ok = bad = 0
    for root in sys.argv[1:] or ['tr_jpvoice/tenp/text', 'jp_orig/tenp/text']:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                if not f.endswith('.narc'):
                    continue
                p = os.path.join(dp, f)
                d = open(p, 'rb').read()
                try:
                    o = read(d)
                    r = build(o, o['members'])
                except Exception as e:
                    bad += 1
                    print('ERR ', p, e)
                    continue
                if r == d:
                    ok += 1
                else:
                    bad += 1
                    print('DIFF', p, len(r), 'vs', len(d))
    print('narc round-trip: %d exact, %d differ' % (ok, bad))
