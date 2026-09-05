"""Compare loudness of the battle-voice waves in the Japanese original CSAR
against ours (peak and RMS, dBFS), per CWAR bank.

    python voice_levels.py <orig.bcsar> <ours.bcsar> [cwar ...]
"""
import sys, struct, math
import numpy as np
import csar, dsp


def pcm_of(w):
    info = csar.cwav_info(w)
    io_, isz = info['secs'][0x7000]; blk = w[io_:io_ + isz]
    ct = 8 + 0x14; ro = struct.unpack_from('<HHI', blk, ct + 4)[2]; cinfo = ct + ro
    ao = struct.unpack_from('<HHI', blk, cinfo + 8)[2] if struct.unpack_from('<H', blk, cinfo + 8)[0] == 0x0300 else struct.unpack_from('<HHI', blk, cinfo)[2]
    coefs = list(struct.unpack_from('<16h', blk, cinfo + ao))
    do_, dsz = info['secs'][0x7001]
    return np.array(dsp.decode(w[do_ + 8 + 0x18:do_ + dsz], coefs, nsamples=info['samples'])[0], dtype=np.float64)


def db(x): return 20 * math.log10(max(x, 1e-9) / 32768.0)


def stats(p):
    return db(np.abs(p).max()), db(math.sqrt((p ** 2).mean()))


if __name__ == '__main__':
    a, b = csar.Csar(sys.argv[1]), csar.Csar(sys.argv[2])
    banks = [int(x) for x in sys.argv[3:]] or list(range(len(a.blobs)))
    print('%5s %5s | %8s %8s | %8s %8s | %s' % ('cwar', 'waves', 'JP peak', 'JP rms', 'our peak', 'our rms', 'rms diff'))
    for ci in banks:
        try:
            wa, wb = csar.Cwar(a.blobs[ci]).waves, csar.Cwar(b.blobs[ci]).waves
        except Exception:
            continue
        if not wa or a.blobs[ci] == b.blobs[ci]:
            continue
        pa = [stats(pcm_of(w)) for w in wa]; pb = [stats(pcm_of(w)) for w in wb]
        jpk = np.mean([p for p, r in pa]); jrm = np.mean([r for p, r in pa]); opk = np.mean([p for p, r in pb]); orm = np.mean([r for p, r in pb])
        print('%5d %5d | %8.1f %8.1f | %8.1f %8.1f | %+.1f dB' % (ci, len(wb), jpk, jrm, opk, orm, orm - jrm))
