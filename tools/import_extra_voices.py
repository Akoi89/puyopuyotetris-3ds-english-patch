"""Import the two voice sets the first pass missed, from Steam's English banks.

  * CWAR files 119..142 = the per-character TITLE CALLS (3 waves each, the
    "Sega / Puyo Puyo Tetris!" heard at launch) <-> title00..23_bank_e.xwb,
    proven by Japanese-take durations (mean |dt| = 0.000 s on all 24).
  * CWAR file 118 = the CHARACTER-SELECT bank: 48 waves, two per character.
    Even waves are the select line (the fan patch already replaced them with
    charactersel_bank_e); odd waves are the CONFIRM line, still Japanese, and
    each equals wave 12 of that character's voiceNNc bank (24/24 exact), so
    the English comes from voiceNNc_bank_e.xwb wave 12.

Starts from the current patch/romfs/sound/tenp.bcsar and rewrites it in place.
"""
import os, re, time
import numpy as np
import dsp, csar
from import_dlc_voices import xwb, resample

SD = r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/sound/voice'
JP = 'jp_orig/sound/tenp.bcsar'
CUR = 'patch/romfs/sound/tenp.bcsar'

jp = csar.Csar(JP)
cur = csar.Csar(CUR)


def durations(blob):
    return [csar.cwav_info(w)['samples'] / csar.cwav_info(w)['rate'] for w in csar.Cwar(blob).waves]


def encode_like(template_wav, rate_src, pcm):
    t = csar.cwav_info(template_wav)
    y = resample(pcm, rate_src, t['rate'])
    y = np.clip(np.round(y), -32768, 32767).astype(int).tolist()
    return csar.build_cwav(y, dsp.correlate_coefs(y), template_wav)


replace = {}
log = []
t0 = time.time()

# --- title calls -------------------------------------------------------------
for c in range(24):
    fi = 119 + c
    jd = durations(jp.blobs[fi])
    ja = [len(p) / r for r, p in xwb(os.path.join(SD, 'title%02d_bank.xwb' % c))]
    err = float(np.mean(np.abs(np.array(jd) - np.array(ja))))
    assert len(jd) == len(ja) == 3 and err < 0.01, (fi, err)
    en = xwb(os.path.join(SD, 'title%02d_bank_e.xwb' % c))
    w = csar.Cwar(jp.blobs[fi])
    replace[fi] = w.build([encode_like(wav, en[i][0], en[i][1]) for i, wav in enumerate(w.waves)])
    log.append('CWAR[%d] <- title%02d_bank_e.xwb: 3 waves, %d -> %d bytes' % (fi, c, len(jp.blobs[fi]), len(replace[fi])))
    print(log[-1], flush=True)

# --- character-select confirm lines -----------------------------------------
w = csar.Cwar(cur.blobs[118])
jw = csar.Cwar(jp.blobs[118])
jd = durations(jp.blobs[118])
waves = list(w.waves)
for c in range(24):
    bank = 'voice%02dc_bank.xwb' % c
    ja = [len(p) / r for r, p in xwb(os.path.join(SD, bank))]
    assert abs(ja[12] - jd[2 * c + 1]) < 0.01, (c, ja[12], jd[2 * c + 1])
    en = xwb(os.path.join(SD, bank.replace('_bank.xwb', '_bank_e.xwb')))
    waves[2 * c + 1] = encode_like(jw.waves[2 * c + 1], en[12][0], en[12][1])
replace[118] = w.build(waves)
log.append('CWAR[118] odd waves <- voiceNNc_bank_e.xwb wave 12 (24 confirm lines); even waves kept (already English)')
print(log[-1], flush=True)

out = cur.build(replace)
open(CUR, 'wb').write(out)
chk = csar.Csar(CUR)
open('import_extra_voices.log', 'w').write('\n'.join(log))
print('DONE: %d banks rewritten; tenp.bcsar %d bytes; re-parses with %d internal files; %.0fs'
      % (len(replace), len(out), len(chk.blobs), time.time() - t0))
