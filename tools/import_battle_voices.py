"""Import the English in-battle character voices from Steam into tenp.bcsar.

3DS CWAR index 9..45 <-> Steam voiceNN[c]_bank_e.xwb, proven by Japanese-take
durations (mean |dt| = 0.000 s). Only banks the fan patch left Japanese are
replaced. Each wave is resampled from Steam's 48 kHz to the 3DS wave's rate
(21.2 kHz), encoded, and written as a CWAV using the Japanese wave as template.

Output: patch/romfs/sound/tenp.bcsar
"""
import os, re, struct, time, sys
import numpy as np
import dsp, csar
from import_dlc_voices import xwb, resample

SD = r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/sound/voice'
JP = 'jp_orig/sound/tenp.bcsar'
CUR = 'tr_envoice/sound/tenp.bcsar'          # the fan build: 13 banks already English

jp = csar.Csar(JP)
cur = csar.Csar(CUR)
cw = [i for i, b in enumerate(cur.blobs) if b[:4] == b'CWAR']


def durations(blob):
    w = csar.Cwar(blob)
    out = []
    for wav in w.waves:
        t = csar.cwav_info(wav)
        out.append(t['samples'] / t['rate'])
    return out


def xwb_durs(path):
    return [len(p) / r for r, p in xwb(path)]


banks = sorted(f for f in os.listdir(SD) if re.match(r'voice\d\d[c]?_bank\.xwb$', f))
steam = {b: xwb_durs(os.path.join(SD, b)) for b in banks}

replace = {}
log = []
t0 = time.time()
for k in range(9, 46):
    fi = cw[k]
    if cur.blobs[fi] != jp.blobs[fi]:
        log.append('CWAR[%d]: already English (fan patch), kept' % k)
        continue
    dv = durations(jp.blobs[fi])
    best = min(((float(np.mean(np.abs(np.array(sv) - np.array(dv)))), b) for b, sv in steam.items() if len(sv) == len(dv)), default=None)
    if best is None or best[0] > 0.02:
        log.append('CWAR[%d]: no Steam bank matches its durations, kept Japanese' % k)
        continue
    bank = best[1]
    en = xwb(os.path.join(SD, bank.replace('_bank.xwb', '_bank_e.xwb')))
    w = csar.Cwar(jp.blobs[fi])
    new_waves = []
    for i, wav in enumerate(w.waves):
        t = csar.cwav_info(wav)
        y = resample(en[i][1], en[i][0], t['rate'])
        y = np.clip(np.round(y), -32768, 32767).astype(int).tolist()
        coefs = dsp.correlate_coefs(y)
        new_waves.append(csar.build_cwav(y, coefs, wav))
    replace[fi] = w.build(new_waves)
    log.append('CWAR[%d] <- %s: %d waves, %d -> %d bytes' % (k, bank, len(new_waves), len(jp.blobs[fi]), len(replace[fi])))
    print('CWAR[%2d] <- %-20s %d waves  (%.0fs)' % (k, bank, len(new_waves), time.time() - t0), flush=True)

out = cur.build(replace)
os.makedirs('patch/romfs/sound', exist_ok=True)
open('patch/romfs/sound/tenp.bcsar', 'wb').write(out)
chk = csar.Csar('patch/romfs/sound/tenp.bcsar')
open('import_battle_voices.log', 'w').write('\n'.join(log))
print('DONE: %d banks replaced; new tenp.bcsar %d bytes (was %d); re-parses with %d internal files; %.0fs'
      % (len(replace), len(out), len(cur.d), len(chk.blobs), time.time() - t0))
