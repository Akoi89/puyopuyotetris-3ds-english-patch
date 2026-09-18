"""Base rebuild 1.0.15 (both editions). The DLC is unchanged and stays at 0.2.8.

    python _issue1_build_115.py            (log: build_115.out)

1.0.15 is the base-game bubble WIDTH pass (issue #1 round 3): 160 adventure entries re-wrapped so no
drawn line exceeds 193 px, the widest width proven to draw cleanly on TheGershon's console captures,
and 28 bubbles raised by _issue1_bubbles_base.py to hold the line counts that result. Words unchanged.
Run _issue1_verify_base115.py first; it must print ALL CHECKS PASSED.

1. stamp_title.py "ENG 1.0.15" (box reference: the 1.0.12 stamped title.narc kept in work/)
2. romfs: romfs_110_tree + patch/romfs -> new_115.romfs; the extracted tree must differ from the
   1.0.14 tree in exactly title/title.narc, the 8 adventure mtx files and the 8 manzai scripts
3. build_cia.py with cci_banner.cci      -> Final/_new/PuyoPuyoTetris-EN-voices-1.0.15.cia
4. sound/ swapped for tr_jpvoice/sound, build_cia.py with cci_banner_jpv.cci
                                         -> Final/_new/PuyoPuyoTetris-JP-voices-1.0.15.cia
"""
import os, sys, shutil, subprocess, hashlib, time, filecmp

TGAA_ROOT = os.environ.get('TGAA_ROOT') or sys.exit('set TGAA_ROOT to the TGAA project folder')
TOOL = os.path.join(TGAA_ROOT, '3dstool', '3dstool.exe')
R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
SHELL = os.path.join(R, '0004000000101200 Puyopuyo Tetris (English Translated, English Voices) (CTR-P-BPTJ) (v0.0.0) (J).standard.cia')
OUT_EN = os.path.join(R, 'Final', '_new', 'PuyoPuyoTetris-EN-voices-1.0.15.cia')
OUT_JP = os.path.join(R, 'Final', '_new', 'PuyoPuyoTetris-JP-voices-1.0.15.cia')
VER = '1.0.15'
STEMS = ['chapter%02d' % i for i in range(1, 8)] + ['general']
EXPECT = {os.path.join('title', 'title.narc')}
for s in STEMS:
    EXPECT.add(os.path.join('tenp', 'text', 'adventure', '%sJapanese.mtx' % s))
    EXPECT.add(os.path.join('script', 'adventure', s if s != 'general' else 'general',
                            'manzai_script_%s.narc' % s))
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


# 0. the pre-build verifier must pass
r = subprocess.run([sys.executable, '_issue1_verify_base115.py'], capture_output=True, text=True)
if r.returncode:
    raise SystemExit('STOP: _issue1_verify_base115.py failed\n' + r.stdout + r.stderr)
log('pre-build verify: ALL CHECKS PASSED')

# 1. stamp
log(run(sys.executable, 'stamp_title.py', 'ENG ' + VER, 'title_1012_stamped.narc').strip().splitlines()[-1])

# 2. romfs
TREE = 'romfs_115_tree'
shutil.rmtree(TREE, ignore_errors=True)
shutil.copytree('romfs_110_tree', TREE)
log('tree copied, overlaid %d files' % overlay(TREE))
pack(TREE, 'new_115.romfs')
log('new_115.romfs %d bytes sha256 %s' % (os.path.getsize('new_115.romfs'), sha('new_115.romfs')))

for name in ('114', '115'):
    d = '_v_%s_tree' % name
    shutil.rmtree(d, ignore_errors=True)
    run(TOOL, '-xtf', 'romfs', 'new_%s.romfs' % name, '--romfs-dir', d)
diff = []
for dp, dn, fn in os.walk('_v_115_tree'):
    for f in fn:
        p = os.path.join(dp, f); rel = os.path.relpath(p, '_v_115_tree')
        q = os.path.join('_v_114_tree', rel)
        if not os.path.exists(q) or not filecmp.cmp(p, q, shallow=False):
            diff.append(rel)
log('files differing 1.0.14 -> 1.0.15: %d' % len(diff))
for d in sorted(diff):
    log('   ' + d)
if set(diff) != EXPECT:
    raise SystemExit('STOP: unexpected romfs differences\nmissing: %s\nextra: %s'
                     % (EXPECT - set(diff), set(diff) - EXPECT))

# 3. English CIA
os.makedirs(os.path.dirname(OUT_EN), exist_ok=True)
run(sys.executable, 'build_cia.py', SHELL, 'cci_banner.cci', 'new_115.romfs', OUT_EN, VER)
log('EN CIA %d bytes sha256 %s' % (os.path.getsize(OUT_EN), sha(OUT_EN)))

# 4. Japanese-voice edition
shutil.rmtree(os.path.join(TREE, 'sound'))
shutil.copytree(os.path.join('tr_jpvoice', 'sound'), os.path.join(TREE, 'sound'))
pack(TREE, 'new_115_jpv.romfs')
log('new_115_jpv.romfs %d bytes sha256 %s' % (os.path.getsize('new_115_jpv.romfs'), sha('new_115_jpv.romfs')))
run(sys.executable, 'build_cia.py', SHELL, 'cci_banner_jpv.cci', 'new_115_jpv.romfs', OUT_JP, VER)
log('JP CIA %d bytes sha256 %s' % (os.path.getsize(OUT_JP), sha(OUT_JP)))
shutil.rmtree(TREE, ignore_errors=True)
shutil.rmtree('_v_114_tree', ignore_errors=True); shutil.rmtree('_v_115_tree', ignore_errors=True)
log('done')
