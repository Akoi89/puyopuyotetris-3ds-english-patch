"""Issue #1 fix build, base game 1.0.13 (English voices).

    python issue1_build_base.py            (log: build_base_113.out)

1. stamp_title.py "ENG 1.0.13" with the 1.0.12 title.narc as the box reference (copied aside first)
2. copy romfs_110_tree -> romfs_113_tree, overlay patch/romfs, 3dstool -ctf -> new_113.romfs
3. extract new_112.romfs and new_113.romfs, list every differing file (expected: exactly
   title/title.narc and tenp/party/party2p/party2p.narc)
4. build_cia.py <fan .standard.cia shell> cci_banner.cci new_113.romfs Final/_new/PuyoPuyoTetris-EN-voices-1.0.13.cia 1.0.13
Nothing published, nothing in Final/_CURRENT touched.
"""
import os, sys, shutil, subprocess, hashlib, time, filecmp

TGAA_ROOT = os.environ.get('TGAA_ROOT') or sys.exit('set TGAA_ROOT to the TGAA project folder')
TOOL = os.path.join(TGAA_ROOT, '3dstool', '3dstool.exe')
R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
SHELL = os.path.join(R, '0004000000101200 Puyopuyo Tetris (English Translated, English Voices) (CTR-P-BPTJ) (v0.0.0) (J).standard.cia')
OUT = os.path.join(R, 'Final', '_new', 'PuyoPuyoTetris-EN-voices-1.0.13.cia')
VER = '1.0.13'
t0 = time.time()


def log(*a):
    print('[%5.0fs]' % (time.time() - t0), *a, flush=True)


def run(*a, **k):
    r = subprocess.run(list(a), capture_output=True, text=True, **k)
    if r.returncode:
        raise SystemExit('FAILED: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))
    return r.stdout


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


# 1. stamp
ref = 'title_1012_stamped.narc'
if not os.path.exists(ref):
    shutil.copy2('patch/romfs/title/title.narc', ref)
log(run(sys.executable, 'stamp_title.py', 'ENG ' + VER, ref).strip())

# 2. romfs
TREE = 'romfs_113_tree'
if os.path.exists(TREE):
    shutil.rmtree(TREE)
shutil.copytree('romfs_110_tree', TREE)
log('copied romfs_110_tree')
n = 0
for dp, dn, fn in os.walk('patch/romfs'):
    for f in fn:
        rel = os.path.relpath(os.path.join(dp, f), 'patch/romfs')
        dst = os.path.join(TREE, rel)
        assert os.path.exists(dst), 'overlay file not in tree: ' + rel
        shutil.copyfile(os.path.join(dp, f), dst); n += 1
log('overlaid %d files' % n)
run(TOOL, '-ctf', 'romfs', 'new_113.romfs', '--romfs-dir', TREE)
log('new_113.romfs %d bytes sha256 %s' % (os.path.getsize('new_113.romfs'), sha('new_113.romfs')))

# 3. diff against 1.0.12
for name in ('112', '113'):
    d = '_v_%s_tree' % name
    if os.path.exists(d):
        shutil.rmtree(d)
    run(TOOL, '-xtf', 'romfs', 'new_%s.romfs' % name, '--romfs-dir', d)
log('extracted both romfs images')
diff = []
for dp, dn, fn in os.walk('_v_113_tree'):
    for f in fn:
        p = os.path.join(dp, f); rel = os.path.relpath(p, '_v_113_tree')
        q = os.path.join('_v_112_tree', rel)
        if not os.path.exists(q) or not filecmp.cmp(p, q, shallow=False):
            diff.append(rel)
missing = [os.path.relpath(os.path.join(dp, f), '_v_112_tree') for dp, dn, fn in os.walk('_v_112_tree') for f in fn
           if not os.path.exists(os.path.join('_v_113_tree', os.path.relpath(os.path.join(dp, f), '_v_112_tree')))]
log('files differing 1.0.12 -> 1.0.13: %d %s   missing in 1.0.13: %d' % (len(diff), diff, len(missing)))
expected = {os.path.join('title', 'title.narc'), os.path.join('tenp', 'party', 'party2p', 'party2p.narc')}
if set(diff) != expected or missing:
    raise SystemExit('STOP: unexpected romfs differences')

# 4. CIA
os.makedirs(os.path.dirname(OUT), exist_ok=True)
log(run(sys.executable, 'build_cia.py', SHELL, 'cci_banner.cci', 'new_113.romfs', OUT, VER))
log('CIA %s %d bytes sha256 %s' % (OUT, os.path.getsize(OUT), sha(OUT)))
log('done')
