"""Assemble the Japanese-voice 1.0.12 base romfs.

1. copy romfs_110_tree (the 1.0.11 tree) -> romfs_jpv_tree
2. overlay all of patch/romfs (the 1.0.12 overlay, 101 files)
3. NULL TEST: repack must equal new_112.romfs byte for byte (proves the recipe)
4. replace sound/ with tr_jpvoice/sound (== jp_orig/sound + the fan's one extra stream)
5. repack -> new_112_jpv.romfs
"""
import os, shutil, subprocess, hashlib, sys, time

TOOL = r'G:\Claude\TGAA 1-2\3dstool\3dstool.exe'
SRC = 'romfs_110_tree'
TREE = 'romfs_jpv_tree'
OVERLAY = os.path.join('patch', 'romfs')
JPSOUND = os.path.join('tr_jpvoice', 'sound')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('FAILED: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))


t0 = time.time()
if os.path.exists(TREE):
    shutil.rmtree(TREE)
shutil.copytree(SRC, TREE)
print('copied tree, %.0f s' % (time.time() - t0), flush=True)

n = 0
for dp, dn, fn in os.walk(OVERLAY):
    for f in fn:
        rel = os.path.relpath(os.path.join(dp, f), OVERLAY)
        dst = os.path.join(TREE, rel)
        assert os.path.exists(dst), 'overlay file not in tree: ' + rel
        shutil.copyfile(os.path.join(dp, f), dst)
        n += 1
print('overlaid %d files' % n, flush=True)

run(TOOL, '-ctf', 'romfs', 'chk_112_jpv.romfs', '--romfs-dir', TREE)
a, b = sha('chk_112_jpv.romfs'), sha('new_112.romfs')
print('NULL TEST repack == new_112.romfs:', a == b, a[:16], b[:16], flush=True)
if a != b:
    raise SystemExit('stop: recipe does not reproduce the shipped 1.0.12 romfs')
os.remove('chk_112_jpv.romfs')

shutil.rmtree(os.path.join(TREE, 'sound'))
shutil.copytree(JPSOUND, os.path.join(TREE, 'sound'))
cnt = sum(len(f) for _, _, f in os.walk(TREE))
print('sound/ replaced from tr_jpvoice; tree now %d files' % cnt, flush=True)

run(TOOL, '-ctf', 'romfs', 'new_112_jpv.romfs', '--romfs-dir', TREE)
print('new_112_jpv.romfs %d bytes sha256 %s' % (os.path.getsize('new_112_jpv.romfs'), sha('new_112_jpv.romfs')))
print('total %.0f s' % (time.time() - t0))
