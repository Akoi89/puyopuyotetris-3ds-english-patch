"""Base rebuild 1.0.14 (both editions). The DLC is unchanged and stays at 0.2.8.

    python issue1_build_114.py            (log: build_114.out)

1. stamp_title.py "ENG 1.0.14" (box reference: the 1.0.12 stamped title.narc kept in work/)
2. romfs: romfs_110_tree + patch/romfs -> new_114.romfs; the extracted tree must differ from the 1.0.13
   tree in exactly title/title.narc and the two scene scripts
3. build_cia.py with cci_banner.cci      -> Final/_new/PuyoPuyoTetris-EN-voices-1.0.14.cia
4. sound/ swapped for tr_jpvoice/sound   -> new_114_jpv.romfs (null test first: the pre-swap repack must
   equal new_114.romfs), build_cia.py with cci_banner_jpv.cci -> PuyoPuyoTetris-JP-voices-1.0.14.cia
"""
import os, sys, shutil, subprocess, hashlib, time, filecmp

TOOL = r'G:\Claude\TGAA 1-2\3dstool\3dstool.exe'
R = r'G:\Claude\PuyoPuyo'
SHELL = os.path.join(R, '0004000000101200 Puyopuyo Tetris (English Translated, English Voices) (CTR-P-BPTJ) (v0.0.0) (J).standard.cia')
OUT_EN = os.path.join(R, 'Final', '_new', 'PuyoPuyoTetris-EN-voices-1.0.14.cia')
OUT_JP = os.path.join(R, 'Final', '_new', 'PuyoPuyoTetris-JP-voices-1.0.14.cia')
VER = '1.0.14'
EXPECT = {os.path.join('title', 'title.narc'),
          os.path.join('script', 'adventure', 'chapter01', 'manzai_script_chapter01.narc'),
          os.path.join('script', 'adventure', 'general', 'manzai_script_general.narc')}
t0 = time.time()


def log(*a):
    print('[%5.0fs]' % (time.time() - t0), *a, flush=True)


def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('FAILED: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))
    return r.stdout


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


def pack(tree, out):
    run(TOOL, '-ctf', 'romfs', out, '--romfs-dir', tree)


def overlay(tree):
    n = 0
    for dp, dn, fn in os.walk('patch/romfs'):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), 'patch/romfs')
            dst = os.path.join(tree, rel)
            assert os.path.exists(dst), 'overlay file not in the tree: ' + rel
            shutil.copyfile(os.path.join(dp, f), dst); n += 1
    return n


# 1. stamp
log(run(sys.executable, 'stamp_title.py', 'ENG ' + VER, 'title_1012_stamped.narc').strip().splitlines()[-1])

# 2. romfs
TREE = 'romfs_114_tree'
shutil.rmtree(TREE, ignore_errors=True)
shutil.copytree('romfs_110_tree', TREE)
log('tree copied, overlaid %d files' % overlay(TREE))
pack(TREE, 'new_114.romfs')
log('new_114.romfs %d bytes sha256 %s' % (os.path.getsize('new_114.romfs'), sha('new_114.romfs')))

for name in ('113', '114'):
    d = '_v_%s_tree' % name
    shutil.rmtree(d, ignore_errors=True)
    run(TOOL, '-xtf', 'romfs', 'new_%s.romfs' % name, '--romfs-dir', d)
diff = []
for dp, dn, fn in os.walk('_v_114_tree'):
    for f in fn:
        p = os.path.join(dp, f); rel = os.path.relpath(p, '_v_114_tree')
        q = os.path.join('_v_113_tree', rel)
        if not os.path.exists(q) or not filecmp.cmp(p, q, shallow=False):
            diff.append(rel)
log('files differing 1.0.13 -> 1.0.14: %d %s' % (len(diff), diff))
if set(diff) != EXPECT:
    raise SystemExit('STOP: unexpected romfs differences')

# 3. English CIA
os.makedirs(os.path.dirname(OUT_EN), exist_ok=True)
run(sys.executable, 'build_cia.py', SHELL, 'cci_banner.cci', 'new_114.romfs', OUT_EN, VER)
log('EN CIA %d bytes sha256 %s' % (os.path.getsize(OUT_EN), sha(OUT_EN)))

# 4. Japanese-voice edition
shutil.rmtree(os.path.join(TREE, 'sound'))
shutil.copytree(os.path.join('tr_jpvoice', 'sound'), os.path.join(TREE, 'sound'))
pack(TREE, 'new_114_jpv.romfs')
log('new_114_jpv.romfs %d bytes sha256 %s' % (os.path.getsize('new_114_jpv.romfs'), sha('new_114_jpv.romfs')))
run(sys.executable, 'build_cia.py', SHELL, 'cci_banner_jpv.cci', 'new_114_jpv.romfs', OUT_JP, VER)
log('JP CIA %d bytes sha256 %s' % (os.path.getsize(OUT_JP), sha(OUT_JP)))
shutil.rmtree(TREE, ignore_errors=True)
shutil.rmtree('_v_113_tree', ignore_errors=True); shutil.rmtree('_v_114_tree', ignore_errors=True)
log('done')
