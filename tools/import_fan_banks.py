"""Re-import the 13 battle banks the fan patch had already replaced, so every
battle bank is our own encode from Steam at Sega's sample rate.

The fan build's waves carry odd per-wave sample rates (24600, 23500, 10000 Hz
...) where Sega's are all 32000 Hz. Same mapping proof as import_battle_voices:
each Japanese bank's durations equal one Steam voiceNN[c]_bank.xwb; the
English comes from the matching _e bank, resampled to the Japanese wave's rate
and encoded with the Japanese wave as template.
Rewrites patch/romfs/sound/tenp.bcsar in place.
"""
import os, re, time
import numpy as np
import dsp, csar
from import_dlc_voices import xwb, resample

SD = r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/sound/voice'
JP = 'jp_orig/sound/tenp.bcsar'
CUR = 'patch/romfs/sound/tenp.bcsar'
FAN = 'tr_envoice/sound/tenp.bcsar'

jp = csar.Csar(JP); cur = csar.Csar(CUR); fan = csar.Csar(FAN)


def durations(blob):
    return [csar.cwav_info(w)['samples'] / csar.cwav_info(w)['rate'] for w in csar.Cwar(blob).waves]


banks = sorted(f for f in os.listdir(SD) if re.match(r'voice\d\d[c]?_bank\.xwb$', f))
steam = {b: [len(p) / r for r, p in xwb(os.path.join(SD, b))] for b in banks}
replace, t0 = {}, time.time()
for fi in range(81, 118):
    if cur.blobs[fi] != fan.blobs[fi]:
        continue                                   # already our own encode
    dv = durations(jp.blobs[fi])
    best = min(((float(np.mean(np.abs(np.array(sv) - np.array(dv)))), b) for b, sv in steam.items() if len(sv) == len(dv)))
    assert best[0] < 0.02, (fi, best)
    en = xwb(os.path.join(SD, best[1].replace('_bank.xwb', '_bank_e.xwb')))
    w = csar.Cwar(jp.blobs[fi])
    waves = []
    for i, wav in enumerate(w.waves):
        t = csar.cwav_info(wav)
        y = resample(en[i][1], en[i][0], t['rate'])
        y = np.clip(np.round(y), -32768, 32767).astype(int).tolist()
        waves.append(csar.build_cwav(y, dsp.correlate_coefs(y), wav))
    replace[fi] = w.build(waves)
    print('CWAR[%d] <- %s (%d waves, %.0fs)' % (fi, best[1], len(waves), time.time() - t0), flush=True)
out = cur.build(replace)
open(CUR, 'wb').write(out)
chk = csar.Csar(CUR)
rates = {}
for i in range(81, 118):
    for w in csar.Cwar(chk.blobs[i]).waves:
        r = csar.cwav_info(w)['rate']; rates[r] = rates.get(r, 0) + 1
print('DONE: %d banks re-imported; battle-bank sample rates now %s; tenp.bcsar %d bytes, %d files' % (len(replace), rates, len(out), len(chk.blobs)))
