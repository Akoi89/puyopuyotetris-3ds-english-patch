"""Redraw the boot notice (logo/Attention.narc: two COMP RGB565 512x256
textures, white text on black) in English.

Member 0 is the anti-piracy notice, member 1 the "your name and location are
shown to other players online" notice. Writes patch/romfs/logo/Attention.narc
and notice_preview.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import narc, tex

SRC = 'tr_envoice/logo/Attention.narc'
OUT = 'patch/romfs/logo/Attention.narc'
FONT = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 15)
FONT_B = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 16)

TEXT = [
    ('< NOTICE >', [
        'Distributing or uploading this game software over the',
        'Internet without the permission of the rights holder,',
        'and downloading it while knowing it to be an illegal',
        'upload, are strictly prohibited by law.',
        'Thank you for your understanding and cooperation.',
    ]),
    (None, [
        'Your Mii nickname or system user name, your Club\'s name',
        'and the location you register will be shown to other',
        'players and third parties in the Internet and Multiplayer',
        'Arcade modes and in replay data. Please do not include',
        'anything offensive, anything that infringes the rights of',
        'others, anything illegal, or personal information.',
    ]),
]

arc = narc.read(SRC)
ms = list(arc['members'])
previews = []
for mi, (title, lines) in enumerate(TEXT):
    img, fmt, hdr = tex.comp_decode(ms[mi])
    assert fmt == tex.RGB565 and img.size == (512, 256)
    new = Image.new('RGBA', img.size, (0, 0, 0, 255))
    d = ImageDraw.Draw(new)
    y = 40 if title else 36
    if title:
        w = d.textlength(title, font=FONT_B); d.text(((512 - w) / 2, y), title, font=FONT_B, fill=(255, 255, 255, 255)); y += 26
    for t in lines:
        w = d.textlength(t, font=FONT); d.text(((512 - w) / 2, y), t, font=FONT, fill=(255, 255, 255, 255)); y += 22
    ms[mi] = tex.comp_encode(new, fmt, hdr, ms[mi])
    previews.append(new)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(narc.build(arc, ms))
sheet = Image.new('RGB', (512, 512)); sheet.paste(previews[0], (0, 0)); sheet.paste(previews[1], (0, 256)); sheet.save('notice_preview.png')
print('wrote', OUT, 'members', [len(m) for m in ms])
