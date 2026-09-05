"""Bring the imported (Steam PCM) voices up to Sega's 3DS loudness.

Sega's Japanese takes sit around -11 dBFS RMS with peaks near 0 dBFS (heavily
limited); Steam's PCM imports sit 5 to 11 dB lower with peaks already near
full scale, so a plain gain would clip. Per wave: gain to the RMS of the
Japanese take at the same index (bank mean if the counts differ), then a
look-ahead peak limiter (ceiling -0.5 dBFS, ~1.5 ms attack window, 60 ms
release), then re-encode DSP-ADPCM. Banks that are not quieter than Sega's by
at least 1 dB are left alone.

    python voice_gain.py <orig.bcsar> <ours.bcsar> <out.bcsar> [--dry]
"""
import sys, struct, math, time
import numpy as np
import csar, dsp
from voice_levels import pcm_of

CEIL = 32768 * 10 ** (-0.5 / 20)
MAX_GAIN_DB = 14.0


def rms(p): return math.sqrt(float((p ** 2).mean())) if len(p) else 1.0


def limiter(y, rate):
    look = max(8, int(rate * 0.0015)); rel = max(1, int(rate * 0.06))
    a = np.abs(y)
    # sliding max over the look-ahead window (peak hold)
    pad = np.concatenate([a, np.zeros(look)])
    env = np.max(np.lib.stride_tricks.sliding_window_view(pad, look + 1), axis=1)[:len(y)]
    need = np.minimum(1.0, CEIL / np.maximum(env, 1e-9))
    # smooth: instant attack, exponential release
    g = np.empty_like(need); cur = 1.0; k = math.exp(-1.0 / rel)
    for i in range(len(need)):
        n = need[i]
        cur = n if n < cur else n + (cur - n) * k        # instant attack, exponential release
        g[i] = cur
    return np.clip(y * g, -32768, 32767)


def main():
    orig, ours, out = sys.argv[1:4]; dry = '--dry' in sys.argv
    a, b = csar.Csar(orig), csar.Csar(ours)
    replace = {}; t0 = time.time()
    for ci in range(len(b.blobs)):
        if b.blobs[ci][:4] != b'CWAR' or a.blobs[ci] == b.blobs[ci]:
            continue
        wa, wb = csar.Cwar(a.blobs[ci]).waves, csar.Cwar(b.blobs[ci]).waves
        if not wa or not wb:
            continue
        ja = [pcm_of(w) for w in wa]; jb = [pcm_of(w) for w in wb]
        bank_target = np.mean([rms(p) for p in ja])
        diff_db = 20 * math.log10(np.mean([rms(p) for p in jb]) / bank_target)
        if diff_db > -1.0:
            print('CWAR blob %d: %+.1f dB vs Sega, left alone' % (ci, diff_db)); continue
        new = []; gains = []
        for i, w in enumerate(wb):
            p = jb[i]; target = rms(ja[i]) if i < len(ja) else bank_target
            g = min(10 ** (MAX_GAIN_DB / 20), target / max(rms(p), 1.0)); gains.append(20 * math.log10(g))
            info = csar.cwav_info(w)
            y = limiter(p * g, info['rate'])
            if dry:
                continue
            pcm = np.round(y).astype(int).tolist()
            coefs = dsp.correlate_coefs(pcm)
            new.append(csar.build_cwav(pcm, coefs, w))
        print('CWAR blob %d: %d waves, was %+.1f dB, gain %.1f..%.1f dB (%.0fs)' % (ci, len(wb), diff_db, min(gains), max(gains), time.time() - t0), flush=True)
        if not dry:
            replace[ci] = csar.Cwar(b.blobs[ci]).build(new)
    if dry:
        return
    data = b.build(replace)
    open(out, 'wb').write(data)
    chk = csar.Csar(out)
    print('wrote %s: %d banks re-levelled, %d bytes, re-parses with %d files' % (out, len(replace), len(data), len(chk.blobs)))


if __name__ == '__main__':
    main()
