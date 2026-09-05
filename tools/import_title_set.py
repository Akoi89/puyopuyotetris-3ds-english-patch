"""Replace the title-screen announcer bank (CWAR file 143, 4 waves) with
Steam's English title_set_bank_e.xwb. The Japanese bank's four durations equal
title_set_bank.xwb's four entries to the millisecond, so index i <-> wave i.
Rewrites patch/romfs/sound/tenp.bcsar in place and audits the result.
"""
import os
import numpy as np
import dsp, csar
from import_dlc_voices import xwb, resample

SD = r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/sound/voice'
CUR = 'patch/romfs/sound/tenp.bcsar'
JP = 'jp_orig/sound/tenp.bcsar'
FI = 143

cur = csar.Csar(CUR); jp = csar.Csar(JP)
jw = csar.Cwar(jp.blobs[FI])
jd = [csar.cwav_info(w)['samples'] / csar.cwav_info(w)['rate'] for w in jw.waves]
sj = [len(p) / r for r, p in xwb(os.path.join(SD, 'title_set_bank.xwb'))]
se = xwb(os.path.join(SD, 'title_set_bank_e.xwb'))
assert len(jd) == len(sj) == len(se) == 4
err = float(np.mean(np.abs(np.array(jd) - np.array(sj))))
print('CWAR[143] Japanese vs title_set_bank.xwb: mean |dt| = %.3f s' % err)
assert err < 0.01

waves = []
for i, wav in enumerate(jw.waves):
    t = csar.cwav_info(wav)
    y = resample(se[i][1], se[i][0], t['rate'])
    y = np.clip(np.round(y), -32768, 32767).astype(int).tolist()
    waves.append(csar.build_cwav(y, dsp.correlate_coefs(y), wav))
out = cur.build({FI: jw.build(waves)})
open(CUR, 'wb').write(out)
chk = csar.Csar(CUR)
nd = [csar.cwav_info(w)['samples'] / csar.cwav_info(w)['rate'] for w in csar.Cwar(chk.blobs[FI]).waves]
ed = [len(p) / r for r, p in se]
print('new durations', [round(x, 3) for x in nd], 'Steam English', [round(x, 3) for x in ed],
      'match:', all(abs(a - b) < 0.01 for a, b in zip(nd, ed)))
print('tenp.bcsar %d bytes, %d internal files' % (len(out), len(chk.blobs)))
