"""Compose the top 44 rows of the four bubble screenshots at 3x with a 10px ruler, to read the
bubble border and text extents by eye."""
from PIL import Image, ImageDraw

S = 'issue1_scratch/'
strips = []
for n in (1, 2, 3, 4):
    im = Image.open(S + 'img%d.png' % n).convert('RGB').crop((0, 0, 400, 44))
    strips.append(im.resize((1200, 132), Image.NEAREST))
out = Image.new('RGB', (1200, 132 * 4 + 20), (0, 0, 0))
d = ImageDraw.Draw(out)
for i, s in enumerate(strips):
    out.paste(s, (0, i * 132))
for x in range(0, 400, 10):
    d.line([(x * 3, 132 * 4), (x * 3, 132 * 4 + (12 if x % 50 == 0 else 6))], fill=(255, 255, 0))
    if x % 50 == 0:
        d.text((x * 3 + 2, 132 * 4 + 8), str(x), fill=(255, 255, 0))
out.save(S + 'strips.png')
print('ok')
