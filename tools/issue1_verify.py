"""Independent read-back of the 1.0.14 base builds against the shipped 1.0.13.

    python issue1_verify.py [en|jp]     (default en)

Base: TMD version 1.0.14; contents 1 and 2 identical to the previous CIA; content 0 identical outside
the romfs and its hash fields (code and exefs untouched); romfs region == new_114[_jpv].romfs; the
extracted romfs tree differs from the previous build's tree in exactly title/title.narc and the two
scene scripts whose bubble size codes were raised.
DLC: unchanged in this build, so only checked to still hash as the published 0.2.8 files.
"""
import os, sys, struct, hashlib, shutil, subprocess, filecmp
TGAA_ROOT = os.environ.get('TGAA_ROOT') or sys.exit('set TGAA_ROOT to the TGAA project folder')
sys.path.insert(0, os.path.join(TGAA_ROOT, 'testimony_pipeline'))
import ncch
from cia import Cia

ED = sys.argv[1] if len(sys.argv) > 1 else 'en'
R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
W = os.path.join(R, 'work'); os.chdir(W)
TOOL = os.path.join(TGAA_ROOT, '3dstool', '3dstool.exe')
MU = 0x200
if ED == 'en':
    OLD = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-EN-voices-1.0.13.cia')
    NEW = os.path.join(R, r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.14.cia')
    ROMFS = 'new_114.romfs'
else:
    OLD = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-JP-voices-1.0.13.cia')
    NEW = os.path.join(R, r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.14.cia')
    ROMFS = 'new_114_jpv.romfs'
EXPECT = {os.path.join('title', 'title.narc'),
          os.path.join('script', 'adventure', 'chapter01', 'manzai_script_chapter01.narc'),
          os.path.join('script', 'adventure', 'general', 'manzai_script_general.narc')}
fails = []


def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)
    if not cond:
        fails.append(msg)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(*a):
    r = subprocess.run([TOOL] + list(a), capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('3dstool failed: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))


def tree_diff(a, b):
    out = []
    fa = {os.path.relpath(os.path.join(dp, f), a) for dp, _, fs in os.walk(a) for f in fs}
    fb = {os.path.relpath(os.path.join(dp, f), b) for dp, _, fs in os.walk(b) for f in fs}
    for rel in sorted(fa | fb):
        pa, pb = os.path.join(a, rel), os.path.join(b, rel)
        if not (os.path.exists(pa) and os.path.exists(pb)) or not filecmp.cmp(pa, pb, shallow=False):
            out.append(rel)
    return out


# ---------------- base ----------------
old, new = Cia(OLD), Cia(NEW)
print('%s: old version %d.%d.%d, new version %d.%d.%d' % ((ED,) + old.version() + new.version()))
check(new.version() == (1, 0, 14), 'new base TMD version is 1.0.14')
check(old.count == new.count == 3, 'both base CIAs have 3 contents')
check(old.contents[1] == new.contents[1] and old.contents[2] == new.contents[2], 'contents 1 and 2 byte-identical to the previous build')
c0o, c0n = old.contents[0], new.contents[0]
fo, fn_ = ncch.fields(c0o), ncch.fields(c0n)
ok_n, _ = ncch.verify(c0n)
check(ok_n, 'new content 0 romfs superblock hash verifies')
romfs_n = c0n[fn_['romfs_off'] * MU: fn_['romfs_off'] * MU + fn_['romfs_size'] * MU]
want = open(ROMFS, 'rb').read()
check(romfs_n == want, 'new content 0 romfs region == %s (%d bytes)' % (ROMFS, len(want)))
head_n = bytearray(c0n[:fn_['romfs_off'] * MU]); head_o = bytearray(c0o[:fo['romfs_off'] * MU])
for h in (head_n, head_o):
    h[0x104:0x108] = b'\0' * 4; h[0x1B4:0x1BC] = b'\0' * 8; h[0x1C0:0x200] = b'\0' * 64
check(bytes(head_n) == bytes(head_o), 'new content 0 outside romfs/hash fields == previous (code and exefs untouched)')
romfs_o = c0o[fo['romfs_off'] * MU: fo['romfs_off'] * MU + fo['romfs_size'] * MU]
for name, blob in (('_v_old.romfs', romfs_o), ('_v_new.romfs', romfs_n)):
    open(name, 'wb').write(blob)
    d = name[:-6] + '_tree'; shutil.rmtree(d, ignore_errors=True)
    run('-xtf', 'romfs', name, '--romfs-dir', d)
d = tree_diff('_v_old_tree', '_v_new_tree')
check(set(d) == EXPECT, 'romfs trees differ in exactly the title stamp and the two scene scripts (got %s)' % d)
for rel in sorted(EXPECT):
    check(filecmp.cmp(os.path.join('_v_new_tree', rel), os.path.join('patch', 'romfs', rel), shallow=False), '%s in the new tree == patch/romfs copy' % rel)
print('new base CIA %d bytes sha256 %s' % (os.path.getsize(NEW), sha(open(NEW, 'rb').read())))
for n in ('_v_old.romfs', '_v_new.romfs'):
    os.remove(n)
shutil.rmtree('_v_old_tree'); shutil.rmtree('_v_new_tree')

# ---------------- DLC ----------------
# 1.0.14 does not touch the DLC; check only that the shipped 0.2.8 CIAs are still the published bytes.
import filecmp as _f
for p in ((r'Final\_CURRENT\PuyoPuyoTetris-DLC-0.2.8.cia', 'de833dede4482b83f24e413dc9f3801c66de6f3e6315d2fd4e4449d29e51971c'),
          (r'Final\_CURRENT\PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia', 'b742243d81c2b7b2ef91d27c5c6570291b5b4cbcdfd3e3c6d847aab33ad00475')):
    check(sha(open(os.path.join(R, p[0]), 'rb').read()) == p[1], '%s is unchanged (DLC 0.2.8 stays published as is)' % os.path.basename(p[0]))

print()
print('RESULT:', 'PASS, 0 failures' if not fails else 'FAIL: %s' % fails)
