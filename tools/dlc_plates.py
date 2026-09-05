"""Redraw the DLC chapter plates on the Adventure map in English.

DLC contents 0010/0011/0012 each hold adv_DL1_0N.narc (64x16, "EXn 章") and
adv_DL2_0N.narc (128x16, the chapter title), one COMP ETC1A4 member each,
white text with alpha. Writes into patch_dlc2/<content>/data/ and a preview.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import narc, tex

PLATES = {
    '0010': ('EX Act 8', 'A Suzuran Dream'),
    '0011': ('EX Act 9', 'A Primp Dream'),
    '0012': ('EX Act 10', 'An Interstellar Dream'),
}
FONT = 'C:/Windows/Fonts/arialbd.ttf'
tiles = []
for content, (small, title) in PLATES.items():
    n = str(int(content, 16) - 0x10 + 1)          # 0010 -> _01, 0011 -> _02, 0012 -> _03
    for kind, text in (('adv_DL1_0%s' % n, small), ('adv_DL2_0%s' % n, title)):
        src = 'dlc_r/%s/data/%s.narc' % (content, kind)
        arc = narc.read(src); ms = list(arc['members'])
        img, fmt, hdr = tex.comp_decode(ms[0])
        w, h = img.size
        new = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(new)
        size = 14
        while size > 7:
            f = ImageFont.truetype(FONT, size)
            if d.textlength(text, font=f) <= w - 4:
                break
            size -= 1
        tw = d.textlength(text, font=f)
        d.text(((w - tw) / 2, (h - size) / 2 - 2), text, font=f, fill=(255, 255, 255, 255))
        ms[0] = tex.comp_encode(new, fmt, hdr, ms[0])
        out = 'patch_dlc2/%s/data/%s.narc' % (content, kind)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'wb').write(narc.build(arc, ms))
        back, _, _ = tex.comp_decode(ms[0])
        bg = Image.new('RGBA', (w, h), (30, 30, 60, 255)); bg.alpha_composite(back); tiles.append(bg)
        print('wrote', out, text, 'size', size)
sheet = Image.new('RGB', (128 * 3, 16 * len(tiles) + 4 * len(tiles)))
y = 0
for t in tiles:
    sheet.paste(t, (0, y)); y += t.height + 4
sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save('dlc_plates_preview.png')
