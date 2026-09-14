"""Issue #1: how many DLC bubble entries need re-wrapping at a given width limit, and how many
cannot be wrapped into 3 lines at all (those need shorter wording).

    python issue1_wrapcheck.py [limit]     default limit 190 (atlas units, see issue1_widths.py)
"""
import sys, os
import mtx
from issue1_widths import atlas, lines
from issue1_model import screen_width as pw, LIMIT as MODEL_LIMIT
from check_glyphs import companions

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else MODEL_LIMIT
BR, END = chr(0xf8fd), chr(0xf813)
CTRL = ''.join(chr(c) for c in range(0xe000, 0xf900))


def wrap(text, a, limit, maxlines=3):
    """Greedy word wrap on the joined text. Returns list of lines or None if it needs > maxlines."""
    words = text.split(' ')
    out, cur = [], ''
    for w in words:
        cand = (cur + ' ' + w) if cur else w
        if pw(a, cand) <= limit:
            cur = cand
        else:
            if cur:
                out.append(cur)
            cur = w
            if pw(a, w) > limit:
                return None
    if cur:
        out.append(cur)
    return out if len(out) <= maxlines else None


tot_entries = tot_over = tot_fail = 0
for cid, ch in [('0010', '08'), ('0011', '09'), ('0012', '10')]:
    rel = '%s/data/chapter%sJapanese.mtx' % (cid, ch)
    cs = companions(rel, 'dlc_r')
    a = atlas(os.path.join('patch_dlc2', cs[0]), 0)
    secs = mtx.parse(os.path.join('patch_dlc2', rel))
    over = fail = n = 0
    for si, s in enumerate(secs):
        for i, t in enumerate(s):
            if not t.strip() or not any(c.isascii() and c.isalpha() for c in t):
                continue
            n += 1
            body = t.replace(END, '')
            ls = body.split(BR)
            if max(pw(a, l) for l in ls) <= LIMIT:
                continue
            over += 1
            joined = ' '.join(l.strip() for l in ls)
            w = wrap(joined, a, LIMIT)
            if w is None:
                fail += 1
                print('  CANNOT FIT ch%s sec%d #%d: %r' % (ch, si, i, joined))
            elif len(w) == 3:
                print('  3 lines   ch%s sec%d #%d: %r' % (ch, si, i, w))
    print('ch%s: english entries %d, over limit %d, cannot fit in 3 lines %d' % (ch, n, over, fail))
    tot_entries += n; tot_over += over; tot_fail += fail
print('TOTAL: entries %d, need re-wrap %d, cannot fit %d  (limit %d)' % (tot_entries, tot_over, tot_fail, LIMIT))
