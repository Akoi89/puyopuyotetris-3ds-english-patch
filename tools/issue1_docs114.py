# -*- coding: utf-8 -*-
"""1.0.14 doc changes (the second half of the issue #1 work: two base-game bubbles). Run from anywhere.

    python issue1_docs114.py texts     public README / RELEASE_NOTES / TESTING, and the zip readme texts
                                        -> work/readmes_1014/ and work/readmes_jpv_114/
    python issue1_docs114.py install   Final/_CURRENT/INSTALL.txt (run after the zips are built)

The DLC is unchanged at 0.2.8, so only the base version moves. Every anchor must exist exactly once
before anything is written, and every hash is read from the built file.
"""
import io, os, sys, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(r'G:\Claude\PuyoPuyo')
NL = chr(10)

STATUS = ('The two bubbles were not looked at in the engine; the edit is one byte in each of two' + NL +
          'scene scripts, and both CIAs were compared against 1.0.13 file by file.')
STATUS_SHORT = 'the two bubbles have not been looked at in the engine'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


def sz(p):
    return '{:,}'.format(os.path.getsize(p))


EN_CIA = r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.14.cia'
JP_CIA = r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.14.cia'
OLD_EN = '505b9c4033c0a3d0c6b61153d59e25a2abbc8506be1f52675fe12a53a083cb88'   # 1.0.13 base
OLD_JP = '78e75703f5749badfbdba48093ef86379b67a9c8afa355f1dc63f24b209b0522'   # 1.0.13 JP base
assert sha(r'Final\_CURRENT\PuyoPuyoTetris-EN-voices-1.0.13.cia') == OLD_EN
assert sha(r'Final\_CURRENT\PuyoPuyoTetris-JP-voices-1.0.13.cia') == OLD_JP
EN_SHA, JP_SHA = sha(EN_CIA), sha(JP_CIA)

RN = """## Current build: 1.0.14 / DLC 0.2.8

The rest of the bubble work from [issue #1](../../issues/1), in the base game
this time. The DLC is unchanged; if you are already on DLC 0.2.8 you only need
the base files.

A speech bubble's height is not worked out from the text. Each scene script
sets it per line, and Sega's values were chosen for the Japanese. Where an
English line needs more lines than the Japanese did, the extra line falls
outside the bubble, which is what the DLC report showed. Every base scene
script was checked against that rule and two bubbles needed a taller box: one
in Chapter 1 and one in the shared end-of-chapter script. Two bytes in total,
and the two archives are otherwise byte for byte Sega's own.

Four more base bubbles hold English that runs to more lines than the bubble
implies, but Sega's own Japanese runs to the same number or more in those same
bubbles, so they draw the way the original game draws them and were left alone.

""" + STATUS + """ The title screen reads **ENG 1.0.14**
and the DLC stays **TMD 0.2.8**.

"""


def rep(path, pairs):
    s = io.open(path, encoding='utf-8', newline='').read()
    for a, b in pairs:
        n = s.count(a)
        assert n == 1, '%s: anchor found %d times: %r' % (path, n, a[:80])
        s = s.replace(a, b)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('edited', path)


def sub(txt, pairs):
    LF, CRLF = chr(10), chr(13) + chr(10)
    crlf = CRLF in txt
    for a, b in pairs:
        if crlf:
            a, b = a.replace(CRLF, LF).replace(LF, CRLF), b.replace(CRLF, LF).replace(LF, CRLF)
        n = txt.count(a)
        assert n == 1, 'anchor found %d times: %r' % (n, a[:80])
        txt = txt.replace(a, b)
    return txt


def scan(paths):
    for p in paths:
        t = io.open(p, encoding='utf-8').read()
        print('%-48s dashes: %d  ellipsis: %d  "1.0.13" left: %d' % (
            p, t.count('\u2014') + t.count('\u2013'), t.count('\u2026'), t.count('1.0.13')))


mode = sys.argv[1]
if mode == 'texts':
    rep('public_repo/README.md', [
        ('(build 1.0.13, DLC\n0.2.8)', '(build 1.0.14, DLC\n0.2.8)'),
        ('`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip`', '`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip`'),
        ('1.0.13** in both editions.', '1.0.14** in both editions.'),
    ])
    rep('public_repo/RELEASE_NOTES.md', [
        ('the current one is **1.0.13** with DLC 0.2.8 (see below).', 'the current one is **1.0.14** with DLC 0.2.8 (see below).'),
        ('1.0.13 fixes the EX chapter line breaks and the Party-mode Time Up graphic).',
         '1.0.13 fixes the EX chapter line breaks and the Party-mode Time Up graphic; 1.0.14 raises two base-game speech bubbles).'),
        ('Title screen reads **ENG 1.0.13**; the built CIA reports 1.0.13.', 'Title screen reads **ENG 1.0.14**; the built CIA reports 1.0.14.'),
        ('`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip` (base and DLC as xdelta3 patches for your own decrypted dumps, xdelta3.exe and a readme inside)',
         '`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip` (base and DLC as xdelta3 patches for your own decrypted dumps, xdelta3.exe and a readme inside)'),
        ('Same title ID and the same ENG 1.0.13 stamp', 'Same title ID and the same ENG 1.0.14 stamp'),
        ('1.0.13 (below) is the current build.', '1.0.14 (below) is the current build.'),
        ('## Current build: 1.0.13 / DLC 0.2.8\n', RN + '## 1.0.13 / DLC 0.2.8\n'),
        ('`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip` (the base patch is', '`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip` (the base patch is'),
        ('Same title ID and the same **ENG 1.0.13** stamp as the English-voice build,', 'Same title ID and the same **ENG 1.0.14** stamp as the English-voice build,'),
    ])
    rep('public_repo/TESTING.md', [
        ('For the Japanese-voice edition use `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip`',
         'For the Japanese-voice edition use `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip`'),
        ("reads **ENG 1.0.13** at its right end.", "reads **ENG 1.0.14** at its right end."),
        ('as version **1.0.13** (a locally built CIA)', 'as version **1.0.14** (a locally built CIA)'),
        ('different font and were not changed; a clipped bubble there is worth a\nscreenshot.',
         'different font and were not re-wrapped, but every base scene script was\nchecked for the second half of the same problem, a bubble scripted for fewer\nlines than the English needs. Two were found and are raised in **1.0.14**\n(14 September 2026): one in Chapter 1, one in the shared end-of-chapter\nscript. ' + STATUS_SHORT.capitalize() + ', so a screenshot of either is still\nworth having.'),
    ])

    os.makedirs('work/readmes_1014', exist_ok=True); os.makedirs('work/readmes_jpv_114', exist_ok=True)
    R13, RJ13 = 'work/readmes_1013/', 'work/readmes_jpv_113/'

    t = io.open(R13 + 'README_base_xdelta.txt', encoding='utf-8', newline='').read()
    t = sub(t, [
        ('(build 1.0.13)', '(build 1.0.14)'),
        ('PuyoPuyoTetris-EN-voices-1.0.13.xdelta PuyoPuyoTetris-EN-voices-1.0.13.cia', 'PuyoPuyoTetris-EN-voices-1.0.14.xdelta PuyoPuyoTetris-EN-voices-1.0.14.cia'),
        (OLD_EN, EN_SHA), ('"ENG 1.0.13"', '"ENG 1.0.14"'),
        ('Build history: 1.0.13 (2026-09-14)',
         'Build history: 1.0.14 (2026-09-14) raises two speech bubbles in the base game\r\nthat were scripted for fewer lines than the English text needs (one in Chapter 1,\r\none in the shared end-of-chapter script), one byte each; nothing else changed\r\nfrom 1.0.13. 1.0.13 (2026-09-14)')])
    io.open('work/readmes_1014/README_base_xdelta.txt', 'w', encoding='utf-8', newline='').write(t)

    t = io.open(R13 + 'README_layeredfs.txt', encoding='utf-8', newline='').read()
    io.open('work/readmes_1014/README_layeredfs.txt', 'w', encoding='utf-8', newline='').write(sub(t, [('v1.0.13', 'v1.0.14')]))

    t = io.open(R13 + 'README_rhdn.md', encoding='utf-8', newline='').read()
    t = sub(t, [
        ('build 1.0.13 / DLC 0.2.8', 'build 1.0.14 / DLC 0.2.8'),
        ('`PuyoPuyoTetris-EN-voices-1.0.13.xdelta` | the complete', '`PuyoPuyoTetris-EN-voices-1.0.14.xdelta` | the complete'),
        ('PuyoPuyoTetris-EN-voices-1.0.13.xdelta PuyoPuyoTetris-EN-voices-1.0.13.cia', 'PuyoPuyoTetris-EN-voices-1.0.14.xdelta PuyoPuyoTetris-EN-voices-1.0.14.cia'),
        ('| `PuyoPuyoTetris-EN-voices-1.0.13.cia` | 513,737,792 | `' + OLD_EN + '` |',
         '| `PuyoPuyoTetris-EN-voices-1.0.14.cia` | ' + sz(EN_CIA) + ' | `' + EN_SHA + '` |'),
        ('reads **ENG 1.0.13** at its right end', 'reads **ENG 1.0.14** at its right end'),
        ('The console lists the base game as version 1.0.13 and the DLC as 0.2.8.', 'The console lists the base game as version 1.0.14 and the DLC as 0.2.8.'),
        ('## Patch set history\n\n',
         '## Patch set history\n\n1.0.14 (2026-09-14): two speech bubbles in the base game were scripted for\nfewer lines than the English text needs, so a line fell outside the bubble.\nOne is in Chapter 1, one in the shared end-of-chapter script. The DLC patch is\nunchanged from 0.2.8.\n\n'),
        ('1.0.13 / 0.2.8 (line breaks and the Time Up graphic) not yet booted anywhere.',
         '1.0.13 / 0.2.8 (line breaks and the Time Up graphic) were checked in Azahar;\nfor 1.0.14 ' + STATUS_SHORT + '.')])
    io.open('work/readmes_1014/README_rhdn.md', 'w', encoding='utf-8', newline='').write(t)

    t = io.open(RJ13 + 'README_rhdn.md', encoding='utf-8', newline='').read()
    t = sub(t, [
        ('build 1.0.13 / DLC 0.2.8', 'build 1.0.14 / DLC 0.2.8'),
        ('The same English patch as the main 1.0.13 release', 'The same English patch as the main 1.0.14 release'),
        ('reads ENG 1.0.13 on\nboth.', 'reads ENG 1.0.14 on\nboth.'),
        ('`PuyoPuyoTetris-JP-voices-1.0.13.xdelta` | the English base game', '`PuyoPuyoTetris-JP-voices-1.0.14.xdelta` | the English base game'),
        ('PuyoPuyoTetris-JP-voices-1.0.13.xdelta PuyoPuyoTetris-JP-voices-1.0.13.cia', 'PuyoPuyoTetris-JP-voices-1.0.14.xdelta PuyoPuyoTetris-JP-voices-1.0.14.cia'),
        ('| `PuyoPuyoTetris-JP-voices-1.0.13.cia` | 490,878,016 | `' + OLD_JP + '` |',
         '| `PuyoPuyoTetris-JP-voices-1.0.14.cia` | ' + sz(JP_CIA) + ' | `' + JP_SHA + '` |'),
        ('reads **ENG 1.0.13** at its right end,', 'reads **ENG 1.0.14** at its right end,'),
        ('version 1.0.13 and the DLC as 0.2.8. The quickest', 'version 1.0.14 and the DLC as 0.2.8. The quickest'),
        ('The English-voice 1.0.13 build was taken apart', 'The English-voice 1.0.14 build was taken apart'),
        ('Report anything here, with which screen (a photo beats a description):',
         '1.0.14 (2026-09-14) raises two speech bubbles in the base game that were\nscripted for fewer lines than the English text needs. The DLC is unchanged from\n0.2.8.\n\nReport anything here, with which screen (a photo beats a description):')])
    io.open('work/readmes_jpv_114/README_rhdn.md', 'w', encoding='utf-8', newline='').write(t)

    t = io.open(RJ13 + 'README_layeredfs.txt', encoding='utf-8', newline='').read()
    io.open('work/readmes_jpv_114/README_layeredfs.txt', 'w', encoding='utf-8', newline='').write(sub(t, [('v1.0.13)', 'v1.0.14)')]))

    scan(['public_repo/README.md', 'public_repo/RELEASE_NOTES.md', 'public_repo/TESTING.md',
          'work/readmes_1014/README_base_xdelta.txt', 'work/readmes_1014/README_layeredfs.txt',
          'work/readmes_1014/README_rhdn.md', 'work/readmes_jpv_114/README_rhdn.md', 'work/readmes_jpv_114/README_layeredfs.txt'])

elif mode == 'install':
    B_EN = r'Final\_new\PuyoPuyoTetris-xdelta-patches-1.0.14.zip'
    B_JP = r'Final\_new\PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip'
    assert os.path.exists(B_EN) and os.path.exists(B_JP)
    rep('Final/_CURRENT/INSTALL.txt', [
        ('as of build 1.0.13 / DLC 0.2.8 (2026-09-14, folder', 'as of build 1.0.14 / DLC 0.2.8 (2026-09-14, folder'),
        ('  2. PuyoPuyoTetris-EN-voices-1.0.13.cia', '  2. PuyoPuyoTetris-EN-voices-1.0.14.cia'),
        ('ENG 1.0.13 stamp; the HOME menu jingle tells them apart):', 'ENG 1.0.14 stamp; the HOME menu jingle tells them apart):'),
        ('  PuyoPuyoTetris-JP-voices-1.0.13.cia      (sha256 ' + OLD_JP + ')', '  PuyoPuyoTetris-JP-voices-1.0.14.cia      (sha256 ' + JP_SHA + ')'),
        ('PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip (sha256 ' + sha(r'Final\_CURRENT\PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip') + ')',
         'PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip (sha256 ' + sha(B_JP) + ')'),
        ('  - PuyoPuyoTetris-xdelta-patches-1.0.13.zip', '  - PuyoPuyoTetris-xdelta-patches-1.0.14.zip'),
        ('Checking a file: the 1.0.13 base CIA has sha256\n  ' + OLD_EN, 'Checking a file: the 1.0.14 base CIA has sha256\n  ' + EN_SHA),
        ('releases/tag/builds-1.0.13', 'releases/tag/builds-1.0.14'),
        ('breaks and the Party-mode Time Up graphic from the first issue #1 report;\nnot yet booted anywhere.',
         'breaks and the Party-mode Time Up graphic from the first issue #1 report,\nchecked in Azahar. 1.0.14 raises two base-game speech bubbles scripted for\nfewer lines than the English needs; ' + STATUS_SHORT + '.'),
    ])
    scan(['Final/_CURRENT/INSTALL.txt'])
print('done')
