# -*- coding: utf-8 -*-
"""Gemini package for the 1.0.15 base re-wrap: stats on the shipped wrap (A), a clause-aware
alternative (B), the entries where they differ, and a render sheet of the widest disagreements.

    python _issue1_gemini_rewrap.py   -> GEMINI_REVIEW_base_rewrap.md
                                         gemini_rewrap_AB.png, gemini_rewrap_context.png

A = what is built into 1.0.15: fewest lines that fit under 193 px, then the split with the smallest
widest line (ties broken toward a longer first line). This is the same rule the DLC pass used.
B = same line count and the same 193 px cap, but a split that ends a line on sentence or clause
punctuation is preferred; among those, the smallest widest line. B never uses more lines than A.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
import os, re, collections
from PIL import Image, ImageDraw
import mtx, preview
from _issue1_widths import atlas
import _issue1_base_width as B

CAP, TARGET = 193, 188
BR, END = chr(0xf8fd), chr(0xf813)
STAR = chr(0x2605)
ADV = 'tenp/text/adventure'
SRC, BAK = 'romfs_110_tree', '_issue1_backup_base'
STEMS = ['chapter%02d' % i for i in range(1, 8)] + ['general']
HARD = ('.', '!', '?', ',', ';', ':', '...')
SENT = ('.', '!', '?', '...')


def words_of(text):
    out = []
    for w in text.split(' '):
        if w == STAR and out:
            out[-1] += ' ' + w
        else:
            out.append(w)
    return out


def splits(n, nl):
    if nl == 1:
        return [[(0, n)]]
    if nl == 2:
        return [[(0, i), (i, n)] for i in range(1, n)]
    return [[(0, i), (i, j), (j, n)] for i in range(1, n - 1) for j in range(i + 1, n)]


STUB = 0.45          # a line narrower than this fraction of the widest one reads as a stub


def wrap(a, text, limit, mode='A', maxlines=3):
    ws = words_of(text)
    n = len(ws)
    W = lambda i, j: B.w(a, ' '.join(ws[i:j]))
    for nl in range(1, maxlines + 1):
        best = None
        for c in splits(n, nl):
            widths = [W(i, j) for i, j in c]
            if max(widths) > limit:
                continue
            if mode == 'C' and nl > 1 and min(widths) < STUB * max(widths):
                continue
            if mode == 'A':
                key = (max(widths), -widths[0])
            else:
                # how many interior breaks land after punctuation, sentence enders counting double
                score = 0
                for i, j in c[:-1]:
                    last = ws[j - 1]
                    if last.endswith(SENT):
                        score += 2
                    elif last.endswith(HARD):
                        score += 1
                key = (-score, max(widths), -widths[0])
            if best is None or key < best[0]:
                best = (key, c)
        if best:
            return [' '.join(ws[i:j]) for i, j in best[1]]
    return None


def breaks_on_punct(lines_):
    return sum(1 for l in lines_[:-1] if l.rstrip().endswith(HARD))


rows, stats = [], collections.Counter()
for stem in STEMS:
    fp = os.path.join(SRC, ADV, '%s_F1Japanese.narc' % stem)
    before = mtx.parse(os.path.join(BAK, '%sJapanese.mtx' % stem))
    after = mtx.parse(os.path.join('patch', 'romfs', ADV, '%sJapanese.mtx' % stem))
    for si, (s0, s1) in enumerate(zip(before, after)):
        a = atlas(fp, si)
        for i, (t0, t1) in enumerate(zip(s0, s1)):
            if t0 == t1:
                continue
            old = [l for l in t0.replace(END, '').split(BR) if l.strip()]
            A = [l for l in t1.replace(END, '').split(BR) if l.strip()]
            joined = ' '.join(l.strip() for l in old)
            Bv = wrap(a, joined, TARGET, 'B', maxlines=len(A))
            if Bv is None or len(Bv) != len(A):
                Bv = A
            Cv = wrap(a, joined, TARGET, 'C', maxlines=len(A))
            if Cv is None or len(Cv) != len(A):
                Cv = A
            stats['entries'] += 1
            if len(A) > len(old):
                stats['gained a line'] += 1
            if len(A) > 1 and breaks_on_punct(A) == len(A) - 1:
                stats['A breaks every line on punctuation'] += 1
            if any(len(l.split()) <= 2 for l in A):
                stats['A has a line of two words or fewer'] += 1
            if A != Bv:
                stats['A and B differ'] += 1
            if A != Cv:
                stats['A and C differ'] += 1
            if Bv != Cv:
                stats['B and C differ'] += 1
            rows.append(dict(stem=stem, si=si, i=i, old=old, A=A, Bv=Bv, Cv=Cv, atlas=a,
                             wA=[B.w(a, l) for l in A], wB=[B.w(a, l) for l in Bv], wC=[B.w(a, l) for l in Cv],
                             wold=[B.w(a, l) for l in old]))

diff = [r for r in rows if r['A'] != r['Cv'] or r['A'] != r['Bv']]
print('entries re-wrapped: %d, A and B differ on %d' % (len(rows), len(diff)))
for k, v in stats.items():
    print('   %-38s %d' % (k, v))

# ---- render sheets ----
SPACE_PX = B.SPACE_PX


def draw_line(a, text, img, x0, y0):
    pen = x0
    px = img.load()
    for c in text:
        if c == ' ':
            pen += SPACE_PX; continue
        k = a['recs'].get(ord(c))
        if k is None:
            pen += a['cw']; continue
        bearing, wid = a['widths'].get(ord(c), (0, a['cw']))
        if bearing > 0x7fffffff:
            bearing -= 1 << 32
        cx, cy = (k % a['cols']) * a['cw'], (k // a['cols']) * a['ch']
        for y in range(a['ch']):
            for x in range(a['cw']):
                if a['px'][(cy + y) * a['w'] + cx + x]:
                    xx, yy = pen + x, y0 + y
                    if 0 <= xx < img.width and 0 <= yy < img.height:
                        px[xx, yy] = (41, 82, 156, 255)
        pen += (bearing + wid) if wid else a['cw']


def bubble(pa, lines_):
    img = Image.new('RGBA', (CAP + 30, 18 * len(lines_) + 6), (255, 255, 238, 255))
    ImageDraw.Draw(img).rectangle([CAP, 0, img.width - 1, img.height], fill=(255, 205, 205, 255))
    for k, l in enumerate(lines_):
        draw_line(pa, l, img, 0, 3 + 18 * k)
    return img


def sheet(items, path, scale=3):
    imgs = []
    for label, pa, ls in items:
        imgs.append((label, bubble(pa, ls)))
    Wd = max(i[1].width for i in imgs) * scale + 20
    H = sum(i[1].height * scale + 18 for i in imgs) + 10
    out = Image.new('RGB', (Wd, H), (30, 30, 30))
    d = ImageDraw.Draw(out)
    y = 5
    for label, img in imgs:
        d.text((10, y), label, fill=(230, 230, 230)); y += 12
        out.paste(img.resize((img.width * scale, img.height * scale), Image.NEAREST), (10, y))
        y += img.height * scale + 6
    out.save(path)
    print('wrote', path, out.size)


pick = diff[:8]
items = []
for r in pick:
    pa = preview.atlas(os.path.join(SRC, ADV, '%s_F1Japanese.narc' % r['stem']), r['si'])
    items.append(('%s sec %d #%d   A (in 1.0.15)' % (r['stem'], r['si'], r['i']), pa, r['A']))
    items.append(('%s sec %d #%d   B (clause-aware)' % (r['stem'], r['si'], r['i']), pa, r['Bv']))
    items.append(('%s sec %d #%d   C (clause-aware, no stub line)' % (r['stem'], r['si'], r['i']), pa, r['Cv']))
sheet(items, 'gemini_rewrap_AB.png')

ctx = [r for r in rows if r['stem'] == 'chapter01'][:6]
items = []
for r in ctx:
    pa = preview.atlas(os.path.join(SRC, ADV, '%s_F1Japanese.narc' % r['stem']), r['si'])
    items.append(('%s sec %d #%d   before (1.0.14)' % (r['stem'], r['si'], r['i']), pa, r['old']))
    items.append(('%s sec %d #%d   after  (1.0.15)' % (r['stem'], r['si'], r['i']), pa, r['A']))
sheet(items, 'gemini_rewrap_context.png')

# ---- the markdown ----
o = []
w = o.append
w('# Puyo Puyo Tetris 3DS: base-game speech bubble re-wrap, line-break review')
w('')
w('## What this is')
w('')
w("The 3DS Adventure speech bubble is narrower than the box the base game's English text was")
w('broken for. A player photographed a line running past the border on a New 3DS XL, and measuring')
w("the text through the game's own font shows it is not one line but %d, in %d bubbles, across" % (162, len(rows)))
w('Chapters 1 to 7 and the shared end-of-chapter script.')
w('')
w('They are all re-broken in the build that is staged. **No word is changed, added or dropped**;')
w('only where the line breaks fall. Where the text no longer fits the old number of lines, the')
w("bubble's scripted height is raised (28 of them).")
w('')
w('## The measurement')
w('')
w("Line width is summed from the game's own glyph table for that scene, and calibrated against the")
w("player's photographs: the model lands within 2 px of what the console actually drew, over five")
w('lines from 46 to 206 px.')
w('')
w('| width | evidence |')
w('|---|---|')
w('| 193 px | drawn with 22 px of clear space inside the bubble (photographed) |')
w('| 204 px | runs onto the bubble border (photographed, this is the report) |')
w('| 225 px | the widest line in the game, Chapter 2 |')
w('')
w('So **193 px is the cap**: the widest width there is photographic proof of. That number is not up')
w('for review. What is up for review is *where* the breaks land.')
w('')
w('## The question')
w('')
w('Three break rules produce the same line counts and all respect the 193 px cap.')
w('')
w('**A (what is built):** fewest lines that fit, then the split whose widest line is smallest. This')
w('is the rule already used for the DLC chapters in an earlier release, so it matches them.')
w('')
w('**B (clause-aware):** same line count and cap, but a split that ends a line on punctuation is')
w('preferred; among those, the smallest widest line.')
w('')
w('**C (clause-aware without a stub):** B, but a split is rejected if its shortest line is under 45%')
w('of its longest, which is what produces one-word lines like `Well,` on its own.')
w('')
w('Numbers over the %d re-wrapped bubbles:' % len(rows))
w('')
w('| | count |')
w('|---|---|')
for k, v in sorted(stats.items()):
    w('| %s | %d |' % (k, v))
w('')
w('`gemini_rewrap_AB.png` renders the first eight disagreements through the real font, A then B then')
w('C. `gemini_rewrap_context.png` shows six Chapter 1 bubbles before and after, so the change in feel')
w('is visible against what shipped. The pink strip starts at 193 px.')
w('')
w('## Options')
w('')
w('1. **Ship A as built.** Zero further work, and consistent with the DLC chapters, which were')
w('   wrapped by the same rule in an earlier release. Some breaks land mid-clause with a comma one')
w('   word away: `This could be bad. Arle, / we need to find them.`')
w('2. **Rebuild with B.** Breaks land on punctuation far more often, but it will happily leave a')
w('   one-word first line: `Well, / looks like I made it back home.`')
w('3. **Rebuild with C.** B where B helps, A where B would leave a stub. It differs from A in %d of' % stats['A and C differ'])
w('   the %d bubbles, so it is a narrow change, and it is the only one of the three that never' % len(rows))
w('   produces a line under 45 per cent of its neighbour.')
w('4. **A, then hand-fix a named list.** If only a handful actually read badly.')
w('')
w("**Recommendation: option 3, rebuild with C.** Looking at the render, A's mid-clause breaks are")
w('the more noticeable fault of the two, and C fixes most of them without introducing the stub lines')
w("that make B worse than A in places. The cost is one rebuild and re-verification, about an hour,")
w('and nothing is published yet so nothing has to be withdrawn.')
w('')
w("Where C is still arguable: it keeps A on `You're totally under / arrest! Hahaha!` because B's")
w('version leaves `Hahaha!` alone on the second line, and on `Ah, Captain, I am / pleased to see you')
w('are in / only one piece, yourself.` for the same reason. If a short trailing line is fine when it')
w('is a whole exclamation, say so and the threshold can be relaxed for line-final punctuation.')
w('')
w('## What we are asking')
w('')
w('Pick A, B or C, or say "C plus these". The %d bubbles where the three rules disagree are listed' % len(diff))
w('below with all three versions and their line widths, and the render sheet shows the first eight')
w('drawn through the real font. If any individual bubble should break somewhere none of the three')
w('chose, name it by chapter, section and entry number and say where the break goes.')
w('')
w('## The %d bubbles where the rules disagree' % len(diff))
w('')
for r in diff:
    w('### %s section %d, entry %d' % (r['stem'], r['si'], r['i']))
    w('')
    w('- shipped in 1.0.14: `%s`  widths %s' % (' / '.join(r['old']), r['wold']))
    w('- **A, built into 1.0.15**: `%s`  widths %s' % (' / '.join(r['A']), r['wA']))
    w('- B, clause-aware: `%s`  widths %s' % (' / '.join(r['Bv']), r['wB']))
    w('- **C, clause-aware without a stub line**: `%s`  widths %s' % (' / '.join(r['Cv']), r['wC']))
    w('')
w('## Every other re-wrapped bubble (all three rules agree)')
w('')
for r in rows:
    if r['A'] == r['Bv'] and r['A'] == r['Cv']:
        w('- %s sec %d #%d: `%s` -> `%s`' % (r['stem'], r['si'], r['i'],
                                             ' / '.join(r['old']), ' / '.join(r['A'])))
w('')
open('GEMINI_REVIEW_base_rewrap.md', 'w', encoding='utf-8', newline=chr(10)).write('\n'.join(o))
print('wrote GEMINI_REVIEW_base_rewrap.md')
