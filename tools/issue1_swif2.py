"""Compare the party2p SWIF layout member (index 17) across 3DS JP, Steam JP and Steam EN.

    python issue1_swif2.py

Prints size, the texture-entry table and the timeup UV rects (in texture pixels) for each.
"""
import os
import struct
import sys
import narc

PUYO_ROOT = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
SRC = [
    ('3DS JP ', 'tr_envoice/tenp/party/party2p/party2p.narc', 256, 128),
    ('StmJP  ', os.path.join(PUYO_ROOT, 'PuyoPuyoTetris', 'data_steam', 'data', 'tenp', 'party', 'party2p', 'party2p.narc'), 1024, 512),
    ('StmEN  ', os.path.join(PUYO_ROOT, 'PuyoPuyoTetris', 'data_steam', 'data', 'tenp', 'party', 'party2p', 'party2p_e.narc'), 1024, 512),
]
for tag, p, TW, TH in SRC:
    m = narc.read(p)['members'][17]
    print('%s len=%d  head=%s' % (tag, len(m), m[:0x30].hex()))
    names = [n.decode('latin1') for n in m[0x30:0x90].split(b'\0') if n and all(32 <= c < 127 for c in n)]
    print('   names', names)
    # texture table: 5 u32 per entry (wh, ?, count, rectoff, ...) - print the ints after the float run
    ints = [struct.unpack_from('<I', m, i)[0] for i in range(0x150, min(len(m), 0x1c0), 4)]
    print('   ints@150:', ' '.join('%x' % v for v in ints))
    rects = []
    for i in range(0, len(m) - 16, 4):
        u0, v0, u1, v1 = struct.unpack_from('<ffff', m, i)
        if not all(0.0 <= x <= 1.0 for x in (u0, v0, u1, v1)) or u1 <= u0 or v1 <= v0:
            continue
        x0, y0, x1, y1 = u0 * TW, v0 * TH, u1 * TW, v1 * TH
        if all(abs(v - round(v)) < 0.01 for v in (x0, y0, x1, y1)) and (x1 - x0) >= 8 and (y1 - y0) >= 8 and (x1 - x0) < TW:
            rects.append((i, int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))))
    for r in rects:
        print('   @%04x  x %4d..%4d  y %4d..%4d   (%dx%d)' % (r[0], r[1], r[3], r[2], r[4], r[3] - r[1], r[4] - r[2]))
