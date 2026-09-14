"""Why do base chapter atlases report no widths? Print FONTDATF record stats per atlas."""
import struct, os, sys
import narc


def recs(path):
    ms = narc.read(path)['members']
    out = []
    for i in range(0, len(ms) - 1, 2):
        f, b = ms[i], ms[i + 1]
        if f[:8] != b'FONTDATF':
            continue
        n = struct.unpack_from('<I', f, 0x10)[0]
        cols, rows, gh = (struct.unpack_from('<H', f, o)[0] for o in (0x22, 0x24, 0x26))
        w, h = struct.unpack_from('<HH', b, 6)
        rows_ = [struct.unpack_from('<iIIHH', f, 56 + r * 16) for r in range(n)]
        nz = sum(1 for r in rows_ if r[1])
        print('%-58s m%-2d n=%3d gh=%2d cell=%dx%d  wid!=0: %3d  sample=%s' % (
            path[-58:], i // 2, n, gh, w // cols, h // rows, nz, [(chr(r[3]), r[0], r[1], r[2]) for r in rows_[40:44]]))
        out.append(rows_)
    return out


for p in sys.argv[1:]:
    recs(p)
