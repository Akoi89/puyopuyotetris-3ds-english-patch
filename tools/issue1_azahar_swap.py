"""Put the staged 1.0.13 / DLC 0.2.8 English build into the user's Azahar install, or restore what was there.

Same method as _jpv_azahar_swap.py (azahar -i is a no-op at the same version, so the .app files and TMDs
are written directly). Azahar must be closed.

    python issue1_azahar_swap.py install    (backs up the installed files + the save first)
    python issue1_azahar_swap.py restore    (puts the newest backup back)
"""
import hashlib, os, shutil, sys, time
sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
from cia import Cia

R = r'G:\Claude\PuyoPuyo'
T = os.path.join(os.environ['APPDATA'], 'AzaharPlus', 'sdmc', 'Nintendo 3DS', '0' * 32, '0' * 32, 'title')
BASE_DIR = os.path.join(T, '00040000', '00101200', 'content')
DLC_DIR = os.path.join(T, '0004008c', '00101200', 'content')
SAVE_DIR = os.path.join(T, '00040000', '00101200', 'data')
BK_ROOT = os.path.join(R, 'work', '_azahar_swap_backup')
NEW = os.path.join(R, r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.13.cia')
NEW_DLC = os.path.join(R, r'Final\_new\PuyoPuyoTetris-DLC-0.2.8.cia')
OLD = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-EN-voices-1.0.12.cia')
OLD_DLC = os.path.join(R, r'Final\_CURRENT\PuyoPuyoTetris-DLC-0.2.7.cia')
DLC_IDX = (0x10, 0x11, 0x12)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fsha(p):
    return sha(open(p, 'rb').read())


def tmd_of(c):
    return bytes(c.raw[c.tmd:c.tmd + c.sizes['tmd']])


def targets():
    base_tmd = [f for f in os.listdir(BASE_DIR) if f.endswith('.tmd')]
    assert len(base_tmd) == 1, base_tmd
    t = {'base_app': os.path.join(BASE_DIR, '00000000.app'), 'base_tmd': os.path.join(BASE_DIR, base_tmd[0]),
         'dlc_tmd': os.path.join(DLC_DIR, '00000000.tmd')}
    for i in DLC_IDX:
        t['dlc_%02x' % i] = os.path.join(DLC_DIR, '00000000', '%08x.app' % i)
    for p in t.values():
        assert os.path.exists(p), p
    return t


def install():
    old, old_dlc, new, new_dlc = Cia(OLD), Cia(OLD_DLC), Cia(NEW), Cia(NEW_DLC)
    t = targets()
    assert fsha(t['base_app']) == sha(old.contents[0]), 'installed base .app is not the EN 1.0.12 content 0'
    assert fsha(t['base_tmd']) == sha(tmd_of(old)), 'installed base TMD is not the EN 1.0.12 TMD'
    for i in DLC_IDX:
        assert fsha(t['dlc_%02x' % i]) == sha(old_dlc.contents[i]), 'installed DLC %08x.app is not the EN 0.2.7 content' % i
    assert fsha(t['dlc_tmd']) == sha(tmd_of(old_dlc)), 'installed DLC TMD is not the EN 0.2.7 TMD'
    stamp = time.strftime('%Y%m%d_%H%M%S')
    bk = os.path.join(BK_ROOT, stamp); os.makedirs(bk)
    for k, p in t.items():
        shutil.copy2(p, os.path.join(bk, k + '__' + os.path.basename(p)))
    shutil.copytree(SAVE_DIR, os.path.join(bk, 'save_data'))
    open(os.path.join(bk, 'MANIFEST.txt'), 'w').write('\n'.join('%s\t%s' % (k, p) for k, p in t.items()))
    print('backed up EN 1.0.12 files + save to', bk)
    open(t['base_app'], 'wb').write(new.contents[0]); open(t['base_tmd'], 'wb').write(tmd_of(new))
    for i in DLC_IDX:
        open(t['dlc_%02x' % i], 'wb').write(new_dlc.contents[i])
    open(t['dlc_tmd'], 'wb').write(tmd_of(new_dlc))
    assert fsha(t['base_app']) == sha(new.contents[0]) and fsha(t['base_tmd']) == sha(tmd_of(new))
    for i in DLC_IDX:
        assert fsha(t['dlc_%02x' % i]) == sha(new_dlc.contents[i])
    assert fsha(t['dlc_tmd']) == sha(tmd_of(new_dlc))
    print('1.0.13 / 0.2.8 installed: base content 0 (%d bytes) + TMD, DLC contents 0010/0011/0012 + TMD, all read back OK' % len(new.contents[0]))


def restore():
    bks = sorted(os.listdir(BK_ROOT)); assert bks, 'no backup'
    bk = os.path.join(BK_ROOT, bks[-1])
    t = dict(l.split('\t') for l in open(os.path.join(bk, 'MANIFEST.txt')).read().splitlines())
    for k, p in t.items():
        src = os.path.join(bk, k + '__' + os.path.basename(p))
        shutil.copy2(src, p)
        assert fsha(p) == fsha(src)
    print('restored %d files from %s (save data left as is)' % (len(t), bk))


def update_dlc():
    """1.0.13 base already installed: refresh only the DLC contents from the rebuilt 0.2.8 CIA."""
    new, new_dlc = Cia(NEW), Cia(NEW_DLC)
    t = targets()
    assert fsha(t['base_app']) == sha(new.contents[0]), 'installed base .app is not the 1.0.13 content 0'
    for i in DLC_IDX:
        open(t['dlc_%02x' % i], 'wb').write(new_dlc.contents[i])
    open(t['dlc_tmd'], 'wb').write(tmd_of(new_dlc))
    for i in DLC_IDX:
        assert fsha(t['dlc_%02x' % i]) == sha(new_dlc.contents[i])
    assert fsha(t['dlc_tmd']) == sha(tmd_of(new_dlc))
    print('DLC 0.2.8 contents 0010/0011/0012 + TMD refreshed from the rebuilt CIA, read back OK')


if __name__ == '__main__':
    {'install': install, 'restore': restore, 'update': update_dlc}[sys.argv[1]]()
