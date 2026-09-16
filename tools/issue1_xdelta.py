# -*- coding: utf-8 -*-
"""Re-encode the release xdelta patches for 1.0.13 / DLC 0.2.8 (both editions), the proven way:
-a (no source armor) and -A (no app header with the builder's path), against a source whose whole header
region is random, then applied back on the real source plus two randomly perturbed copies.

    python issue1_xdelta.py en    -> work/rhdn_xdelta_v5/        (EN voices 1.0.13 + DLC 0.2.8)
    python issue1_xdelta.py jp    -> work/rhdn_xdelta_jpv_113/   (JP voices 1.0.13 + DLC JP voices 0.2.8)
"""
import os, sys, shutil, subprocess, hashlib, zlib, struct

R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
TGAA_ROOT = os.environ.get('TGAA_ROOT') or sys.exit('set TGAA_ROOT to the TGAA project folder')
XD = os.path.join(TGAA_ROOT, 'patches', 'xdelta3.exe')
ED = sys.argv[1]
BASE_SRC = os.path.join(R, '0004000000101200 Jap-ORG-Base (CTR-P-BPTJ) (v0.1.0) (J).piratelegit-decrypted.cci')
if ED == 'en':
    OUT = os.path.join(R, 'work', 'rhdn_xdelta_v5')
    JOBS = [dict(name='PuyoPuyoTetris-EN-voices-1.0.13.xdelta', src=BASE_SRC,
                 tgt=os.path.join(R, r'Final\_new\PuyoPuyoTetris-EN-voices-1.0.13.cia'), scrub=(0, 0x4000), volatile=(0x1010, 0x2C)),
            dict(name='PuyoPuyoTetris-DLC-0.2.8.xdelta', src=os.path.join(R, r'work\dlc_shell.cia'),
                 tgt=os.path.join(R, r'Final\_new\PuyoPuyoTetris-DLC-0.2.8.cia'), scrub=None, volatile=None)]
else:
    OUT = os.path.join(R, 'work', 'rhdn_xdelta_jpv_113')
    JOBS = [dict(name='PuyoPuyoTetris-JP-voices-1.0.13.xdelta', src=BASE_SRC,
                 tgt=os.path.join(R, r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.13.cia'), scrub=(0, 0x4000), volatile=(0x1010, 0x2C)),
            dict(name='PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta', src=os.path.join(R, r'work\dlc_shell.cia'),
                 tgt=os.path.join(R, r'Final\_new\PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia'), scrub=None, volatile=None)]


def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('FAILED: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))


def digest(p):
    h = hashlib.sha256(); c = 0; n = 0
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b); c = zlib.crc32(b, c); n += len(b)
    return h.hexdigest(), '%08X' % (c & 0xffffffff), n


def cia_regions(p):
    h = open(p, 'rb').read(0x20)
    hsz, _, _, csz, tsz, msz = struct.unpack_from('<IHHIII', h, 0)
    a = lambda x: (x + 63) // 64 * 64
    tik = a(hsz) + a(csz)
    return (0, tik + a(tsz) + a(msz)), (tik, tsz)


def copy_with_random(src, dst, off, n):
    shutil.copyfile(src, dst)
    with open(dst, 'r+b') as f:
        f.seek(off); f.write(os.urandom(n))


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, '_tmp'); os.makedirs(tmp, exist_ok=True)
    only = sys.argv[2] if len(sys.argv) > 2 else ''      # optional substring filter, e.g. "DLC"
    for j in JOBS:
        if only and only not in j['name']:
            continue
        scrub, vol = j['scrub'], j['volatile']
        if scrub is None:
            scrub, vol = cia_regions(j['src'])
        enc = os.path.join(tmp, 'enc_src.bin'); copy_with_random(j['src'], enc, *scrub)
        xd = os.path.join(OUT, j['name'])
        run(XD, '-e', '-f', '-a', '-A', '-9', '-S', 'djw', '-B', '1073741824', '-s', enc, j['tgt'], xd)
        os.remove(enc)
        head = open(xd, 'rb').read(64)
        assert (head[4] & 0x04) == 0, 'app header flag set: %s' % head[:8].hex()   # bit0 = djw secondary compression, expected
        want = digest(j['tgt'])[0]
        chk = os.path.join(tmp, 'applied.bin')
        run(XD, '-d', '-f', '-B', '1073741824', '-s', j['src'], xd, chk)
        assert digest(chk)[0] == want, 'does not reproduce the target from the real source'
        for i in range(2):
            pert = os.path.join(tmp, 'pert.bin'); copy_with_random(j['src'], pert, *vol)
            run(XD, '-d', '-f', '-B', '1073741824', '-s', pert, xd, chk)
            assert digest(chk)[0] == want, 'FAILS on a perturbed source (round %d)' % i
            os.remove(pert)
        os.remove(chk)
        s, c, n = digest(xd)
        blob = open(xd, 'rb').read()
        needles = (b'G:' + chr(92).encode() + b'Claude', b'Users' + chr(92).encode() + os.environ.get('USERNAME', 'nobody').encode(), b'scratch-workspaces')
        assert not [n for n in needles if n in blob], 'local path inside the patch'
        print('%-44s %11d bytes  sha256 %s  crc32 %s  (real + 2 perturbed sources OK, no local path)' % (j['name'], n, s, c), flush=True)
    shutil.rmtree(tmp)


if __name__ == '__main__':
    main()
