"""Issue #1 round 3 (TheGershon, 2026-09-17): re-wrap the BASE adventure bubble text so no line is
wider than the 3DS speech bubble.

1.0.13 did this for the DLC EX chapters only. The base never got a width pass because
check_glyphs.companions() hands back Sega's Japanese font narc for base chapters, so every ASCII
char misses the table and falls back to the cell width; base lines read as ~570 px and the scan was
never run. The Latin glyphs are in chapterNN_F1Japanese.narc, FONTDATF member index == mtx section
index (see _issue1_base_width.py, which also carries the +/-2 px calibration against the reporter's
console captures).

Ceiling, measured off those captures: the bubble fill leaves about 209 px of room on the first line
of a slot-0 bubble and about 214 on slot 1, and the border ring is drawn about 6 px inside the fill.
His overflowing line is 204 and his widest clean line is 193. FLAG 198 therefore sits about 5 px
under the tightest usable width; everything over it is re-wrapped, to a TARGET of 190 so the lines
that do get touched come out with real margin.

    python _issue1_rewrap_base.py nulltest   mtx.build(mtx.parse(f)) must equal the shipped bytes
    python _issue1_rewrap_base.py review     -> _issue1_rewrap_base_review.md, every entry before/after
    python _issue1_rewrap_base.py apply      -> patch/romfs/tenp/text/adventure/*.mtx

Rules, same as the DLC pass: only entries with a line over FLAG are touched; the words are never
changed; the joined text is wrapped into the fewest lines that fit, then the split with the smallest
widest line; at most 3 lines (Sega's own Japanese uses up to 3); the terminator U+F813 is kept;
debug table rows are never touched; nothing else in the file moves.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
import os, re, shutil
import mtx
from _issue1_widths import atlas
import _issue1_base_width as B

FLAG = int(os.environ.get('FLAG', '198'))
TARGET = int(os.environ.get('TARGET', '190'))
MAXLINES = 3
BR, END = chr(0xf8fd), chr(0xf813)
STAR = chr(0x2605)
ADV = 'tenp/text/adventure'
SRC = 'romfs_110_tree'
DST = os.path.join('patch', 'romfs')
BAK = '_issue1_backup_base'
# chapter00 is ours already and uses the other (gh 12) font; its widest drawn English line is 193
# in that font's units, so it is not in this pass.
STEMS = ['chapter%02d' % i for i in range(1, 8)] + ['general']


def is_debug(t):
    return re.match(r'^[A-Z][A-Z0-9_]{1,10}[_ ]?\d*\s+\d+\s*//', t) is not None


HARD = ('.', '!', '?', ',', ';', ':')
SENT = ('.', '!', '?')
STUB = 0.45          # a line this much narrower than the widest reads as an orphan...
# ...unless it is a complete exclamation. Gemini's verdict, 2026-09-17: rule C (prefer a break on
# punctuation, but never leave a stub) with the stub rule relaxed for a line ending in . ! or ?
# Six bubbles were named in that verdict. Four of them fall out of the relaxed rule on their own.
# Two do not, because their short line ends in a comma rather than sentence punctuation, and
# relaxing for commas would bring back the "Well," orphans the rule exists to stop. Those two are
# listed here instead, so the exception is visible rather than buried in a threshold.
OVERRIDES = {('chapter04', 6, 19): ['Hey,', 'you are besmirching my honor!'],
             ('chapter04', 8, 45): ['After all that,', 'we have to battle her ANYHOW!'],
             # the verdict named this bubble as one the relaxation should fix. It does not fall out
             # of the rule: two splits tie on punctuation score and the narrower one wins, which is
             # the one that breaks "pleased to / see". This is the version the verdict was shown.
             ('chapter02', 2, 35): ['Ah, Captain,', 'I am pleased to see you are',
                                    'in only one piece, yourself.']}


def wrap(a, text, limit, maxlines=MAXLINES):
    """Fewest lines that fit; then most breaks landing on punctuation; then the smallest widest
    line. A line under STUB of the widest is rejected unless it ends a sentence."""
    words = []
    for w in text.split(' '):
        if w == STAR and words:              # the star icon stays glued to the word before it
            words[-1] += ' ' + w
        else:
            words.append(w)
    n = len(words)
    W = lambda i, j: B.w(a, ' '.join(words[i:j]))
    for nl in range(1, maxlines + 1):
        best = None
        if nl == 1:
            cands = [[(0, n)]]
        elif nl == 2:
            cands = [[(0, i), (i, n)] for i in range(1, n)]
        else:
            cands = [[(0, i), (i, j), (j, n)] for i in range(1, n - 1) for j in range(i + 1, n)]
        for c in cands:
            ws = [W(i, j) for i, j in c]
            if max(ws) > limit:
                continue
            if nl > 1 and any(w_ < STUB * max(ws) and not words[j - 1].endswith(SENT)
                              for w_, (i, j) in zip(ws, c)):
                continue
            score = 0
            for i, j in c[:-1]:
                last = words[j - 1]
                if last.endswith(SENT):
                    score += 2
                elif last.endswith(HARD):
                    score += 1
            key = (-score, max(ws), -ws[0])
            if best is None or key < best[0]:
                best = (key, c)
        if best:
            return [' '.join(words[i:j]) for i, j in best[1]]
    return None


def source(stem):
    """The 1.0.14 file: the backup if this has already been applied once, else the stock tree."""
    b = os.path.join(BAK, '%sJapanese.mtx' % stem)
    return b if os.path.exists(b) else os.path.join(SRC, ADV, '%sJapanese.mtx' % stem)


def process(stem):
    path = os.path.join(DST, ADV, '%sJapanese.mtx' % stem)
    fp = os.path.join(SRC, ADV, '%s_F1Japanese.narc' % stem)
    raw = open(source(stem), 'rb').read()
    W = mtx.width(raw)
    secs = mtx._read(raw, W)
    new, changes, fails = [], [], []
    for si, s in enumerate(secs):
        a = atlas(fp, si)
        row = []
        for i, t in enumerate(s):
            ls = [l for l in t.replace(END, '').split(BR) if l.strip()]
            if not ls or is_debug(t) or not any(c.isascii() and c.isalpha() for c in t):
                row.append(t); continue
            widths = [B.w(a, l) for l in ls]
            if max(widths) <= FLAG:
                row.append(t); continue
            has_end = t.endswith(END)
            joined = ' '.join(l.strip() for l in ls)
            nw = OVERRIDES.get((stem, si, i)) or wrap(a, joined, TARGET)
            if nw is None:
                fails.append((si, i, ' '.join(ls))); row.append(t); continue
            assert ' '.join(nw).split() == joined.split(), 'override changes the words: %s %d %d' % (stem, si, i)
            assert max(B.w(a, l) for l in nw) <= FLAG, 'override is over the cap: %s %d %d' % (stem, si, i)
            row.append(BR.join(nw) + (END if has_end else ''))
            changes.append((si, i, ls, widths, nw, [B.w(a, l) for l in nw]))
        new.append(row)
    return path, raw, W, secs, new, changes, fails


def widest(path, fp, skip_debug=True):
    out = 0
    for si, s in enumerate(mtx.parse(path)):
        a = atlas(fp, si)
        for t in s:
            if skip_debug and is_debug(t):
                continue
            if not any(c.isascii() and c.isalpha() for c in t):
                continue
            for l in t.replace(END, '').split(BR):
                if l.strip():
                    out = max(out, B.w(a, l))
    return out


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'review'
    if mode == 'nulltest':
        for stem in STEMS:
            path, raw, W, secs, new, changes, fails = process(stem)
            ok = mtx.build(secs, W) == raw
            print('%-9s W=%d entries=%d  rebuild %s original' % (
                stem, W, sum(len(s) for s in secs), 'EQUALS' if ok else 'DIFFERS FROM'))
    elif mode == 'review':
        out = ['# Issue #1 base re-wrap review',
               '',
               'Flagged over %d px, re-wrapped to %d px, at most %d lines. Words unchanged.' % (FLAG, TARGET, MAXLINES),
               '']
        tot = grow = 0
        for stem in STEMS:
            path, raw, W, secs, new, changes, fails = process(stem)
            g = sum(1 for c in changes if len(c[4]) > len(c[2]))
            out += ['', '## %s: %d entries re-wrapped, %d gain a line, %d impossible' % (
                stem, len(changes), g, len(fails)), '']
            for si, i, ls, ws, nw, nws in changes:
                out.append('- sec %d #%d  %s -> %s%s' % (si, i, ws, nws, '  (+line)' if len(nw) > len(ls) else ''))
                out.append('  - before: ' + ' / '.join(ls))
                out.append('  - after:  ' + ' / '.join(nw))
            for si, i, j in fails:
                out.append('- CANNOT FIT sec %d #%d: %s' % (si, i, j))
            tot += len(changes); grow += g
        out += ['', 'Total: %d entries re-wrapped, %d of them gain a line.' % (tot, grow), '']
        open('_issue1_rewrap_base_review.md', 'w', encoding='utf-8').write('\n'.join(out))
        print('review written: _issue1_rewrap_base_review.md  (%d entries, %d gain a line)' % (tot, grow))
    elif mode == 'apply':
        os.makedirs(BAK, exist_ok=True)
        for stem in STEMS:
            path, raw, W, secs, new, changes, fails = process(stem)
            assert not fails, fails
            bak = os.path.join(BAK, '%sJapanese.mtx' % stem)
            if not os.path.exists(bak):
                shutil.copy2(os.path.join(SRC, ADV, '%sJapanese.mtx' % stem), bak)
            assert open(bak, 'rb').read() == raw, stem
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data = mtx.build(new, W)
            open(path, 'wb').write(data)
            chk = mtx.parse(path)
            assert [len(s) for s in chk] == [len(s) for s in secs], stem
            fp = os.path.join(SRC, ADV, '%s_F1Japanese.narc' % stem)
            print('%-9s %d entries re-wrapped, %d -> %d bytes, widest drawn line now %d px (flag %d)' % (
                stem, len(changes), len(raw), len(data), widest(path, fp), FLAG))
    else:
        raise SystemExit(__doc__)
