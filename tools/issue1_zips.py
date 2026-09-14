# -*- coding: utf-8 -*-
"""Build and verify the 1.0.13 / DLC 0.2.8 zips. Run from anywhere, EN first, then JP.

    python issue1_zips.py en
      work/PuyoPuyoTetris-Base-xdelta.zip        (README + EN base xdelta)          old -> Final/_superseded/...-1.0.12.zip
      work/PuyoPuyoTetris-DLC-xdelta.zip         (README + DLC xdelta)              old -> Final/_superseded/...-0.2.7.zip
      work/PuyoPuyoTetris-LayeredFS.zip          (101 romfs files from patch/romfs, 2 replaced, README)   old -> _superseded
      Final/_new/PuyoPuyoTetris-xdelta-patches-1.0.13.zip   (README.md + both xdeltas + xdelta3.exe)
    python issue1_zips.py jp
      work/PuyoPuyoTetris-JP-voices-LayeredFS.zip   (the new EN LayeredFS entries minus sound/tenp.bcsar)   old -> _superseded
      Final/_new/PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip
Every xdelta is re-applied out of its zip to the decrypted dump and hash-checked against the built CIA.
"""
import io, os, sys, zipfile, hashlib, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'G:\Claude\PuyoPuyo'
W = os.path.join(R, 'work')
os.chdir(R)
ED = sys.argv[1]
BASE_SRC = os.path.join(R, '0004000000101200 Jap-ORG-Base (CTR-P-BPTJ) (v0.1.0) (J).piratelegit-decrypted.cci')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fsha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


def ascii_ok(b):
    return not [c for c in b if c > 126 or (c < 32 and c not in (10, 13))]


def zwrite(path, entries):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in entries:
            z.writestr(name, data)


def verify_bundle(bundle, jobs):
    tmp = os.path.join(W, '_verify_zip'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    z = zipfile.ZipFile(bundle)
    names = z.namelist()
    open(os.path.join(tmp, 'xdelta3.exe'), 'wb').write(z.read('xdelta3.exe'))
    for src, xd, want in jobs:
        assert xd in names, (xd, names)
        open(os.path.join(tmp, xd), 'wb').write(z.read(xd))
        out = os.path.join(tmp, 'out.bin')
        r = subprocess.run([os.path.join(tmp, 'xdelta3.exe'), '-d', '-f', '-B', '1073741824', '-s', src, os.path.join(tmp, xd), out], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        got = fsha(out)
        print('%-46s applied out of the zip -> sha256 %s %s' % (xd, got, 'OK' if got == want else 'MISMATCH'))
        assert got == want
        os.remove(out)
    shutil.rmtree(tmp)


def retire(src, dst):
    """Move the previous zip aside; if the superseded copy already exists (second pass of the same
    version), the current file is just a first-pass 1.0.13 zip and is deleted instead."""
    if os.path.exists(dst):
        os.remove(src)
    else:
        shutil.move(src, dst)


xd3 = zipfile.ZipFile(r'Final\_CURRENT\PuyoPuyoTetris-xdelta-patches-1.0.12.zip').read('xdelta3.exe')
os.makedirs(r'Final\_superseded', exist_ok=True); os.makedirs(r'Final\_new', exist_ok=True)

if ED == 'en':
    EN_SHA = fsha(r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.13.cia')
    DLC_SHA = fsha(r'Final\_new\PuyoPuyoTetris-DLC-0.2.8.cia')
    base_xd = open(os.path.join(W, r'rhdn_xdelta_v5\PuyoPuyoTetris-EN-voices-1.0.13.xdelta'), 'rb').read()
    dlc_xd = open(os.path.join(W, r'rhdn_xdelta_v5\PuyoPuyoTetris-DLC-0.2.8.xdelta'), 'rb').read()
    for xd in (base_xd, dlc_xd):
        assert xd[:3] == b'\xd6\xc3\xc4' and (xd[4] & 0x04) == 0, 'xdelta carries an app header'
    RD = os.path.join(W, 'readmes_1013')

    rd = open(os.path.join(RD, 'README_base_xdelta.txt'), 'rb').read(); assert ascii_ok(rd)
    retire(os.path.join(W, 'PuyoPuyoTetris-Base-xdelta.zip'), r'Final\_superseded\PuyoPuyoTetris-Base-xdelta-1.0.12.zip')
    zwrite(os.path.join(W, 'PuyoPuyoTetris-Base-xdelta.zip'), [('README.txt', rd), ('PuyoPuyoTetris-EN-voices-1.0.13.xdelta', base_xd)])

    rd = open(os.path.join(RD, 'README_dlc_xdelta.txt'), 'rb').read(); assert ascii_ok(rd)
    retire(os.path.join(W, 'PuyoPuyoTetris-DLC-xdelta.zip'), r'Final\_superseded\PuyoPuyoTetris-DLC-xdelta-0.2.7.zip')
    zwrite(os.path.join(W, 'PuyoPuyoTetris-DLC-xdelta.zip'), [('README.txt', rd), ('PuyoPuyoTetris-DLC-0.2.8.xdelta', dlc_xd)])

    tree = os.path.join(W, 'patch', 'romfs')
    old_lfs = zipfile.ZipFile(os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'))
    entries = []; changed = []; checked = 0
    PFX = 'luma/titles/0004000000101200/romfs/'
    for i in old_lfs.infolist():
        if i.filename == 'README.txt':
            d = open(os.path.join(RD, 'README_layeredfs.txt'), 'rb').read(); assert ascii_ok(d)
        else:
            assert i.filename.startswith(PFX), i.filename
            rel = i.filename[len(PFX):].replace('/', os.sep)
            d = open(os.path.join(tree, rel), 'rb').read()
            if d != old_lfs.read(i.filename):
                changed.append(i.filename)
            checked += 1
        entries.append((i.filename, d))
    old_lfs.close()
    assert checked == 101, checked
    # first pass: the shipped 1.0.12 zip is the reference (2 files replaced); second pass of 1.0.13: none
    assert sorted(changed) in (sorted([PFX + 'title/title.narc', PFX + 'tenp/party/party2p/party2p.narc']), []), changed
    retire(os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'), r'Final\_superseded\PuyoPuyoTetris-LayeredFS-1.0.12.zip')
    zwrite(os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'), entries)
    print('LayeredFS: %d romfs files from the 1.0.13 overlay, replaced: %s' % (checked, changed))

    rh = open(os.path.join(RD, 'README_rhdn.md'), 'rb').read()
    bundle = r'Final\_new\PuyoPuyoTetris-xdelta-patches-1.0.13.zip'
    zwrite(bundle, [('README.md', rh), ('PuyoPuyoTetris-EN-voices-1.0.13.xdelta', base_xd),
                    ('PuyoPuyoTetris-DLC-0.2.8.xdelta', dlc_xd), ('xdelta3.exe', xd3)])
    shutil.copyfile(os.path.join(RD, 'README_rhdn.md'), r'Final\_new\rhdn_bundle_README_1.0.13.md')
    verify_bundle(bundle, [(BASE_SRC, 'PuyoPuyoTetris-EN-voices-1.0.13.xdelta', EN_SHA),
                           (os.path.join(W, 'dlc_shell.cia'), 'PuyoPuyoTetris-DLC-0.2.8.xdelta', DLC_SHA)])
    for p in (os.path.join(W, 'PuyoPuyoTetris-Base-xdelta.zip'), os.path.join(W, 'PuyoPuyoTetris-DLC-xdelta.zip'),
              os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'), bundle):
        print('%-62s %12d  sha256 %s' % (os.path.relpath(p, R), os.path.getsize(p), fsha(p)))

else:
    JP_SHA = fsha(r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.13.cia')
    JP_DLC_SHA = fsha(r'Final\_new\PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia')
    base_xd = open(os.path.join(W, r'rhdn_xdelta_jpv_113\PuyoPuyoTetris-JP-voices-1.0.13.xdelta'), 'rb').read()
    dlc_xd = open(os.path.join(W, r'rhdn_xdelta_jpv_113\PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta'), 'rb').read()
    for xd in (base_xd, dlc_xd):
        assert xd[:3] == b'\xd6\xc3\xc4' and (xd[4] & 0x04) == 0, 'xdelta carries an app header'
    RD = os.path.join(W, 'readmes_jpv_113')

    rd = open(os.path.join(RD, 'README_layeredfs.txt'), 'rb').read(); assert ascii_ok(rd)
    tree = os.path.join(W, 'patch', 'romfs')
    en = zipfile.ZipFile(os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'))
    en_rd = en.read('README.txt').decode('utf-8'); assert 'v1.0.13' in en_rd, 'run the EN zips first'
    PFX = 'luma/titles/0004000000101200/romfs/'
    entries = []; dropped = []; checked = 0
    for i in en.infolist():
        if i.filename == 'README.txt':
            entries.append((i.filename, rd)); continue
        assert i.filename.startswith(PFX), i.filename
        rel = i.filename[len(PFX):]
        if rel.startswith('sound/'):
            dropped.append(rel); continue
        d = open(os.path.join(tree, rel.replace('/', os.sep)), 'rb').read()
        assert d == en.read(i.filename), 'overlay drifted from the EN LayeredFS zip: ' + rel
        entries.append((i.filename, d)); checked += 1
    en.close()
    assert dropped == ['sound/tenp.bcsar'], dropped
    assert checked == 100, checked
    lfs = os.path.join(W, 'PuyoPuyoTetris-JP-voices-LayeredFS.zip')
    retire(lfs, r'Final\_superseded\PuyoPuyoTetris-JP-voices-LayeredFS-1.0.12.zip')
    zwrite(lfs, entries)
    print('LayeredFS JP: %d romfs files (dropped %s), %d bytes sha256 %s' % (checked, dropped, os.path.getsize(lfs), fsha(lfs)))

    rh = open(os.path.join(RD, 'README_rhdn.md'), 'rb').read().decode('utf-8')
    rh = rh.replace('{BASE_XD_MB}', str(round(len(base_xd) / 1048576))).encode('utf-8')
    assert b'{' + b'BASE_XD_MB}' not in rh
    bundle = r'Final\_new\PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.13.zip'
    zwrite(bundle, [('README.md', rh), ('PuyoPuyoTetris-JP-voices-1.0.13.xdelta', base_xd),
                    ('PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta', dlc_xd), ('xdelta3.exe', xd3)])
    open(r'Final\_new\rhdn_bundle_README_JP-voices_1.0.13.md', 'wb').write(rh)
    verify_bundle(bundle, [(BASE_SRC, 'PuyoPuyoTetris-JP-voices-1.0.13.xdelta', JP_SHA),
                           (os.path.join(W, 'dlc_shell.cia'), 'PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta', JP_DLC_SHA)])
    print('bundle %d bytes sha256 %s   (base xdelta %d bytes, DLC xdelta %d bytes)' % (os.path.getsize(bundle), fsha(bundle), len(base_xd), len(dlc_xd)))
print('done')
