"""Level matching with ONE re-encode.

voice_gain.py re-encoded DSP-ADPCM on every pass (three passes = four
generations of encoder error, audible as grit). This decodes the pre-gain
audio once, iterates gain + limiter in floating point until the RMS meets
Sega's Japanese take, and encodes once.

    python voice_gain_clean.py base <orig.bcsar> <pre_gain.bcsar> <out.bcsar>
    python voice_gain_clean.py dlc  <pre_gain_dir> <out_dir>      (patch_dlc2 trees)
    python voice_gain_clean.py snr  <orig.bcsar> <pre_gain.bcsar> <candidate.bcsar> cwar:wave ...
"""
import os, sys, glob, math, time
import numpy as np
import csar, dsp
from voice_levels import pcm_of
from voice_gain import limiter, rms, MAX_GAIN_DB

ITER = 6


def level(p, target, rate):
    """Iterate gain + limiter in float so the limited signal lands on target RMS."""
    y = p.copy(); g_total = 1.0
    for _ in range(ITER):
        g = target / max(rms(y), 1.0)
        g = min(g, 10 ** (MAX_GAIN_DB / 20) / g_total)
        if abs(20 * math.log10(g)) < 0.15:
            break
        g_total *= g
        y = limiter(y * g, rate)
    return y, 20 * math.log10(g_total)


def base(orig, pre, out):
    a, b = csar.Csar(orig), csar.Csar(pre); replace = {}; t0 = time.time()
    for ci in range(len(b.blobs)):
        if b.blobs[ci][:4] != b'CWAR' or a.blobs[ci] == b.blobs[ci]:
            continue
        wa, wb = csar.Cwar(a.blobs[ci]).waves, csar.Cwar(b.blobs[ci]).waves
        if not wa or not wb:
            continue
        ja = [pcm_of(w) for w in wa]; jb = [pcm_of(w) for w in wb]
        bank_target = float(np.mean([rms(p) for p in ja]))
        diff_db = 20 * math.log10(float(np.mean([rms(p) for p in jb])) / bank_target)
        if diff_db > -1.0:
            print('CWAR blob %d: %+.1f dB vs Sega, left alone' % (ci, diff_db)); continue
        new = []; gains = []
        for i, w in enumerate(wb):
            target = rms(ja[i]) if i < len(ja) else bank_target
            y, gdb = level(jb[i], target, csar.cwav_info(w)['rate']); gains.append(gdb)
            pcm = np.round(y).astype(int).tolist()
            new.append(csar.build_cwav(pcm, dsp.correlate_coefs(pcm), w))
        replace[ci] = csar.Cwar(b.blobs[ci]).build(new)
        print('CWAR blob %d: %d waves, was %+.1f dB, gain %.1f..%.1f dB (%.0fs)' % (ci, len(wb), diff_db, min(gains), max(gains), time.time() - t0), flush=True)
    data = b.build(replace); open(out, 'wb').write(data)
    print('wrote %s: %d banks, %d bytes, re-parses with %d files' % (out, len(replace), len(data), len(csar.Csar(out).blobs)))


def cstm_pcm(c):
    return np.array(dsp.decode(c['data'], c['chans'][0]['coefs'], nsamples=c['total'])[0], dtype=np.float64)


def dlc(pre_dir, out_dir):
    t0 = time.time(); total = 0; gains = []
    for cid in ('0010', '0011', '0012'):
        n = 0
        for p in sorted(glob.glob('%s/%s/adv_sound/stream/*.bcstm' % (pre_dir, cid))):
            q = 'dlc_r/%s/adv_sound/stream/%s' % (cid, os.path.basename(p))
            o = '%s/%s/adv_sound/stream/%s' % (out_dir, cid, os.path.basename(p))
            if not os.path.exists(q) or open(p, 'rb').read() == open(q, 'rb').read():
                continue
            cj, co = dsp.read_cstm(q), dsp.read_cstm(p)
            y, gdb = level(cstm_pcm(co), rms(cstm_pcm(cj)), co['st']['rate']); gains.append(gdb)
            pcm = np.round(y).astype(int).tolist()
            os.makedirs(os.path.dirname(o), exist_ok=True)
            open(o, 'wb').write(dsp.build_cstm(pcm, co['st']['rate'], dsp.correlate_coefs(pcm), q)); n += 1
        total += n; print('%s: %d clips (%.0fs)' % (cid, n, time.time() - t0), flush=True)
    print('total %d clips, gain %.1f..%.1f dB (mean %.1f)' % (total, min(gains), max(gains), float(np.mean(gains))))


def snr(orig, pre, cand, specs):
    """Noise of a candidate encode against the float-levelled intent, per wave."""
    a, b, c = csar.Csar(orig), csar.Csar(pre), csar.Csar(cand)
    for spec in specs:
        ci, wi = (int(x) for x in spec.split(':'))
        wa, wb, wc = csar.Cwar(a.blobs[ci]).waves[wi], csar.Cwar(b.blobs[ci]).waves[wi], csar.Cwar(c.blobs[ci]).waves[wi]
        rate = csar.cwav_info(wb)['rate']
        intent, gdb = level(pcm_of(wb), rms(pcm_of(wa)), rate)
        got = pcm_of(wc)
        # align gain (candidate may sit at a slightly different level), then noise
        n = min(len(intent), len(got)); x, y = intent[:n], got[:n]
        k = float((x * y).sum() / max((y * y).sum(), 1.0)); noise = x - k * y
        pcm = np.round(intent).astype(int).tolist(); once = np.array(dsp.decode(dsp.encode(pcm, dsp.correlate_coefs(pcm)), dsp.correlate_coefs(pcm), nsamples=len(pcm))[0], float)
        noise1 = x - once[:n]
        print('%s: candidate SNR %.1f dB, single-encode SNR %.1f dB (intent gain %+.1f dB)' % (spec, 10 * math.log10((x ** 2).sum() / max((noise ** 2).sum(), 1e-9)), 10 * math.log10((x ** 2).sum() / max((noise1 ** 2).sum(), 1e-9)), gdb))


if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'base': base(*sys.argv[2:5])
    elif m == 'dlc': dlc(*sys.argv[2:4])
    elif m == 'snr': snr(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
