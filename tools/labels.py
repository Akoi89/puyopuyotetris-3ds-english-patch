"""Find text labels on UI texture atlases, crop them for review, and redraw them.

    python labels.py detect            -> labels.json (boxes) + label_review_NN.png (crops, 3x)
    python labels.py apply             -> reads labels_en.json {id: english}, redraws, writes narcs
                                          into patch/romfs (base) / patch_dlc2 (DLC)

Textures are CTPK RGBA4 / RGBA8, Morton 8x8 tiles in naive order (no flips).
A label box is a connected blob of alpha>0 after a small horizontal dilation,
so the characters of one word/line merge. Text colour and outline are sampled
from the original box so the redrawn label matches its neighbours.
"""
import os, sys, json, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from check_glyphs import narc_members
import narc

MORTON = [((i & 1) | ((i >> 1) & 2) | ((i >> 2) & 4), ((i >> 1) & 1) | ((i >> 2) & 2) | ((i >> 3) & 4)) for i in range(64)]
SOURCES = [('tr_envoice', 'patch/romfs', ['internet', 'adventure/complete', 'adventure/adv_popup']),
           ('dlc_r', 'patch_dlc2', [])]
FONT = 'C:/Windows/Fonts/arialbd.ttf'
FONT_REG = 'C:/Windows/Fonts/arial.ttf'


def dec(data, w, h, fmt):
    img = Image.new('RGBA', (w, h)); px = img.load(); k = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for m in range(64):
                x, y = tx + MORTON[m][0], ty + MORTON[m][1]
                if fmt == 4:
                    v = struct.unpack_from('<H', data, k * 2)[0]
                    px[x, y] = ((v >> 12) * 17, ((v >> 8) & 0xF) * 17, ((v >> 4) & 0xF) * 17, (v & 0xF) * 17)
                elif fmt == 0:
                    a, b, g, r = data[k * 4:k * 4 + 4]; px[x, y] = (r, g, b, a)
                elif fmt == 1:
                    b, g, r = data[k * 3:k * 3 + 3]; px[x, y] = (r, g, b, 255)
                k += 1
    return img


def enc(img, fmt):
    w, h = img.size; px = img.load(); out = bytearray()
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for m in range(64):
                r, g, b, a = px[tx + MORTON[m][0], ty + MORTON[m][1]]
                if fmt == 4:
                    out += struct.pack('<H', ((r >> 4) << 12) | ((g >> 4) << 8) | ((b >> 4) << 4) | (a >> 4))
                elif fmt == 0:
                    out += bytes((a, b, g, r))
                elif fmt == 1:
                    out += bytes((b, g, r))
    return bytes(out)


def ctpk_entries(blob):
    ver, count, texoff, texsize = struct.unpack_from('<HHII', blob, 4)
    out = []
    for i in range(count):
        e = 0x20 + i * 0x20
        noff, size, doff, fmt, w, h, mip = struct.unpack_from('<IIIIHHB', blob, e)
        out.append(dict(i=i, name=blob[noff:blob.index(b'\0', noff)].decode('latin1'), size=size, off=texoff + doff, fmt=fmt, w=w, h=h))
    return out


def boxes(img, dil=6, minh=7, maxh=64):
    a = np.array(img)[:, :, 3] > 32
    h, w = a.shape
    # dilate horizontally so characters of a word merge
    d = a.copy()
    for s in range(1, dil + 1):
        d[:, s:] |= a[:, :-s]; d[:, :-s] |= a[:, s:]
    d[1:, :] |= a[:-1, :]; d[:-1, :] |= a[1:, :]
    lab = np.zeros((h, w), dtype=np.int32); n = 0
    stack = []
    for y in range(h):
        for x in range(w):
            if d[y, x] and not lab[y, x]:
                n += 1; lab[y, x] = n; stack.append((y, x))
                while stack:
                    cy, cx = stack.pop()
                    for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                        if 0 <= ny < h and 0 <= nx < w and d[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; stack.append((ny, nx))
    out = []
    for k in range(1, n + 1):
        ys, xs = np.where((lab == k) & a)
        if len(ys) == 0: continue
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        if not (minh <= (y1 - y0) <= maxh and (x1 - x0) >= 6 and (x1 - x0) < 400 and len(ys) > 30):
            continue
        # split on runs of >= 7 empty columns inside the box
        sub = a[y0:y1, x0:x1].any(axis=0)
        segs = []; start = None; gap = 0
        for x in range(len(sub)):
            if sub[x]:
                if start is None: start = x
                gap = 0
            else:
                gap += 1
                if start is not None and gap >= 7:
                    segs.append((start, x - gap + 1)); start = None
        if start is not None: segs.append((start, len(sub)))
        for sx0, sx1 in segs:
            if sx1 - sx0 >= 6:
                cys = np.where(a[y0:y1, x0 + sx0:x0 + sx1].any(axis=1))[0]
                out.append((int(x0 + sx0), int(y0 + cys.min()), int(x0 + sx1), int(y0 + cys.max() + 1)))
    return sorted(out, key=lambda b: (b[1] // 12, b[0]))


def detect():
    labels = []; crops = []
    for root, outroot, dirs in SOURCES:
        for dp, dn, fn in os.walk(root):
            rel_dir = os.path.relpath(dp, root).replace(os.sep, '/')
            if dirs and not any(rel_dir == d or rel_dir.startswith(d + '/') for d in dirs): continue
            if root == 'dlc_r' and not rel_dir.endswith('/data'): continue
            for f in sorted(fn):
                if not f.endswith('.narc'): continue
                p = os.path.join(dp, f)
                try: ms = narc_members(p)
                except Exception: continue
                for mi, m in enumerate(ms):
                    if m[:4] != b'CTPK': continue
                    for e in ctpk_entries(m):
                        if e['fmt'] not in (0, 1, 4): continue
                        img = dec(m[e['off']:e['off'] + e['size']], e['w'], e['h'], e['fmt'])
                        for b in boxes(img):
                            lid = len(labels)
                            labels.append(dict(id=lid, root=root, narc=os.path.relpath(p, root).replace(os.sep, '/'), member=mi, tex=e['name'], fmt=e['fmt'], box=b))
                            crops.append((lid, img.crop(b)))
    import hashlib
    groups = {}
    for lid, c in crops:
        key = hashlib.md5(c.tobytes() + repr(c.size).encode()).hexdigest()
        labels[lid]['group'] = groups.setdefault(key, len(groups))
    json.dump(labels, open('labels.json', 'w', encoding='utf-8'), indent=0)
    seen = set(); uniq = []
    for lid, c in crops:
        g = labels[lid]['group']
        if g in seen: continue
        seen.add(g); uniq.append((lid, c))
    print('labels detected: %d in %d unique groups' % (len(labels), len(uniq)))
    per = 60; cols = 4; S = 3
    crops = uniq
    for page in range(0, len(crops), per):
        chunk = crops[page:page + per]
        rows = (len(chunk) + cols - 1) // cols
        cw = max(c.size[0] for _, c in chunk) * S + 12; ch = max(c.size[1] for _, c in chunk) * S + 22
        sheet = Image.new('RGB', (cols * min(cw, 420), rows * min(ch, 140)), (60, 60, 60)); d = ImageDraw.Draw(sheet)
        for k, (lid, c) in enumerate(chunk):
            big = c.resize((c.size[0] * S, c.size[1] * S), Image.NEAREST)
            bg = Image.new('RGBA', big.size, (60, 60, 60, 255)); bg.paste(big, (0, 0), big)
            x, y = (k % cols) * min(cw, 420), (k // cols) * min(ch, 140)
            bg.thumbnail((min(cw, 420) - 8, min(ch, 140) - 20))
            sheet.paste(bg.convert('RGB'), (x + 4, y + 18)); d.text((x + 4, y + 2), 'g%d %s' % (labels[lid]['group'], labels[lid]['tex'][:24]), fill=(255, 255, 0))
        sheet.save('label_review_%02d.png' % (page // per))
    print('review pages:', (len(crops) + per - 1) // per)


def apply():
    import glob
    labels = {l['id']: l for l in json.load(open('labels.json', encoding='utf-8'))}
    en = {}
    for fn in sorted(glob.glob('labels_en_p*.json')):
        en.update(json.load(open(fn, encoding='utf-8')))
    print('translations loaded:', len(en))
    bygroup = {}
    for l in labels.values():
        bygroup.setdefault(l['group'], []).append(l)
    # jobs: (root, narc, member, tex, box, text); "A+B" keys merge two boxes of the same texture
    jobs = []
    for key, txt in en.items():
        gids = [int(k) for k in key.split('+')]
        members = [bygroup.get(g, []) for g in gids]
        if not all(members):
            continue
        if len(gids) == 1:
            for l in members[0]:
                jobs.append((l['root'], l['narc'], l['member'], l['tex'], l['fmt'], tuple(l['box']), txt))
        else:
            for a in members[0]:
                for b in members[1]:
                    if (a['root'], a['narc'], a['member'], a['tex']) == (b['root'], b['narc'], b['member'], b['tex']):
                        box = (min(a['box'][0], b['box'][0]), min(a['box'][1], b['box'][1]), max(a['box'][2], b['box'][2]), max(a['box'][3], b['box'][3]))
                        jobs.append((a['root'], a['narc'], a['member'], a['tex'], a['fmt'], box, txt))
    by = {}
    for j in jobs:
        by.setdefault((j[0], j[1]), []).append(j)
    total = 0
    for (root, rel), items in by.items():
        arc = narc.read(os.path.join(root, rel)); ms = list(arc['members'])
        for mi in sorted({j[2] for j in items}):
            m = bytearray(ms[mi]); ents = {e['name']: e for e in ctpk_entries(m)}
            for name in sorted({j[3] for j in items if j[2] == mi}):
                e = ents[name]; img = dec(m[e['off']:e['off'] + e['size']], e['w'], e['h'], e['fmt'])
                d = ImageDraw.Draw(img)
                for j in items:
                    if j[2] != mi or j[3] != name: continue
                    x0, y0, x1, y1 = j[5]; txt = j[6]
                    crop = np.array(img.crop((x0, y0, x1, y1))).astype(int)
                    opaque = crop[:, :, 3] > 128
                    if not opaque.any():
                        continue
                    cols = crop[opaque][:, :3]
                    lum = cols.sum(axis=1)
                    fill = tuple(int(v) for v in cols[lum.argmax()]); line = tuple(int(v) for v in cols[lum.argmin()])
                    # text pixels: near the fill or the outline colour; the rest (if plentiful) is a plate
                    def near(c, ref, t=70): return (abs(c[:, :, 0] - ref[0]) + abs(c[:, :, 1] - ref[1]) + abs(c[:, :, 2] - ref[2])) < t
                    textpx = opaque & (near(crop, fill) | near(crop, line))
                    plate = opaque & ~textpx
                    region = img.crop((x0, y0, x1, y1)); rp = region.load()
                    border = np.concatenate([opaque[0, :], opaque[-1, :], opaque[:, 0], opaque[:, -1]])
                    has_plate = border.mean() > 0.6 and plate.sum() > 0.25 * opaque.sum()
                    outline = (sum(line) < sum(fill) - 200) and (near(crop, line) & opaque).sum() > 0.12 * textpx.sum()
                    if has_plate:
                        pc = crop[plate][:, :3]
                        vals, counts = np.unique(pc, axis=0, return_counts=True)
                        pcol = tuple(int(v) for v in vals[counts.argmax()]) + (255,)
                        for yy in range(y1 - y0):
                            for xx in range(x1 - x0):
                                if textpx[yy, xx]: rp[xx, yy] = pcol
                    else:
                        for yy in range(y1 - y0):
                            for xx in range(x1 - x0):
                                if opaque[yy, xx] or crop[yy, xx, 3] > 0: rp[xx, yy] = (0, 0, 0, 0)
                    img.paste(region, (x0, y0))
                    if not txt.strip():
                        total += 1; continue
                    lines = txt.split(chr(10)); nl = len(lines)
                    hh = (y1 - y0) // nl; size = max(7, hh - (2 if outline else 1))
                    while size > 6:
                        fpath = FONT if (outline or size >= 12) else FONT_REG
                        font = ImageFont.truetype(fpath, size)
                        if max(d.textlength(t, font=font) for t in lines) + (2 if outline else 0) <= (x1 - x0): break
                        size -= 1
                    for li, t in enumerate(lines):
                        tw = d.textlength(t, font=font)
                        if outline:
                            d.text((x0 + max(0, ((x1 - x0) - tw) / 2), y0 - 1 + li * hh), t, font=font, fill=fill, stroke_width=1, stroke_fill=line)
                        else:
                            d.text((x0 + max(0, ((x1 - x0) - tw) / 2), y0 + li * hh), t, font=font, fill=fill)
                    total += 1
                m[e['off']:e['off'] + e['size']] = enc(img, e['fmt'])
            ms[mi] = bytes(m)
        out = os.path.join({'tr_envoice': 'patch/romfs', 'dlc_r': 'patch_dlc2'}[root], rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'wb').write(narc.build(arc, ms))
        print('wrote %s  (%d labels)' % (out, len(items)))
    print('labels redrawn:', total)


if __name__ == '__main__':
    detect() if sys.argv[1] == 'detect' else apply()
