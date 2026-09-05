"""Decode EVERY texture in the base game and the DLC (CTPK entries in every
format, and Sega's COMP members) into contact sheets for review.

    python survey2.py [base|dlc]

Writes tex_survey2/<root>/<dir>__<narc>.png (one sheet per archive, every
texture labelled, composited on dark grey so white text is visible) and
tex_survey2/<root>_index.txt listing archive, member, name, format, size.
"""
import os, sys, glob, struct
from PIL import Image, ImageDraw, ImageFont
import narc, labels, tex

ROOTS = {'base': 'tr_envoice', 'dlc': 'dlc_r'}
OUT = 'tex_survey2'
FONT = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 11)
MAXW = 1400
THUMB = 384          # longest side of a thumbnail


def sheet(items, title):
    """items: [(label, RGBA image)] -> one contact sheet image."""
    thumbs = []
    for label, img in items:
        s = min(1.0, THUMB / max(img.size))
        t = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.NEAREST) if s < 1 else img
        bg = Image.new('RGBA', t.size, (40, 40, 48, 255)); bg.alpha_composite(t)
        thumbs.append((label, bg))
    x = y = 8; rowh = 0; placed = []
    for label, t in thumbs:
        if x + t.width + 8 > MAXW and x > 8:
            x = 8; y += rowh + 24; rowh = 0
        placed.append((x, y, label, t)); x += t.width + 8; rowh = max(rowh, t.height)
    H = y + rowh + 40
    out = Image.new('RGB', (MAXW, H), (20, 20, 20)); d = ImageDraw.Draw(out)
    d.text((8, H - 16), title, font=FONT, fill=(200, 200, 200))
    for x, y, label, t in placed:
        out.paste(t, (x, y + 14)); d.text((x, y), label, font=FONT, fill=(255, 220, 120))
    return out


def run(which):
    root = ROOTS[which]
    os.makedirs(os.path.join(OUT, which), exist_ok=True)
    index = []
    for p in sorted(glob.glob(os.path.join(root, '**', '*.narc'), recursive=True)):
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        try:
            m = narc.read(p)
        except Exception:
            continue
        items = []
        for mi, b in enumerate(m['members']):
            if b[:4] == b'CTPK':
                for e in labels.ctpk_entries(b):
                    try:
                        img = tex.decode(b[e['off']:e['off'] + e['size']], e['w'], e['h'], e['fmt'])
                    except Exception as ex:
                        index.append((rel, mi, e['name'], e['fmt'], e['w'], e['h'], 'ERR %s' % ex)); continue
                    items.append(('m%d %s %s %dx%d' % (mi, e['name'], tex.NAMES.get(e['fmt'], e['fmt']), e['w'], e['h']), img))
                    index.append((rel, mi, e['name'], e['fmt'], e['w'], e['h'], 'ctpk'))
            elif b[:4] == b'COMP':
                try:
                    img, fmt, hdr = tex.comp_decode(b)
                except Exception as ex:
                    index.append((rel, mi, 'COMP', -1, 0, 0, 'ERR %s' % ex)); continue
                items.append(('m%d COMP %s %dx%d' % (mi, tex.NAMES.get(fmt, fmt), img.width, img.height), img))
                index.append((rel, mi, 'COMP', fmt, img.width, img.height, 'comp'))
        if items:
            name = rel.replace('/', '__')[:-5] + '.png'
            sheet(items, rel).save(os.path.join(OUT, which, name))
            print('sheet', rel, len(items), flush=True)
    with open(os.path.join(OUT, which + '_index.txt'), 'w', encoding='utf-8') as f:
        for r in index:
            f.write('%s\t%d\t%s\t%s\t%dx%d\t%s\n' % (r[0], r[1], r[2], tex.NAMES.get(r[3], r[3]), r[4], r[5], r[6]))
    print('index entries', len(index))


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'base')
