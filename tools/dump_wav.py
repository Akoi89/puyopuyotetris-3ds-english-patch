"""Decode CWAV waves out of a CSAR into .wav files for listening.

    python dump_wav.py <bcsar> <outdir> <cwar_index>:<wave_index> [...]
"""
import os, sys, wave, struct
import csar, dsp

path, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
c = csar.Csar(path)
for spec in sys.argv[3:]:
    ci, wi = (int(x) for x in spec.split(':'))
    w = csar.Cwar(c.blobs[ci]).waves[wi]
    info = csar.cwav_info(w)
    io_, isz = info['secs'][0x7000]
    blk = w[io_:io_ + isz]
    ct = 8 + 0x14
    ro = struct.unpack_from('<HHI', blk, ct + 4)[2]
    cinfo = ct + ro
    ao = struct.unpack_from('<HHI', blk, cinfo + 8)[2] if struct.unpack_from('<H', blk, cinfo + 8)[0] == 0x0300 else struct.unpack_from('<HHI', blk, cinfo)[2]
    coefs = list(struct.unpack_from('<16h', blk, cinfo + ao))
    do_, dsz = info['secs'][0x7001]
    body = w[do_ + 8 + 0x18:do_ + dsz]
    pcm = dsp.decode(body, coefs, nsamples=info["samples"])[0]
    out = os.path.join(outdir, 'cwar%03d_wave%02d.wav' % (ci, wi))
    with wave.open(out, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(info['rate'])
        f.writeframes(struct.pack('<%dh' % len(pcm), *[max(-32768, min(32767, int(v))) for v in pcm]))
    print(out, '%.2fs' % (len(pcm) / info['rate']))
