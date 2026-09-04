"""Translate the DLC contents: text via the TM, then font atlases, then safety.

    python dlc_patch.py

Reads dlc_r/<content>/data/*.mtx (untranslated Japanese, identical to Steam's
Japanese DLC text), writes patch_dlc/<content>/data/ with:
  - every .mtx that gained English
  - every companion .narc whose FONTDATF atlases had to be swapped for a donor
Strings no atlas can draw are reverted, exactly as safe_patch.py does for the base.
"""
import os, re, json, struct, collections, unicodedata, shutil
import mtx, narc
from check_glyphs import narc_members, companions, charset

SRC, OUT = 'dlc_r', 'patch_dlc'
JP = re.compile('[' + chr(0x3040) + '-' + chr(0x30ff) + chr(0x3400) + '-' + chr(0x9fff) + chr(0xff66) + '-' + chr(0xff9d) + ']')
CTRL = re.compile('[' + chr(0xe000) + '-' + chr(0xf8ff) + ']')
END = chr(0xf813)
PH = re.compile(r'^\s*(no_text|NO_TEXT|dummy|DUMMY|nodata)')


def norm(s):
    s = unicodedata.normalize('NFKC', s).replace(chr(0x3000), ' ')
    s = CTRL.sub('', s)
    return re.sub(r'\s+', ' ', s).strip()


def nospace(s):
    return re.sub(r'\s+', '', norm(s))


T = json.load(open('tiers.json', encoding='utf-8'))
T['human'] = json.load(open('human.json', encoding='utf-8')) if os.path.exists('human.json') else {}
TIERS = [('human', lambda s: s), ('steam', lambda s: s), ('steam_n', norm), ('steam_s', nospace),
         ('fan', lambda s: s), ('fan_n', norm), ('fan_s', nospace)]


def translate(x):
    for name, fn in TIERS:
        k = fn(x)
        if k in T[name] and not PH.match(T[name][k]):
            en = T[name][k].rstrip(END)
            if x.rstrip().endswith(END):
                en += END
            return en, name
    return None, None


def cps_of(strings):
    return {ord(c) for t in strings for c in CTRL.sub('', t) if c.strip()}


# --- font donor pool ------------------------------------------------------------
def fmembers(p):
    ms = narc_members(p)
    out = []
    for i in range(0, len(ms) - 1, 2):
        f, b = ms[i], ms[i + 1]
        if f[:8] != b'FONTDATF':
            continue
        n = struct.unpack_from('<I', f, 0x10)[0]
        cols, rows, gh = (struct.unpack_from('<H', f, o)[0] for o in (0x22, 0x24, 0x26))
        w, h = struct.unpack_from('<HH', b, 6)
        cps = {struct.unpack_from('<H', f, 56 + r * 16 + 12)[0] for r in range(n)}
        out.append(dict(i=i, n=n, gh=gh, cw=w // cols, ch=h // rows, cps=cps, fif=f, bmp=b, path=p))
    return out


pool = []
for root in ('tr_jpvoice/tenp/text', 'jp_orig/tenp/text', SRC):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.endswith('.narc'):
                try:
                    pool.extend(fmembers(os.path.join(dp, f)))
                except Exception:
                    pass
print('font donor pool: %d members' % len(pool))

# --- pass 1: translate ------------------------------------------------------------
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
stats = collections.Counter()
work = {}           # rel -> (orig_secs, new_secs)
for dp, dn, fn in os.walk(SRC):
    for f in sorted(fn):
        if not f.endswith('.mtx'):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, SRC)
        raw = open(p, 'rb').read()
        W = mtx.width(raw)
        secs = mtx._read(raw, W)
        new = []
        n = 0
        for sec in secs:
            row = []
            for x in sec:
                if x.strip() and JP.search(x):
                    en, tier = translate(x)
                    if en is not None:
                        row.append(en); stats[tier] += 1; n += 1
                        continue
                    stats['untranslated'] += 1
                row.append(x)
            new.append(row)
        if n:
            work[rel] = (secs, new, W)
print('translated: %d   untranslated: %d   files: %d' % (
    sum(v for k, v in stats.items() if k != 'untranslated'), stats['untranslated'], len(work)))

# --- pass 2: atlases --------------------------------------------------------------
swapped = 0
rebuilt = {}      # narc rel -> new bytes
for rel, (orig, new, W) in work.items():
    need = cps_of(t for sec in new for t in sec)
    orig_need = cps_of(t for sec in orig for t in sec)
    cands = [m for m in pool if not (need - m['cps'])]
    for c in companions(rel, SRC):
        arc = narc.read(os.path.join(SRC, c))
        ms = list(arc['members'])
        changed = False
        for m in fmembers(os.path.join(SRC, c)):
            if not (need - m['cps']):
                continue
            if orig_need and len(orig_need & m['cps']) < len(orig_need) / 2:
                continue                                  # special-purpose font
            if not cands:
                continue
            d = min(cands, key=lambda q: (abs(q['gh'] - m['gh']),
                                          abs(q['cw'] - m['cw']) + abs(q['ch'] - m['ch']), -q['n']))
            ms[m['i']], ms[m['i'] + 1] = d['fif'], d['bmp']
            changed = True; swapped += 1
        if changed:
            rebuilt[c] = narc.build(arc, ms)
print('atlas members swapped: %d   narcs rebuilt: %d' % (swapped, len(rebuilt)))

# --- pass 3: safety + write ---------------------------------------------------------
def atlas_sets(rel):
    out = []
    for c in companions(rel, SRC):
        if c in rebuilt:
            tmp = os.path.join(OUT, '_tmp.narc')
            os.makedirs(OUT, exist_ok=True)
            open(tmp, 'wb').write(rebuilt[c]); out.append(charset(tmp)); os.remove(tmp)
        else:
            out.append(charset(os.path.join(SRC, c)))
    return out


kept = reverted = 0
per = collections.Counter()
for rel, (orig, new, W) in work.items():
    sets = atlas_sets(rel)
    final = []
    for so, sn in zip(orig, new):
        row = []
        for x, y in zip(so, sn):
            if x == y:
                row.append(y); continue
            need = {c for c in CTRL.sub('', y) if c.strip()}
            if any(all(ord(c) in s for c in need) for s in sets):
                row.append(y); kept += 1
            else:
                row.append(x); reverted += 1; per[rel] += 1
        final.append(row)
    dst = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(mtx.build(final, W))
for c, data in rebuilt.items():
    dst = os.path.join(OUT, c)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(data)
print('strings kept: %d   reverted: %d' % (kept, reverted))
for rel, n in per.most_common():
    print('   %-40s %d reverted' % (rel, n))
print('contents touched:', sorted({rel.split(os.sep)[0] for rel in list(work) + list(rebuilt)}))
