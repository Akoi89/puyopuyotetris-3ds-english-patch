# -*- coding: utf-8 -*-
"""Derive the 1.0.15 readme set from the 1.0.14 one: version strings, the hash tables read back from
the built files, the patch-size figure measured rather than repeated, and a new history paragraph.

    python _issue1_docs115.py     -> readmes_1015/, readmes_jpv_115/
"""
import io, os, sys, hashlib, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
W = os.path.join(R, 'work')
os.chdir(W)


def fsha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


EN_CIA = os.path.join(R, r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.15.cia')
JP_CIA = os.path.join(R, r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.15.cia')
EN_XD = os.path.join(W, r'rhdn_xdelta_v7\PuyoPuyoTetris-EN-voices-1.0.15.xdelta')
JP_XD = os.path.join(W, r'rhdn_xdelta_jpv_115\PuyoPuyoTetris-JP-voices-1.0.15.xdelta')
EN = (os.path.getsize(EN_CIA), fsha(EN_CIA))
JP = (os.path.getsize(JP_CIA), fsha(JP_CIA))
EN_MB = round(os.path.getsize(EN_XD) / 1e6)
print('EN cia %d %s   xdelta %d bytes (~%d MB)' % (EN + (os.path.getsize(EN_XD), EN_MB)))
print('JP cia %d %s   xdelta %d bytes' % (JP + (os.path.getsize(JP_XD),)))

HIST_RHDN = """1.0.15 (2026-09-17): the base game's Adventure dialogue is re-broken so every
line fits the 3DS speech bubble. That text comes from the earlier fan
translation and its line breaks were set for a wider box, so 162 lines in 160
bubbles across Chapters 1 to 7 and the shared script ran past the bubble
border. The words are unchanged, only the breaks moved, and 28 bubbles were
raised to hold the extra line that results. Found from console photos in
issue #1, and every line is now at or under the widest width those photos
prove draws cleanly. The DLC patch is unchanged from 0.2.8.

"""

HIST_XD = """Build history: 1.0.15 (2026-09-17) re-breaks the base game's Adventure
dialogue so every line fits the 3DS speech bubble (162 lines in 160 bubbles
across Chapters 1 to 7 and the shared script, words unchanged), and raises 28
bubbles to hold the extra line that results; nothing else changed from 1.0.14.
1.0.14 (2026-09-14) raises two speech bubbles in the base game"""

HIST_JPV = """1.0.15 (2026-09-17) carries the main release's base-game line-break fix: the
Adventure dialogue is re-broken so every line fits the 3DS speech bubble (162
lines in 160 bubbles across Chapters 1 to 7 and the shared script, words
unchanged), with 28 bubbles raised to hold the extra line that results. Text
tables and script bytes only, so every voice file is untouched. The DLC is
unchanged from 0.2.8.

"""


def bump(s, old_cia, new_cia):
    s = s.replace('1.0.14', '1.0.15')
    s = s.replace('%s` | %s | `%s`' % ('', '', ''), '')     # no-op, keeps the intent visible
    s = s.replace('{:,}'.format(old_cia[0]), '{:,}'.format(new_cia[0]))
    s = s.replace(old_cia[1], new_cia[1])
    s = s.replace(str(old_cia[0]), str(new_cia[0]))
    return s


OLD_EN = (513737792, '23fbaaba952ff9c423b7e01703a6853442b89c1efe60592f81ab5db039481b39')
OLD_JP = (490878016, 'a25d9003bec2ad630f372fc35e6cc9d844caeabb3e6297f8aa382fae4af89be9')

# ---- English edition ----
src, dst = 'readmes_1014', 'readmes_1015'
shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)

s = open(os.path.join(src, 'README_rhdn.md'), encoding='utf-8').read()
s = bump(s, OLD_EN, EN)
s = s.replace('about 173 MB', 'about %d MB' % EN_MB)
assert '## Patch set history\n\n' in s
s = s.replace('## Patch set history\n\n', '## Patch set history\n\n' + HIST_RHDN, 1)
old_test = ("1.0.12 / 0.2.7 (eight re-encoded textures) were checked in Azahar,\n"
            "not yet on the console; 1.0.13 / 0.2.8 (line breaks and the Time Up graphic) were checked in Azahar;\n"
            "for 1.0.15 the two bubbles have not been looked at in the engine. Actual play on hardware is still short; a match or a chapter played\n"
            "through on a console is worth reporting.")
new_test = ("1.0.12 / 0.2.7 (eight re-encoded textures) were checked in Azahar,\n"
            "not yet on the console. 1.0.13 / 0.2.8 (the EX chapter line breaks and the\n"
            "Time Up graphic) were confirmed on a New 3DS XL on 14 and 16 September 2026.\n"
            "Of the two bubbles 1.0.14 raised, the Chapter 1 one was photographed drawing\n"
            "correctly on 17 September; the shared end-of-chapter one has not been seen\n"
            "running. 1.0.15 has not been seen running anywhere yet: it is line breaks in\n"
            "eight text tables and 28 single script bytes, each verified byte for byte on\n"
            "the way in and out of the CIAs, but nobody has watched it draw. A chapter\n"
            "played through on a console is worth reporting.")
assert old_test in s, 'testing paragraph not found'
s = s.replace(old_test, new_test)
open(os.path.join(dst, 'README_rhdn.md'), 'w', encoding='utf-8', newline='\n').write(s)

s = open(os.path.join(src, 'README_base_xdelta.txt'), encoding='utf-8').read()
s = bump(s, OLD_EN, EN)
s = s.replace('about 173 MB', 'about %d MB' % EN_MB)
assert 'Build history: 1.0.15 (2026-09-14) raises two speech bubbles in the base game' in s
s = s.replace('Build history: 1.0.15 (2026-09-14) raises two speech bubbles in the base game', HIST_XD)
open(os.path.join(dst, 'README_base_xdelta.txt'), 'w', encoding='utf-8', newline='\n').write(s)

s = bump(open(os.path.join(src, 'README_layeredfs.txt'), encoding='utf-8').read(), OLD_EN, EN)
open(os.path.join(dst, 'README_layeredfs.txt'), 'w', encoding='utf-8', newline='\n').write(s)

# ---- Japanese-voice edition ----
src, dst = 'readmes_jpv_114', 'readmes_jpv_115'
shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)

s = open(os.path.join(src, 'README_rhdn.md'), encoding='utf-8').read()
s = bump(s, OLD_JP, JP)
old = '1.0.15 (2026-09-14) raises two speech bubbles in the base game that were'
assert old in s
s = s.replace(old, HIST_JPV + old.replace('1.0.15', '1.0.14'))
NL = chr(10)
s = s.replace('1.0.13 and 1.0.15 changed only text' + NL + 'tables, one texture and two script bytes,',
              '1.0.13, 1.0.14 and 1.0.15 changed only' + NL + 'text tables, one texture and 30 single script bytes,')
open(os.path.join(dst, 'README_rhdn.md'), 'w', encoding='utf-8', newline='\n').write(s)

s = bump(open(os.path.join(src, 'README_layeredfs.txt'), encoding='utf-8').read(), OLD_JP, JP)
open(os.path.join(dst, 'README_layeredfs.txt'), 'w', encoding='utf-8', newline='\n').write(s)

# ---- the blanket bump also renamed 1.0.14's own history paragraphs; put them back ----
for d, f in (('readmes_1015', 'README_rhdn.md'), ('readmes_jpv_115', 'README_rhdn.md')):
    q = os.path.join(d, f)
    t = open(q, encoding='utf-8').read()
    t = t.replace('1.0.15 (2026-09-14)', '1.0.14 (2026-09-14)')
    open(q, 'w', encoding='utf-8', newline=chr(10)).write(t)

# ---- checks ----
bad = []
for d in ('readmes_1015', 'readmes_jpv_115'):
    for f in sorted(os.listdir(d)):
        t = open(os.path.join(d, f), encoding='utf-8').read()
        for ch in ('\u2014', '\u2013'):
            if ch in t:
                bad.append('%s/%s contains U+%04X' % (d, f, ord(ch)))
        if '1.0.14' in t and 'README_rhdn' not in f:
            bad.append('%s/%s still names 1.0.14' % (d, f))
        print('%-28s %6d bytes' % ('%s/%s' % (d, f), len(t)))
print('PROBLEMS:', bad if bad else 'none')
