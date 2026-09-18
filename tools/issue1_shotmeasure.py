"""Measure drawn bubble line widths in a 400x240 capture.

Text is the saturated non-cream ink inside the bubble's cream run on each row; trailing clusters
more than 15 px from the body (the cyan advance icon) are dropped.
"""
import sys
import numpy as np
from PIL import Image


def measure(path, y0=5, y1=95):
    im = np.array(Image.open(path).convert('RGB')).astype(int)
    r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    cream = (r > 235) & (g > 235) & (b > 215) & (b < 250)
    blue = (b - r > 60) & (r < 120) & (g - r < 80) & (b > 110)
    pink = (r - b > 60) & (r > 180) & (g < 160)
    ink = blue | pink
    recs = []
    for y in range(y0, y1):
        cx = np.where(cream[y])[0]
        if len(cx) < 30:
            recs.append(None); continue
        lo, hi = cx.min(), cx.max()
        m = np.zeros(im.shape[1], bool); m[lo:hi + 1] = True
        recs.append((lo, hi, np.where(ink[y] & m)[0]))
    ys = [i for i, rc in enumerate(recs) if rc and len(rc[2]) > 2]
    grp, cur = [], []
    for y in ys:
        if cur and y - cur[-1] > 1:
            grp.append(cur); cur = []
        cur.append(y)
    if cur:
        grp.append(cur)
    out = []
    for gp in grp:
        xs = np.unique(np.concatenate([recs[y][2] for y in gp]))
        keep = [xs[0]]
        for x in xs[1:]:
            if x - keep[-1] > 15:
                break
            keep.append(x)
        out.append((gp[0] + y0, gp[-1] + y0, int(keep[0]), int(keep[-1]),
                    int(keep[-1] - keep[0] + 1), int(max(recs[y][1] for y in gp))))
    return out


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print('===', p)
        for y0, y1, x0, x1, w, br in measure(p):
            print('  y%3d-%3d  x %3d-%3d  w=%3d  bubbleR=%3d  rightgap=%3d' % (y0, y1, x0, x1, w, br, br - x1))
