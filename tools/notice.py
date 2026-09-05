"""Redraw the boot notice (logo/Attention.narc: two COMP RGB565 512x256
textures, white text on black) in English.

Member 0 is the anti-piracy notice, member 1 the "your name and location are
shown to other players online" notice. The game only displays the left part
of each texture: Sega's Japanese block spans x 60..350, and an English render
centred on the full 512 width was cut off on screen. So the text is wrapped
to a 290 px column centred at x 205 (the Japanese block's own centre).
Writes patch/romfs/logo/Attention.narc and notice_preview.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import narc, tex

SRC = 'tr_envoice/logo/Attention.narc'
OUT = 'patch/romfs/logo/Attention.narc'
COLUMNS = [(205, 290), (179, 236)]      # (centre, max width) per member: top screen shows x ~60..350, bottom screen x ~70..315
FONT = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
FONT_B = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 15)

TEXT = [
    ('< NOTICE >',
     'Distributing or uploading this game software over the Internet without the '
     'permission of the rights holder, and downloading it while knowing it to be an '
     'illegal upload, are strictly prohibited by law. '
     'Thank you for your understanding and cooperation.'),
    (None,
     'Your Mii nickname or system user name, your Club\'s name and the location you '
     'register will be shown to other players and third parties in the Internet and '
     'Multiplayer Arcade modes and in replay data. Please do not include anything '
     'offensive, anything that infringes the rights of others, anything illegal, or '
     'personal information.'),
]


def wrap(d, text, font, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


arc = narc.read(SRC)
ms = list(arc['members'])
previews = []
for mi, (title, body) in enumerate(TEXT):
    img, fmt, hdr = tex.comp_decode(ms[mi])
    assert fmt == tex.RGB565 and img.size == (512, 256)
    new = Image.new('RGBA', img.size, (0, 0, 0, 255))
    d = ImageDraw.Draw(new)
    CENTRE, MAXW = COLUMNS[mi]
    lines = wrap(d, body, FONT, MAXW)
    total = (26 if title else 0) + 19 * len(lines)
    y = (256 - total) // 2 - 10
    if title:
        w = d.textlength(title, font=FONT_B); d.text((CENTRE - w / 2, y), title, font=FONT_B, fill=(255, 255, 255, 255)); y += 26
    for t in lines:
        w = d.textlength(t, font=FONT); d.text((CENTRE - w / 2, y), t, font=FONT, fill=(255, 255, 255, 255)); y += 19
    assert max(d.textlength(t, font=FONT) for t in lines) <= MAXW
    ms[mi] = tex.comp_encode(new, fmt, hdr, ms[mi])
    previews.append(new)
    print('member %d: %d lines, widest %.0f px, block x %d..%d' % (mi, len(lines), max(d.textlength(t, font=FONT) for t in lines), CENTRE - MAXW // 2, CENTRE + MAXW // 2))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(narc.build(arc, ms))
sheet = Image.new('RGB', (512, 512)); sheet.paste(previews[0], (0, 0)); sheet.paste(previews[1], (0, 256))
dd = ImageDraw.Draw(sheet); dd.line([(350, 0), (350, 256)], fill=(255, 0, 0), width=1); dd.line([(60, 0), (60, 256)], fill=(255, 0, 0), width=1); dd.line([(315, 256), (315, 512)], fill=(255, 0, 0), width=1); dd.line([(70, 256), (70, 512)], fill=(255, 0, 0), width=1)
sheet.save('notice_preview.png')
print('wrote', OUT, '(red lines = visible window: top x 60..350, bottom x 70..315)')
