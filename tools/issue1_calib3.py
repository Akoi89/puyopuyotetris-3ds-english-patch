"""Which advance model reproduces the on-screen widths? Test variants against the four captures.

Model: screen = sum over glyphs of (bearing + wid [+ third]) + c * nglyphs + s * nspaces
Fit c and s by least squares for each variant; print residuals.
"""
import os, struct
import numpy as np
import narc
from check_glyphs import companions
from issue1_calib2 import rows, CASES   # re-measures the screenshots (prints), gives (screen, ours, nsp)


def recs(path, member=0):
    ms = narc.read(path)['members']
    fifs = [(ms[i], ms[i + 1]) for i in range(0, len(ms) - 1, 2) if ms[i][:8] == b'FONTDATF']
    f, b = fifs[member]
    n = struct.unpack_from('<I', f, 0x10)[0]
    out = {}
    for r in range(n):
        o = 56 + r * 16
        bearing, wid, third, cp, idx = struct.unpack_from('<iIiHH', f, o)
        out[cp] = (bearing, wid, third)
    return out


lines = [(c[2], c[1]) for c in CASES]
for use_third in (False, True):
    A, b = [], []
    for (line, rel), (scr, ours, nsp) in zip(lines, rows):
        cs = companions(rel, 'dlc_r')
        R = recs(os.path.join('patch_dlc2', cs[0]))
        base = 0; ng = 0
        for ch in line:
            if ch == ' ':
                continue
            bb, ww, tt = R.get(ord(ch), (0, 14, 0))
            base += bb + ww + (tt if use_third else 0); ng += 1
        A.append([ng, nsp]); b.append(scr - base)
    A = np.array(A, float); b = np.array(b, float)
    (c, s), res = np.linalg.lstsq(A, b, rcond=None)[:2]
    pred = A @ np.array([c, s]) + (np.array([scr for scr, o, n in rows]) - b)
    print('third=%s  per-glyph c=%.2f  space s=%.2f  residuals=%s' % (
        use_third, c, s, np.round(np.array([scr for scr, o, n in rows]) - pred, 1)))
    # also the integer-friendly variants
    for cc, ss in ((0, 8), (0, 9), (0, 10), (1, 7), (1, 8)):
        p = A @ np.array([cc, ss]) + (np.array([scr for scr, o, n in rows]) - b)
        print('    c=%d s=%d  residual(actual-pred)=%s' % (cc, ss, np.round(np.array([scr for scr, o, n in rows]) - p, 1)))
