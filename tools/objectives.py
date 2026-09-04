"""Generate English for the 3DS-only Adventure objective strings.

The _F1 difficulty variants carry the same objective sentences as the base
files but with DIFFERENT numbers, so they cannot be looked up in Steam's text.
They are rigidly formulaic, so they are generated here from the 3DS's own
numbers, in the phrasing the fan patch already ships for the base files.
Stage names in section 0 are taken positionally from the parent file's
translation (same stage, same slot).

Writes gen.json: {japanese: english}. inject.py loads it as a tier.
"""
import os, re, json, unicodedata, mtx

BR = chr(0xf8fd)
END = chr(0xf813)
CTRL = re.compile('[' + chr(0xe000) + '-' + chr(0xf8ff) + ']')

T = json.load(open('tiers.json', encoding='utf-8'))
W = lambda s: unicodedata.normalize('NFKC', s)


def wrap(s, limit=30):
    """One line break at a space so neither half exceeds the limit."""
    if len(s) <= limit:
        return s
    cut = s.rfind(' ', 0, limit + 1)
    return s[:cut] + BR + s[cut + 1:] if cut > 0 else s


# --- character names, learned from the official pairs --------------------------
names = {}
pat = re.compile(r'^(テトリス|ぷよぷよ)で\s*(.+?)\((テトリス|ぷよぷよ)\)に\s*しょうり[!！]$')
for jp, en in list(T['steam'].items()) + list(T['fan'].items()):
    m = pat.match(W(CTRL.sub('', jp)).replace(' ', '').replace('　', ''))
    if not m:
        continue
    e = re.match(r'^Beat (.+?)!', CTRL.sub(' ', en))
    if e:
        names.setdefault(m.group(2), e.group(1))
short = re.compile(r'^(.+?)にしょうり[!！]$')
for jp, en in list(T['steam'].items()) + list(T['fan'].items()):
    m = short.match(W(CTRL.sub('', jp)).replace(' ', '').replace(chr(0x3000), ''))
    e = re.match(r'^Beat (.+?)!', CTRL.sub(' ', en)) if m else None
    if m and e:
        names.setdefault(m.group(1), e.group(1))
SIDE = {'テトリス': 'Tetris', 'ぷよぷよ': 'Puyo Puyo'}


def side(a, b):
    if a == b == 'ぷよぷよ':
        return 'Puyo vs Puyo'
    return '%s vs %s' % (SIDE[a], SIDE[b])


def tm(t):
    n = int(re.match(r'(\d+)', t).group(1))
    m = re.search(r'(\d+)分', t)
    s = re.search(r'(\d+)秒', t)
    if m and s and int(s.group(1)):
        return '%d min %d sec' % (int(m.group(1)), int(s.group(1)))
    if m:
        return '%d min' % int(m.group(1))
    return '%d sec' % int(s.group(1))


def gen(jp):
    x = W(CTRL.sub('', jp)).replace('　', '').replace(' ', '')
    m = pat.match(x)
    if m:
        nm = names.get(m.group(2))
        return ('Beat %s!' % nm) + BR + '(%s)' % side(m.group(1), m.group(3)) if nm else None
    m = re.match(r'^(.+?)にしょうり[!！]$', x)
    if m and m.group(1) in names:
        return 'Beat %s!' % names[m.group(1)]
    m = re.match(r'^(\d+分\d*秒?|\d+秒)いないに(\d+)LINES消せばクリア[!！]$', x)
    if m:
        return wrap('Clear %d lines within %s!' % (int(m.group(2)), tm(m.group(1))))
    m = re.match(r'^(\d+分\d*秒?|\d+秒)いないに(\d+)点いじょうでクリア[!！]$', x)
    if m:
        return wrap('Score %s pts within %s!' % (format(int(m.group(2)), ','), tm(m.group(1))))
    m = re.match(r'^(\d+)LINES消すまでに(\d+)点いじょうでクリア[!！]$', x)
    if m:
        return wrap('Score %s pts before clearing %d lines!' % (format(int(m.group(2)), ','), int(m.group(1))))
    m = re.match(r'^レベル(\d+)までに(\d+)点いじょうでクリア[!！]$', x)
    if m:
        return wrap('Score %s pts before level %d!' % (format(int(m.group(2)), ','), int(m.group(1))))
    m = re.match(r'^(\d+分\d*秒?|\d+秒)いないにレベル(\d+)いじょうでクリア[!！]$', x)
    if m:
        return wrap('Reach level %d within %s!' % (int(m.group(2)), tm(m.group(1))))
    return None


out = {}
miss = []
for dp, dn, fn in os.walk('tr_jpvoice/tenp/text'):
    for f in sorted(fn):
        if not re.match(r'.+_F\d+Japanese\.mtx$', f):
            continue
        rel = os.path.join(dp, f)
        parent = re.sub(r'_F\d+Japanese\.mtx$', 'Japanese.mtx', rel)
        S = mtx.parse(rel)
        P = mtx.parse(parent) if os.path.exists(parent) else None
        for si, sec in enumerate(S):
            for i, x in enumerate(sec):
                if not re.search('[぀-ヿ㐀-鿿]', x):
                    continue
                e = gen(x)
                if e is None and si == 0 and P and si < len(P) and i < len(P[si]) \
                        and not re.search('[぀-ヿ㐀-鿿]', P[si][i]) and P[si][i].strip():
                    e = P[si][i]                        # stage name, same slot in parent
                if e is not None:
                    out[x] = e + (END if x.rstrip().endswith(END) else '')
                else:
                    miss.append((f, si, i, x))
json.dump(out, open('gen.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('names learned: %d   generated: %d   unmatched: %d' % (len(names), len(out), len(miss)))
for f, si, i, x in miss[:10]:
    print('   %-28s [%d:%d] %r' % (f, si, i, CTRL.sub(' ', x)[:50]))
for jp, en in list(out.items())[:8]:
    print('   %-44r -> %r' % (CTRL.sub(' ', jp)[:42], en.replace(BR, ' / ').replace(END, '')))
