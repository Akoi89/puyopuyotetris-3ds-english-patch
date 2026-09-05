"""Put the English title call into the HOME-menu banner's CWAV.

The banner CWAV is PCM16 stereo 48 kHz (2.51 s = the Japanese title bank's
take 3). Steam's title_set_bank_e.xwb entry 3 is the English take of the same
line; it goes in as PCM (no ADPCM), duplicated to both channels, levelled to
the Japanese clip's RMS through the limiter in float.

CWAV layout used: 0x40 header (file size at 0x0C; section table: INFO at 0x14,
DATA at 0x20); INFO (offsets from the INFO section start): encoding u8 at +8, rate +0xC, loop start +0x10, loop end (= sample count) +0x14, channel refs at +0x1C.., each channel's sample ref
offset is relative to DATA+8; DATA = 'DATA' + size + 0x18 padding + ch0 + ch1.

    python banner_cwav.py <banner.bin in> <banner.bin out>
"""
import os, struct, sys, math
import numpy as np
import csar
from import_dlc_voices import xwb, resample
from voice_gain import limiter, rms

SD = r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/sound/voice'
TAKE = 3


def main(src, out):
    b = open(src, 'rb').read(); cw = struct.unpack_from('<I', b, 0x84)[0]; w = b[cw:]
    info = csar.cwav_info(w); assert info['enc'] == 1, 'banner CWAV is not PCM16'
    io_, isz = info['secs'][0x7000]; do_, dsz = info['secs'][0x7001]
    blk = bytearray(w[io_:io_ + isz])
    ct = 8 + 0x14; n = struct.unpack_from('<I', blk, ct)[0]; assert n == 2
    refs = []
    for k in range(n):
        cinfo = ct + struct.unpack_from('<HHI', blk, ct + 4 + k * 8)[2]; refs.append(cinfo)
    ch0_off = struct.unpack_from('<I', blk, refs[0] + 4)[0]
    # Japanese clip level (channel 0)
    jp = np.frombuffer(w[do_ + 8 + ch0_off:do_ + 8 + ch0_off + info['samples'] * 2], dtype='<i2').astype(np.float64)
    # Steam English take
    rate_in, pcm = xwb(os.path.join(SD, 'title_set_bank_e.xwb'))[TAKE]
    y = np.asarray(resample(pcm, rate_in, info['rate']) if rate_in != info['rate'] else pcm, dtype=np.float64)
    g = min(10 ** (14 / 20), rms(jp) / max(rms(y), 1.0)); y = limiter(y * g, info['rate'])
    for _ in range(4):
        g2 = rms(jp) / max(rms(y), 1.0)
        if abs(20 * math.log10(g2)) < 0.15: break
        y = limiter(y * g2, info['rate'])
    s = np.round(y).astype('<i2').tobytes(); ns = len(y)
    print('Steam take %d: %.2fs at %d Hz (source %d Hz), gain %+.1f dB, final RMS %.1f dBFS vs JP %.1f' % (TAKE, ns / info['rate'], info['rate'], rate_in, 20 * math.log10(g), 20 * math.log10(rms(y) / 32768), 20 * math.log10(rms(jp) / 32768)))
    ch1_off = (0x18 + len(s) + 7) // 8 * 8
    struct.pack_into('<I', blk, 0x10, 0); struct.pack_into('<I', blk, 0x14, ns)
    struct.pack_into('<I', blk, refs[0] + 4, 0x18); struct.pack_into('<I', blk, refs[1] + 4, ch1_off)
    body = bytes(0x18) + s + bytes(ch1_off - 0x18 - len(s)) + s
    body += bytes((-len(body)) % 0x20)
    data = b'DATA' + struct.pack('<I', 8 + len(body)) + body
    head = bytearray(w[:0x40]); struct.pack_into('<I', head, 0x0C, 0x40 + len(blk) + len(data))
    struct.pack_into('<HHII', head, 0x14, 0x7000, 0, 0x40, len(blk)); struct.pack_into('<HHII', head, 0x20, 0x7001, 0, 0x40 + len(blk), len(data))
    new_w = bytes(head) + bytes(blk) + data
    chk = csar.cwav_info(new_w); assert chk['samples'] == ns and chk['rate'] == info['rate']
    open(out, 'wb').write(b[:cw] + new_w)
    print('banner CWAV %d -> %d bytes; banner.bin %d -> %d bytes; wrote %s' % (len(w), len(new_w), len(b), cw + len(new_w), out))
    # listening copy
    import wave
    with wave.open('gain_demo/banner_title_call_en.wav', 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(info['rate']); f.writeframes(s)


if __name__ == '__main__':
    main(*sys.argv[1:3])
