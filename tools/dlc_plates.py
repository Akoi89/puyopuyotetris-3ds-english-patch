"""Redraw the DLC chapter plates on the Adventure map in English.

DLC contents 0010/0011/0012 each hold adv_DL1_0N.narc (64x16, "EXn 章") and
adv_DL2_0N.narc (128x16, the chapter title), one COMP ETC1A4 member each,
white text with alpha. The game shows only the part of the texture the
Japanese ink occupied (measured: x 5..52 on the small plate, x 3..87 on the
title plate; wider English was cut off on screen), so the English is fitted
into exactly that window, left-aligned at the Japanese ink's own left edge.
Writes into patch_dlc2/<content>/data/ and dlc_plates_preview.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import narc, tex

PLATES = {
    '0010': ('EX Act 8', 'A Suzuran Dream'),
    '0011': ('EX Act 9', 'A Primp Dream'),
    '0012': ('EX Act 10', 'An Interstellar Dream'),
}
WINDOW = {'adv_DL1': (5, 52), 'adv_DL2': (3, 87)}          # x0..x1 of the Japanese ink, measured
FONT = 'C:/Windows/Fonts/bahnschrift.ttf'      # variable font: Bold SemiCondensed / Bold Condensed give tall letters at plate width
OUTLINE = (12, 52, 28, 255)                        # the dark green Sega's Act plates use around white text


def load(size, variation):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(variation)
    return f

tiles = []
for content, (small, title) in PLATES.items():
    n = str(int(content, 16) - 0x10 + 1)
    for kind, text in (('adv_DL1_0%s' % n, small), ('adv_DL2_0%s' % n, title)):
        src = 'dlc_r/%s/data/%s.narc' % (content, kind)
        arc = narc.read(src); ms = list(arc['members'])
        img, fmt, hdr = tex.comp_decode(ms[0])
        w, h = img.size
        x0, x1 = WINDOW[kind[:7]]
        new = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(new)
        best = None
        for variation in ('Bold SemiCondensed', 'Bold Condensed'):
            size = 16
            while size > 6:
                f = load(size, variation)
                l, t, r, b = d.textbbox((0, 0), text, font=f, stroke_width=1)
                if r - l <= x1 - x0 and b - t <= h:
                    break
                size -= 1
            if best is None or size > best[0]:
                best = (size, variation, f, (l, t, r, b))
        size, variation, f, (l, t, r, b) = best
        d.text((x0 - l, (h - (b - t)) // 2 - t), text, font=f, fill=(255, 255, 255, 255), stroke_width=1, stroke_fill=OUTLINE)
        ms[0] = tex.comp_encode(new, fmt, hdr, ms[0])
        out = 'patch_dlc2/%s/data/%s.narc' % (content, kind)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'wb').write(narc.build(arc, ms))
        back, _, _ = tex.comp_decode(ms[0])
        bg = Image.new('RGBA', (w, h), (30, 60, 30, 255)); bg.alpha_composite(back)
        dd = ImageDraw.Draw(bg); dd.line([(x1, 0), (x1, h)], fill=(255, 0, 0, 255))
        tiles.append(bg)
        print('wrote', out, repr(text), variation, 'size', size, 'ink %dx%d of %dx%d' % (r - l, b - t, x1 - x0, h))
sheet = Image.new('RGB', (128, (16 + 4) * len(tiles)))
y = 0
for t in tiles:
    sheet.paste(t, (0, y)); y += 20
sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save('dlc_plates_preview.png')
print('preview: red line = right edge of the window the game shows')
