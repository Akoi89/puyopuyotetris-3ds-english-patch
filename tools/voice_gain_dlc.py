"""Bring the imported DLC story clips (CSTM streams) up to Sega's loudness.
Same recipe as voice_gain.py: per clip, gain to the RMS of the Japanese
original of the same file, look-ahead limiter at -0.5 dBFS, re-encode.

    python voice_gain_dlc.py [--dry]      (patch_dlc2/00xx/adv_sound/stream, in place)
"""
import os, sys, glob, math, time
import numpy as np
import dsp
from voice_gain import limiter, rms, MAX_GAIN_DB

dry = '--dry' in sys.argv
t0 = time.time(); total = 0; gains = []


def pcm(c):
    return np.array(dsp.decode(c['data'], c['chans'][0]['coefs'], nsamples=c['total'])[0], dtype=np.float64)


for cid in ('0010', '0011', '0012'):
    ours = sorted(glob.glob('patch_dlc2/%s/adv_sound/stream/*.bcstm' % cid)); n = 0
    for p in ours:
        q = 'dlc_r/%s/adv_sound/stream/%s' % (cid, os.path.basename(p))
        if not os.path.exists(q) or open(p, 'rb').read() == open(q, 'rb').read():
            continue                                    # not one of our imports
        cj, co = dsp.read_cstm(q), dsp.read_cstm(p)
        a, b = pcm(cj), pcm(co)
        g = min(10 ** (MAX_GAIN_DB / 20), rms(a) / max(rms(b), 1.0)); gains.append(20 * math.log10(g))
        if g < 10 ** (1.0 / 20):
            continue                                    # within 1 dB already
        rate = co['st']['rate']
        y = np.round(limiter(b * g, rate)).astype(int).tolist()
        if not dry:
            blob = dsp.build_cstm(y, rate, dsp.correlate_coefs(y), q)   # template: the untouched original
            open(p, 'wb').write(blob)
        n += 1
    total += n
    print('%s: %d clips re-levelled (%.0fs)' % (cid, n, time.time() - t0), flush=True)
print('total %d clips, gain %.1f..%.1f dB (mean %.1f)' % (total, min(gains), max(gains), float(np.mean(gains))))
