"""Swap-mode call logotypes (tenp/swap/swap2p/swap2p.narc, pla_swap_notice_d4444):
the "Puyo Puyo" (green) and "Tetris" (pink) logos shown above the frame when
the mode switches mid-match. Only the logo cells are touched; the curved
"PUYO PUYO" / "TET RIS" lettering under them stays. Redrawn as bold condensed
Sega's official English "Puyo" / "Tetris" logos taken from Steam's swap2p_e.narc
(the same texture at 4x), scaled down to fill each logo cell.
Reads the fan tree, writes patch/romfs, saves swap_logos_preview.png.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import narc, labels2, tex

SRC = 'tr_envoice/tenp/swap/swap2p/swap2p.narc'
OUT = 'patch/romfs/tenp/swap/swap2p/swap2p.narc'
TEX = 'pla_swap_notice_d4444'
FONT = 'C:/Windows/Fonts/bahnschrift.ttf'

arc = narc.read(SRC); ms = list(arc['members'])
mi, e, img, fmt, hdr = labels2.get_texture(arc, TEX)
a = np.array(img).astype(int)

# the logo band: rows 97.. up to the blank row before the arc lettering, within x 0..160
ink = (a[:, :160, 3] > 64).sum(axis=1)
y0 = 94
while ink[y0] == 0:
    y0 += 1
y1 = y0
while y1 < 170 and ink[y1] > 0:
    y1 += 1
cols = (a[y0:y1, :, 3] > 64).any(axis=0)
runs, s = [], None
for x, v in enumerate(list(cols) + [False]):
    if v and s is None: s = x
    elif not v and s is not None: runs.append((s, x)); s = None
runs = [r for r in runs if r[1] - r[0] > 30][:2]
print('logo band y %d..%d, logo columns %s' % (y0, y1, runs))

# Official English logos: Steam's swap2p_e.narc member 3 holds this very texture at 4x
# (1024x1024, same layout), with "Puyo" and "Tetris" where the 3DS has the Japanese marks.
STEAM = 'steam_dump/swap2p_e_3_1.png'
st = Image.open(STEAM).convert('RGBA')
WINDOWS = {'Puyo': (20, 395, 305, 540), 'Tetris': (320, 390, 640, 540)}
px = img.load()
for (x0, x1), name in zip(runs, ('Puyo', 'Tetris')):
    box = (x0 - 2, y0 - 2, x1 + 2, y1 + 1)
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            px[x, y] = (0, 0, 0, 0)
    crop = st.crop(WINDOWS[name]); crop = crop.crop(crop.getbbox())
    bw, bh = box[2] - box[0], box[3] - box[1]
    sc = min(bw / crop.width, bh / crop.height)
    logo = crop.resize((max(1, round(crop.width * sc)), max(1, round(crop.height * sc))), Image.LANCZOS)
    pos = (box[0] + (bw - logo.width) // 2, box[1] + (bh - logo.height) // 2)
    img.alpha_composite(logo, pos)
    print('  %s: steam %s -> %dx%d at %s (scale %.3f)' % (name, crop.size, logo.width, logo.height, pos, sc))
m = bytearray(ms[mi]); m[e['off']:e['off'] + e['size']] = tex.encode(img, fmt); ms[mi] = bytes(m)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(narc.build(arc, ms))
crop = img.crop((0, 90, 256, 172)); bg = Image.new('RGBA', crop.size, (40, 40, 60, 255)); bg.alpha_composite(crop)
bg.resize((1024, 328), Image.NEAREST).save('swap_logos_preview.png')
print('wrote', OUT)
