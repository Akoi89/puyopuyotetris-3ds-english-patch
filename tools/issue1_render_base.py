"""Render base adventure bubbles through the real per-section Latin atlas, before and after the
1.0.15 re-wrap, at true pixel size.

    python _issue1_render_base.py   -> rewrap_render_gemini.png

The pink strip starts at 193 px, the widest line proven to draw cleanly on TheGershon's captures;
anything reaching into it is what was running past the bubble border.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
import os
from PIL import Image, ImageDraw
import mtx, preview
import _issue1_base_width as B

CAP = 193
BR, END = chr(0xf8fd), chr(0xf813)
ADV = 'tenp/text/adventure'
SPACE_PX = B.SPACE_PX
# the line the reporter photographed, plus the widest in the game and a spread of the rest
PICK = [('chapter02', 5, 1), ('chapter03', 3, 6), ('chapter04', 6, 11), ('chapter04', 6, 19),
        ('chapter04', 8, 45), ('chapter06', 3, 0), ('chapter02', 2, 35), ('chapter01', 6, 24)]


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
                if a['px'][(cy + y) * a['w'] + cx + x]:
                    xx, yy = pen + x, y0 + y
                    if 0 <= xx < img.width and 0 <= yy < img.height:
                        px[xx, yy] = (41, 82, 156, 255)
        pen += (bearing + wid) if wid else a['cw']
    return pen


rows = []
for stem, si, i in PICK:
    a = preview.atlas(os.path.join('romfs_110_tree', ADV, '%s_F1Japanese.narc' % stem), si)
    before = mtx.parse(os.path.join('_issue1_backup_base', '%sJapanese.mtx' % stem))[si][i]
    after = mtx.parse(os.path.join('patch', 'romfs', ADV, '%sJapanese.mtx' % stem))[si][i]
    for tag, t in (('1.0.14', before), ('1.0.15', after)):
        ls = [l for l in t.replace(END, '').split(BR) if l.strip()]
        img = Image.new('RGBA', (CAP + 45, 18 * len(ls) + 6), (255, 255, 238, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([CAP, 0, img.width - 1, img.height], fill=(255, 205, 205, 255))
        for k, l in enumerate(ls):
            draw_line(a, l, img, 0, 3 + 18 * k)
        rows.append(('%s sec %d #%d   %s' % (stem, si, i, tag), img))

W = max(r[1].width for r in rows) * 3 + 20
H = sum(r[1].height * 3 + 18 for r in rows) + 10
sheet = Image.new('RGB', (W, H), (30, 30, 30))
d = ImageDraw.Draw(sheet)
y = 5
for label, img in rows:
    d.text((10, y), label, fill=(230, 230, 230)); y += 12
    sheet.paste(img.resize((img.width * 3, img.height * 3), Image.NEAREST), (10, y))
    y += img.height * 3 + 6
sheet.save('rewrap_render_gemini.png')
print('wrote rewrap_render_gemini.png', sheet.size)
