"""Issue #1 fix build, Japanese-voice edition 1.0.13 / DLC 0.2.8.  (log: build_jpv_113.out)

1. cci_banner_jpv.cci = exefs_banner.py on the fan decrypted CCI with banner_jpv.bin (regenerated; deleted as scratch on 13 Sep)
2. romfs: copy romfs_110_tree -> romfs_jpv_tree, overlay patch/romfs, NULL TEST (== new_113.romfs), swap sound/ for
   tr_jpvoice/sound -> new_113_jpv.romfs
3. build_cia.py <fan shell> cci_banner_jpv.cci new_113_jpv.romfs Final/_new/PuyoPuyoTetris-JP-voices-1.0.13.cia 1.0.13
4. _jpv_dlc_overlay.py (patch_dlc2_jpv := patch_dlc2 minus adv_sound), then build_dlc_cia.py with the jpv overlay -> DLC-JP-voices-0.2.8
5. issue1_verify.py jp
"""
import os, sys, shutil, subprocess, hashlib, time

TOOL = r'G:\Claude\TGAA 1-2\3dstool\3dstool.exe'
R = r'G:\Claude\PuyoPuyo'
FAN_CCI = os.path.join(R, '0004000000101200 Puyopuyo Tetris (English Translated, English Voices) (CTR-P-BPTJ) (v0.0.0) (J).standard-decrypted.cci')
SHELL = os.path.join(R, '0004000000101200 Puyopuyo Tetris (English Translated, English Voices) (CTR-P-BPTJ) (v0.0.0) (J).standard.cia')
OUT = os.path.join(R, 'Final', '_new', 'PuyoPuyoTetris-JP-voices-1.0.13.cia')
OUT_DLC = os.path.join(R, 'Final', '_new', 'PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia')
t0 = time.time()


def log(*a):
    print('[%5.0fs]' % (time.time() - t0), *a, flush=True)


def run(*a, env=None):
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run(list(a), capture_output=True, text=True, env=e)
    if r.returncode:
        raise SystemExit('FAILED: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))
    return r.stdout


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


# 1. banner CCI
assert os.path.getsize('banner_jpv.bin') == 1016682, 'banner_jpv.bin is not the 11 Sep file'
log(run(sys.executable, 'exefs_banner.py', FAN_CCI, 'banner_jpv.bin', 'cci_banner_jpv.cci').strip())

# 2. romfs
TREE = 'romfs_jpv_tree'
if os.path.exists(TREE):
    shutil.rmtree(TREE)
shutil.copytree('romfs_110_tree', TREE)
n = 0
for dp, dn, fn in os.walk('patch/romfs'):
    for f in fn:
        rel = os.path.relpath(os.path.join(dp, f), 'patch/romfs')
        dst = os.path.join(TREE, rel)
        assert os.path.exists(dst), rel
        shutil.copyfile(os.path.join(dp, f), dst); n += 1
log('tree copied, %d overlay files' % n)
run(TOOL, '-ctf', 'romfs', 'chk_113_jpv.romfs', '--romfs-dir', TREE)
a, b = sha('chk_113_jpv.romfs'), sha('new_113.romfs')
log('NULL TEST repack == new_113.romfs: %s' % (a == b))
if a != b:
    raise SystemExit('stop: recipe does not reproduce new_113.romfs')
os.remove('chk_113_jpv.romfs')
shutil.rmtree(os.path.join(TREE, 'sound'))
shutil.copytree(os.path.join('tr_jpvoice', 'sound'), os.path.join(TREE, 'sound'))
run(TOOL, '-ctf', 'romfs', 'new_113_jpv.romfs', '--romfs-dir', TREE)
log('new_113_jpv.romfs %d bytes sha256 %s' % (os.path.getsize('new_113_jpv.romfs'), sha('new_113_jpv.romfs')))

# 3. base CIA
log(run(sys.executable, 'build_cia.py', SHELL, 'cci_banner_jpv.cci', 'new_113_jpv.romfs', OUT, '1.0.13'))
log('JP base CIA %d bytes sha256 %s' % (os.path.getsize(OUT), sha(OUT)))

# 4. DLC
log(run(sys.executable, '_jpv_dlc_overlay.py').strip())
log(run(sys.executable, 'build_dlc_cia.py', 'dlc_shell.cia', OUT_DLC, '0.2.8', env={'PUYO_DLC_PATCH': 'patch_dlc2_jpv', 'PUYO_DLC_WORK': 'dlc_build_jpv'}).strip()[-600:])
log('JP DLC CIA %d bytes sha256 %s' % (os.path.getsize(OUT_DLC), sha(OUT_DLC)))

# 5. verify
log(run(sys.executable, 'issue1_verify.py', 'jp'))
log('done')
