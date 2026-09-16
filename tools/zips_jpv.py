# -*- coding: utf-8 -*-
"""Build and verify the Japanese-voice edition zips (1.0.12 / DLC 0.2.7). Run from anywhere.
 - work/PuyoPuyoTetris-JP-voices-LayeredFS.zip            (the 1.0.12 LayeredFS files minus sound/tenp.bcsar + README)
 - Final/_new/PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.12.zip   (README.md + both xdeltas + xdelta3.exe)
Both xdeltas come from work/rhdn_xdelta_jpv (rebuild_rhdn_xdelta_jpv.py, proven on perturbed sources)."""
import io, os, sys, zipfile, hashlib, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
W = os.path.join(R, 'work')
os.chdir(R)
BASE_SHA = 'fe2d1927728e258f108d889985b29fe77e3378139957f519d7f60a72a9dc1349'
DLC_SHA = 'd7af2e37acd97d2482ed32ab67ea996e452996951729e010b1f7fb8753eaec09'
sha = lambda b: hashlib.sha256(b).hexdigest()

base_xd = open(os.path.join(W, r'rhdn_xdelta_jpv\PuyoPuyoTetris-JP-voices-1.0.12.xdelta'), 'rb').read()
dlc_xd = open(os.path.join(W, r'rhdn_xdelta_jpv\PuyoPuyoTetris-DLC-JP-voices-0.2.7.xdelta'), 'rb').read()
xd3 = zipfile.ZipFile(r'Final\_CURRENT\PuyoPuyoTetris-xdelta-patches-1.0.12.zip').read('xdelta3.exe')
for xd in (base_xd, dlc_xd):
    assert xd[:3] == b'\xd6\xc3\xc4' and (xd[4] & 0x04) == 0, 'xdelta carries an app header'


def ascii_ok(b):
    return not [c for c in b if c > 126 or (c < 32 and c not in (10, 13))]


def zwrite(path, entries):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in entries:
            z.writestr(name, data)


# 1. LayeredFS zip: the shipped 1.0.12 entry list minus sound/tenp.bcsar, every file re-read from the overlay
rd = open(os.path.join(W, r'readmes_jpv\README_layeredfs.txt'), 'rb').read(); assert ascii_ok(rd)
tree = os.path.join(W, 'patch', 'romfs')
en = zipfile.ZipFile(os.path.join(W, 'PuyoPuyoTetris-LayeredFS.zip'))
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
    assert d == en.read(i.filename), 'overlay drifted from the shipped LayeredFS zip: ' + rel
    entries.append((i.filename, d)); checked += 1
en.close()
assert dropped == ['sound/tenp.bcsar'], dropped
assert checked == 100, checked
lfs = os.path.join(W, 'PuyoPuyoTetris-JP-voices-LayeredFS.zip')
zwrite(lfs, entries)
print('LayeredFS JP: %d romfs files (dropped %s), %d bytes sha256 %s' % (checked, dropped, os.path.getsize(lfs), sha(open(lfs, 'rb').read())))

# 2. bundle
rh = open(os.path.join(W, r'readmes_jpv\README_rhdn.md'), 'rb').read().decode('utf-8')
rh = rh.replace('{BASE_XD_MB}', str(round(len(base_xd) / 1048576))).encode('utf-8')
assert b'{' + b'BASE_XD_MB}' not in rh
bundle = r'Final\_new\PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.12.zip'
zwrite(bundle, [
    ('README.md', rh), ('PuyoPuyoTetris-JP-voices-1.0.12.xdelta', base_xd),
    ('PuyoPuyoTetris-DLC-JP-voices-0.2.7.xdelta', dlc_xd), ('xdelta3.exe', xd3)])
open(r'Final\_new\rhdn_bundle_README_JP-voices_1.0.12.md', 'wb').write(rh)

# 3. verify: apply both xdeltas out of the bundle to the decrypted dumps
tmp = os.path.join(W, '_verify_jpv'); os.makedirs(tmp, exist_ok=True)
z = zipfile.ZipFile(bundle)
for n in ('PuyoPuyoTetris-JP-voices-1.0.12.xdelta', 'PuyoPuyoTetris-DLC-JP-voices-0.2.7.xdelta', 'xdelta3.exe'):
    open(os.path.join(tmp, n), 'wb').write(z.read(n))
for src, xd, want in ((os.path.join(R, '0004000000101200 Jap-ORG-Base (CTR-P-BPTJ) (v0.1.0) (J).piratelegit-decrypted.cci'), 'PuyoPuyoTetris-JP-voices-1.0.12.xdelta', BASE_SHA),
                      (os.path.join(W, 'dlc_shell.cia'), 'PuyoPuyoTetris-DLC-JP-voices-0.2.7.xdelta', DLC_SHA)):
    out = os.path.join(tmp, 'out.bin')
    r = subprocess.run([os.path.join(tmp, 'xdelta3.exe'), '-d', '-f', '-s', src, os.path.join(tmp, xd), out], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    got = sha(open(out, 'rb').read())
    assert got == want, (xd, got, want)
    print('bundle patch %s applies from the zip and reproduces %s...' % (xd, want[:12]))
    os.remove(out)
shutil.rmtree(tmp)
print('bundle %d bytes sha256 %s' % (os.path.getsize(bundle), sha(open(bundle, 'rb').read())))
print('base xdelta %d bytes, DLC xdelta %d bytes' % (len(base_xd), len(dlc_xd)))
