"""Nintendo DSP-ADPCM decode/encode and a CSTM (.bcstm) reader/writer.

    python dsp.py roundtrip <clip.bcstm>      decode -> re-encode with the clip's own
                                              coefficients -> compare DATA byte-for-byte
    python dsp.py rebuild   <clip.bcstm>      decode -> rebuild a whole CSTM from scratch
                                              -> compare the FILE byte-for-byte

Frame: 8 bytes = header (predictor<<4 | scale) + 14 signed nibbles, high first.
    sample = clamp16((nibble << scale) * 2048 + c1*h1 + c2*h2 + 1024) >> 11
"""
import struct, sys, os


def clamp16(v):
    return -32768 if v < -32768 else 32767 if v > 32767 else v


def decode(data, coefs, h1=0, h2=0, nsamples=None):
    out = []
    for f in range(0, len(data), 8):
        hdr = data[f]
        scale = 1 << (hdr & 0xF)
        c1, c2 = coefs[(hdr >> 4) * 2], coefs[(hdr >> 4) * 2 + 1]
        for b in data[f + 1:f + 8]:
            for n in ((b >> 4), (b & 0xF)):
                n = n - 16 if n >= 8 else n
                s = clamp16((n * scale * 2048 + c1 * h1 + c2 * h2 + 1024) >> 11)
                out.append(s)
                h2, h1 = h1, s
                if nsamples is not None and len(out) >= nsamples:
                    return out, h1, h2
    return out, h1, h2


def encode_frame(pcm, h1, h2, coefs):
    """Encode up to 14 samples. Returns (8 bytes, new h1, new h2).

    Closed-loop search over the 8 predictors and three scales, keeping the
    (predictor, scale) whose reconstruction has the least squared error, which
    is what Nintendo's encoder does.
    """
    n = len(pcm)
    best = None
    for p in range(8):
        c1, c2 = coefs[p * 2], coefs[p * 2 + 1]
        # open-loop residual on the true samples decides the starting scale
        a, b = h1, h2
        maxd = 0
        for s in pcm:
            pred = (c1 * a + c2 * b + 1024) >> 11
            d = s - pred
            maxd = max(maxd, abs(d))
            b, a = a, s
        scale = 0
        while scale < 12 and maxd > (7 << scale):
            scale += 1
        for sc in (scale - 1, scale, scale + 1):
            if not 0 <= sc <= 12:
                continue
            a, b = h1, h2
            nib = []
            err = 0
            for s in pcm:
                pred = (c1 * a + c2 * b + 1024) >> 11
                q = (s - pred + (1 << sc >> 1)) >> sc if sc else (s - pred)
                q = -8 if q < -8 else 7 if q > 7 else q
                r = clamp16(((q << sc) * 2048 + c1 * a + c2 * b + 1024) >> 11)
                err += (r - s) * (r - s)
                nib.append(q)
                b, a = a, r
            if best is None or err < best[0]:
                best = (err, p, sc, nib, a, b)
    err, p, sc, nib, a, b = best
    nib += [0] * (14 - n)
    out = bytes([(p << 4) | sc]) + bytes(((nib[i] & 0xF) << 4) | (nib[i + 1] & 0xF) for i in range(0, 14, 2))
    return out, a, b


def encode(pcm, coefs, h1=0, h2=0):
    out = bytearray()
    for i in range(0, len(pcm), 14):
        fr, h1, h2 = encode_frame(pcm[i:i + 14], h1, h2, coefs)
        out += fr
    return bytes(out)


def correlate_coefs(pcm):
    """Derive 16 Q11 coefficients (8 predictor pairs) for a clip.

    Order-2 LPC per 14-sample frame, then split-and-refine clustering of the
    frame predictors into 8 pairs, the way the SDK tool does it in spirit.
    """
    import math
    frames = []
    hist = [0, 0]
    for i in range(0, len(pcm), 14):
        blk = hist + list(pcm[i:i + 14])
        if len(blk) < 16:
            blk += [0] * (16 - len(blk))
        # autocorrelation over the frame with history
        r = [0.0, 0.0, 0.0]
        for k in range(3):
            r[k] = sum(blk[j] * blk[j - k] for j in range(2, 16))
        if r[0] > 0:
            # Levinson-Durbin, order 2
            k1 = r[1] / r[0]
            a1 = k1
            e = r[0] * (1 - k1 * k1)
            k2 = (r[2] - a1 * r[1]) / e if e > 0 else 0.0
            a2 = k2
            a1 = a1 - k2 * a1
            c1, c2 = a1, a2
            if abs(c1) < 4 and abs(c2) < 4:
                frames.append((c1, c2))
        hist = blk[14:16]
    if not frames:
        return [0] * 16
    means = [(sum(f[0] for f in frames) / len(frames), sum(f[1] for f in frames) / len(frames))]
    while len(means) < 8:
        means = [m for pair in ((m[0] + 0.01, m[1] + 0.01), (m[0] - 0.01, m[1] - 0.01)) for m in [pair] for pair in [pair]] if False else \
                [(m[0] + 0.01 * (1 if i else -1), m[1] + 0.01 * (1 if i else -1)) for m in means for i in (0, 1)]
        for _ in range(8):
            groups = [[] for _ in means]
            for f in frames:
                j = min(range(len(means)), key=lambda k: (f[0] - means[k][0]) ** 2 + (f[1] - means[k][1]) ** 2)
                groups[j].append(f)
            means = [(sum(g[0] for g in grp) / len(grp), sum(g[1] for g in grp) / len(grp)) if grp else m
                     for grp, m in zip(groups, means)]
    coefs = []
    for c1, c2 in means:
        coefs += [clamp16(int(round(c1 * 2048))), clamp16(int(round(c2 * 2048)))]
    return coefs


# ------------------------------------------------------------------------------ CSTM
def read_cstm(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'CSTM'
    nblk = struct.unpack_from('<H', d, 0x10)[0]
    refs = {t: (o, s) for t, _, o, s in (struct.unpack_from('<HHII', d, 0x14 + i * 12) for i in range(nblk))}
    info = refs[0x4000][0]
    si = info + 8 + struct.unpack_from('<HHI', d, info + 8)[2]
    f = struct.unpack_from('<BBBBIIIIIIIIIII', d, si)
    st = dict(enc=f[0], loop=f[1], ch=f[2], rate=f[4], loop_start=f[5], loop_end=f[6], nblocks=f[7],
              bsize=f[8], bsamp=f[9], lbsize=f[10], lbsamp=f[11], lbpad=f[12], seek_size=f[13], seek_iv=f[14])
    ct = info + 8 + struct.unpack_from('<HHI', d, info + 0x18)[2]
    n = struct.unpack_from('<I', d, ct)[0]
    chans = []
    for k in range(n):
        ro = struct.unpack_from('<HHI', d, ct + 4 + k * 8)[2]
        cinfo = ct + ro
        adpcm = cinfo + struct.unpack_from('<HHI', d, cinfo)[2]
        coefs = list(struct.unpack_from('<16h', d, adpcm))
        ps, yn1, yn2, lps, lyn1, lyn2 = struct.unpack_from('<HhhHhh', d, adpcm + 32)
        chans.append(dict(coefs=coefs, ps=ps, yn1=yn1, yn2=yn2, lps=lps, lyn1=lyn1, lyn2=lyn2))
    data_off, data_sz = refs[0x4002]
    seek_off, seek_sz = refs[0x4001]
    body = data_off + 0x20
    total = (st['nblocks'] - 1) * st['bsamp'] + st['lbsamp']
    return dict(raw=d, st=st, chans=chans, data=d[body:body + st['nblocks'] * st['bsize']],
                seek=d[seek_off + 8:seek_off + seek_sz], total=total, info_raw=d[info:info + refs[0x4000][1]])


def build_cstm(pcm, rate, coefs, template, adpcm=None):
    """Write a mono, non-looping CSTM using an original clip as the layout template.

    INFO is copied from the template and only the fields that depend on this
    clip are patched (rate, sample count, block counts, coefficients, first
    predictor/scale). SEEK stores the decoder history at the START of each block.
    """
    t = read_cstm(template)
    raw = t['raw']
    total = len(pcm)
    adpcm = encode(pcm, coefs) if adpcm is None else adpcm
    bsize, bsamp = t['st']['bsize'], t['st']['bsamp']       # block geometry from the template
    nblocks = max(1, (total + bsamp - 1) // bsamp)
    lbsamp = total - (nblocks - 1) * bsamp
    lbsize = (lbsamp * 8 + 13) // 14          # Sega: ceil(samples*8/14), not whole frames
    lbpad = (lbsize + 31) // 32 * 32
    seek = bytearray()
    h1 = h2 = 0
    for b in range(nblocks):
        seek += struct.pack('<hh', h1, h2)                 # history BEFORE block b
        blk = adpcm[b * bsize:(b + 1) * bsize]
        n = bsamp if b < nblocks - 1 else lbsamp
        _, h1, h2 = decode(blk, coefs, h1, h2, n)
    seek_sz = 8 + len(seek)
    seek_sz += (-seek_sz) % 0x20
    seek_sec = b'SEEK' + struct.pack('<I', seek_sz) + bytes(seek)
    seek_sec += bytes(seek_sz - len(seek_sec))
    nblk = struct.unpack_from('<H', raw, 0x10)[0]
    refs = {tt: (o, sz) for tt, _, o, sz in (struct.unpack_from('<HHII', raw, 0x14 + i * 12) for i in range(nblk))}
    io_, isz = refs[0x4000]
    info = bytearray(raw[io_:io_ + isz])
    si = 8 + struct.unpack_from('<HHI', info, 8)[2]
    struct.pack_into('<IIIIIIIIII', info, si + 4, rate, 0, total, nblocks, bsize, bsamp, lbsize, lbsamp, lbpad, 4)
    ct = 8 + struct.unpack_from('<HHI', info, 0x18)[2]
    cinfo = ct + struct.unpack_from('<HHI', info, ct + 4)[2]
    adp = cinfo + struct.unpack_from('<HHI', info, cinfo)[2]
    struct.pack_into('<16h', info, adp, *coefs)
    struct.pack_into('<HhhHhh', info, adp + 32, adpcm[0] if adpcm else 0, 0, 0, 0, 0, 0)
    body = bytearray(adpcm)
    want = (nblocks - 1) * bsize + lbpad
    body += bytes(want - len(body))
    data_sec = b'DATA' + struct.pack('<I', 8 + 0x18 + len(body)) + bytes(0x18) + bytes(body)
    off_info = 0x40
    off_seek = off_info + len(info)
    off_data = off_seek + len(seek_sec)
    head = bytearray(raw[:0x40])
    struct.pack_into('<I', head, 0x0C, off_data + len(data_sec))
    struct.pack_into('<HHII', head, 0x14, 0x4000, 0, off_info, len(info))
    struct.pack_into('<HHII', head, 0x20, 0x4001, 0, off_seek, len(seek_sec))
    struct.pack_into('<HHII', head, 0x2C, 0x4002, 0, off_data, len(data_sec))
    return bytes(head) + bytes(info) + seek_sec + data_sec


if __name__ == '__main__':
    mode, path = sys.argv[1], sys.argv[2]
    c = read_cstm(path)
    st, ch = c['st'], c['chans'][0]
    pcm, _, _ = decode(c['data'], ch['coefs'], 0, 0, c['total'])
    print('%s: %d samples @ %d Hz, %d blocks' % (os.path.basename(path), len(pcm), st['rate'], st['nblocks']))
    if mode == 'roundtrip':
        re_ = encode(pcm, ch['coefs'])
        orig = c['data'][:len(re_)]
        same = sum(1 for i in range(0, len(re_), 8) if re_[i:i + 8] == orig[i:i + 8])
        print('frames byte-identical to Sega\'s encoder: %d / %d' % (same, len(re_) // 8))
        dec2, _, _ = decode(re_, ch['coefs'], 0, 0, len(pcm))
        import math
        sig = sum(s * s for s in pcm) or 1
        noise = sum((a - b) ** 2 for a, b in zip(pcm, dec2)) or 1
        print('re-encoded vs original PCM: SNR %.1f dB' % (10 * math.log10(sig / noise)))
        # and with freshly derived coefficients, as a real import would use
        mine = correlate_coefs(pcm)
        re2 = encode(pcm, mine)
        dec3, _, _ = decode(re2, mine, 0, 0, len(pcm))
        noise = sum((a - b) ** 2 for a, b in zip(pcm, dec3)) or 1
        print('with my own coefficients:       SNR %.1f dB   coefs=%s' % (10 * math.log10(sig / noise), mine))
    elif mode == 'rebuild':
        raw = c['raw']
        outw = build_cstm(pcm, st['rate'], ch['coefs'], path, adpcm=c['data'][:(st['nblocks'] - 1) * st['bsize'] + st['lbsize']])
        print('container rebuilt around Sega frames: byte-identical: %s' % (outw == raw))
        out = build_cstm(pcm, st['rate'], ch['coefs'], path)
        print('rebuilt with my encoder: %d bytes vs %d; byte-identical: %s' % (len(out), len(raw), out == raw))
        if out != raw:
            diff = [i for i in range(min(len(out), len(raw))) if out[i] != raw[i]]
            print('   first difference at 0x%X (%d differing bytes in common length)' % (diff[0], len(diff)) if diff else '   (prefix identical; lengths differ)')
