"""Redraw the Options-screen prefecture list (mydata/option/option.narc,
texture TDS_option04_d4444) in English.

The fan patch never touched it: 未設定 ("Not set"), the 47 prefectures in two
styles, and ON/OFF, laid out on a 5-column x 21-row grid of 48x24 cells. Names
are romanised exactly as on the online-ranking buttons (labels_en_p2.json).
Writes patch/romfs/mydata/option/option.narc and prefectures_preview.png.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import narc, labels

SRC = 'tr_envoice/mydata/option/option.narc'
OUT = 'patch/romfs/mydata/option/option.narc'
TEX = 'TDS_option04_d4444'
COL_X = [36, 84, 132, 180, 228]          # cell centres
ROW_Y0, PITCH, CELL_W, CELL_H = 4, 24, 46, 16

EAST = ['Yamagata', 'Fukushima', 'Ibaraki', 'Tochigi', 'Gunma', 'Saitama', 'Chiba', 'Tokyo',
        'Kanagawa', 'Niigata', 'Toyama', 'Ishikawa', 'Fukui', 'Yamanashi', 'Nagano', 'Gifu',
        'Shizuoka', 'Aichi', 'Mie', 'Shiga', 'Kyoto']
WEST = ['Osaka', 'Hyogo', 'Nara', 'Wakayama', 'Tottori', 'Shimane', 'Okayama', 'Hiroshima',
        'Yamaguchi', 'Tokushima', 'Kagawa', 'Ehime', 'Kochi', 'Fukuoka', 'Saga', 'Nagasaki',
        'Kumamoto', 'Oita', 'Miyazaki', 'Kagoshima', 'Okinawa']
NORTH = ['Not set', 'Hokkaido', 'Aomori', 'Iwate', 'Miyagi', 'Akita']

grid = {}
for r, n in enumerate(EAST):
    grid[(1, r)] = n; grid[(2, r)] = n
for r, n in enumerate(WEST):
    grid[(3, r)] = n; grid[(4, r)] = n
for r, n in enumerate(NORTH):
    grid[(0, r)] = n; grid[(0, r + 6)] = n
# (0, 12..15) are ON / ON / OFF / OFF: already Latin, left alone

arc = narc.read(SRC)
ms = list(arc['members'])
mi = next(i for i, b in enumerate(ms) if b[:4] == b'CTPK')
m = bytearray(ms[mi])
e = {x['name']: x for x in labels.ctpk_entries(m)}[TEX]
img = labels.dec(m[e['off']:e['off'] + e['size']], e['w'], e['h'], e['fmt'])
d = ImageDraw.Draw(img)
px = img.load()

for (c, r), name in sorted(grid.items()):
    cx, y0 = COL_X[c], ROW_Y0 + r * PITCH
    x0, x1, y1 = cx - 24, cx + 24, y0 + CELL_H
    crop = np.array(img.crop((x0, y0, x1, y1))).astype(int)
    opaque = crop[:, :, 3] > 128
    if not opaque.any():
        raise SystemExit('empty cell %d,%d' % (c, r))
    cols = crop[opaque][:, :3]; lum = cols.sum(axis=1)
    fill = tuple(int(v) for v in cols[lum.argmax()]); line = tuple(int(v) for v in cols[lum.argmin()])
    for yy in range(y0, y1):                    # erase the Japanese ink (transparent background here)
        for xx in range(x0, x1):
            px[xx, yy] = (0, 0, 0, 0)
    size = CELL_H - 2
    while size > 6:
        font = ImageFont.truetype(labels.FONT, size)
        if d.textlength(name, font=font) + 2 <= CELL_W:
            break
        size -= 1
    tw = d.textlength(name, font=font)
    d.text((cx - tw / 2, y0 - 1), name, font=font, fill=fill, stroke_width=1, stroke_fill=line)

m[e['off']:e['off'] + e['size']] = labels.enc(img, e['fmt'])
ms[mi] = bytes(m)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(narc.build(arc, ms))
img.resize((img.width * 2, img.height * 2), Image.NEAREST).save('prefectures_preview.png')
print('redrew %d cells -> %s' % (len(grid), OUT))
