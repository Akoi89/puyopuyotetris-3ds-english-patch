"""Decode the UV rectangles in party2p.narc member 17 (SWIF) that reference timeup_d4444.

Floats are read as (u0, v0, u1, v1) with u in 1/256 and v in 1/128 of the 256x128 texture.
Prints every 4-float group in the member that maps to a plausible rect.
"""
import struct, sys
import narc

ms = narc.read('tr_envoice/tenp/party/party2p/party2p.narc')['members']
m = ms[17]
names = [n for n in m[0x30:0x90].split(b'\0') if n]
print('texture names in SWIF:', names)
rects = []
for i in range(0, len(m) - 16, 4):
    u0, v0, u1, v1 = struct.unpack_from('<ffff', m, i)
    ok = all(0.0 <= x <= 1.0 for x in (u0, v0, u1, v1)) and u1 > u0 and v1 > v0
    if not ok:
        continue
    x0, y0, x1, y1 = u0 * 256, v0 * 128, u1 * 256, v1 * 128
    if all(abs(v - round(v)) < 0.01 for v in (x0, y0, x1, y1)) and (x1 - x0) >= 8 and (y1 - y0) >= 8:
        rects.append((i, int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))))
for r in rects:
    print('@%04x  x %3d..%3d  y %3d..%3d   (%dx%d)' % (r[0], r[1], r[3], r[2], r[4], r[3] - r[1], r[4] - r[2]))
