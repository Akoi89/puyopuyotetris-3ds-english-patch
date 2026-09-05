"""Rebuild the DLC CIA with the translated contents.

    python build_dlc_cia.py <shell.cia> <out.cia>

The DLC's contents are NCCH-encrypted CFAs, so the in-place splice used for the
base game would write plaintext into ciphertext. Each touched content goes
through 3dstool instead, which decrypts on extract and re-encrypts on build:

    3dstool -xtf cfa  content --header h --romfs plain.romfs
    3dstool -xtf romfs plain.romfs --romfs-dir tree      (overlay patch_dlc2 here)
    3dstool -ctf romfs new.romfs --romfs-dir tree
    3dstool -ctf cfa  new.cfa --header h --romfs new.romfs

Null test first: content 0010 is round-tripped untouched and must come back
byte-identical before anything is modified.
"""
import os, sys, shutil, subprocess, hashlib
sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
from cia import Cia

TOOL = r'G:\Claude\TGAA 1-2\3dstool\3dstool.exe'
PATCH = 'patch_dlc2'
WORK = 'dlc_build'
shell, out = sys.argv[1], sys.argv[2]


def run(*a):
    r = subprocess.run([TOOL] + list(a), capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('3dstool failed: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))


def roundtrip(idx, blob, overlay=None):
    d = os.path.join(WORK, '%04x' % idx)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    src = os.path.join(d, 'orig.cfa')
    open(src, 'wb').write(blob)
    run('-xtf', 'cfa', src, '--header', os.path.join(d, 'h.bin'), '--romfs', os.path.join(d, 'r.bin'))
    tree = os.path.join(d, 'tree')
    run('-xtf', 'romfs', os.path.join(d, 'r.bin'), '--romfs-dir', tree)
    if overlay:
        n = 0
        for dp, dn, fn in os.walk(overlay):
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), overlay)
                dst = os.path.join(tree, rel)
                assert os.path.exists(dst), 'patched file not in content: ' + rel
                shutil.copyfile(os.path.join(dp, f), dst)
                n += 1
        print('   content %04x: %d files overlaid' % (idx, n))
    run('-ctf', 'romfs', os.path.join(d, 'new.romfs'), '--romfs-dir', tree)
    run('-ctf', 'cfa', os.path.join(d, 'new.cfa'), '--header', os.path.join(d, 'h.bin'),
        '--romfs', os.path.join(d, 'new.romfs'))
    return open(os.path.join(d, 'new.cfa'), 'rb').read()


print('reading shell CIA ...')
c = Cia(shell)
print('  %d contents' % c.count)

touched = sorted(int(x, 16) for x in os.listdir(PATCH))
print('contents to rebuild:', ['%04x' % i for i in touched])

# --- null test on the biggest real content, untouched ------------------------------
big = 0x12
rt = roundtrip(big, c.contents[big])
same = rt == c.contents[big]
print('NULL TEST content %04x untouched round-trip byte-identical: %s' % (big, same))
if not same:
    raise SystemExit('stop: 3dstool does not reproduce this content')

# --- rebuild every touched content ---------------------------------------------------
replace = {}
for idx in touched:
    new = roundtrip(idx, c.contents[idx], os.path.join(PATCH, '%04x' % idx))
    replace[idx] = new
    print('   content %04x: %d -> %d bytes' % (idx, len(c.contents[idx]), len(new)))

print('writing %s ...' % out)
chk = Cia(shell).write(out, replace=replace, version=(0, 2, 3))
print('done: %d contents, %.1f MB' % (chk.count, sum(len(b) for b in chk.contents) / 1048576))

# --- verify: extract a rebuilt content back out of the finished CIA -----------------
v = roundtrip(0x10, chk.contents[0x10])   # extracts fine == decrypts fine
tree = os.path.join(WORK, '0010', 'tree')
bad = 0
for dp, dn, fn in os.walk(os.path.join(PATCH, '0010')):
    for f in fn:
        rel = os.path.relpath(os.path.join(dp, f), os.path.join(PATCH, '0010'))
        if open(os.path.join(dp, f), 'rb').read() != open(os.path.join(tree, rel), 'rb').read():
            bad += 1
print('content 0010 read back from the new CIA: patched files match = %s' % (bad == 0))
