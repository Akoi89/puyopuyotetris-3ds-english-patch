"""Import the English DLC story voices from Steam into the 3DS DLC tree.

Steam bank manzai_CCSSPP_e.xwb  <->  3DS clips MZV_dlNN_SS_P_iii.dspadpcm.bcstm
    CC 08/09/10 -> dl01/dl02/dl03,  SS scene,  PP part.
Within a scene, all parts are concatenated on both sides and the two duration
sequences (Japanese take vs 3DS clip - the same recordings) are aligned
monotonically; only matched pairs are imported. This absorbs clips that moved
across a part boundary and lines that were re-recorded.
Output goes to patch_dlc2/<content>/adv_sound/stream/.

    python import_dlc_voices.py            all scenes
    python import_dlc_voices.py 0805 0907  only those chapter+scene codes
"""
import os, re, struct, math, sys, time
import numpy as np
import dsp

SD = r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/sound/manzai'
CH = {'08': ('0010', 'dl01'), '09': ('0011', 'dl02'), '10': ('0012', 'dl03')}


def xwb(path):
    x = open(path, 'rb').read()
    segs = [struct.unpack_from('<II', x, 12 + i * 8) for i in range(5)]
    bd = segs[0][0]
    count = struct.unpack_from('<I', x, bd + 4)[0]
    esize = struct.unpack_from('<I', x, bd + 72)[0]
    e0, wave = segs[1][0], segs[4][0]
    out = []
    for i in range(count):
        e = e0 + i * esize
        fd, off, ln = struct.unpack_from('<III', x, e + 4)
        tag, ch, rate, bits = fd & 3, (fd >> 2) & 7, (fd >> 5) & 0x3FFFF, (fd >> 31) & 1
        if tag != 0 or ch != 1 or bits != 1:
            raise SystemExit('unexpected codec in %s entry %d' % (path, i))
        out.append((rate, np.frombuffer(x[wave + off: wave + off + ln], dtype='<i2')))
    return out


def resample(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x.astype(np.float64)
    t = np.arange(int(round(len(x) * sr_out / sr_in))) * (sr_in / sr_out)
    cutoff = 0.5 * min(1.0, sr_out / sr_in)
    half = 16
    win = np.kaiser(2 * half + 1, 8.0)
    xf = x.astype(np.float64)
    base = np.floor(t).astype(int)
    frac0 = t - base
    y = np.zeros(len(t))
    for k in range(-half, half + 1):
        idx = base + k
        w = np.sinc(2 * cutoff * (frac0 - k)) * 2 * cutoff * win[k + half]
        v = np.where((idx >= 0) & (idx < len(xf)), xf[np.clip(idx, 0, len(xf) - 1)], 0.0)
        y += v * w
    return y


def align(a, b, tol=0.05, look=3):
    """Monotone alignment of two duration sequences; returns index pairs."""
    i = j = 0
    pairs = []
    while i < len(a) and j < len(b):
        if abs(a[i] - b[j]) <= tol:
            pairs.append((i, j))
            i += 1
            j += 1
            continue
        best = None
        for di in range(0, look + 1):
            for dj in range(0, look + 1):
                if (di or dj) and i + di < len(a) and j + dj < len(b) and abs(a[i + di] - b[j + dj]) <= tol:
                    if best is None or di + dj < best[0]:
                        best = (di + dj, di, dj)
        if best is None:
            break
        i += best[1]
        j += best[2]
    return pairs


def main(only=None):
    log = []
    done = skipped = 0
    t0 = time.time()
    banks = sorted(f for f in os.listdir(SD) if re.match(r'manzai_(08|09|10)[0-9]{4}_e[.]xwb$', f))
    scenes = {}
    for bank in banks:
        cc, ss, pp = re.match(r'manzai_([0-9][0-9])([0-9][0-9])([0-9][0-9])_e[.]xwb$', bank).groups()
        scenes.setdefault((cc, ss), []).append((int(pp), bank))
    for (cc, ss), parts in sorted(scenes.items()):
        if only and (cc + ss) not in only:
            continue
        content, dl = CH[cc]
        tree = 'dlc_r/%s/adv_sound/stream' % content
        clips = sorted(f for f in os.listdir(tree) if f.startswith('MZV_%s_%s_' % (dl, ss)))
        steam = []
        for pp, bank in sorted(parts):
            en = xwb(os.path.join(SD, bank))
            jp = xwb(os.path.join(SD, bank.replace('_e.xwb', '.xwb')))
            for i in range(len(en)):
                steam.append((bank, i, len(jp[i][1]) / jp[i][0], en[i][0], en[i][1]))
        d3 = [(f, dsp.read_cstm(os.path.join(tree, f))) for f in clips]
        pairs = align([c['total'] / c['st']['rate'] for f, c in d3], [s[2] for s in steam])
        out_dir = 'patch_dlc2/%s/adv_sound/stream' % content
        os.makedirs(out_dir, exist_ok=True)
        for k3, ks in pairs:
            f, c = d3[k3]
            bank, i, dj, rate_in, pcm = steam[ks]
            tpl = os.path.join(tree, f)
            rate = c['st']['rate']
            y = resample(pcm, rate_in, rate)
            y = np.clip(np.round(y), -32768, 32767).astype(int).tolist()
            open(os.path.join(out_dir, f), 'wb').write(dsp.build_cstm(y, rate, dsp.correlate_coefs(y), tpl))
            done += 1
        skipped += len(clips) - len(pairs)
        log.append('chapter %s scene %s: %d of %d 3DS clips matched a Steam take by duration (%d Steam entries)'
                   % (cc, ss, len(pairs), len(clips), len(steam)))
        print('ch%s sc%s  %d/%d clips  (%d done, %.0fs)' % (cc, ss, len(pairs), len(clips), done, time.time() - t0), flush=True)
    open('import_dlc_voices.log', 'w').write(chr(10).join(log))
    print('DONE: %d clips imported, %d left Japanese, %.0fs' % (done, skipped, time.time() - t0))


if __name__ == '__main__':
    main(sys.argv[1:] or None)
