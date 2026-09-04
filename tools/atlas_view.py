"""Render a FONTDATF glyph atlas to PNG so the layout can be seen.

    python atlas_view.py <narc> <member-pair-index> <out.png> [--raw]

Bitmap member header:
    +0x00 u32 data size   +0x06 u16 width   +0x08 u16 height
Pixels are 4bpp alpha. 3DS textures are normally Morton-swizzled in 8x8 tiles,
so both orders are offered and the eye decides.
"""
import struct, sys, zlib
from check_glyphs import narc_members


def png(path, w, h, gray):
    raw = b''.join(b'\x00' + bytes(gray[y * w:(y + 1) * w]) for y in range(h))
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c))
    open(path, 'wb').write(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(raw))
        + chunk(b'IEND', b''))


MORTON = []
for i in range(64):
    x = (i & 1) | ((i >> 1) & 2) | ((i >> 2) & 4)
    y = ((i >> 1) & 1) | ((i >> 2) & 2) | ((i >> 3) & 4)
    MORTON.append((x, y))


def decode(blob, swizzled=True):
    size, = struct.unpack_from('<I', blob, 0)
    w, h = struct.unpack_from('<HH', blob, 6)
    data = blob[16:16 + size]
    out = bytearray(w * h)
    if not swizzled:
        for i in range(w * h):
            b = data[i >> 1]
            out[i] = ((b & 0xF) if i % 2 == 0 else (b >> 4)) * 17
        return w, h, out
    i = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for k in range(64):
                dx, dy = MORTON[k]
                b = data[i >> 1]
                v = ((b & 0xF) if i % 2 == 0 else (b >> 4)) * 17
                px, py = tx + dx, ty + dy
                if px < w and py < h:
                    out[py * w + px] = v
                i += 1
    return w, h, out


if __name__ == '__main__':
    narc, idx, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    raw = '--raw' in sys.argv
    ms = narc_members(narc)
    fifs = [(ms[i], ms[i + 1]) for i in range(0, len(ms), 2) if ms[i][:8] == b'FONTDATF']
    f, b = fifs[idx]
    n = struct.unpack_from('<I', f, 0x10)[0]
    w, h, px = decode(b, swizzled=not raw)
    png(out, w, h, px)
    print('%s  glyphs=%d  texture=%dx%d  -> %s%s' % (narc.split('/')[-1], n, w, h, out,
                                                     ' (raw order)' if raw else ' (morton)'))
