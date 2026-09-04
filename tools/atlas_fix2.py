"""Per-section font atlas fixing and safety, for the base game and the DLC.

    python atlas_fix2.py base     patch_full/romfs -> patch/romfs     (narcs from tr_jpvoice / jp_orig)
    python atlas_fix2.py dlc      patch_dlc/...    -> patch_dlc2/...  (narcs from dlc_r)

Established on the untouched ROM: a companion .narc holds ONE FONTDATF member per
.mtx section, and member i is the only one that can draw section i (it covers its
own section with 0 missing; the best other member misses 5..537 codepoints).
So every check and every swap here is (section i, member i), never a union.

A companion is *viable* only if it has one member per section and each member
covered its section's ORIGINAL text - a companion that could not even draw the
Japanese was never the live one and is left untouched.
"""
import os, re, sys, struct, collections
import mtx, narc
from check_glyphs import narc_members, companions

CTRL = re.compile('[' + chr(0xe000) + '-' + chr(0xf8ff) + ']')

JOBS = {
    'base': dict(cand='patch_full/romfs', orig='tr_jpvoice', narc_roots=('tr_jpvoice', 'jp_orig'),
                 jp='jp_orig', out='patch/romfs'),
    'dlc':  dict(cand='patch_dlc', orig='dlc_r', narc_roots=('dlc_r',), jp='dlc_r', out='patch_dlc2'),
    # jp = Sega's untouched tree: viability (which companion is live) is decided there,
    # where member i covering section i is proven exact; the swap is then applied to the
    # current narc of that name from narc_roots.
}
job = JOBS[sys.argv[1]]


def cps(strings):
    return {ord(c) for t in strings for c in CTRL.sub('', t) if c.strip() and ord(c) >= 0x20}   # skip ASCII effect codes


def fmembers(blobs):
    out = []
    for i in range(0, len(blobs) - 1, 2):
        f, b = blobs[i], blobs[i + 1]
        if f[:8] != b'FONTDATF':
            continue
        n = struct.unpack_from('<I', f, 0x10)[0]
        cols, rows, gh = (struct.unpack_from('<H', f, o)[0] for o in (0x22, 0x24, 0x26))
        w, h = struct.unpack_from('<HH', b, 6)
        out.append(dict(i=i, n=n, gh=gh, cw=w // cols, ch=h // rows,
                        cps={struct.unpack_from('<H', f, 56 + r * 16 + 12)[0] for r in range(n)},
                        fif=f, bmp=b))
    return out


def find(rel, roots):
    for r in roots:
        p = os.path.join(r, rel)
        if os.path.exists(p):
            return p
    return None


# donor pool: every atlas member in the game and the DLC
pool = []
for root in ('tr_jpvoice/tenp/text', 'jp_orig/tenp/text', 'dlc_r'):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.endswith('.narc'):
                try:
                    pool.extend(fmembers(narc_members(os.path.join(dp, f))))
                except Exception:
                    pass
print('donor pool: %d members' % len(pool))

kept = reverted = swapped = 0
per = collections.Counter()
rebuilt = {}
for dp, dn, fn in os.walk(job['cand']):
    for f in sorted(fn):
        if not f.endswith('.mtx'):
            continue
        rel = os.path.relpath(os.path.join(dp, f), job['cand'])
        cand = mtx.parse(os.path.join(dp, f))
        orig = mtx.parse(os.path.join(job['orig'], rel))
        W = mtx.width(open(os.path.join(job['orig'], rel), 'rb').read())
        if not any(x != y for a, b in zip(orig, cand) for x, y in zip(a, b)):
            continue
        need = [cps(sec) for sec in cand]
        jpref = mtx.parse(os.path.join(job['jp'], rel))
        jpneed = [cps(sec) for sec in jpref]

        # viable companions, with their (possibly already rebuilt) members
        viable = []
        for c in companions(rel, job['orig']):
            src = find(c, job['narc_roots'])
            if not src:
                continue
            jpsrc = os.path.join(job['jp'], c)
            if not os.path.exists(jpsrc):
                continue
            J = fmembers(narc_members(jpsrc))
            if len(J) != len(jpref) or any(jpneed[i] and len(jpneed[i] - J[i]['cps']) > 8 for i in range(len(J))):   # Sega's own atlases miss a few glyphs in a handful of files
                continue                                    # Sega's own copy never drew this text
            arc = narc.read(src)
            ms = list(rebuilt[c]['members']) if c in rebuilt else list(arc['members'])
            M = fmembers(ms)
            if len(M) != len(cand):
                continue
            viable.append((c, arc, ms, M))

        # swap member i wherever section i now needs glyphs it lacks
        for c, arc, ms, M in viable:
            changed = False
            for i, m in enumerate(M):
                miss = need[i] - m['cps']
                if not miss:
                    continue
                cands = [d for d in pool if not (need[i] - d['cps'])]
                if not cands:
                    continue
                d = min(cands, key=lambda q: (abs(q['gh'] - m['gh']),
                                              abs(q['cw'] - m['cw']) + abs(q['ch'] - m['ch']), -q['n']))
                ms[m['i']], ms[m['i'] + 1] = d['fif'], d['bmp']
                M[i] = dict(m, cps=d['cps'])
                changed = True; swapped += 1
            if changed:
                rebuilt[c] = dict(arc=arc, members=ms)

        # safety: a string in section i ships only if some viable member i draws it
        final = []
        for i, (so, sc) in enumerate(zip(orig, cand)):
            row = []
            covers = [M[i]['cps'] for c, arc, ms, M in viable]
            for x, y in zip(so, sc):
                if x == y:
                    row.append(y); continue
                nd = cps([y])
                if any(not (nd - s) for s in covers):
                    row.append(y); kept += 1
                else:
                    row.append(x); reverted += 1; per[rel] += 1
            final.append(row)
        dst = os.path.join(job['out'], rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'wb').write(mtx.build(final, W))

for c, r in rebuilt.items():
    dst = os.path.join(job['out'], c)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(narc.build(r['arc'], r['members']))

print('strings kept: %d   reverted: %d   members swapped: %d   narcs rebuilt: %d'
      % (kept, reverted, swapped, len(rebuilt)))
for rel, n in per.most_common(12):
    print('   %-46s %d reverted' % (rel, n))
