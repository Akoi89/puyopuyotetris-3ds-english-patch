"""Fit the game's on-screen line width to our atlas measure: screen = k * ours + d * spaces.

Ink is measured in the bubble band (rows 5..32) of each 400x240 capture: pixels with g < 170
(all three text colours qualify; bubble white, cyan border and green ground do not).
"""
import os
import numpy as np
from PIL import Image
from issue1_widths import atlas, pw
from check_glyphs import companions

S = 'issue1_scratch/'
CASES = [
    ('img1.png', '0010/data/chapter08Japanese.mtx', 'THE SUZURAN SHOPPING DISTRICT', (12, 27)),
    ('img2.png', '0010/data/chapter08Japanese.mtx', 'Well, this DOES sound like a rather', (18, 33)),
    ('img3.png', '0010/data/chapter08Japanese.mtx', 'First up, the comedic stylings of...', (12, 27)),
    ('img4.png', '0011/data/chapter09Japanese.mtx', 'HA! I sense a hidden power deep, deep', (12, 27)),
]
rows = []
for shot, rel, line, (y0, y1) in CASES:
    im = np.array(Image.open(S + shot).convert('RGB')).astype(int)
    band = im[y0:y1, 60:400]
    ink = (band[:, :, 1] < 170) & (band[:, :, 0] > 20)
    cols = np.where(ink.sum(axis=0) >= 1)[0] + 60
    # drop stray columns: keep the longest cluster with gaps < 12 px
    clusters, cur = [], [cols[0]]
    for c in cols[1:]:
        if c - cur[-1] < 12:
            cur.append(c)
        else:
            clusters.append(cur); cur = [c]
    clusters.append(cur)
    best = max(clusters, key=len)
    cs = companions(rel, 'dlc_r')
    a = atlas(os.path.join('patch_dlc2', cs[0]), 0)
    ours = pw(a, line); nsp = line.count(' ')
    scr = best[-1] - best[0] + 1
    rows.append((scr, ours, nsp))
    print('%s  screen ink x %3d..%3d = %3d px   ours=%3d  spaces=%d  %r' % (shot, best[0], best[-1], scr, ours, nsp, line))
    print('    space glyph in atlas:', a['widths'].get(32), ' cw', a['cw'])
A = np.array([[o, n] for s, o, n in rows], float); b = np.array([s for s, o, n in rows], float)
k, d = np.linalg.lstsq(A, b, rcond=None)[0]
print('fit: screen = %.3f * ours + %.2f * spaces' % (k, d))
for s, o, n in rows:
    print('   pred %.1f  actual %d' % (k * o + d * n, s))
