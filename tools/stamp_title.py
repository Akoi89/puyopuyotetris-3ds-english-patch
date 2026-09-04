"""Paint the version stamp on the title logo (title_tds2_d8888 in title/title.narc).

    python stamp_title.py "ENG 1.0.1" [<previously stamped title.narc>]

The stamp box is recovered by diffing the untouched fan texture against the
previously stamped one (default: the shipped 1.0.0 overlay in patch_backup*),
so the new text lands exactly where the old one did. The box is first restored
to the untouched pixels, then the text is drawn white with a dark outline,
auto-fitted to the box. Writes patch/romfs/title/title.narc and
title_stamp_preview.png.
"""
import glob, os, sys
from PIL import Image, ImageDraw, ImageFont
import narc, labels

text = sys.argv[1]
ORIG = 'tr_envoice/title/title.narc'
prev = sys.argv[2] if len(sys.argv) > 2 else sorted(glob.glob('patch_backup_*/title/title.narc'))[-1]
TEX = 'title_tds2_d8888'


def tex(path):
    m = narc.read(path)
    for mi, b in enumerate(m['members']):
        if b[:4] == b'CTPK':
            for e in labels.ctpk_entries(b):
                if e['name'] == TEX:
                    return m, mi, e, labels.dec(b[e['off']:e['off'] + e['size']], e['w'], e['h'], e['fmt'])
    raise SystemExit('texture not found')


mo, mi, e, orig = tex(ORIG)
_, _, _, old = tex(prev)
po, pn = orig.load(), old.load()
xs, ys = [], []
for y in range(e['h']):
    for x in range(e['w']):
        if po[x, y] != pn[x, y]:
            xs.append(x); ys.append(y)
if not xs:
    raise SystemExit('no stamp found in %s' % prev)
box = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
print('previous stamp box', box, 'in', prev)

img = orig.copy()
d = ImageDraw.Draw(img)
bw, bh = box[2] - box[0], box[3] - box[1]
size = bh
while size > 6:
    f = ImageFont.truetype(labels.FONT, size)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    if r - l <= bw and b - t <= bh:
        break
    size -= 1
x = box[2] - (r - l) - l                      # right-aligned in the box, like the 1.0.0 stamp
y = box[1] + (bh - (b - t)) // 2 - t
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        if dx or dy:
            d.text((x + dx, y + dy), text, font=f, fill=(40, 20, 60, 255))
d.text((x, y), text, font=f, fill=(255, 255, 255, 255))
print('drew %r at size %d, box %dx%d' % (text, size, bw, bh))

blob = bytearray(mo['members'][mi])
blob[e['off']:e['off'] + e['size']] = labels.enc(img, e['fmt'])
members = list(mo['members']); members[mi] = bytes(blob)
out = narc.build(mo, members)
os.makedirs('patch/romfs/title', exist_ok=True)
open('patch/romfs/title/title.narc', 'wb').write(out)
crop = img.crop((max(0, box[0] - 40), max(0, box[1] - 20), min(e['w'], box[2] + 20), min(e['h'], box[3] + 20)))
crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST).save('title_stamp_preview.png')
print('wrote patch/romfs/title/title.narc (%d bytes) and title_stamp_preview.png' % len(out))
