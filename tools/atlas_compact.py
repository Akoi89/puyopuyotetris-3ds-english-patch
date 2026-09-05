"""Shrink swapped font atlases back to the size Sega shipped.

atlas_fix2 replaces an incomplete FONTDATF member with a whole donor atlas,
so a 32 KB (512x128, ~130 glyph) member becomes a 131 KB (512x512, 820 glyph)
one. 60 of 101 members in the base overlay more than doubled, and the game
hung at the one screen that loads three such members at once (the Versus
win/lose dialogue). This subsets every swapped member to the glyphs its
section actually uses, laid out in the donor's cell geometry on the smallest
power-of-two-high bitmap that fits.

    python atlas_compact.py selftest        subset an untouched atlas to its own
                                            full set: must be byte-identical
    python atlas_compact.py base|dlc        rewrite the overlay in place

FONTDATF (56-byte header): +0x10 u32 count, +0x14 u32 capacity, +0x1A/+0x1E u16
bitmap width, +0x1C/+0x20 u16 bitmap height, +0x22 u16 cols, +0x24 u16 rows,
+0x26 u16 glyph height; 16-byte records sorted by codepoint, +0x0C u16
codepoint, +0x0E u16 glyph index (== record order). Bitmap member: +0 u32 data
size, +6 u16 w, +8 u16 h, 16-byte header, 4bpp low-nibble-first, 8x8 Morton
tiles. Glyph k occupies cell (k % cols, k // cols) of (w // cols) x (h // rows).
"""
import os, re, struct, sys, collections
import mtx, narc
from check_glyphs import companions

CTRL = re.compile('[' + chr(0xE000) + '-' + chr(0xF8FF) + ']')
MORTON = []
for i in range(64):
    MORTON.append(((i & 1) | ((i >> 1) & 2) | ((i >> 2) & 4), ((i >> 1) & 1) | ((i >> 2) & 2) | ((i >> 3) & 4)))

JOBS = {
    'base': dict(out='patch/romfs', text_root='patch/romfs/tenp/text', src_text='tr_jpvoice', orig_roots=('tr_jpvoice', 'jp_orig')),
    'dlc': dict(out='patch_dlc2', text_root='patch_dlc2', src_text='dlc_r', orig_roots=('dlc_r',)),
}


def cps(strings):
    return {ord(c) for t in strings for c in CTRL.sub('', t) if c.strip() and ord(c) >= 0x20}


def decode(b):
    size = struct.unpack_from('<I', b, 0)[0]; w, h = struct.unpack_from('<HH', b, 6)
    data = b[16:16 + size]; out = bytearray(w * h); i = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for k in range(64):
                dx, dy = MORTON[k]; v = data[i >> 1]
                out[(ty + dy) * w + tx + dx] = (v & 0xF) if i % 2 == 0 else (v >> 4); i += 1
    return w, h, out


def encode(w, h, px, header):
    data = bytearray((w * h) // 2); i = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for k in range(64):
                dx, dy = MORTON[k]; v = px[(ty + dy) * w + tx + dx] & 0xF
                if i % 2 == 0: data[i >> 1] |= v
                else: data[i >> 1] |= v << 4
                i += 1
    hdr = bytearray(header[:16]); struct.pack_into('<I', hdr, 0, len(data)); struct.pack_into('<HH', hdr, 6, w, h)
    return bytes(hdr) + bytes(data)


def records(f):
    n = struct.unpack_from('<I', f, 0x10)[0]
    return [f[56 + r * 16:56 + r * 16 + 16] for r in range(n)]


def subset(f, b, keep, target_h=None):
    """Return (fontdatf, bitmap) holding only codepoints in `keep`, in donor geometry."""
    n, cap = struct.unpack_from('<II', f, 0x10)
    cols, rows = struct.unpack_from('<HH', f, 0x22)
    w, h, px = decode(b)
    cw, ch = w // cols, h // rows
    donor_cap = cols * rows                       # cells that exist in the bitmap; a donor can declare more glyphs than cells
    recs = [r for r in records(f) if struct.unpack_from('<H', r, 12)[0] in keep and struct.unpack_from('<H', r, 14)[0] < donor_cap]
    dropped = [hex(struct.unpack_from('<H', r, 12)[0]) for r in records(f) if struct.unpack_from('<H', r, 12)[0] in keep and struct.unpack_from('<H', r, 14)[0] >= donor_cap]
    if dropped:
        print('    note: %d wanted glyphs have no cell in the donor (indices beyond %d): %s' % (len(dropped), donor_cap, dropped[:5]))
    cnt = len(recs)
    need_rows = max(1, -(-cnt // cols))
    nh = 8
    while nh < need_rows * ch:
        nh *= 2
    if target_h:
        nh = max(nh, target_h)
    nrows = max(1, nh // ch)
    ncap = cols * nrows
    assert cnt <= ncap, (cnt, ncap)
    npx = bytearray(w * nh)
    out_recs = []
    for k, r in enumerate(recs):
        src = struct.unpack_from('<H', r, 14)[0]
        sx, sy = (src % cols) * cw, (src // cols) * ch
        dx, dy = (k % cols) * cw, (k // cols) * ch
        for yy in range(ch):
            npx[(dy + yy) * w + dx:(dy + yy) * w + dx + cw] = px[(sy + yy) * w + sx:(sy + yy) * w + sx + cw]
        rr = bytearray(r); struct.pack_into('<H', rr, 14, k); out_recs.append(bytes(rr))
    nf = bytearray(f[:56])
    struct.pack_into('<II', nf, 0x10, cnt, ncap)
    struct.pack_into('<H', nf, 0x18, 1)              # single page, as every original member
    for o in (0x1A, 0x1E): struct.pack_into('<H', nf, o, w)
    for o in (0x1C, 0x20): struct.pack_into('<H', nf, o, nh)
    struct.pack_into('<HH', nf, 0x22, cols, nrows)
    return bytes(nf) + b''.join(out_recs), encode(w, nh, npx, b)


def selftest():
    ms = narc.read('jp_orig/tenp/text/win_dialogue/vs_winJapanese.narc')['members']
    ok = True
    for i in range(0, len(ms) - 1, 2):
        f, b = ms[i], ms[i + 1]
        keep = {struct.unpack_from('<H', r, 12)[0] for r in records(f)}
        nf, nb = subset(f, b, keep, target_h=struct.unpack_from('<H', b, 8)[0])
        same = (nf == f, nb == b)
        print('member %d: fontdatf identical %s, bitmap identical %s' % (i // 2, *same)); ok &= all(same)
    print('SELFTEST', 'PASS' if ok else 'FAIL')
    return ok


def run(job):
    J = JOBS[job]
    # which .mtx files draw through which .narc, and what each section needs (union over parent + variants)
    need = collections.defaultdict(lambda: collections.defaultdict(set))
    for dp, dn, fn in os.walk(J['text_root']):
        for fl in fn:
            if not fl.endswith('.mtx'): continue
            p = os.path.join(dp, fl)
            rel = os.path.relpath(p, J['out']) if job == 'base' else os.path.relpath(p, J['out'])
            S = mtx.parse(p)
            for c in companions(rel.replace(os.sep, '/'), J['src_text']):
                for si, sec in enumerate(S):
                    need[c.replace('/', os.sep)][si] |= cps(sec)
    total_before = total_after = 0; done = 0
    for c, secs in sorted(need.items()):
        out = os.path.join(J['out'], c)
        if not os.path.exists(out): continue                 # never swapped, nothing to shrink
        orig = None
        for r in J['orig_roots']:
            if os.path.exists(os.path.join(r, c)): orig = narc.read(os.path.join(r, c)); break
        arc = narc.read(out); ms = list(arc['members']); changed = False
        pairs = [i for i in range(0, len(ms) - 1, 2) if ms[i][:8] == b'FONTDATF']
        for si, i in enumerate(pairs):
            f, b = ms[i], ms[i + 1]
            if orig and i + 1 < len(orig['members']) and orig['members'][i] == f and orig['members'][i + 1] == b:
                continue                                        # Sega's own member, untouched
            have = {struct.unpack_from('<H', r, 12)[0] for r in records(f)}
            keep = (secs.get(si, set()) | {c_ for c_ in range(0x20, 0x7F)}) & have
            miss = secs.get(si, set()) - have
            if miss:
                print('  WARNING %s member %d lacks %s' % (c, si, [hex(x) for x in sorted(miss)][:5]))
            oh = struct.unpack_from('<H', orig['members'][i + 1], 8)[0] if orig and i + 1 < len(orig['members']) and orig['members'][i][:8] == b'FONTDATF' else None
            nf, nb = subset(f, b, keep, target_h=oh)
            total_before += len(b); total_after += len(nb)
            ms[i], ms[i + 1] = nf, nb; changed = True; done += 1
        if changed:
            open(out, 'wb').write(narc.build(arc, ms))
    print('%s: %d swapped members compacted, bitmaps %d -> %d bytes' % (job, done, total_before, total_after))


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        sys.exit(0 if selftest() else 1)
    run(sys.argv[1])
