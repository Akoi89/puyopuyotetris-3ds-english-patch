"""Replace ALL 24 character-select pick lines (even waves of CWAR file 118).

The fan patch replaced only some of them; the rest still carry the Japanese
take (their durations equal Steam's Japanese charactersel_bank.xwb). Wave 2c
<-> charactersel_bank_e.xwb entry c, proven by the Japanese durations.
Rewrites patch/romfs/sound/tenp.bcsar in place and prints a per-wave audit of
the whole bank against Steam's English durations.
"""
import os
import numpy as np
import dsp, csar
from import_dlc_voices import xwb, resample

SD = r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/sound/voice'
CUR = 'patch/romfs/sound/tenp.bcsar'
JP = 'jp_orig/sound/tenp.bcsar'

cur = csar.Csar(CUR); jp = csar.Csar(JP)
jw = csar.Cwar(jp.blobs[118]); cw = csar.Cwar(cur.blobs[118])
jd = [csar.cwav_info(w)['samples'] / csar.cwav_info(w)['rate'] for w in jw.waves]
sel_j = [(len(p) / r, r, p) for r, p in xwb(os.path.join(SD, 'charactersel_bank.xwb'))]
sel_e = [(len(p) / r, r, p) for r, p in xwb(os.path.join(SD, 'charactersel_bank_e.xwb'))]
assert len(sel_j) == len(sel_e) == 24
err = float(np.mean([abs(jd[2 * c] - sel_j[c][0]) for c in range(24)]))
print('Japanese pick lines vs charactersel_bank.xwb: mean |dt| = %.3f s' % err)
assert err < 0.01

waves = list(cw.waves)
replaced = 0
for c in range(24):
    t = csar.cwav_info(jw.waves[2 * c])
    y = resample(sel_e[c][2], sel_e[c][1], t['rate'])
    y = np.clip(np.round(y), -32768, 32767).astype(int).tolist()
    waves[2 * c] = csar.build_cwav(y, dsp.correlate_coefs(y), jw.waves[2 * c])
    replaced += 1
out = cur.build({118: cw.build(waves)})
open(CUR, 'wb').write(out)

chk = csar.Csar(CUR); nw = csar.Cwar(chk.blobs[118]).waves
nd = [csar.cwav_info(w)['samples'] / csar.cwav_info(w)['rate'] for w in nw]
bad = []
for c in range(24):
    if abs(nd[2 * c] - sel_e[c][0]) > 0.01:
        bad.append(('pick', c, nd[2 * c], sel_e[c][0]))
print('replaced %d pick lines; bank now %d waves; pick lines matching Steam English durations: %d/24' % (replaced, len(nw), 24 - len(bad)))
for b in bad:
    print('  MISMATCH', b)
print('tenp.bcsar %d bytes, %d internal files' % (len(out), len(chk.blobs)))
