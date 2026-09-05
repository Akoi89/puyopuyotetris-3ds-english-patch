"""Second label pass: the Japanese texture labels the first pass never covered
(in-game HUD, pause menus, results, system dialogs, the Internet hub...),
including Sega's COMP-compressed members and ETC1A4 textures.

    python labels2.py detect      -> labels2.json + labels2_review_NN.png (one crop per group, numbered)
    python labels2.py apply       -> redraws from labels2_en.json into patch/romfs (base) / patch_dlc2 (dlc)

labels2_en.json is keyed by GROUP id ("12", or "12+13" to merge two boxes of one
texture into one line box). "" = erase only. "\\n" = second line.
Same detection and drawing rules as labels.py; the codec is tex.py.
"""
import glob, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import narc, labels, tex

FONT, FONT_REG = labels.FONT, labels.FONT_REG

# (root, archive, selector) - selector = CTPK texture name, or 'COMP:<member index>'
SOURCES = [
    ('tr_envoice', 'menu/nettop.narc', 'nettop01_d4444'),
    ('tr_envoice', 'menu/nettop.narc', 'nettop04_d4444'),
    ('tr_envoice', 'arcade_select/minnade_machiuke/minnade_machiuke.narc', 'minnade07_d4444'),
    ('tr_envoice', 'arcade_select/minnade/minnade.narc', 'minnade02_s_d4444'),
    ('tr_envoice', 'arcade_select/minnade/minnade.narc', 'minnade03_d4444'),
    ('tr_envoice', 'mydata/kansyou/kansyou.narc', 'kansyou_07_d4444'),
    ('tr_envoice', 'mydata/kansyou/kansyou.narc', 'puyotetoBS02_d4444'),
    ('tr_envoice', 'replay_quick_report/replay_quick_report.narc', 'replay01_bc3'),
    ('tr_envoice', 'replay_quick_report/replay_quick_report.narc', 'replay02_bc3'),
    ('tr_envoice', 'replay_quick_report/replay_quick_report.narc', 'replay03_bc3'),
    ('tr_envoice', 'replay_quick_report/replay_quick_report.narc', 'replay04_bc3'),
    ('tr_envoice', 'replay_quick_report/replay_quick_report.narc', 'replay05_bc3'),
    ('tr_envoice', 'replay_quick_report/replay_quick_report.narc', 'replay06_bc3'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:2'),
    ('tr_envoice', 'toko/toko.narc', 'newrecord_etc1a4'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:5'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:7'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:8'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:10'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:12'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:14'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:16'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:18'),
    ('tr_envoice', 'toko/toko.narc', 'COMP:20'),
    ('tr_envoice', 'tenp/adventure/ingame_common/ingame_common.narc', 'gamesetting02_d565'),
    ('tr_envoice', 'tenp/adventure/ingame_common/ingame_common.narc', 'gamesetting03_d4444'),
    ('tr_envoice', 'title/Advertisedemo.narc', 'demo_ps3_02_d4444'),
    ('tr_envoice', 'tenp/party/party2p/party2p.narc', 'timeup_d4444'),
    ('tr_envoice', 'tenp/party/party2p/party2p.narc', 'COMP:21'),
    ('tr_envoice', 'adventure/unlock/surfboard/adv_unlock.narc', 'unlock_01b_d4444'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:0'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:1'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:2'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:12'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:13'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:14'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:15'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:16'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:25'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:38'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:46'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:49'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:65'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:80'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:81'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:82'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:83'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:84'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:85'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:86'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:88'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:90'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:91'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:92'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:93'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:94'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:95'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:101'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:102'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:104'),
    ('tr_envoice', 'puyo/puyo2P/puyo2P.narc', 'COMP:105'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:3'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:4'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:5'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:6'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:7'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:8'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:9'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:10'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:11'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:12'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:13'),
    ('tr_envoice', 'tenp/Puyo/bottom_bg/bottom_bg.narc', 'COMP:14'),
    ('tr_envoice', 'puyo/result/result_04/result_04.narc', 'result_04a_3DS_etc1a4'),
    ('tr_envoice', 'puyo/result/result_04/result_04.narc', 'result_04b_3DS_d4444'),
    ('tr_envoice', 'puyo/result/result_05/result_05.narc', 'result_05b_3DS_d4444'),
    ('tr_envoice', 'system/system.narc', 'COMP:4'),
    ('tr_envoice', 'system/system.narc', 'COMP:5'),
    ('tr_envoice', 'system/system.narc', 'COMP:6'),
    ('tr_envoice', 'system/system.narc', 'COMP:10'),
    ('tr_envoice', 'system/system.narc', 'COMP:11'),
    ('tr_envoice', 'tenp/replay/replay.narc', 'COMP:0'),
    # strict-alpha pass (glowing plates merge under the normal threshold); appended so ids above stay stable
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:12', 'strict'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:13', 'strict'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:14', 'strict'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:15', 'strict'),
    ('tr_envoice', 'puyo/menu/puyo_menu.narc', 'COMP:16', 'strict'),
    ('tr_envoice', 'system/system.narc', 'COMP:5', 'strict'),
    # Endless-mode record card (found in-engine 2026-09-04)
    ('tr_envoice', 'toko/toko.narc', 'pla_tournament_d4444'),
    ('tr_envoice', 'toko/toko.narc', 'num_tournament_d4444'),
]


def get_texture(arc, sel):
    """-> (member index, ctpk entry or None, image, fmt, comp header or None)"""
    for mi, b in enumerate(arc['members']):
        if sel.startswith('COMP:'):
            if mi == int(sel[5:]) and b[:4] == b'COMP':
                img, fmt, hdr = tex.comp_decode(b)
                return mi, None, img, fmt, hdr
        elif b[:4] == b'CTPK':
            for e in labels.ctpk_entries(b):
                if e['name'] == sel:
                    return mi, e, tex.decode(b[e['off']:e['off'] + e['size']], e['w'], e['h'], e['fmt']), e['fmt'], None
    raise SystemExit('texture %s not found' % sel)


def detect():
    out, groups, crops = [], {}, []
    for src in SOURCES:
        root, rel, sel = src[:3]; strict = len(src) > 3
        arc = narc.read(os.path.join(root, rel))
        mi, e, img, fmt, hdr = get_texture(arc, sel)
        maxh = 128 if img.height <= 128 or 'bottom_bg' in rel or 'toko' in rel or 'party' in rel else 64
        probe = img
        if strict:                                   # keep only near-opaque ink for the box search
            a = np.array(img); a[a[:, :, 3] < 200] = 0; probe = Image.fromarray(a, 'RGBA')
        bx = labels.boxes(probe, maxh=maxh)
        for b in bx:
            crop = img.crop(b)
            key = (crop.size, crop.tobytes())
            g = groups.setdefault(key, len(groups))
            if g == len(crops):
                crops.append((crop, root, rel, sel))
            out.append(dict(id=len(out), root=root, narc=rel, member=mi, tex=sel, fmt=fmt, box=list(b), group=g))
        print('%-60s %-22s %3d boxes' % (rel, sel, len(bx)))
    # keep the manual boxes (ids >= 1000) added by labels2_manual.py
    try:
        out += [l for l in json.load(open('labels2.json', encoding='utf-8')) if l['id'] >= 1000]
    except Exception:
        pass
    json.dump(out, open('labels2.json', 'w', encoding='utf-8'), indent=0)
    # review sheets: one crop per group, numbered, 3x, 40 per sheet
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
    per = 40
    for s in range(0, len(crops), per):
        chunk = crops[s:s + per]
        rows = []
        for gi, (crop, root, rel, sel) in enumerate(chunk, start=s):
            c = crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST)
            bg = Image.new('RGBA', (c.width + 8, c.height + 8), (60, 60, 70, 255)); bg.alpha_composite(c, (4, 4))
            rows.append((gi, bg, rel.split('/')[-1][:-5] + ' ' + sel))
        W = max(r[1].width for r in rows) + 330; H = sum(r[1].height + 6 for r in rows) + 10
        sheet = Image.new('RGB', (W, H), (20, 20, 20)); d = ImageDraw.Draw(sheet); y = 5
        for gi, im, tag in rows:
            d.text((4, y + 2), '%d' % gi, font=font, fill=(255, 220, 120)); d.text((40, y + 2), tag, font=font, fill=(150, 150, 150))
            sheet.paste(im, (320, y)); y += im.height + 6
        sheet.save('labels2_review_%02d.png' % (s // per))
    print('labels: %d  groups: %d  review sheets: %d' % (len(out), len(crops), (len(crops) + per - 1) // per))


def draw_label(img, d, box, txt):
    x0, y0, x1, y1 = box
    crop = np.array(img.crop((x0, y0, x1, y1))).astype(int)
    opaque = crop[:, :, 3] > 128
    if not opaque.any():
        return
    cols = crop[opaque][:, :3]; lum = cols.sum(axis=1)
    fill = tuple(int(v) for v in cols[lum.argmax()]); line = tuple(int(v) for v in cols[lum.argmin()])

    def near(c, ref, t=70):
        return (abs(c[:, :, 0] - ref[0]) + abs(c[:, :, 1] - ref[1]) + abs(c[:, :, 2] - ref[2])) < t
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
                if textpx[yy, xx]:
                    rp[xx, yy] = pcol
    else:
        for yy in range(y1 - y0):
            for xx in range(x1 - x0):
                if opaque[yy, xx] or crop[yy, xx, 3] > 0:
                    rp[xx, yy] = (0, 0, 0, 0)
    img.paste(region, (x0, y0))
    if not txt.strip():
        return
    lines = txt.split(chr(10)); nl = len(lines)
    hh = (y1 - y0) // nl; size = max(7, hh - (2 if outline else 1))
    while size > 6:
        fpath = FONT if (outline or size >= 12) else FONT_REG
        font = ImageFont.truetype(fpath, size)
        if max(d.textlength(t, font=font) for t in lines) + (2 if outline else 0) <= (x1 - x0):
            break
        size -= 1
    for li, t in enumerate(lines):
        tw = d.textlength(t, font=font)
        if outline:
            d.text((x0 + max(0, ((x1 - x0) - tw) / 2), y0 - 1 + li * hh), t, font=font, fill=fill, stroke_width=1, stroke_fill=line)
        else:
            d.text((x0 + max(0, ((x1 - x0) - tw) / 2), y0 + li * hh), t, font=font, fill=fill)


def apply():
    L = json.load(open('labels2.json', encoding='utf-8'))
    en = json.load(open('labels2_en.json', encoding='utf-8'))
    bygroup = {}
    for l in L:
        bygroup.setdefault(l['group'], []).append(l)
    jobs = []
    for key, txt in en.items():
        gids = [int(k) for k in key.split('+')]
        members = [bygroup.get(g, []) for g in gids]
        if not all(members):
            print('  no labels for key', key); continue
        if len(gids) == 1:
            for l in members[0]:
                jobs.append((l['root'], l['narc'], l['member'], l['tex'], tuple(l['box']), txt))
        else:
            for a in members[0]:
                for b in members[1]:
                    if (a['root'], a['narc'], a['member'], a['tex']) == (b['root'], b['narc'], b['member'], b['tex']):
                        box = (min(a['box'][0], b['box'][0]), min(a['box'][1], b['box'][1]), max(a['box'][2], b['box'][2]), max(a['box'][3], b['box'][3]))
                        jobs.append((a['root'], a['narc'], a['member'], a['tex'], box, txt))
    by = {}
    for j in jobs:
        by.setdefault((j[0], j[1]), []).append(j)
    total = 0
    for (root, rel), items in by.items():
        arc = narc.read(os.path.join(root, rel)); ms = list(arc['members'])
        for sel in sorted({j[3] for j in items}):
            mi, e, img, fmt, hdr = get_texture(arc, sel)
            d = ImageDraw.Draw(img)
            for j in items:
                if j[3] != sel:
                    continue
                draw_label(img, d, j[4], j[5]); total += 1
            if sel.startswith('COMP:'):
                ms[mi] = tex.comp_encode(img, fmt, hdr, ms[mi])
            else:
                m = bytearray(ms[mi])
                base = bytes(m[e['off']:e['off'] + e['size']])
                m[e['off']:e['off'] + e['size']] = tex.encode(img, fmt, base)
                ms[mi] = bytes(m)
        out = os.path.join({'tr_envoice': 'patch/romfs', 'dlc_r': 'patch_dlc2'}[root], rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'wb').write(narc.build(arc, ms))
        print('wrote %s  (%d labels)' % (out, len(items)))
    print('labels redrawn:', total)


if __name__ == '__main__':
    detect() if sys.argv[1] == 'detect' else apply()
