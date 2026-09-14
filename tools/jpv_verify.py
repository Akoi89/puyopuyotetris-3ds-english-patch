"""Independent read-back of the two Japanese-voice CIAs against the shipped English ones.

Base: contents 1 and 2 identical to the EN 1.0.12 CIA; content 0 identical outside the
romfs + its superblock hash + the ExeFS banner; romfs region == new_112_jpv.romfs; banner
== banner_jpv.bin; the extracted romfs tree differs from the EN tree only under sound/,
and sound/ == tr_jpvoice/sound. TMD version 1.0.12.
DLC: only contents 0010/0011/0012 differ from the EN 0.2.7 CIA; inside each, every file
equals the Japanese shell except the 12 data files, which equal patch_dlc2_jpv.
"""
import os, sys, struct, hashlib, shutil, subprocess, filecmp
sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
import ncch
from cia import Cia

R = r'G:\Claude\PuyoPuyo'
W = os.path.join(R, 'work'); os.chdir(W)
TOOL = r'G:\Claude\TGAA 1-2\3dstool\3dstool.exe'
MU = 0x200
EN = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-EN-voices-1.0.12.cia')
JP = os.path.join(R, r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.12.cia')
EN_DLC = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-DLC-0.2.7.cia')
JP_DLC = os.path.join(R, r'Final\_new\PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia')
fails = []


def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond:
        fails.append(msg)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(*a):
    r = subprocess.run([TOOL] + list(a), capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('3dstool failed: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))


def tree_diff(a, b):
    """relative paths present in either tree whose bytes differ or that are missing on one side"""
    out = []
    fa = {os.path.relpath(os.path.join(dp, f), a) for dp, _, fs in os.walk(a) for f in fs}
    fb = {os.path.relpath(os.path.join(dp, f), b) for dp, _, fs in os.walk(b) for f in fs}
    for rel in sorted(fa | fb):
        pa, pb = os.path.join(a, rel), os.path.join(b, rel)
        if not (os.path.exists(pa) and os.path.exists(pb)) or not filecmp.cmp(pa, pb, shallow=False):
            out.append(rel)
    return out


# ---------------- base ----------------
en, jp = Cia(EN), Cia(JP)
print('EN version %d.%d.%d, JP version %d.%d.%d' % (en.version() + jp.version()))
check(jp.version() == (1, 0, 12), 'JP base TMD version is 1.0.12')
check(en.count == jp.count == 3, 'both base CIAs have 3 contents')
check(en.contents[1] == jp.contents[1] and en.contents[2] == jp.contents[2], 'contents 1 and 2 byte-identical to EN')
c0e, c0j = en.contents[0], jp.contents[0]
fe, fj = ncch.fields(c0e), ncch.fields(c0j)
ok_j, _ = ncch.verify(c0j)
check(ok_j, 'JP content 0 romfs superblock hash verifies')
romfs_j = c0j[fj['romfs_off'] * MU: fj['romfs_off'] * MU + fj['romfs_size'] * MU]
want = open('new_112_jpv.romfs', 'rb').read()
check(romfs_j == want, 'JP content 0 romfs region == new_112_jpv.romfs (%d bytes)' % len(want))
# everything before the romfs must match EN except the exefs banner and the hash fields
g = lambda d, o: struct.unpack_from('<I', d, o)[0]
ex_off, ex_size = g(c0j, 0x1A0) * MU, g(c0j, 0x1A4) * MU
head_j = bytearray(c0j[:fj['romfs_off'] * MU]); head_e = bytearray(c0e[:fe['romfs_off'] * MU])
# neutralise the fields that legitimately differ: content size (0x104), romfs size (0x1B4), hash region (0x1B8),
# romfs superblock hash (0x1E0..0x200), exefs superblock hash (0x1C0..0x1E0), and the whole exefs region
for h in (head_j, head_e):
    h[0x104:0x108] = b'\0' * 4; h[0x1B4:0x1BC] = b'\0' * 8; h[0x1C0:0x200] = b'\0' * 64
    h[ex_off:ex_off + ex_size] = b'\0' * ex_size
check(bytes(head_j) == bytes(head_e), 'JP content 0 outside romfs/exefs/hash fields == EN (code untouched)')
# exefs: banner replaced, everything else identical
ex_j, ex_e = c0j[ex_off:ex_off + ex_size], c0e[ex_off:ex_off + ex_size]
def exefs_files(ex):
    out = {}
    for i in range(10):
        name = ex[i * 16:i * 16 + 8].rstrip(b'\0'); off, size = struct.unpack_from('<II', ex, i * 16 + 8)
        if name:
            out[name] = ex[0x200 + off:0x200 + off + size]
    return out
xj, xe = exefs_files(ex_j), exefs_files(ex_e)
check(xj[b'banner'] == open('banner_jpv.bin', 'rb').read(), 'JP exefs banner == banner_jpv.bin')
check(all(xj[k] == xe[k] for k in xe if k != b'banner') and set(xj) == set(xe), 'JP exefs other files == EN (%s)' % ', '.join(k.decode() for k in xe))
# tree-level: extract both romfs and diff
romfs_e = c0e[fe['romfs_off'] * MU: fe['romfs_off'] * MU + fe['romfs_size'] * MU]
for name, blob in (('_v_en.romfs', romfs_e), ('_v_jp.romfs', romfs_j)):
    open(name, 'wb').write(blob)
    d = name[:-6] + '_tree'; shutil.rmtree(d, ignore_errors=True)
    run('-xtf', 'romfs', name, '--romfs-dir', d)
d = tree_diff('_v_en_tree', '_v_jp_tree')
print('  files differing between EN and JP romfs trees: %d' % len(d))
check(d and all(x.startswith('sound' + os.sep) for x in d), 'EN vs JP trees differ only under sound/')
check(tree_diff(os.path.join('_v_jp_tree', 'sound'), os.path.join('tr_jpvoice', 'sound')) == [], 'JP tree sound/ == tr_jpvoice/sound')
check(tree_diff(os.path.join('_v_jp_tree', 'sound'), os.path.join('jp_orig', 'sound')) == [os.path.join('stream', 'MZV_07_01_1_039.dspadpcm.bcstm')],
      'JP tree sound/ == jp_orig/sound except the fan tree\'s one extra stream MZV_07_01_1_039')
nonsound = [x for x in tree_diff('_v_jp_tree', 'romfs_110_tree') if not x.startswith('sound' + os.sep)]
# romfs_110_tree IS the 1.0.11 tree, so only the overlay files 1.0.12 changed may differ outside sound/
changed_1012 = sorted(rel for rel in (os.path.relpath(os.path.join(dp, f), os.path.join('patch', 'romfs')) for dp, _, fs in os.walk(os.path.join('patch', 'romfs')) for f in fs)
                      if not rel.startswith('sound') and not filecmp.cmp(os.path.join('patch', 'romfs', rel), os.path.join('romfs_110_tree', rel), shallow=False))
check(sorted(nonsound) == changed_1012 and len(changed_1012) == 3,
      'JP tree vs the 1.0.11 tree differs outside sound/ in exactly the 3 archives 1.0.12 changed: %s' % ', '.join(changed_1012))
print('JP base CIA %d bytes sha256 %s' % (os.path.getsize(JP), sha(open(JP, 'rb').read())))

# ---------------- DLC ----------------
de, dj, sh = Cia(EN_DLC), Cia(JP_DLC), Cia('dlc_shell.cia')
check(dj.version() == (0, 2, 7), 'JP DLC TMD version is 0.2.7')
check(de.count == dj.count == sh.count == 701, 'DLC CIAs have 701 contents')
diff_idx = [i for i in range(de.count) if de.contents[i] != dj.contents[i]]
check(diff_idx == [0x10, 0x11, 0x12], 'JP DLC differs from EN DLC only in contents 0010/0011/0012 (got %s)' % ['%04x' % i for i in diff_idx])
same_shell = [i for i in range(sh.count) if sh.contents[i] == dj.contents[i]]
print('  JP DLC contents identical to the Japanese shell: %d of 701' % len(same_shell))
for idx in (0x10, 0x11, 0x12):
    for tag, c in (('jp', dj), ('sh', sh)):
        d = os.path.join('_v_dlc', '%04x_%s' % (idx, tag)); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        open(os.path.join(d, 'c.cfa'), 'wb').write(c.contents[idx])
        run('-xtf', 'cfa', os.path.join(d, 'c.cfa'), '--header', os.path.join(d, 'h.bin'), '--romfs', os.path.join(d, 'r.bin'))
        run('-xtf', 'romfs', os.path.join(d, 'r.bin'), '--romfs-dir', os.path.join(d, 'tree'))
    dd = tree_diff(os.path.join('_v_dlc', '%04x_jp' % idx, 'tree'), os.path.join('_v_dlc', '%04x_sh' % idx, 'tree'))
    ov = os.path.join('patch_dlc2_jpv', '%04x' % idx)
    ovf = sorted(os.path.relpath(os.path.join(dp, f), ov) for dp, _, fs in os.walk(ov) for f in fs)
    check(sorted(dd) == ovf, 'content %04x: differs from the Japanese shell in exactly the %d overlay data files, no voice clip touched' % (idx, len(ovf)))
    check(all(filecmp.cmp(os.path.join(ov, f), os.path.join('_v_dlc', '%04x_jp' % idx, 'tree', f), shallow=False) for f in ovf), 'content %04x: overlay files read back byte-identical' % idx)
    nvoice = len([f for f in dd if 'adv_sound' in f])
    check(nvoice == 0, 'content %04x: zero adv_sound files differ from the shell' % idx)
print('JP DLC CIA %d bytes sha256 %s' % (os.path.getsize(JP_DLC), sha(open(JP_DLC, 'rb').read())))

print()
print('RESULT:', 'PASS, 0 failures' if not fails else 'FAIL: %s' % fails)
