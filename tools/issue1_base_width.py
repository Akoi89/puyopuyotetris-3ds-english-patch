import sys; sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
"""Base-game bubble line widths, measured through each section's own Latin atlas.

The plain `chapterNNJapanese.narc` companion is Sega's Japanese font: every ASCII char misses and
falls back to `cw`, which is why a DLC-fitted model reads base lines as ~570 px. The Latin glyphs
live in `chapterNN_F1Japanese.narc`, and the FONTDATF member index equals the mtx section index
(verified: every drawn char of section i is present in member i, 0 missing, for chapters 00-07 and
general).

Chapters 01-07 and general carry the full 589-glyph font (gh 11, cw 13) in every member; chapter00
carries a per-section subset at gh 12, cw 14 - a different size, so its numbers are NOT on the same
scale and are reported separately.

Scale: width = sum of (bearing + advance), spaces charged SPACE_PX. Fitted 2026-09-17 against
TheGershon's chapter01 captures (issue #1) at SPACE_PX=4: model minus drawn = -1, +1, +1, +2, -2 px
over five lines of 46-206 px, i.e. the model is the drawn width to +/-2 px.

    python _issue1_base_width.py [limit]
"""
import os, sys, glob
import mtx
from _issue1_widths import atlas
from check_glyphs import companions

SPACE_PX = int(os.environ.get('SPACE_PX', '4'))
LIMIT = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1].isdigit()) else 200
BR, END = chr(0xf8fd), chr(0xf813)
ADV = 'tenp/text/adventure'


def w(a, ln):
    pen = 0
    for c in ln:
        if c == ' ':
            pen += SPACE_PX; continue
        bw = a['widths'].get(ord(c))
        pen += (bw[0] + bw[1]) if (bw and bw[1]) else a['cw']
    return pen


def scan(tree='romfs_110_tree'):
    out = []
    files = sorted(glob.glob(os.path.join(tree, ADV, 'chapter??Japanese.mtx'))) + \
            sorted(glob.glob(os.path.join(tree, ADV, 'generalJapanese.mtx')))
    for f in files:
        stem = os.path.basename(f)[:-len('Japanese.mtx')]
        fp = os.path.join(tree, ADV, '%s_F1Japanese.narc' % stem)
        for si, s in enumerate(mtx.parse(f)):
            a = atlas(fp, si)
            for i, t in enumerate(s):
                ls = t.replace(END, '').split(BR)
                nl = len([l for l in ls if l.strip()])
                for li, l in enumerate(ls):
                    if l.strip():
                        out.append((w(a, l), stem, si, i, li, nl, l))
    return out


if __name__ == '__main__':
    o = sorted(scan(), reverse=True)
    full = [h for h in o if h[1] != 'chapter00']
    c00 = [h for h in o if h[1] == 'chapter00']
    print('SPACE_PX=%d  limit=%d  lines: ch01-07+general %d, chapter00 %d (gh12 font, own scale)'
          % (SPACE_PX, LIMIT, len(full), len(c00)))
    for tag, rows in (('ch01-07+general', full), ('chapter00', c00)):
        over = [h for h in rows if h[0] > LIMIT]
        print('--- %s: %d over %d ---' % (tag, len(over), LIMIT))
        for h in over:
            print('  %3d  %-9s sec%-3d #%-4d ln%d/%d  %r' % h)
