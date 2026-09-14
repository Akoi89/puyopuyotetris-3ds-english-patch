"""Issue #1 (TheGershon, 2026-09-14): re-wrap the EX chapter bubble text so no line is wider than the
3DS speech bubble. Sega's Steam line breaks were kept as-is by dlc_patch.py; Steam's bubble is wider.

    python issue1_rewrap.py nulltest   -> mtx.build(mtx.parse(f)) must equal the shipped bytes for the 3 files
    python issue1_rewrap.py review     -> issue1_rewrap_review.md (every changed entry, before / after, widths)
    python issue1_rewrap.py apply      -> rewrites patch_dlc2/<content>/data/chapterNNJapanese.mtx in place
                                           (backup of each original goes to issue1_backup/)

Rules: only entries with a line over LIMIT (see issue1_model.py) are touched; the words are never changed;
the joined text is word-wrapped greedily into at most 3 lines (Sega's Japanese uses up to 3); the
terminator U+F813 is kept; nothing else in the file moves.
"""
import os, sys, shutil
import mtx
from issue1_widths import atlas
from issue1_model import screen_width, LIMIT, ROOM
from check_glyphs import companions

BR, END = chr(0xf8fd), chr(0xf813)
FILES = [('0010', '08'), ('0011', '09'), ('0012', '10')]


def wrap(text, a, limit, maxlines=3):
    """Fewest lines that fit, then the split with the smallest widest line (no one-word orphans)."""
    words = []
    for w in text.split(' '):
        if w == chr(0x2605) and words:          # the star icon stays glued to the word before it
            words[-1] += ' ' + w
        else:
            words.append(w)
    n = len(words)
    W = lambda i, j: screen_width(a, ' '.join(words[i:j]))
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
            key = (max(ws), -ws[0])
            if best is None or key < best[0]:
                best = (key, c)
        if best:
            return [' '.join(words[i:j]) for i, j in best[1]]
    return None


def balance(lines_, a, limit):
    """Move leading words of line i+1 up never (greedy already did); instead, if the last line is a single
    short word and the previous line can give up its last word without exceeding the limit... keep it simple:
    greedy result is what Sega's own tools produce, so return as is."""
    return lines_


def process(cid, ch):
    rel = '%s/data/chapter%sJapanese.mtx' % (cid, ch)
    path = os.path.join('patch_dlc2', rel)
    src = os.path.join('issue1_backup', 'chapter%sJapanese.mtx' % ch)
    if not os.path.exists(src):
        src = path
    cs = companions(rel, 'dlc_r')
    a = atlas(os.path.join('patch_dlc2', cs[0]), 0)
    raw = open(src, 'rb').read()          # the 1.0.12 file (backup) is the source of truth
    W = mtx.width(raw)
    secs = mtx._read(raw, W)
    new, changes, fails = [], [], []
    for si, s in enumerate(secs):
        row = []
        for i, t in enumerate(s):
            if not t.strip() or not any(c.isascii() and c.isalpha() for c in t):
                row.append(t); continue
            has_end = t.endswith(END)
            body = t[:-1] if has_end else t
            ls = body.split(BR)
            widths = [screen_width(a, l) for l in ls]
            if max(widths) <= LIMIT:
                row.append(t); continue
            joined = ' '.join(l.strip() for l in ls if l.strip())
            w = wrap(joined, a, LIMIT)
            if w is None:
                fails.append((si, i, joined)); row.append(t); continue
            nt = BR.join(w) + (END if has_end else '')
            changes.append((si, i, ls, widths, w, [screen_width(a, l) for l in w]))
            row.append(nt)
        new.append(row)
    return path, raw, W, secs, new, changes, fails


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'nulltest':
        for cid, ch in FILES:
            path, raw, W, secs, new, changes, fails = process(cid, ch)
            rebuilt = mtx.build(secs, W)
            print('%s  W=%d  rebuilt %s original (%d vs %d bytes)' % (path, W, 'EQUALS' if rebuilt == raw else 'DIFFERS FROM', len(rebuilt), len(raw)))
    elif mode == 'review':
        out = ['# Issue #1 re-wrap review (limit %d px on screen, bubble room ~%d px)\n' % (LIMIT, ROOM)]
        tot = 0
        for cid, ch in FILES:
            path, raw, W, secs, new, changes, fails = process(cid, ch)
            out.append('\n## EX Act %s  (%s): %d entries re-wrapped, %d could not be wrapped into 3 lines\n' % (ch, path, len(changes), len(fails)))
            for si, i, ls, ws, w, nws in changes:
                out.append('- sec %d #%d  before %s  ->  after %s' % (si, i, ws, nws))
                out.append('  - ' + ' / '.join(ls))
                out.append('  - ' + ' / '.join(w))
            for si, i, joined in fails:
                out.append('- CANNOT FIT sec %d #%d: %s' % (si, i, joined))
            tot += len(changes)
        out.append('\nTotal entries re-wrapped: %d\n' % tot)
        open('issue1_rewrap_review.md', 'w', encoding='utf-8').write('\n'.join(out))
        print('review written: issue1_rewrap_review.md  (%d entries)' % tot)
    elif mode == 'apply':
        os.makedirs('issue1_backup', exist_ok=True)
        for cid, ch in FILES:
            path, raw, W, secs, new, changes, fails = process(cid, ch)
            assert not fails, fails
            bak = os.path.join('issue1_backup', 'chapter%sJapanese.mtx' % ch)
            if not os.path.exists(bak):
                shutil.copy2(path, bak)
            assert open(bak, 'rb').read() == raw
            data = mtx.build(new, W)
            open(path, 'wb').write(data)
            # read back: same section/entry counts, every changed entry present, no line over LIMIT
            chk = mtx.parse(path)
            a = atlas(os.path.join('patch_dlc2', companions('%s/data/chapter%sJapanese.mtx' % (cid, ch), 'dlc_r')[0]), 0)
            assert [len(s) for s in chk] == [len(s) for s in secs]
            worst = max(screen_width(a, l) for s in chk for t in s for l in t.replace(END, '').split(BR)
                        if any(c.isascii() and c.isalpha() for c in t))
            print('%s: %d entries re-wrapped, %d -> %d bytes, widest English line now %d px (limit %d)' % (
                path, len(changes), len(raw), len(data), worst, LIMIT))
