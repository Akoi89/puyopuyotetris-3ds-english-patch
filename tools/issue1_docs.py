# -*- coding: utf-8 -*-
"""1.0.13 / DLC 0.2.8 doc changes (issue #1 fixes). Run from anywhere.

    python issue1_docs.py texts     public_repo README / RELEASE_NOTES / TESTING, and the zip readme texts
                                     -> work/readmes_1013/ (4 files) and work/readmes_jpv_113/ (2 files)
    python issue1_docs.py install   Final/_CURRENT/INSTALL.txt (needs the bundle zips: run after issue1_zips.py)

Every anchor must exist exactly once (or exactly the count given) before anything is written.
Hashes are read from the built files, never typed. Set STATUS below to what was actually checked.
"""
import io, os, sys, zipfile, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(r'G:\Claude\PuyoPuyo')

# What has been checked in-engine for 1.0.13. Edit before running if the rig run happened.
STATUS = ('Not yet booted anywhere; the change is line breaks in three' + chr(10) + 'text tables and one '
          'texture, each verified byte for byte on the way in and' + chr(10) + 'out of the CIAs.')
STATUS_SHORT = 'not yet booted anywhere'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


def sz(p):
    return '{:,}'.format(os.path.getsize(p))


EN_CIA = r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.13.cia'
EN_DLC = r'Final\_new\PuyoPuyoTetris-DLC-0.2.8.cia'
JP_CIA = r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.13.cia'
JP_DLC = r'Final\_new\PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia'
for p in (EN_CIA, EN_DLC, JP_CIA, JP_DLC):
    assert os.path.exists(p), p
EN_SHA, EN_DLC_SHA, JP_SHA, JP_DLC_SHA = sha(EN_CIA), sha(EN_DLC), sha(JP_CIA), sha(JP_DLC)
OLD_SHA = '238589ac07b650c0001c3e871612582d960f28c60fd113144ca8dde4695fd905'   # 1.0.12 base CIA
OLD_DLC = 'a34fac38e7b6756a583f47f46643ba4775698a1c1a73b570e206926f09fc83b7'   # DLC 0.2.7
OLD_JP = 'fe2d1927728e258f108d889985b29fe77e3378139957f519d7f60a72a9dc1349'    # JP base 1.0.12
OLD_JP_DLC = 'd7af2e37acd97d2482ed32ab67ea996e452996951729e010b1f7fb8753eaec09'  # JP DLC 0.2.7
assert sha(r'Final\_CURRENT\PuyoPuyoTetris-EN-voices-1.0.12.cia') == OLD_SHA
assert sha(r'Final\_CURRENT\PuyoPuyoTetris-JP-voices-1.0.12.cia') == OLD_JP

RN_1013 = """## Current build: 1.0.13 / DLC 0.2.8

Two fixes from the first report in [issue #1](../../issues/1) (14 September
2026, a New 3DS XL running the Japanese-voice edition). Nothing else changed.

1. **EX chapter dialogue ran off the right edge of its speech bubble.** The
   three DLC story chapters (EX Acts 8, 9 and 10) took Sega's English lines
   from the Steam release with Steam's line breaks, and the 3DS bubble is
   narrower: about 215 pixels of text room, measured on the reporter's
   screenshots. 276 of the 734 English bubbles had at least one line too
   wide. DLC 0.2.8 re-breaks those bubbles onto two or three lines so that no
   line is wider than 205 pixels. The words are Sega's and unchanged; only
   where the lines break has moved, and Sega's own Japanese script already
   uses three-line bubbles in the same scenes. The base game's chapters 1 to
   7 draw through a different, narrower font and were left alone; if a bubble
   there looks clipped too, say so in the issue.
2. **The "Time Up" call in Party mode was drawn as slices.** The game draws
   that graphic as six separate sprites, one per Japanese character, and 1.0.12
   had painted "TIME UP!" across the whole texture, so each sprite showed a
   piece of it. 1.0.13 uses Sega's own "TIME!" art from the Steam release, cut
   into one letter per sprite.

Files changed: base game 2 (the title screen stamp and the Party-mode texture
archive), DLC 3 (the three chapter text tables). Both CIAs were compared
against 1.0.12 / 0.2.7 file by file and differ in exactly those. """ + STATUS + """
The Japanese-voice edition was rebuilt the same way and carries the same two
fixes; its release files now read 1.0.13 / 0.2.8. The title screen reads
**ENG 1.0.13** and the DLC is **TMD 0.2.8**.

"""


def rep(path, pairs, newline=''):
    s = io.open(path, encoding='utf-8', newline='').read()
    for a, b, *cnt in pairs:
        want = cnt[0] if cnt else 1
        n = s.count(a)
        assert n == want, '%s: anchor found %d times (want %d): %r' % (path, n, want, a[:80])
        s = s.replace(a, b)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('edited', path)


def sub(txt, pairs):
    LF, CRLF = chr(10), chr(13) + chr(10)
    crlf = CRLF in txt
    for a, b, *cnt in pairs:
        if crlf:
            a, b = a.replace(CRLF, LF).replace(LF, CRLF), b.replace(CRLF, LF).replace(LF, CRLF)
        want = cnt[0] if cnt else 1
        n = txt.count(a)
        assert n == want, 'anchor found %d times (want %d): %r' % (n, want, a[:80])
        txt = txt.replace(a, b)
    return txt


def scan(paths):
    for p in paths:
        t = io.open(p, encoding='utf-8').read()
        print('%-50s em/en dashes: %d  ellipsis: %d  "1.0.12" left: %d  "0.2.7" left: %d' % (
            p, t.count('\u2014') + t.count('\u2013'), t.count('\u2026'), t.count('1.0.12'), t.count('0.2.7')))


mode = sys.argv[1]
if mode == 'texts':
    rep('public_repo/README.md', [
        ('(build 1.0.12, DLC\n0.2.7)', '(build 1.0.13, DLC\n0.2.8)'),
        ('`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.12.zip` (base and DLC patches for your own decrypted dumps), `PuyoPuyoTetris-JP-voices-LayeredFS.zip` (Luma3DS) and `PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia`.',
         '`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip` (base and DLC patches for your own decrypted dumps), `PuyoPuyoTetris-JP-voices-LayeredFS.zip` (Luma3DS) and `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`.'),
        ('1.0.12** in both editions.', '1.0.13** in both editions.'),
    ])
    rep('public_repo/RELEASE_NOTES.md', [
        ('the current one is **1.0.12** with DLC 0.2.7 (see below).', 'the current one is **1.0.13** with DLC 0.2.8 (see below).'),
        ('1.0.12 changes eight textures and was checked in Azahar).',
         '1.0.12 changes eight textures and was checked in Azahar; 1.0.13 fixes the EX chapter line breaks and the Party-mode Time Up graphic).'),
        ('Title screen reads **ENG 1.0.12**; the built CIA reports 1.0.12.', 'Title screen reads **ENG 1.0.13**; the built CIA reports 1.0.13.'),
        ('33 shop icons and the three EX chapter plates. TMD 0.2.7.', '33 shop icons and the three EX chapter plates. TMD 0.2.8.'),
        ('`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.12.zip` (base and DLC as xdelta3 patches for your own decrypted dumps, xdelta3.exe and a readme inside), `PuyoPuyoTetris-JP-voices-LayeredFS.zip` (the LayeredFS files without the English voice bank) and `PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia`. Same title ID and the same ENG 1.0.12 stamp',
         '`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip` (base and DLC as xdelta3 patches for your own decrypted dumps, xdelta3.exe and a readme inside), `PuyoPuyoTetris-JP-voices-LayeredFS.zip` (the LayeredFS files without the English voice bank) and `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`. Same title ID and the same ENG 1.0.13 stamp'),
        ('1.0.12 (below) is the current build.', '1.0.13 (below) is the current build.'),
        ('## Current build: 1.0.12 / DLC 0.2.7\n', RN_1013 + '## 1.0.12 / DLC 0.2.7\n'),
        ('`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.12.zip` (the base patch is', '`PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip` (the base patch is'),
        ('a ready CIA, `PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia`.', 'a ready CIA, `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`.'),
        ('Same title ID and the same **ENG 1.0.12** stamp as the English-voice build,', 'Same title ID and the same **ENG 1.0.13** stamp as the English-voice build,'),
        ('and were Japanese; the rest rests on the file comparison above. Not yet on\na console.',
         'and were Japanese; the rest rests on the file comparison above. Not yet on\na console. Rebuilt on 14 September 2026 as 1.0.13 / DLC 0.2.8 with the two\nfixes described under the current build; the recipe and the file-by-file\ncomparison were repeated on the new files.'),
    ])
    rep('public_repo/TESTING.md', [
        ('For the Japanese-voice edition use `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.12.zip`', 'For the Japanese-voice edition use `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip`'),
        ('`PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia`. One edition or the other, not both.', '`PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`. One edition or the other, not both.'),
        ('reads **ENG 1.0.12** at its right end.', 'reads **ENG 1.0.13** at its right end.'),
        ('as version **1.0.12** (a locally built CIA)\n  and the DLC as **0.2.7**', 'as version **1.0.13** (a locally built CIA)\n  and the DLC as **0.2.8**'),
        ('In that edition a voice in Japanese is correct, not a bug.\n',
         'In that edition a voice in Japanese is correct, not a bug.\n\n**1.0.13 / DLC 0.2.8 (14 September 2026)** fix the two things the first report\nin issue #1 found: EX chapter dialogue running past the right edge of its\nbubble (276 of 734 bubbles re-broken onto two or three lines, words unchanged)\nand the Party-mode Time Up graphic drawn as slices (now Sega\'s own "TIME!"\nart, one letter per sprite). ' + STATUS + ' The base\nchapters 1 to 7 draw through a different font and were not changed; a clipped\nbubble there is worth a screenshot.\n'),
    ])

if mode in ('texts', 'readmes'):
    os.makedirs('work/readmes_1013', exist_ok=True); os.makedirs('work/readmes_jpv_113', exist_ok=True)
    R12 = 'work/readmes_1012/'; RJ = 'work/readmes_jpv/'
    base_txt = io.open(R12 + 'README_base_xdelta.txt', encoding='utf-8', newline='').read()
    base_txt = sub(base_txt, [
        ('(build 1.0.12)', '(build 1.0.13)'),
        ('PuyoPuyoTetris-EN-voices-1.0.12.xdelta PuyoPuyoTetris-EN-voices-1.0.12.cia', 'PuyoPuyoTetris-EN-voices-1.0.13.xdelta PuyoPuyoTetris-EN-voices-1.0.13.cia'),
        (OLD_SHA, EN_SHA), ('"ENG 1.0.12"', '"ENG 1.0.13"'),
        ('The result is a 513,737,792 byte .cia', 'The result is a ' + sz(EN_CIA) + ' byte .cia'),
        ('Build history: 1.0.12 (2026-09-07)', 'Build history: 1.0.13 (2026-09-14) fixes the Party-mode "Time Up" graphic, which\r\n1.0.12 drew as slices (the game draws it as six sprites; the fix is Sega\'s own\r\n"TIME!" art, one letter per sprite), and restamps the title; nothing else\r\nchanged from 1.0.12. 1.0.12 (2026-09-07)')])
    io.open('work/readmes_1013/README_base_xdelta.txt', 'w', encoding='utf-8', newline='').write(base_txt)

    dlc_txt = io.open(R12 + 'README_dlc_xdelta.txt', encoding='utf-8', newline='').read()
    dlc_txt = sub(dlc_txt, [
        ('(DLC 0.2.7)', '(DLC 0.2.8)'),
        ('PuyoPuyoTetris-DLC-0.2.7.xdelta PuyoPuyoTetris-DLC-patched.cia', 'PuyoPuyoTetris-DLC-0.2.8.xdelta PuyoPuyoTetris-DLC-patched.cia'),
        (OLD_DLC, EN_DLC_SHA), ('(TMD version 0.2.7)', '(TMD version 0.2.8)'),
        ('The result should be 111,889,472 bytes', 'The result should be ' + sz(EN_DLC) + ' bytes'),
        ('Build history: 0.2.7 (2026-09-07)', 'Build history: 0.2.8 (2026-09-14) re-breaks the EX chapter dialogue so every line\r\nfits the 3DS speech bubble (276 of 734 bubbles; Sega\'s words unchanged) and sets\r\neach bubble\'s scripted height from the English line count (the scene scripts\r\ncarry a height per line, and Sega\'s values follow the Japanese line count, which\r\nwas cutting off second and third English lines); nothing else changed from\r\n0.2.7. 0.2.7 (2026-09-07)')])
    io.open('work/readmes_1013/README_dlc_xdelta.txt', 'w', encoding='utf-8', newline='').write(dlc_txt)

    lfs_txt = io.open(R12 + 'README_layeredfs.txt', encoding='utf-8', newline='').read()
    io.open('work/readmes_1013/README_layeredfs.txt', 'w', encoding='utf-8', newline='').write(sub(lfs_txt, [('v1.0.12', 'v1.0.13')]))

    rh = io.open(R12 + 'README_rhdn.md', encoding='utf-8', newline='').read()
    rh = sub(rh, [
        ('build 1.0.12 / DLC 0.2.7', 'build 1.0.13 / DLC 0.2.8'),
        ('`PuyoPuyoTetris-EN-voices-1.0.12.xdelta` | the complete', '`PuyoPuyoTetris-EN-voices-1.0.13.xdelta` | the complete'),
        ('`PuyoPuyoTetris-DLC-0.2.7.xdelta` | the English DLC', '`PuyoPuyoTetris-DLC-0.2.8.xdelta` | the English DLC'),
        ('PuyoPuyoTetris-EN-voices-1.0.12.xdelta PuyoPuyoTetris-EN-voices-1.0.12.cia', 'PuyoPuyoTetris-EN-voices-1.0.13.xdelta PuyoPuyoTetris-EN-voices-1.0.13.cia'),
        ('PuyoPuyoTetris-DLC-0.2.7.xdelta PuyoPuyoTetris-DLC-0.2.7.cia', 'PuyoPuyoTetris-DLC-0.2.8.xdelta PuyoPuyoTetris-DLC-0.2.8.cia'),
        ('| `PuyoPuyoTetris-EN-voices-1.0.12.cia` | 513,737,792 | `' + OLD_SHA + '` |', '| `PuyoPuyoTetris-EN-voices-1.0.13.cia` | ' + sz(EN_CIA) + ' | `' + EN_SHA + '` |'),
        ('| `PuyoPuyoTetris-DLC-0.2.7.cia` | 111,889,472 | `' + OLD_DLC + '` |', '| `PuyoPuyoTetris-DLC-0.2.8.cia` | ' + sz(EN_DLC) + ' | `' + EN_DLC_SHA + '` |'),
        ('reads **ENG 1.0.12** at its right end', 'reads **ENG 1.0.13** at its right end'),
        ('The console lists the base game as version 1.0.12 and the DLC as 0.2.7.', 'The console lists the base game as version 1.0.13 and the DLC as 0.2.8.'),
        ('## Patch set history\n\n', '## Patch set history\n\n1.0.13 / DLC 0.2.8 (2026-09-14): the EX chapter dialogue is re-broken so every\nline fits the 3DS speech bubble (276 of 734 bubbles, words unchanged), each\nbubble\'s scripted height now follows the English line count instead of the\nJapanese one (which was cutting off second and third lines), and the\nParty-mode "Time Up" graphic, drawn as slices since 1.0.12, is Sega\'s own\n"TIME!" art one letter per sprite. Both from the first report in issue #1.\nNothing else changed; ' + STATUS_SHORT + '.\n\n'),
        ('1.0.12 / 0.2.7 (eight re-encoded textures) were checked in Azahar,\nnot yet on the console.',
         '1.0.12 / 0.2.7 (eight re-encoded textures) were checked in Azahar,\nnot yet on the console; 1.0.13 / 0.2.8 (line breaks and the Time Up graphic) ' + STATUS_SHORT + '.'),
    ])
    io.open('work/readmes_1013/README_rhdn.md', 'w', encoding='utf-8', newline='').write(rh)

if mode in ('texts', 'jptexts', 'readmes'):
    RJ = 'work/readmes_jpv/'; os.makedirs('work/readmes_jpv_113', exist_ok=True)
    rj = io.open(RJ + 'README_rhdn.md', encoding='utf-8', newline='').read()
    rj = sub(rj, [
        ('build 1.0.12 / DLC 0.2.7', 'build 1.0.13 / DLC 0.2.8'),
        ('The same English patch as the main 1.0.12 release', 'The same English patch as the main 1.0.13 release'),
        ('reads ENG 1.0.12 on\nboth.', 'reads ENG 1.0.13 on\nboth.'),
        ('`PuyoPuyoTetris-JP-voices-1.0.12.xdelta` | the English base game', '`PuyoPuyoTetris-JP-voices-1.0.13.xdelta` | the English base game'),
        ('`PuyoPuyoTetris-DLC-JP-voices-0.2.7.xdelta` | the English DLC', '`PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta` | the English DLC'),
        ('PuyoPuyoTetris-JP-voices-1.0.12.xdelta PuyoPuyoTetris-JP-voices-1.0.12.cia', 'PuyoPuyoTetris-JP-voices-1.0.13.xdelta PuyoPuyoTetris-JP-voices-1.0.13.cia'),
        ('PuyoPuyoTetris-DLC-JP-voices-0.2.7.xdelta PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia', 'PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia'),
        ('| `PuyoPuyoTetris-JP-voices-1.0.12.cia` | 490,878,016 | `' + OLD_JP + '` |', '| `PuyoPuyoTetris-JP-voices-1.0.13.cia` | ' + sz(JP_CIA) + ' | `' + JP_SHA + '` |'),
        ('| `PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia` | 116,165,696 | `' + OLD_JP_DLC + '` |', '| `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia` | ' + sz(JP_DLC) + ' | `' + JP_DLC_SHA + '` |'),
        ('reads **ENG 1.0.12** at its right end,', 'reads **ENG 1.0.13** at its right end,'),
        ('version 1.0.12 and the DLC as 0.2.7. The quickest', 'version 1.0.13 and the DLC as 0.2.8. The quickest'),
        ('The English-voice 1.0.12 build was taken apart', 'The English-voice 1.0.13 build was taken apart'),
        ('Report anything here, with which screen (a photo beats a description):',
         '1.0.13 / DLC 0.2.8 (2026-09-14) carry the two fixes of the main release, both\nfrom the first report in issue #1 (made on this edition): the EX chapter\ndialogue is re-broken so every line fits the 3DS speech bubble (276 of 734\nbubbles, words unchanged), each bubble\'s scripted height follows the English\nline count instead of the Japanese one (which was cutting off second and third\nlines), and the Party-mode "Time Up" graphic is Sega\'s own "TIME!" art one\nletter per sprite instead of slices. ' + STATUS + '\n\nReport anything here, with which screen (a photo beats a description):'),
    ])
    io.open('work/readmes_jpv_113/README_rhdn.md', 'w', encoding='utf-8', newline='').write(rj)
    lj = io.open(RJ + 'README_layeredfs.txt', encoding='utf-8', newline='').read()
    lj = sub(lj, [('v1.0.12)', 'v1.0.13)'), ('PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia instead', 'PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia instead')])
    io.open('work/readmes_jpv_113/README_layeredfs.txt', 'w', encoding='utf-8', newline='').write(lj)

if mode in ('texts', 'jptexts', 'readmes', 'bubblefix'):
    scan(['public_repo/README.md', 'public_repo/RELEASE_NOTES.md', 'public_repo/TESTING.md',
          'work/readmes_1013/README_base_xdelta.txt', 'work/readmes_1013/README_dlc_xdelta.txt', 'work/readmes_1013/README_layeredfs.txt',
          'work/readmes_1013/README_rhdn.md', 'work/readmes_jpv_113/README_rhdn.md', 'work/readmes_jpv_113/README_layeredfs.txt'])

elif mode == 'bubblefix':
    rep('public_repo/RELEASE_NOTES.md', [
        ("   uses three-line bubbles in the same scenes. The base game's chapters 1 to",
         "   uses three-line bubbles in the same scenes. The bubble's height is not" + NL +
         "   worked out from the text: each scene script sets it per line, and Sega's" + NL +
         "   values follow the Japanese line count, so a second or third English line" + NL +
         "   was being cut off at the bubble's edge. 0.2.8 sets those values from the" + NL +
         "   English line count (319 of 763 lines). The base game's chapters 1 to"),
        ("archive), DLC 3 (the three chapter text tables).",
         "archive), DLC 6 (the three chapter text tables and the three scene" + NL + "scripts that carry the bubble heights)."),
    ])
    rep('public_repo/TESTING.md', [
        ("bubble (276 of 734 bubbles re-broken onto two or three lines, words unchanged)",
         "bubble (276 of 734 bubbles re-broken onto two or three lines, words unchanged," + NL +
         "and the scripted bubble heights set to the English line counts)"),
    ])
elif mode == 'install':
    B_EN = r'Final\_new\PuyoPuyoTetris-xdelta-patches-1.0.13.zip'
    B_JP = r'Final\_new\PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip'
    assert os.path.exists(B_EN) and os.path.exists(B_JP)
    rep('Final/_CURRENT/INSTALL.txt', [
        ('as of build 1.0.12 / DLC 0.2.7 (2026-09-07, folder', 'as of build 1.0.13 / DLC 0.2.8 (2026-09-14, folder'),
        ('  2. PuyoPuyoTetris-EN-voices-1.0.12.cia', '  2. PuyoPuyoTetris-EN-voices-1.0.13.cia'),
        ('  4. PuyoPuyoTetris-DLC-0.2.7.cia', '  4. PuyoPuyoTetris-DLC-0.2.8.cia'),
        ('ENG 1.0.12 stamp; the HOME menu jingle tells them apart):', 'ENG 1.0.13 stamp; the HOME menu jingle tells them apart):'),
        ('  PuyoPuyoTetris-JP-voices-1.0.12.cia      (sha256 ' + OLD_JP + ')', '  PuyoPuyoTetris-JP-voices-1.0.13.cia      (sha256 ' + JP_SHA + ')'),
        ('  PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia   (sha256 ' + OLD_JP_DLC + ')', '  PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia   (sha256 ' + JP_DLC_SHA + ')'),
        ('PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.12.zip (sha256 3b38e9bcd2481dadc2397a5619be32d72dbbba734a162825196e03afbc64f14c)',
         'PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip (sha256 ' + sha(B_JP) + ')'),
        ('  - PuyoPuyoTetris-xdelta-patches-1.0.12.zip', '  - PuyoPuyoTetris-xdelta-patches-1.0.13.zip'),
        ('Checking a file: the 1.0.12 base CIA has sha256\n  ' + OLD_SHA, 'Checking a file: the 1.0.13 base CIA has sha256\n  ' + EN_SHA),
        ('releases/tag/builds-1.0.12', 'releases/tag/builds-1.0.13'),
        ('Puzzle League rank plates, the six DLC chapter plates), checked in Azahar\n(2026-09-07).',
         'Puzzle League rank plates, the six DLC chapter plates), checked in Azahar\n(2026-09-07). 1.0.13 / DLC 0.2.8 (2026-09-14) fix the EX chapter bubble line\nbreaks and the Party-mode Time Up graphic from the first issue #1 report;\n' + STATUS_SHORT + '.'),
    ])
    scan(['Final/_CURRENT/INSTALL.txt'])
print('done')
