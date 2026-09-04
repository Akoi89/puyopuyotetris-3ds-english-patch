"""Decode every CTPK texture (and raw .icn) in the game and DLC into contact sheets.

    python survey_textures.py

Writes tex_survey/<narc>__<texture>.png for every texture, plus one contact sheet
per source directory, so baked-in Japanese lettering can be found by eye.
Formats: RGBA4, RGB565, RGBA8, RGB8, RGBA5551, L8, A8, LA8, LA4, L4, A4 decoded
here; ETC1 / ETC1A4 through the TGAA decoder.
"""
import os, sys, struct, zlib
sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
from check_glyphs import narc_members
try:
    import etc1a4
except Exception:
    etc1a4 = None
from PIL import Image

OUT = 'tex_survey'
MORTON = [((i & 1) | ((i >> 1) & 2) | ((i >> 2) & 4), ((i >> 1) & 1) | ((i >> 2) & 2) | ((i >> 3) & 4)) for i in range(64)]
FMT = {0: 'RGBA8', 1: 'RGB8', 2: 'RGBA5551', 3: 'RGB565', 4: 'RGBA4', 5: 'LA8', 6: 'HL8', 7: 'L8', 8: 'A8', 9: 'LA4', 10: 'L4', 11: 'A4', 12: 'ETC1', 13: 'ETC1A4'}
BPP = {0: 32, 1: 24, 2: 16, 3: 16, 4: 16, 5: 16, 6: 16, 7: 8, 8: 8, 9: 8, 10: 4, 11: 4, 12: 4, 13: 8}


def unswizzle(data, w, h, fmt):
    img = Image.new('RGBA', (w, h))
    px = img.load()
    bpp = BPP[fmt]
    k = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for m in range(64):
                x, y = tx + MORTON[m][0], ty + MORTON[m][1]
                if bpp == 4:
                    v = (data[k >> 1] >> (4 if k & 1 else 0)) & 0xF
                    c = (v * 17,) * 3 + (255,) if fmt == 10 else (255, 255, 255, v * 17)
                elif bpp == 8:
                    v = data[k]
                    if fmt == 7: c = (v, v, v, 255)
                    elif fmt == 8: c = (255, 255, 255, v)
                    else: l, a = (v >> 4) * 17, (v & 0xF) * 17; c = (l, l, l, a)
                elif bpp == 16:
                    v = struct.unpack_from('<H', data, k * 2)[0]
                    if fmt == 4: c = ((v >> 12) * 17, ((v >> 8) & 0xF) * 17, ((v >> 4) & 0xF) * 17, (v & 0xF) * 17)
                    elif fmt == 3: c = ((v >> 11) * 255 // 31, ((v >> 5) & 0x3F) * 255 // 63, (v & 0x1F) * 255 // 31, 255)
                    elif fmt == 2: c = ((v >> 11) * 255 // 31, ((v >> 6) & 0x1F) * 255 // 31, ((v >> 1) & 0x1F) * 255 // 31, (v & 1) * 255)
                    else: c = (v >> 8, v >> 8, v >> 8, v & 0xFF)
                elif bpp == 24:
                    b, g, r = data[k * 3:k * 3 + 3]; c = (r, g, b, 255)
                else:
                    a, b, g, r = data[k * 4:k * 4 + 4]; c = (r, g, b, a)
                if x < w and y < h:
                    px[x, h - 1 - y] = c          # stored bottom-up
                k += 1
    return img


def ctpk_textures(blob):
    if blob[:4] != b'CTPK':
        return []
    ver, count, texoff, texsize = struct.unpack_from('<HHII', blob, 4)
    out = []
    for i in range(count):
        e = 0x20 + i * 0x20
        noff, size, doff, fmt, w, h, mip = struct.unpack_from('<IIIIHHB', blob, e)
        name = blob[noff:blob.index(b'\0', noff)].decode('latin1')
        data = blob[texoff + doff: texoff + doff + size]
        out.append((name, w, h, fmt, data))
    return out


def decode(name, w, h, fmt, data):
    if fmt in (12, 13):
        if etc1a4 is None:
            return None
        rgba = etc1a4.decode(data, w, h, alpha=(fmt == 13))
        img = Image.frombytes('RGBA', (w, h), bytes(rgba)) if not isinstance(rgba, Image.Image) else rgba
        return img.transpose(Image.FLIP_TOP_BOTTOM) if fmt in (12, 13) and False else img
    return unswizzle(data, w, h, fmt)


os.makedirs(OUT, exist_ok=True)
sheets = {}
n = 0
for root in ('tr_envoice', 'dlc_r'):
    for dp, dn, fn in os.walk(root):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            imgs = []
            if f.endswith('.narc'):
                try:
                    ms = narc_members(p)
                except Exception:
                    continue
                for mi, m in enumerate(ms):
                    for name, w, h, fmt, data in ctpk_textures(m):
                        try:
                            img = decode(name, w, h, fmt, data)
                        except Exception as ex:
                            img = None
                        if img is not None:
                            imgs.append(('%s[%d]:%s %s' % (f, mi, name, FMT.get(fmt, fmt)), img))
            elif f.endswith('.icn') and os.path.getsize(p) == 4608:
                imgs.append((f, unswizzle(open(p, 'rb').read(), 48, 48, 3)))
            for label, img in imgs:
                rel = os.path.relpath(dp, root).replace(os.sep, '_')
                key = root + '_' + rel
                sheets.setdefault(key, []).append((label, img))
                n += 1
print('textures decoded:', n)
for key, items in sheets.items():
    cols = 4
    thumbs = []
    for label, img in items:
        t = img.convert('RGBA')
        t.thumbnail((256, 256))
        bg = Image.new('RGBA', (260, 276), (40, 40, 40, 255))
        bg.paste(t, (2, 2), t)
        from PIL import ImageDraw
        ImageDraw.Draw(bg).text((3, 262), label[:44], fill=(255, 255, 0, 255))
        thumbs.append(bg)
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * 260, rows * 276), (40, 40, 40, 255))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % cols) * 260, (i // cols) * 276))
    sheet.save(os.path.join(OUT, key + '.png'))
print('contact sheets:', len(sheets), '->', OUT)
