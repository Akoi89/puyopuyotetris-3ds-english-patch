"""Calibrate the atlas width measure against TheGershon's screenshots (400x240 native captures).

For each screenshot: find the bubble's white area on the top text row and the ink extent of the
dark text inside it, print both, and print our measured width for the same line.
"""
import sys, os
import numpy as np
from PIL import Image
from issue1_widths import atlas, pw
from check_glyphs import companions

SHOTS = 'issue1_scratch/'
CASES = [
    ('img1.png', '0010/data/chapter08Japanese.mtx', 'THE SUZURAN SHOPPING DISTRICT'),
    ('img2.png', '0010/data/chapter08Japanese.mtx', 'Well, this DOES sound like a rather'),
    ('img3.png', '0010/data/chapter08Japanese.mtx', 'First up, the comedic stylings of...'),
    ('img4.png', '0011/data/chapter09Japanese.mtx', 'HA! I sense a hidden power deep, deep'),
]
for shot, rel, line in CASES:
    im = np.array(Image.open(SHOTS + shot).convert('RGB')).astype(int)
    # find the text row: rows 0..40 whose darkest pixels sit inside a white run
    best = None
    for y in range(4, 40):
        row = im[y]
        white = np.where(row.min(axis=1) > 230)[0]
        if len(white) < 100:
            continue
        x0, x1 = white.min(), white.max()
        seg = row[x0:x1]
        ink = np.where(np.abs(seg - np.array([255, 255, 238])).max(axis=1) > 80)[0]
        if len(ink) > 20 and (best is None or len(ink) > best[0]):
            best = (len(ink), y, x0 + ink.min(), x0 + ink.max(), x0, x1)
    # widen: take the union of ink over the 14 rows around the best row
    n, y, ix0, ix1, wx0, wx1 = best
    band = im[y - 7:y + 8]
    inkcols = np.where((np.abs(band - np.array([255, 255, 238])).max(axis=2) > 80).any(axis=0))[0]
    inkcols = inkcols[(inkcols >= wx0 + 2) & (inkcols <= wx1 - 2)]
    cs = companions(rel, 'dlc_r')
    a = atlas(os.path.join('patch_dlc2', cs[0]), 0)
    print('%s row %2d  ink x %3d..%3d (%3d px)   white run x %3d..%3d (%3d)   ours=%d  ratio=%.3f  %r' % (
        shot, y, inkcols.min(), inkcols.max(), inkcols.max() - inkcols.min() + 1, wx0, wx1, wx1 - wx0 + 1,
        pw(a, line), (inkcols.max() - inkcols.min() + 1) / pw(a, line), line))
