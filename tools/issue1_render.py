"""Render bubble lines through the real DLC atlas (preview.draw, true pixel size) inside a 215 px box,
before and after the re-wrap, for the four lines TheGershon photographed plus a few three-liners.

    python issue1_render.py   -> <scratch>/rewrap_render.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw
import mtx, preview
from issue1_model import ROOM, LIMIT, SPACE_PX
from check_glyphs import companions

SCR = 'issue1_scratch/'
BR, END = chr(0xf8fd), chr(0xf813)
PICK = [('0010', '08', 0, 1), ('0010', '08', 0, 7), ('0010', '08', 0, 9), ('0011', '09', 0, 10),
        ('0010', '08', 3, 4), ('0012', '10', 8, 14), ('0012', '10', 0, 7)]


def draw_line(a, text, img, x0, y0):
    pen = x0
    px = img.load()
    for c in text:
        cp = ord(c)
        if c == ' ':
            pen += SPACE_PX; continue
        i = a['recs'].get(cp)
        if i is None:
            pen += a['cw']; continue
        bearing, wid = a['widths'].get(cp, (0, a['cw']))
        if bearing > 0x7fffffff:
            bearing -= 1 << 32
        cx, cy = (i % a['cols']) * a['cw'], (i // a['cols']) * a['ch']
        for y in range(a['ch']):
            for x in range(a['cw']):
                v = a['px'][(cy + y) * a['w'] + cx + x]
                if v:
                    xx, yy = pen + x, y0 + y
                    if 0 <= xx < img.width and 0 <= yy < img.height:
                        px[xx, yy] = (40, 40, 120, 255)
        pen += (bearing + wid) if wid else a['cw']
    return pen


rows = []
for cid, ch, si, i in PICK:
    rel = '%s/data/chapter%sJapanese.mtx' % (cid, ch)
    cs = companions(rel, 'dlc_r')
    a = preview.atlas(os.path.join('patch_dlc2', cs[0]), 0)
    before = mtx.parse(os.path.join('issue1_backup', 'chapter%sJapanese.mtx' % ch))[si][i]
    after = mtx.parse(os.path.join('patch_dlc2', rel))[si][i]
    for tag, t in (('1.0.12', before), ('fixed', after)):
        ls = t.replace(END, '').split(BR)
        img = Image.new('RGBA', (ROOM + 60, 22 * len(ls) + 8), (255, 255, 238, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([ROOM, 0, ROOM + 59, img.height], fill=(255, 200, 200, 255))   # past the bubble border
        d.line([(LIMIT, 0), (LIMIT, img.height)], fill=(200, 200, 100, 255))
        for k, l in enumerate(ls):
            draw_line(a, l, img, 0, 4 + 22 * k)
        rows.append((('EX Act %s sec %d #%d  %s' % (ch, si, i, tag)), img))
W = max(r[1].width for r in rows) * 2 + 20
H = sum(r[1].height * 2 + 18 for r in rows) + 10
sheet = Image.new('RGB', (W, H), (30, 30, 30))
d = ImageDraw.Draw(sheet)
y = 5
for label, img in rows:
    d.text((10, y), label, fill=(230, 230, 230)); y += 12
    sheet.paste(img.resize((img.width * 2, img.height * 2), Image.NEAREST), (10, y)); y += img.height * 2 + 6
sheet.save(SCR + 'rewrap_render.png')
print('wrote rewrap_render.png', sheet.size)
