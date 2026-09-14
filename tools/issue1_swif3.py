"""Find, in the 3DS party2p SWIF (member 17), the fields Sega changed on Steam for the English Time Up:
the sprite size tuple (w, h, w/2, h/2) of cell 1, the per-sprite visibility flags and screen positions.

    python issue1_swif3.py
"""
import struct
import narc

m = narc.read('tr_envoice/tenp/party/party2p/party2p.narc')['members'][17]
print('len', len(m))


def f(o):
    return struct.unpack_from('<f', m, o)[0]


def u(o):
    return struct.unpack_from('<I', m, o)[0]


# 1. size tuples: four floats (w, h, w/2, h/2) with w,h in 8..256
for o in range(0, len(m) - 16, 4):
    w, h, hw, hh = (f(o + k) for k in (0, 4, 8, 12))
    if 8 <= w <= 256 and 8 <= h <= 256 and abs(hw * 2 - w) < 0.01 and abs(hh * 2 - h) < 0.01 and w == int(w) and h == int(h):
        print('size tuple @%04x: %g x %g' % (o, w, h))
# 2. dump the tail (from 0x0e00) as mixed int/float rows so the anim/position block can be read by eye
print('--- tail dump: offset, then 8 dwords as int|float')
for o in range(0x0c00, len(m), 32):
    cells = []
    for k in range(0, 32, 4):
        if o + k + 4 > len(m):
            break
        iv, fv = u(o + k), f(o + k)
        if iv == 0:
            cells.append('0')
        elif 1e-3 < abs(fv) < 1e5:
            cells.append('%.4g' % fv)
        else:
            cells.append('%08x' % iv)
    print('%04x  %s' % (o, ' '.join('%9s' % c for c in cells)))
