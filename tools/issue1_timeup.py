"""Issue #1: rebuild timeup_d4444 (tenp/party/party2p/party2p.narc, CTPK member 18, RGBA4 256x128)
from Sega's own Steam English art, one letter per sprite cell, so the six per-letter sprites the
layout member draws spell TIME! on screen.

    python issue1_timeup.py preview   -> <scratch>/timeup_new.png (texture), timeup_sim.png (JP vs EN as the
                                          sprites land on screen), no files in the patch tree touched
    python issue1_timeup.py apply     -> writes the texture into patch/romfs/tenp/party/party2p/party2p.narc
                                          via labels2's CTPK path (tex.encode against Sega's member)

Cells (UV rects in the 3DS SWIF, texture px) and their screen offsets (x relative to centre, from the SWIF):
  1 (1,1,63,65)    x=-102     2 (65,1,119,61)   x=-60     3 (121,1,182,62)  x=-13
  4 (1,67,62,126)  x=34       5 (64,67,108,111) x=59      6 (185,1,247,67)  x=95
Letters: T I M E in cells 1-4, "!" in cell 6, cell 5 (the small tsu cell) left empty.
"""
import os, sys
import numpy as np
from PIL import Image
import narc, labels, tex, labels2

SCR = 'issue1_scratch/'
PUYO_ROOT = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
STEAM = os.path.join(PUYO_ROOT, 'PuyoPuyoTetris', 'data_steam', 'data', 'tenp', 'party', 'party2p', 'party2p_e.narc')
NARC = 'tenp/party/party2p/party2p.narc'
CELLS = [((1, 1, 63, 65), -102, 0), ((65, 1, 119, 61), -60, -16), ((121, 1, 182, 62), -13, -3),
         ((1, 67, 62, 126), 34, 3), ((64, 67, 108, 111), 59, -18), ((185, 1, 247, 67), 95, -3)]
# letter column cuts in the 1024x512 Steam art (red-outline runs, cut mid-gap so each keeps its own shadow)
CUTS = [(125, 312), (312, 397), (397, 637), (637, 792), (792, 1010)]
# letter -> cell index, horizontal placement inside the cell: 'l' left, 'c' centre, 'r' right, or an int x offset
PLACE = [(0, 'c'), (1, 'c'), (2, 'l'), (3, 'r'), (5, 'c')]
SCALE = 0.235          # 1024-art px -> 3DS px (letters end up ~58 px tall, the katakana were 59-66)


def steam_letters():
    import io
    ms = narc.read(STEAM)['members']
    m = ms[18]
    offs = []
    j = m.find(b'DDS ')
    while j >= 0:
        offs.append(j); j = m.find(b'DDS ', j + 4)
    blob = m[offs[2]:]
    im = Image.open(io.BytesIO(blob)); im.load(); im = im.convert('RGBA')
    assert im.size == (1024, 512), im.size
    out = []
    for x0, x1 in CUTS:
        crop = im.crop((x0, 40, x1, 400))          # rows 40..400: the letters; the white glow sits below 420
        a = np.array(crop)[:, :, 3] > 40
        ys = np.where(a.any(axis=1))[0]; xs = np.where(a.any(axis=0))[0]
        crop = crop.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        w, h = crop.size
        out.append(crop.resize((max(1, round(w * SCALE)), max(1, round(h * SCALE))), Image.LANCZOS))
    return out


def build_texture(base):
    """base: Sega's 256x128 RGBA texture (for the alpha-4 look nothing is reused, just the size)."""
    img = Image.new('RGBA', base.size, (0, 0, 0, 0))
    letters = steam_letters()
    for L, (ci, how) in zip(letters, PLACE):
        (x0, y0, x1, y1), _, _ = CELLS[ci]
        cw, chh = x1 - x0, y1 - y0
        lw, lh = L.size
        if lw > cw or lh > chh:
            f = min(cw / lw, chh / lh)
            L = L.resize((max(1, int(lw * f)), max(1, int(lh * f))), Image.LANCZOS); lw, lh = L.size
        if how == 'l':
            px = x0
        elif how == 'r':
            px = x1 - lw
        elif how == 'c':
            px = x0 + (cw - lw) // 2
        else:
            px = x0 + int(how)
        py = y0 + (chh - lh) // 2
        img.alpha_composite(L, (px, py))
    return img


def simulate(texture, tag):
    """Lay the six cells out at their screen offsets on a 400x240 canvas, centred, 1:1."""
    can = Image.new('RGBA', (400, 240), (70, 110, 70, 255))
    for (x0, y0, x1, y1), sx, sy in CELLS:
        cell = texture.crop((x0, y0, x1, y1))
        w, h = cell.size
        can.alpha_composite(cell, (200 + sx - w // 2, 120 + sy - h // 2))
    return can


if __name__ == '__main__':
    mode = sys.argv[1]
    arc = narc.read(os.path.join('tr_envoice', NARC))
    mi, e, base, fmt, hdr = labels2.get_texture(arc, 'timeup_d4444')
    new = build_texture(base)
    if mode == 'preview':
        bg = Image.new('RGBA', new.size, (90, 90, 110, 255)); bg.alpha_composite(new)
        bg.resize((768, 384), Image.NEAREST).save(SCR + 'timeup_new.png')
        sim = Image.new('RGBA', (400, 490), (0, 0, 0, 255))
        sim.paste(simulate(base, 'JP'), (0, 0)); sim.paste(simulate(new, 'EN'), (0, 250))
        sim.resize((800, 980), Image.NEAREST).save(SCR + 'timeup_sim.png')
        print('wrote', SCR + 'timeup_new.png', 'and timeup_sim.png')
    elif mode == 'apply':
        out = os.path.join('patch/romfs', NARC)
        arc_out = narc.read(out) if os.path.exists(out) else arc
        ms = list(arc_out['members'])
        m = bytearray(ms[mi])
        basebytes = bytes(arc['members'][mi][e['off']:e['off'] + e['size']])
        m[e['off']:e['off'] + e['size']] = tex.encode(new, fmt, basebytes)
        ms[mi] = bytes(m)
        open(out, 'wb').write(narc.build(arc_out, ms))
        # read back
        mi2, e2, img2, fmt2, hdr2 = labels2.get_texture(narc.read(out), 'timeup_d4444')
        d = np.abs(np.array(img2).astype(int) - np.array(new).astype(int)).max()
        print('wrote', out, ' read-back max channel diff vs intended (RGBA4 quantisation expected <= 17):', d)
