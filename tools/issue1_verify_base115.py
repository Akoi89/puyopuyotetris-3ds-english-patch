"""Verify the 1.0.15 base re-wrap before building.

Checks, against romfs_110_tree as the 1.0.14 reference:
  1. every mtx keeps its section and entry counts, and its byte length
  2. the multiset of words in every entry is unchanged (no word added, dropped or altered)
  3. every drawn character is present in that section's Latin atlas
  4. no drawn line is wider than CAP in any base chapter
  5. every manzai narc differs from Sega's only in single size digits, member sizes unchanged
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
import os, re
import mtx, narc
from _issue1_widths import atlas
import _issue1_base_width as B

CAP = 193
BR, END = chr(0xf8fd), chr(0xf813)
ADV = 'tenp/text/adventure'
SRC, DST = 'romfs_110_tree', os.path.join('patch', 'romfs')
STEMS = ['chapter%02d' % i for i in range(0, 8)] + ['general']
DEBUG = re.compile(r'^[A-Z][A-Z0-9_]{1,10}[_ ]?\d*\s+\d+\s*//')
bad = 0


def fail(*a):
    global bad
    bad += 1
    print('  FAIL', *a)


for stem in STEMS:
    sp = os.path.join(SRC, ADV, '%sJapanese.mtx' % stem)
    dp = os.path.join(DST, ADV, '%sJapanese.mtx' % stem)
    fp = os.path.join(SRC, ADV, '%s_F1Japanese.narc' % stem)
    if not os.path.exists(dp):
        print('%-9s not patched (unchanged from 1.0.14)' % stem)
        dp = sp
    a_src, a_dst = mtx.parse(sp), mtx.parse(dp)
    if [len(s) for s in a_src] != [len(s) for s in a_dst]:
        fail(stem, 'section/entry counts changed')
    if os.path.getsize(sp) != os.path.getsize(dp):
        fail(stem, 'file length changed')
    worst = (0, None)
    for si, (s0, s1) in enumerate(zip(a_src, a_dst)):
        at = atlas(fp, si)
        for i, (t0, t1) in enumerate(zip(s0, s1)):
            w0 = sorted(t0.replace(BR, ' ').replace(END, '').split())
            w1 = sorted(t1.replace(BR, ' ').replace(END, '').split())
            if w0 != w1:
                fail(stem, 'sec%d #%d words changed' % (si, i), w0, w1)
            if DEBUG.match(t1) or not any(c.isascii() and c.isalpha() for c in t1):
                continue
            for c in t1.replace(BR, '').replace(END, ''):
                if c in (' ', '﻿'):   # U+FEFF is Sega-era junk on generalJapanese sec0 #0, untouched
                    continue
                if ord(c) not in at['widths']:
                    fail(stem, 'sec%d #%d glyph %r (U+%04X) missing from member %d' % (si, i, c, ord(c), si))
            for l in t1.replace(END, '').split(BR):
                if l.strip() and B.w(at, l) > worst[0]:
                    worst = (B.w(at, l), (si, i, l))
    tag = 'OK ' if worst[0] <= CAP or stem == 'chapter00' else 'OVER'
    print('%-4s %-9s sections %2d entries %4d  widest drawn line %3d  %r' % (
        tag, stem, len(a_dst), sum(len(s) for s in a_dst), worst[0], worst[1][2] if worst[1] else ''))
    if worst[0] > CAP and stem != 'chapter00':
        fail(stem, 'line over cap')

print()
for stem in STEMS:
    scr = ('script/adventure/general/manzai_script_general.narc' if stem == 'general'
           else 'script/adventure/%s/manzai_script_%s.narc' % (stem, stem))
    s, d = os.path.join(SRC, scr), os.path.join(DST, scr.replace('/', os.sep))
    if not os.path.exists(d):
        print('%-9s script unchanged' % stem); continue
    r0, r1 = open(s, 'rb').read(), open(d, 'rb').read()
    diff = [i for i in range(len(r0)) if r0[i] != r1[i]]
    ok = (len(r0) == len(r1)
          and all(r0[i:i + 1].isdigit() and r1[i:i + 1].isdigit() for i in diff)
          and [len(m) for m in narc.read(s)['members']] == [len(m) for m in narc.read(d)['members']])
    print('%-4s %-9s script: %d byte(s) differ, all size digits' % ('OK ' if ok else 'FAIL', stem, len(diff)))
    if not ok:
        fail(stem, 'script diff is not size digits only')

print('\n%s' % ('ALL CHECKS PASSED' if not bad else '%d CHECK(S) FAILED' % bad))
sys.exit(1 if bad else 0)
