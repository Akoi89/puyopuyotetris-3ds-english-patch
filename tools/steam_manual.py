"""Official English art for the sprites the label passes never caught: the
Replay Report badge rows, the Puzzle League rank pills, and the Broadcast
Station TV logo. Each of these lives in a Steam texture whose Japanese and
English versions share ONE layout, so the Japanese 3DS sprite is located in
Steam's Japanese texture by template matching (1x, 2x or 4x) and the English
sprite is lifted from the same spot in Steam's English texture.

    python steam_manual.py preview     -> steam_manual_preview/*.png
    python steam_manual.py apply       -> patch/romfs rewritten (after labels passes)
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
import narc, labels, tex
from labels2 import get_texture
from steam_labels import find, premul

OVERLAY = 'patch/romfs'
ST = 'steam_sweep/'
# (3DS narc, texture, region (x0,y0,x1,y1) to search for sprites, min/max sprite height, Steam pair stem, note)
# mode 'match': Steam jp/en share a layout, locate by template.  mode 'ordered': take the
# Steam EN sprites in reading order (region, min/max height) and assign them to the 3DS
# sprites in the given order, starting at `skip`.
JOBS = [
    ('replay_quick_report/replay_quick_report.narc', 'replay02_bc3', (0, 0, 175, 256), 22, 40, 'mydata__kansyou__kansyou_e/1_1', 'replay report badges',
     dict(mode='ordered', en_region=(0, 0, 512, 680), en_h=(40, 80), order='rows', skip=0)),
    ('replay_quick_report/replay_quick_report.narc', 'replay01_bc3', (0, 60, 175, 256), 22, 40, 'mydata__kansyou__kansyou_e/1_1', 'replay report badges',
     dict(mode='ordered', en_region=(0, 0, 512, 680), en_h=(40, 80), order='rows', skip=7)),
    ('internet/standby_puzzleleague.narc', 'standby_puzzleleague04_etc1a4', (0, 0, 512, 256), 18, 40, 'internet__standby_puzzleleague_e/1_46', 'league rank pills',
     dict(mode='ordered', en_region=(0, 0, 1024, 1024), en_h=(80, 120), order='cols', skip=0)),
    ('internet/puyotetoBS.narc', 'puyotetoBS02_d4444', (220, 430, 390, 512), 40, 90, 'internet__puyotetoBS_e/1_0', 'Broadcast Station TV logo', dict(mode='fixed', en_box=(438, 383, 776, 492))),
    ('mydata/kansyou/kansyou.narc', 'puyotetoBS02_d4444', (220, 430, 390, 512), 40, 90, 'internet__puyotetoBS_e/1_0', 'Broadcast Station TV logo', dict(mode='fixed', en_box=(438, 383, 776, 492))),
]


def sprite_boxes(img, region, minh, maxh):
    a = np.array(img)[:, :, 3] > 32
    x0, y0, x1, y1 = region
    sub = np.zeros_like(a); sub[y0:y1, x0:x1] = a[y0:y1, x0:x1]
    # connected components of opaque pixels, 4-connected, with a 2 px horizontal bridge
    d = sub.copy(); d[:, 1:] |= sub[:, :-1]; d[:, :-1] |= sub[:, 1:]
    h, w = d.shape; lab = np.zeros((h, w), np.int32); n = 0; out = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if d[y, x] and not lab[y, x]:
                n += 1; stack = [(y, x)]; lab[y, x] = n; ys = []; xs = []
                while stack:
                    cy, cx = stack.pop(); ys.append(cy); xs.append(cx)
                    for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                        if y0 <= ny < y1 and x0 <= nx < x1 and d[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; stack.append((ny, nx))
                bx = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
                if minh <= bx[3] - bx[1] <= maxh and bx[2] - bx[0] >= 30:
                    out.append(bx)
    return sorted(out, key=lambda b: (b[1], b[0]))


def grow(im, box, lim=12):
    a = np.array(im)[:, :, 3] > 16
    x0, y0, x1, y1 = box; X0, Y0, X1, Y1 = x0 - lim, y0 - lim, x1 + lim, y1 + lim
    while x0 > max(0, X0) and a[y0:y1, x0 - 1].any(): x0 -= 1
    while x1 < min(im.width, X1) and a[y0:y1, x1].any(): x1 += 1
    while y0 > max(0, Y0) and a[y0 - 1, x0:x1].any(): y0 -= 1
    while y1 < min(im.height, Y1) and a[y1, x0:x1].any(): y1 += 1
    return x0, y0, x1, y1


_cache = {}


def steam(stem, which, s):
    k = (stem, which, s)
    if k not in _cache:
        im = Image.open(ST + stem + '_%s.png' % which).convert('RGBA')
        _cache[k] = im if s == 1 else im.resize((im.width // s, im.height // s), Image.BOX)
    return _cache[k]


def run(preview_only):
    os.makedirs('steam_manual_preview', exist_ok=True)
    by = {}
    for j in JOBS:
        by.setdefault(j[0], []).append(j)
    for rel, jobs in by.items():
        outp = os.path.join(OVERLAY, rel); src = outp if os.path.exists(outp) else os.path.join('tr_envoice', rel)
        arc = narc.read(src); ms = list(arc['members']); orig_arc = narc.read(os.path.join('jp_orig', rel))
        for _, sel, region, minh, maxh, stem, note, opt in jobs:
            mi, e, img, fmt, hdr = get_texture(arc, sel); img = img.copy(); before = img.copy()
            _, _, orig, _, _ = get_texture(orig_arc, sel)
            boxes = sprite_boxes(orig, region, minh, maxh)
            if opt.get('order') == 'cols':
                boxes.sort(key=lambda b: (b[0] // 150, b[1]))
            print('%s %s: %d sprites in %s' % (rel, sel, len(boxes), region))
            px = img.load(); done = 0
            en = steam(stem, 'en', 1)
            en_boxes = None
            if opt['mode'] == 'ordered':
                eb = sprite_boxes(en, opt['en_region'], *opt['en_h'])
                eb.sort(key=lambda b: (b[0] // (en.width // 2), b[1]) if opt.get('order') == 'cols' else (b[1], b[0]))
                en_boxes = eb[opt['skip']:]
                print('   %d Steam EN sprites, using from #%d' % (len(eb), opt['skip']))
            for k, bx in enumerate(boxes):
                crop = orig.crop(bx)
                if opt['mode'] == 'ordered':
                    if k >= len(en_boxes): print('   sprite %s: no Steam sprite left' % (bx,)); continue
                    gb = en_boxes[k]; score = 1.0; s = 1; sb = gb
                elif opt['mode'] == 'fixed':
                    gb = tuple(opt['en_box']); score = 1.0; s = 1; sb = gb
                else:
                    best = None
                    for s in (1, 2, 4):
                        r = find(crop, steam(stem, 'jp', s))
                        if r and (best is None or r[0] > best[0]): best = (r[0], r[1], s)
                    if best is None or best[0] < 0.75:
                        print('   sprite %s: no match (%s)' % (bx, None if best is None else round(best[0], 2))); continue
                    score, (x, y), s = best
                    sb = (x * s, y * s, (x + crop.width) * s, (y + crop.height) * s)
                    gb = grow(en, sb, lim=4 * s)
                sp = en.crop(gb)
                room = grow(orig, bx, lim=6)
                rw, rh = room[2] - room[0], room[3] - room[1]
                sc = min(1.0, rw / sp.width, rh / sp.height)
                if sc < 1.0: sp = sp.resize((max(1, round(sp.width * sc)), max(1, round(sp.height * sc))), Image.LANCZOS)
                for yy in range(room[1], room[3]):
                    for xx in range(room[0], room[2]): px[xx, yy] = (0, 0, 0, 0)
                img.alpha_composite(sp, (room[0] + (rw - sp.width) // 2, room[1] + (rh - sp.height) // 2)); done += 1
                print('   sprite %s -> steam %s /%d score %.2f, pasted %dx%d' % (bx, sb, s, score, sp.width, sp.height))
            if not preview_only and done:
                if sel.startswith('COMP:'): ms[mi] = tex.comp_encode(img, fmt, hdr, ms[mi])
                else:
                    m = bytearray(ms[mi]); base = bytes(m[e['off']:e['off'] + e['size']]); m[e['off']:e['off'] + e['size']] = tex.encode(img, fmt, base); ms[mi] = bytes(m)
            W = min(512, img.width); scl = W / img.width; H = int(img.height * scl)
            sheet = Image.new('RGBA', (W * 3 + 16, H + 16), (40, 40, 60, 255)); d = ImageDraw.Draw(sheet)
            for c, (lab, im) in enumerate((('3DS jp', orig), ('current', before), ('official EN', img))):
                xx = c * (W + 8); d.text((xx + 2, 0), lab, fill=(255, 220, 0, 255)); t = im.resize((W, H)); sheet.paste(t, (xx, 16), t)
            sheet.save('steam_manual_preview/%s__%s.png' % (rel.replace('/', '__')[:-5], sel))
        if not preview_only:
            os.makedirs(os.path.dirname(outp), exist_ok=True); open(outp, 'wb').write(narc.build(arc, ms)); print('wrote', outp)


if __name__ == '__main__':
    run(sys.argv[1] != 'apply')
