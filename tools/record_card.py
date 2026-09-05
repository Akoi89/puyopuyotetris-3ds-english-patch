"""Endless-mode record card (toko/toko.narc): a dedicated redraw, because the
generic label pass cannot erase text that sits on a gradient plate.

  pla_tournament_d4444  "Best Record" plate (orange), "This Run" plate (cyan),
                        two "players beaten" suffixes (orange, blue)
  num_tournament_d4444  "players beaten" suffix (green)

Each plate's text band is inpainted row by row from the plate's own untouched
interior columns (the gradient is vertical), then the English is drawn in the
original style: white fill with the plate's accent outline. Runs AFTER
labels2.py apply (which rewrites toko.narc) and reads/writes patch/romfs.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import narc, labels, labels2, tex

ARC = 'patch/romfs/toko/toko.narc'
FONT = labels.FONT


def fit(d, text, maxw, maxh, start=20):
    size = start
    while size > 6:
        f = ImageFont.truetype(FONT, size)
        l, t, r, b = d.textbbox((0, 0), text, font=f, stroke_width=1)
        if r - l <= maxw and b - t <= maxh:
            return f, (l, t, r, b)
        size -= 1
    return f, (l, t, r, b)


def draw_centre(d, box, text, fill, outline, start=20):
    x0, y0, x1, y1 = box
    f, (l, t, r, b) = fit(d, text, x1 - x0 - 2, y1 - y0 - 1, start)
    d.text((x0 + ((x1 - x0) - (r - l)) / 2 - l, y0 + ((y1 - y0) - (b - t)) / 2 - t), text, font=f, fill=fill, stroke_width=1, stroke_fill=outline)


def inpaint_band(img, box, sample_x):
    """Fill box rows with that row's dominant plate colour: the median of the
    plate-interior pixels that are neither the white text, its red/blue
    outline, nor the dark shadow (the gradient is vertical, so per row is exact)."""
    a = np.array(img).astype(int); px = img.load(); x0, y0, x1, y1 = box
    for y in range(y0, y1):
        row = a[y, 4:86]
        keep = (row[:, 3] > 200) & ~((row[:, :3] > 200).all(axis=1)) & ~((row[:, 0] > 150) & (row[:, 1] < 120)) & ~((row[:, 2] > 150) & (row[:, 0] < 120)) & (row[:, :3].sum(axis=1) > 240)
        src = row[keep][:, :3] if keep.sum() >= 4 else a[y - 1, x0:x1, :3]
        c = tuple(int(v) for v in np.median(src, axis=0)) + (255,)
        for x in range(x0, x1):
            px[x, y] = c


def ink_box(a, x0, y0, x1, y1, thr=32, pad=2):
    m = a[y0:y1, x0:x1, 3] > thr
    ys, xs = np.where(m)
    return (max(0, x0 + int(xs.min()) - pad), max(0, y0 + int(ys.min()) - pad), min(a.shape[1], x0 + int(xs.max()) + 1 + pad), min(a.shape[0], y0 + int(ys.max()) + 1 + pad))


def redraw_transparent(img, a, box, text, start=14):
    """Erase everything in box (transparent background) and draw text using the
    box's own brightest and darkest ink colours."""
    x0, y0, x1, y1 = box
    crop = a[y0:y1, x0:x1]; op = crop[:, :, 3] > 128
    cols = crop[op][:, :3]; lum = cols.sum(axis=1)
    fill = tuple(int(v) for v in cols[lum.argmax()]) + (255,); line = tuple(int(v) for v in cols[lum.argmin()]) + (255,)
    px = img.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            px[x, y] = (0, 0, 0, 0)
    draw_centre(ImageDraw.Draw(img), box, text, fill, line, start)


arc = narc.read(ARC); ms = list(arc['members'])

# --- pla_tournament -----------------------------------------------------------
mi, e, img, fmt, hdr = labels2.get_texture(arc, 'pla_tournament_d4444')
a = np.array(img).astype(int)
d = ImageDraw.Draw(img)
# plate interiors: sample column 86 (inside the plate, right of the text)
top = (5, 8, 85, 32); bot = (5, 74, 85, 98)
inpaint_band(img, top, 86); inpaint_band(img, bot, 86)
draw_centre(d, top, 'Best Record', (255, 255, 255, 255), (205, 40, 20, 255))
draw_centre(d, bot, 'This Run', (255, 255, 255, 255), (40, 120, 220, 255))
# the two suffixes to the right: find their rows from the alpha
rows = (a[:, 92:128, 3] > 128).any(axis=1)
runs, s = [], None
for y, v in enumerate(list(rows) + [False]):
    if v and s is None: s = y
    elif not v and s is not None: runs.append((s, y)); s = None
print('suffix rows on pla_tournament:', runs)
for y0, y1 in runs[:2]:
    box = ink_box(a, 88, y0, 128, y1)
    redraw_transparent(img, a, box, 'beaten')
    print('  suffix box', box)
m = bytearray(ms[mi]); m[e['off']:e['off'] + e['size']] = tex.encode(img, fmt); ms[mi] = bytes(m)

# --- num_tournament -----------------------------------------------------------
mi2, e2, img2, fmt2, hdr2 = labels2.get_texture(arc, 'num_tournament_d4444')
a2 = np.array(img2).astype(int)
box = ink_box(a2, 74, 0, 128, 16)
redraw_transparent(img2, a2, box, 'beaten')
print('num_tournament suffix box', box)
m = bytearray(ms[mi2]); m[e2['off']:e2['off'] + e2['size']] = tex.encode(img2, fmt2); ms[mi2] = bytes(m)

open(ARC, 'wb').write(narc.build(arc, ms))
from survey2 import sheet
sheet([('pla_tournament', img.resize((384, 384), Image.NEAREST)), ('num_tournament', img2.resize((384, 192), Image.NEAREST))], 'record card').save('toko_after.png')
print('wrote', ARC, 'and toko_after.png')
