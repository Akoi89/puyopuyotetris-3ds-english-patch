# -*- coding: utf-8 -*-
"""Build and verify the 1.0.14 zips. The DLC is unchanged at 0.2.8, so its xdelta and CIA are reused
as published; only the base patch, the two LayeredFS zips and the two bundles are rebuilt.

    python issue1_zips114.py en      Base-xdelta.zip, LayeredFS.zip, bundle 1.0.14
    python issue1_zips114.py jp      JP-voices-LayeredFS.zip, JP bundle 1.0.14   (run after en)

The LayeredFS entry list is taken from the overlay tree itself rather than from the previous zip, because
1.0.14 adds two files to it (the scene scripts). Every entry is checked to be either one of the previous
zip's paths or one of the two new ones.
"""
import io, os, sys, zipfile, hashlib, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
W = os.path.join(R, 'work')
os.chdir(R)
ED = sys.argv[1]
PFX = 'luma/titles/0004000000101200/romfs/'
BASE_SRC = os.path.join(R, '0004000000101200 Jap-ORG-Base (CTR-P-BPTJ) (v0.1.0) (J).piratelegit-decrypted.cci')
NEW_PATHS = {PFX + 'script/adventure/chapter01/manzai_script_chapter01.narc',
             PFX + 'script/adventure/general/manzai_script_general.narc'}


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


def retire(src, dst):
    if os.path.exists(dst):
        os.remove(src)
    else:
        shutil.move(src, dst)


def layeredfs_entries(readme, drop_sound):
    """Every file in the 1.0.14 overlay, in the previous zip's order, with the new files appended."""
    old = zipfile.ZipFile(os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'))
    order = [i.filename for i in old.infolist() if i.filename != 'README.txt']
    old.close()
    tree = os.path.join(W, 'patch', 'romfs')
    have = {PFX + os.path.relpath(os.path.join(dp, f), tree).replace(os.sep, '/')
            for dp, dn, fn in os.walk(tree) for f in fn}
    assert set(order) - have == set(), 'a file in the previous zip is no longer in the overlay'
    extra = sorted(have - set(order))
    assert set(extra) <= NEW_PATHS, extra
    entries = [('README.txt', readme)]
    for name in order + extra:
        rel = name[len(PFX):]
        if drop_sound and rel.startswith('sound/'):
            continue
        entries.append((name, open(os.path.join(tree, rel.replace('/', os.sep)), 'rb').read()))
    return entries, extra


def verify_bundle(bundle, jobs):
    tmp = os.path.join(W, '_verify_zip'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    z = zipfile.ZipFile(bundle)
    open(os.path.join(tmp, 'xdelta3.exe'), 'wb').write(z.read('xdelta3.exe'))
    for src, xd, want in jobs:
        open(os.path.join(tmp, xd), 'wb').write(z.read(xd))
        out = os.path.join(tmp, 'out.bin')
        r = subprocess.run([os.path.join(tmp, 'xdelta3.exe'), '-d', '-f', '-B', '1073741824', '-s', src,
                            os.path.join(tmp, xd), out], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        got = fsha(out)
        print('%-46s applied out of the zip -> sha256 %s %s' % (xd, got, 'OK' if got == want else 'MISMATCH'))
        assert got == want
        os.remove(out)
    shutil.rmtree(tmp)


xd3 = zipfile.ZipFile(r'Final\_CURRENT\PuyoPuyoTetris-xdelta-patches-1.0.13.zip').read('xdelta3.exe')

if ED == 'en':
    RD = os.path.join(W, 'readmes_1014')
    EN_SHA = fsha(r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.14.cia')
    DLC_SHA = fsha(r'Final\_CURRENT\PuyoPuyoTetris-DLC-0.2.8.cia')
    base_xd = open(os.path.join(W, r'rhdn_xdelta_v6\PuyoPuyoTetris-EN-voices-1.0.14.xdelta'), 'rb').read()
    dlc_xd = open(os.path.join(W, r'rhdn_xdelta_v5\PuyoPuyoTetris-DLC-0.2.8.xdelta'), 'rb').read()
    for xd in (base_xd, dlc_xd):
        assert xd[:3] == b'\xd6\xc3\xc4' and (xd[4] & 0x04) == 0, 'xdelta carries an app header'

    rd = open(os.path.join(RD, 'README_base_xdelta.txt'), 'rb').read(); assert ascii_ok(rd)
    retire(os.path.join(W, 'PuyoPuyoTetris-Base-xdelta.zip'), r'Final\_superseded\PuyoPuyoTetris-Base-xdelta-1.0.13.zip')
    zwrite(os.path.join(W, 'PuyoPuyoTetris-Base-xdelta.zip'), [('README.txt', rd), ('PuyoPuyoTetris-EN-voices-1.0.14.xdelta', base_xd)])

    rd = open(os.path.join(RD, 'README_layeredfs.txt'), 'rb').read(); assert ascii_ok(rd)
    entries, extra = layeredfs_entries(rd, drop_sound=False)
    retire(os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'), r'Final\_superseded\PuyoPuyoTetris-LayeredFS-1.0.13.zip')
    zwrite(os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'), entries)
    print('LayeredFS: %d romfs files (%d new: %s)' % (len(entries) - 1, len(extra), [e[len(PFX):] for e in extra]))

    rh = open(os.path.join(RD, 'README_rhdn.md'), 'rb').read()
    bundle = r'Final\_new\PuyoPuyoTetris-xdelta-patches-1.0.14.zip'
    zwrite(bundle, [('README.md', rh), ('PuyoPuyoTetris-EN-voices-1.0.14.xdelta', base_xd),
                    ('PuyoPuyoTetris-DLC-0.2.8.xdelta', dlc_xd), ('xdelta3.exe', xd3)])
    shutil.copyfile(os.path.join(RD, 'README_rhdn.md'), r'Final\_new\rhdn_bundle_README_1.0.14.md')
    verify_bundle(bundle, [(BASE_SRC, 'PuyoPuyoTetris-EN-voices-1.0.14.xdelta', EN_SHA),
                           (os.path.join(W, 'dlc_shell.cia'), 'PuyoPuyoTetris-DLC-0.2.8.xdelta', DLC_SHA)])
    for p in (os.path.join(W, 'PuyoPuyoTetris-Base-xdelta.zip'), os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'), bundle):
        print('%-62s %12d  sha256 %s' % (os.path.relpath(p, R), os.path.getsize(p), fsha(p)))
else:
    RD = os.path.join(W, 'readmes_jpv_114')
    JP_SHA = fsha(r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.14.cia')
    JP_DLC_SHA = fsha(r'Final\_CURRENT\PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia')
    base_xd = open(os.path.join(W, r'rhdn_xdelta_jpv_114\PuyoPuyoTetris-JP-voices-1.0.14.xdelta'), 'rb').read()
    dlc_xd = open(os.path.join(W, r'rhdn_xdelta_jpv_113\PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta'), 'rb').read()
    for xd in (base_xd, dlc_xd):
        assert xd[:3] == b'\xd6\xc3\xc4' and (xd[4] & 0x04) == 0, 'xdelta carries an app header'

    rd = open(os.path.join(RD, 'README_layeredfs.txt'), 'rb').read(); assert ascii_ok(rd)
    entries, extra = layeredfs_entries(rd, drop_sound=True)
    lfs = os.path.join(W, 'PuyoPuyoTetris-JP-voices-LayeredFS.zip')
    retire(lfs, r'Final\_superseded\PuyoPuyoTetris-JP-voices-LayeredFS-1.0.13.zip')
    zwrite(lfs, entries)
    print('LayeredFS JP: %d romfs files (%d new)' % (len(entries) - 1, len(extra)))

    rh = open(os.path.join(RD, 'README_rhdn.md'), 'rb').read().decode('utf-8')
    rh = rh.replace('{BASE_XD_MB}', str(round(len(base_xd) / 1048576))).encode('utf-8')
    assert b'{' + b'BASE_XD_MB}' not in rh
    bundle = r'Final\_new\PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip'
    zwrite(bundle, [('README.md', rh), ('PuyoPuyoTetris-JP-voices-1.0.14.xdelta', base_xd),
                    ('PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta', dlc_xd), ('xdelta3.exe', xd3)])
    open(r'Final\_new\rhdn_bundle_README_JP-voices_1.0.14.md', 'wb').write(rh)
    verify_bundle(bundle, [(BASE_SRC, 'PuyoPuyoTetris-JP-voices-1.0.14.xdelta', JP_SHA),
                           (os.path.join(W, 'dlc_shell.cia'), 'PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta', JP_DLC_SHA)])
    print('%-62s %12d  sha256 %s' % (os.path.relpath(lfs, R), os.path.getsize(lfs), fsha(lfs)))
    print('%-62s %12d  sha256 %s' % (bundle, os.path.getsize(bundle), fsha(bundle)))
print('done')
