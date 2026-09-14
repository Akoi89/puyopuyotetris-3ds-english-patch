"""Issue #1 (TheGershon, 2026-09-14): measure bubble line widths through each chapter's own atlas.

    python issue1_widths.py            -> prints per-file max widths, base + DLC, JP + EN

Width = sum over glyphs of (bearing + advance) from the FONTDATF record (bearing is SIGNED).
"""
import sys, os, glob, struct, collections
import mtx, narc
from check_glyphs import companions


def atlas(path, member=0):
    ms = narc.read(path)['members']
    fifs = [(ms[i], ms[i + 1]) for i in range(0, len(ms) - 1, 2) if ms[i][:8] == b'FONTDATF']
    f, b = fifs[member]
    n = struct.unpack_from('<I', f, 0x10)[0]
    cols, rows, gh = (struct.unpack_from('<H', f, o)[0] for o in (0x22, 0x24, 0x26))
    w, h = struct.unpack_from('<HH', b, 6)
    widths = {}
    for r in range(n):
        o = 56 + r * 16
        bearing, wid = struct.unpack_from('<iI', f, o)
        cp = struct.unpack_from('<H', f, o + 12)[0]
        widths[cp] = (bearing, wid)
    return dict(widths=widths, cw=w // cols, gh=gh, n=n)


def pw(a, ln):
    pen = 0
    for c in ln:
        cp = ord(c)
        if cp not in a['widths']:
            pen += a['cw']; continue
        b, w = a['widths'][cp]
        pen += (b + w) if w else a['cw']
    return pen


def lines(p):
    out = []
    for si, s in enumerate(mtx.parse(p)):
        for i, t in enumerate(s):
            for ln in t.replace(chr(0xf813), '').split(chr(0xf8fd)):
                if ln.strip():
                    out.append((si, i, ln))
    return out


def report(tag, mtxp, narcp, top=2):
    a = atlas(narcp, 0)
    L = lines(mtxp)
    ws = sorted(((pw(a, ln), si, i, ln) for si, i, ln in L), reverse=True)
    print('%-42s gh=%d lines=%4d max=%3d  >200:%3d  >195:%3d  >190:%3d' % (
        tag, a['gh'], len(L), ws[0][0], sum(1 for w in ws if w[0] > 200),
        sum(1 for w in ws if w[0] > 195), sum(1 for w in ws if w[0] > 190)))
    for w in ws[:top]:
        print('      ', w)
    return ws


if __name__ == '__main__':
    allw = []
    print('=== base chapters (romfs_110_tree = shipped English; jp_orig = Sega)')
    for f in sorted(glob.glob('romfs_110_tree/tenp/text/adventure/chapter??Japanese.mtx')):
        rel = os.path.relpath(f, 'romfs_110_tree').replace(os.sep, '/')
        cs = companions(rel, 'romfs_110_tree')
        ws = report('EN ' + os.path.basename(f), f, os.path.join('romfs_110_tree', cs[0]))
        allw += [w[0] for w in ws]
        jp = os.path.join('jp_orig', rel)
        if os.path.exists(jp):
            report('JP ' + os.path.basename(f), jp, os.path.join('jp_orig', cs[0]), 1)
    h = collections.Counter((w // 5) * 5 for w in allw)
    print('base EN width histogram (5px bins):', sorted(h.items())[-12:])
    print('=== DLC chapters (dlc_r = Sega JP; patch_dlc2 = shipped English)')
    for cid, ch in [('0010', '08'), ('0011', '09'), ('0012', '10')]:
        rel = '%s/data/chapter%sJapanese.mtx' % (cid, ch)
        cs = companions(rel, 'dlc_r')
        jp_n = os.path.join('dlc_r', cs[0]); en_n = os.path.join('patch_dlc2', cs[0])
        if not os.path.exists(en_n):
            en_n = jp_n
        report('JP ch' + ch, os.path.join('dlc_r', rel), jp_n, 1)
        report('EN ch' + ch, os.path.join('patch_dlc2', rel), en_n, 3)
