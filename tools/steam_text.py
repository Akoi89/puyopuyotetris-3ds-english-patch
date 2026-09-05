"""Pair our redrawn 3DS labels with Sega's official English sprites by TEXT.

Steam's English textures are laid out differently from both the 3DS and
Steam's own Japanese textures, so positions cannot be matched. Instead
steam_ocr.ps1 reads every Steam English texture with Windows OCR
(steam_ocr.json); this script normalises that text, pairs each OCR line (or
two vertically adjacent lines, for two-line labels) with the label groups in
labels_en_p*.json / labels2_en.json whose English is the same, grows the OCR
rectangle to the sprite's transparent margins (so pills and outlines come
along), scales the sprite into the room the Japanese label had on the 3DS
texture, and pastes it over the current overlay.

    python steam_text.py match          -> steam_text.json + steam_text_report.md
    python steam_text.py preview        -> steam_text_preview/*.png (no writes)
    python steam_text.py apply          -> patch/romfs, patch_dlc2 rewritten
                                           (run after labels.py apply / labels2.py apply)
"""
import os, re, sys, json, collections
import numpy as np
from PIL import Image, ImageDraw
import narc, tex
from labels2 import get_texture

OVERLAY = {'tr_envoice': 'patch/romfs', 'tr_jpvoice': 'patch/romfs', 'dlc_r': 'patch_dlc2'}
STOP = {'e', 'narc', 'data', 'menu', 'internet', 'tenp', 'puyo', 'common', 'adventure', 'mydata', 'title', 'dlc', 'surfboard', 'ext', 'texture', 'tex', 'png'}


def norm(t):
    t = t.lower().replace('&', 'and')
    return re.sub(r'[^a-z0-9]+', '', t)


def tokens(s):
    return {t for t in re.split(r'[^a-z0-9]+', s.lower()) if len(t) >= 3 and t not in STOP}


_img = {}


def steam_img(rel):
    if rel not in _img:
        _img[rel] = Image.open(os.path.join('steam_sweep', rel)).convert('RGBA')
    return _img[rel]


def grow(im, box, limit_x, limit_y):
    a = np.array(im)[:, :, 3] > 16
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(im.width, x1), min(im.height, y1)
    L0, T0, R0, B0 = x0 - limit_x, y0 - limit_y, x1 + limit_x, y1 + limit_y
    def col_ink(x): return a[y0:y1, x].any()
    def row_ink(y): return a[y, x0:x1].any()
    while x0 > max(0, L0) and col_ink(x0 - 1): x0 -= 1
    while x1 < min(im.width, R0) and col_ink(x1): x1 += 1
    while y0 > max(0, T0) and row_ink(y0 - 1): y0 -= 1
    while y1 < min(im.height, B0) and row_ink(y1): y1 += 1
    return x0, y0, x1, y1


def our_texts():
    """group id -> English text, for both label passes (composite keys 'a+b' map both)."""
    out = {}
    for f in ('labels_en_p0.json', 'labels_en_p1.json', 'labels_en_p2.json'):
        for k, v in json.load(open(f, encoding='utf-8')).items():
            for g in k.split('+'):
                out[('labels.json', int(g))] = v
    for k, v in json.load(open('labels2_en.json', encoding='utf-8')).items():
        for g in k.split('+'):
            out[('labels2.json', int(g))] = v
    return out


OCR_LINES = {}


def ocr_candidates():
    """normalised text -> list of (steam rel png, box, raw text)."""
    O = json.load(open('steam_ocr.json', encoding='utf-8-sig'))
    for rel, lines in O.items():
        OCR_LINES[rel] = [(l['x'], l['y'], l['x'] + l['w'], l['y'] + l['h']) for l in lines if l['w'] > 0 and l['h'] > 0]
    cands = collections.defaultdict(list)
    for rel, lines in O.items():
        lines = sorted(lines, key=lambda l: (l['y'], l['x']))
        for l in lines:
            if l['w'] <= 0 or l['h'] <= 0: continue
            k = norm(l['text'])
            if not k: continue
            cands[k].append((rel, (l['x'], l['y'], l['x'] + l['w'], l['y'] + l['h']), l['text']))
            m = re.match(r'\s*japan\s*[(（](.+)[)）]\s*$', l['text'], re.I)    # prefecture pills: 'Japan(Hokkaido)'
            if m:
                cands['pref:' + norm(m.group(1))].append((rel, (l['x'], l['y'], l['x'] + l['w'], l['y'] + l['h']), l['text']))
        # two-line labels: consecutive lines with overlapping x range and a small gap
        for i, a in enumerate(lines):
            for b in lines[i + 1:i + 4]:
                if b['y'] < a['y'] + a['h'] - 2 or b['y'] > a['y'] + a['h'] + a['h']: continue
                if b['x'] + b['w'] < a['x'] or b['x'] > a['x'] + a['w']: continue
                box = (min(a['x'], b['x']), a['y'], max(a['x'] + a['w'], b['x'] + b['w']), b['y'] + b['h'])
                cands[norm(a['text'] + b['text'])].append((rel, box, a['text'] + ' / ' + b['text']))
    return cands


_tds = {}


def tds_texture(root, rel, sel):
    k = (root, rel, sel)
    if k not in _tds:
        _tds[k] = get_texture(narc.read(os.path.join(root, rel)), sel)[2]
    return _tds[k]


def ink_colour(im, box):
    a = np.array(im.crop(tuple(int(v) for v in box))).astype(float)
    m = a[:, :, 3] > 128
    if m.sum() < 5:
        return None
    return a[:, :, :3][m].mean(axis=0)


EXCLUDE = {'chain!', 'Mild', 'Hot', 'Spicy', 'Sweet', 'Medium'}


def match():
    texts = our_texts(); cands = ocr_candidates()
    results = []; missing = collections.Counter(); found = collections.Counter()
    for f in ('labels.json', 'labels2.json'):
        for l in json.load(open(f, encoding='utf-8')):
            t = texts.get((f, l['group']))
            if t is None or t in EXCLUDE:
                continue
            jp_col = ink_colour(tds_texture(l['root'], l['narc'], l['tex']), l['box'])
            bx = l['box']; jp_aspect = (bx[2] - bx[0]) / max(1, bx[3] - bx[1])
            jp_fill = float((np.array(tds_texture(l['root'], l['narc'], l['tex']).crop(tuple(bx)))[:, :, 3] > 128).mean())
            key = norm(t)
            if not key: continue
            opts = cands.get(key, []) or cands.get('pref:' + key, [])
            if not opts:
                missing[t] += 1
                results.append(dict(id=l['id'], src=f, root=l['root'], narc=l['narc'], tex=l['tex'], box=l['box'], text=t, ok=False)); continue
            tk = tokens(l['narc'])
            scored = []
            punct = lambda z: ''.join(sorted(c for c in z if c in '.!?'))
            opts = [o for o in opts if punct(o[2]) == punct(t)] or []
            if not opts:
                missing[t + '  [punctuation differs]'] += 1
                results.append(dict(id=l['id'], src=f, root=l['root'], narc=l['narc'], tex=l['tex'], box=l['box'], text=t, ok=False, why='punctuation')); continue
            for rel, box, raw in opts:
                im = steam_img(rel); bh = box[3] - box[1]
                gb = grow(im, box, limit_x=max(8, bh), limit_y=max(6, bh // 2))
                col = ink_colour(im, gb)
                cdist = float(np.abs(col - jp_col).mean()) if (col is not None and jp_col is not None) else 999.0
                fill = float((np.array(im.crop(gb))[:, :, 3] > 128).mean())
                cdist += 150.0 * max(0.0, abs(fill - jp_fill) - 0.2)      # a filled pill where the 3DS had bare text, or vice versa
                aspect = (gb[2] - gb[0]) / max(1, gb[3] - gb[1])
                same = len(tokens(rel.split('/')[0]) & tk)
                scored.append(((cdist <= 40, -int(abs(aspect - jp_aspect) * 2), same, -int(cdist // 10), (gb[2] - gb[0]) * (gb[3] - gb[1])), rel, box, raw, gb, cdist))
            _, rel, box, raw, gb, cdist = max(scored, key=lambda z: z[0])
            # reject: OCR line is only part of a larger sprite, or the sprite would shrink to unreadable
            ow, oh = box[2] - box[0], box[3] - box[1]; gw, gh = gb[2] - gb[0], gb[3] - gb[1]
            orig = tds_texture(l['root'], l['narc'], l['tex'])
            room = grow(orig, tuple(l['box']), limit_x=(l['box'][2] - l['box'][0]) // 2, limit_y=2)
            rw, rh = room[2] - room[0], room[3] - room[1]
            sc = min(rw / gw, rh / gh)
            why = None
            others = [o for o in OCR_LINES.get(rel, []) if not (o[0] >= box[0] - 2 and o[1] >= box[1] - 2 and o[2] <= box[2] + 2 and o[3] <= box[3] + 2)]
            inside = [o for o in others if gb[0] < (o[0] + o[2]) / 2 < gb[2] and gb[1] < (o[1] + o[3]) / 2 < gb[3]]
            if inside: why = 'partial sprite'
            elif cdist > 40: why = 'colour too different (%.0f)' % cdist
            elif sc * gh < 0.6 * rh: why = 'would shrink to %d%% of the slot height' % round(100 * sc * gh / rh)
            if why:
                missing[t + '  [' + why + ']'] += 1
                results.append(dict(id=l['id'], src=f, root=l['root'], narc=l['narc'], tex=l['tex'], box=l['box'], text=t, ok=False, why=why)); continue
            results.append(dict(id=l['id'], src=f, root=l['root'], narc=l['narc'], tex=l['tex'], box=l['box'], text=t, ok=True,
                                steam=dict(rel=rel, ocr=list(box), box=list(gb), raw=raw, cdist=round(cdist, 1))))
            found[t] += 1
    json.dump(results, open('steam_text.json', 'w', encoding='utf-8'), indent=0)
    ok = [r for r in results if r['ok']]
    with open('steam_text_report.md', 'w', encoding='utf-8') as f:
        f.write('# Steam official-sprite pairing by text\n\n%d of %d labels paired.\n\n## Paired texts (%d)\n\n' % (len(ok), len(results), len(found)))
        for t, n in sorted(found.items()):
            f.write('- %r x%d\n' % (t, n))
        f.write('\n## No Steam sprite with this text (%d texts)\n\n' % len(missing))
        for t, n in sorted(missing.items(), key=lambda kv: -kv[1]):
            f.write('- %r x%d\n' % (t, n))
    print('paired %d of %d labels (%d distinct texts found, %d texts missing); see steam_text_report.md' % (len(ok), len(results), len(found), len(missing)))


def composite(img, orig, r):
    st = r['steam']; sp = steam_img(st['rel']).crop(st['box'])
    room = grow(orig, tuple(r['box']), limit_x=(r['box'][2] - r['box'][0]) // 2, limit_y=2)
    rw, rh = room[2] - room[0], room[3] - room[1]
    sc = min(rw / sp.width, rh / sp.height)
    sp = sp.resize((max(1, round(sp.width * sc)), max(1, round(sp.height * sc))), Image.LANCZOS)
    px = img.load()
    for y in range(room[1], room[3]):
        for x in range(room[0], room[2]):
            px[x, y] = (0, 0, 0, 0)
    img.alpha_composite(sp, (room[0] + (rw - sp.width) // 2, room[1] + (rh - sp.height) // 2))


def apply(preview_only=False):
    R = [r for r in json.load(open('steam_text.json', encoding='utf-8')) if r['ok']]
    by = collections.defaultdict(list)
    for r in R:
        by[(r['root'], r['narc'])].append(r)
    total = 0; os.makedirs('steam_text_preview', exist_ok=True)
    for (root, rel), items in sorted(by.items()):
        outp = os.path.join(OVERLAY[root], rel)
        src = outp if os.path.exists(outp) else os.path.join(root, rel)
        arc = narc.read(src); ms = list(arc['members']); orig_arc = narc.read(os.path.join(root, rel))
        for sel in sorted({r['tex'] for r in items}):
            mi, e, img, fmt, hdr = get_texture(arc, sel); img = img.copy()
            _, _, orig, _, _ = get_texture(orig_arc, sel); before = img.copy()
            for r in items:
                if r['tex'] == sel:
                    composite(img, orig, r); total += 1
            if not preview_only:
                if sel.startswith('COMP:'):
                    ms[mi] = tex.comp_encode(img, fmt, hdr, ms[mi])
                else:
                    m = bytearray(ms[mi]); base = bytes(m[e['off']:e['off'] + e['size']])
                    m[e['off']:e['off'] + e['size']] = tex.encode(img, fmt, base); ms[mi] = bytes(m)
            W = min(512, img.width); sc = W / img.width; H = int(img.height * sc)
            sheet = Image.new('RGBA', (W * 3 + 16, H + 16), (40, 40, 60, 255)); d = ImageDraw.Draw(sheet)
            for c, (lab, im) in enumerate((('3DS jp', orig), ('current overlay', before), ('official EN', img))):
                x = c * (W + 8); d.text((x + 2, 0), lab, fill=(255, 220, 0, 255)); t = im.resize((W, H)); sheet.paste(t, (x, 16), t)
            sheet.save(os.path.join('steam_text_preview', '%s__%s.png' % (rel.replace('/', '__')[:-5], sel.replace(':', ''))))
        if not preview_only:
            os.makedirs(os.path.dirname(outp), exist_ok=True); open(outp, 'wb').write(narc.build(arc, ms))
        print('%-55s %d labels' % (rel, len(items)), flush=True)
    print('total', total, 'labels', 'previewed' if preview_only else 'applied')


if __name__ == '__main__':
    {'match': match, 'apply': apply, 'preview': lambda: apply(True)}[sys.argv[1]]()
