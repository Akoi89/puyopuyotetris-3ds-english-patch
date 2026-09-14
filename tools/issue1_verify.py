"""Independent read-back of the 1.0.13 / DLC 0.2.8 builds against the shipped 1.0.12 / 0.2.7.

    python issue1_verify.py [en|jp]     (default en)

Base: TMD version 1.0.13; contents 1 and 2 identical to the previous CIA; content 0 identical outside
the romfs and its hash fields (exefs untouched); romfs region == new_113[_jpv].romfs; the extracted
romfs tree differs from the previous build's tree in exactly title/title.narc and
tenp/party/party2p/party2p.narc (jp: same, both trees carry the JP sound).
DLC: only contents 0010/0011/0012 differ from the previous DLC CIA; inside each, the tree differs in
exactly data/chapterNNJapanese.mtx, which equals the overlay file.
"""
import os, sys, struct, hashlib, shutil, subprocess, filecmp
sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
import ncch
from cia import Cia

ED = sys.argv[1] if len(sys.argv) > 1 else 'en'
R = r'G:\Claude\PuyoPuyo'
W = os.path.join(R, 'work'); os.chdir(W)
TOOL = r'G:\Claude\TGAA 1-2\3dstool\3dstool.exe'
MU = 0x200
if ED == 'en':
    OLD = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-EN-voices-1.0.12.cia')
    NEW = os.path.join(R, r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.13.cia')
    OLD_DLC = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-DLC-0.2.7.cia')
    NEW_DLC = os.path.join(R, r'Final\_new\PuyoPuyoTetris-DLC-0.2.8.cia')
    ROMFS = 'new_113.romfs'; OVERLAY = 'patch_dlc2'
else:
    OLD = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-JP-voices-1.0.12.cia')
    NEW = os.path.join(R, r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.13.cia')
    OLD_DLC = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia')
    NEW_DLC = os.path.join(R, r'Final\_new\PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia')
    ROMFS = 'new_113_jpv.romfs'; OVERLAY = 'patch_dlc2_jpv'
EXPECT = {os.path.join('title', 'title.narc'), os.path.join('tenp', 'party', 'party2p', 'party2p.narc')}
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
check(new.version() == (1, 0, 13), 'new base TMD version is 1.0.13')
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
check(set(d) == EXPECT, 'romfs trees differ in exactly title.narc and party2p.narc (got %s)' % d)
for rel in sorted(EXPECT):
    check(filecmp.cmp(os.path.join('_v_new_tree', rel), os.path.join('patch', 'romfs', rel), shallow=False), '%s in the new tree == patch/romfs copy' % rel)
print('new base CIA %d bytes sha256 %s' % (os.path.getsize(NEW), sha(open(NEW, 'rb').read())))
for n in ('_v_old.romfs', '_v_new.romfs'):
    os.remove(n)
shutil.rmtree('_v_old_tree'); shutil.rmtree('_v_new_tree')

# ---------------- DLC ----------------
do, dn = Cia(OLD_DLC), Cia(NEW_DLC)
check(dn.version() == (0, 2, 8), 'new DLC TMD version is 0.2.8')
check(do.count == dn.count == 701, 'DLC CIAs have 701 contents')
diff_idx = [i for i in range(do.count) if do.contents[i] != dn.contents[i]]
check(diff_idx == [0x10, 0x11, 0x12], 'new DLC differs from the previous only in contents 0010/0011/0012 (got %s)' % ['%04x' % i for i in diff_idx])
for idx, ch in ((0x10, '08'), (0x11, '09'), (0x12, '10')):
    for tag, c in (('old', do), ('new', dn)):
        d = os.path.join('_v_dlc', '%04x_%s' % (idx, tag)); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        open(os.path.join(d, 'c.cfa'), 'wb').write(c.contents[idx])
        run('-xtf', 'cfa', os.path.join(d, 'c.cfa'), '--header', os.path.join(d, 'h.bin'), '--romfs', os.path.join(d, 'r.bin'))
        run('-xtf', 'romfs', os.path.join(d, 'r.bin'), '--romfs-dir', os.path.join(d, 'tree'))
    dd = tree_diff(os.path.join('_v_dlc', '%04x_old' % idx, 'tree'), os.path.join('_v_dlc', '%04x_new' % idx, 'tree'))
    mtxrel = os.path.join('data', 'chapter%sJapanese.mtx' % ch)
    scrrel = os.path.join('data', 'manzai_script_chapter%s.narc' % ch)
    check(sorted(dd) == sorted([mtxrel, scrrel]), 'content %04x: differs from the previous build in exactly the chapter table and the scene script (got %s)' % (idx, dd))
    for rel in (mtxrel, scrrel):
        check(filecmp.cmp(os.path.join('_v_dlc', '%04x_new' % idx, 'tree', rel), os.path.join(OVERLAY, '%04x' % idx, rel), shallow=False),
              'content %04x: %s read back == %s overlay file' % (idx, rel, OVERLAY))
shutil.rmtree('_v_dlc')
print('new DLC CIA %d bytes sha256 %s' % (os.path.getsize(NEW_DLC), sha(open(NEW_DLC, 'rb').read())))
print()
print('RESULT:', 'PASS, 0 failures' if not fails else 'FAIL: %s' % fails)
