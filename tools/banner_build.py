"""Rebuild the HOME-menu banner (ExeFS banner.bin, CBMD container) with a new
256x128 texture in every region's CGFX model.

CBMD: 'CBMD' + u32 0 + 14 x u32 offsets of LZ11-compressed CGFX blobs (index 0
common, then one per region/language; 0 = absent) + u32 CWAV offset at 0x84.
Inside each CGFX the 256x128 TXOB is RGB565 (format 3), 0x10000 bytes, at the
pointer stored 16 words after the TXOB magic (relative to that pointer).

    python banner_build.py <orig banner.bin> <texture.png> <out banner.bin>
"""
import re, struct, sys
import comp, tex
from PIL import Image


def txob(d):
    for o in [m.start() for m in re.finditer(b'TXOB', d)]:
        h, w = struct.unpack_from('<II', d, o + 0x14)
        if w == 256 and h == 128:
            fmt = struct.unpack_from('<I', d, o + 4 + 11 * 4)[0]; size = struct.unpack_from('<I', d, o + 4 + 15 * 4)[0]
            data = o + 4 + 16 * 4 + struct.unpack_from('<I', d, o + 4 + 16 * 4)[0]
            return o, fmt, size, data
    return None


def main(src, png, out):
    b = open(src, 'rb').read(); assert b[:4] == b'CBMD'
    offs = list(struct.unpack_from('<14I', b, 8)); cw = struct.unpack_from('<I', b, 0x84)[0]
    img = Image.open(png).convert('RGBA'); assert img.size == (256, 128)
    ends = [o for o in offs if o] + [cw]
    chunks = []; k = 0
    for i, off in enumerate(offs):
        if not off:
            chunks.append(None); continue
        raw = b[off:ends[k + 1]]; k += 1
        d = bytearray(comp.lz11_decode(raw, 0)[0] if isinstance(comp.lz11_decode(raw, 0), tuple) else comp.lz11_decode(raw, 0))
        t = txob(d)
        if t:
            o, fmt, size, data = t
            enc = tex.encode(img, fmt); assert len(enc) == size, (len(enc), size)
            d[data:data + size] = enc
            chunks.append(comp.lz11_encode(bytes(d)))
        else:
            chunks.append(raw)
    hdr = bytearray(b[:0x88]); pos = 0x88; body = b''
    for i, c in enumerate(chunks):
        if c is None:
            offs[i] = 0; continue
        offs[i] = pos; body += c; pos += len(c)
    struct.pack_into('<14I', hdr, 8, *offs); struct.pack_into('<I', hdr, 0x84, pos)
    new = bytes(hdr) + body + b[cw:]
    open(out, 'wb').write(new)
    # verify: every model decodes to the new texture
    ok = 0
    for i, off in enumerate(offs):
        if not off: continue
        nxt = min([o for o in offs if o > off] + [pos])
        d = comp.lz11_decode(new[off:nxt], 0); d = d[0] if isinstance(d, tuple) else d
        t = txob(d)
        if t:
            o, fmt, size, data = t
            back = tex.decode(d[data:data + size], 256, 128, fmt).convert('RGBA')
            ok += back.tobytes() == tex.decode(tex.encode(img, fmt), 256, 128, fmt).convert('RGBA').tobytes()
    print('wrote %s: %d bytes (was %d), %d models carry the new texture, CWAV kept (%d bytes)' % (out, len(new), len(b), ok, len(b) - cw))


if __name__ == '__main__':
    main(*sys.argv[1:4])
