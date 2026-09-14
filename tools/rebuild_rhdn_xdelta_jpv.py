# -*- coding: utf-8 -*-
r"""xdelta patches for the Japanese-voice edition (1.0.12 / DLC 0.2.7), same method as
rebuild_rhdn_xdelta_1012.py: -a (no source armor) against a header-scrubbed copy of the
source, proven on the real source and two perturbed copies. Adds -A (no application
header) so no local path text lands in the patch (the TGAA finding of 2026-09-11).

Usage: python rebuild_rhdn_xdelta_jpv.py   (writes into work\rhdn_xdelta_jpv\)
"""
import hashlib, os, shutil, struct, subprocess, zlib

R = r'G:\Claude\PuyoPuyo'
XD = r'G:\Claude\TGAA 1-2\patches\xdelta3.exe'
OUT = os.path.join(R, 'work', 'rhdn_xdelta_jpv')
JOBS = [
    dict(name='PuyoPuyoTetris-JP-voices-1.0.12.xdelta',
         src=os.path.join(R, '0004000000101200 Jap-ORG-Base (CTR-P-BPTJ) (v0.1.0) (J).piratelegit-decrypted.cci'),
         tgt=os.path.join(R, r'Final\_new\PuyoPuyoTetris-JP-voices-1.0.12.cia'),
         scrub=(0, 0x4000), volatile=(0x1010, 0x2C)),
    dict(name='PuyoPuyoTetris-DLC-JP-voices-0.2.7.xdelta',
         src=os.path.join(R, r'work\dlc_shell.cia'),
         tgt=os.path.join(R, r'Final\_new\PuyoPuyoTetris-DLC-JP-voices-0.2.7.cia'),
         scrub=None, volatile=None),   # computed from the CIA header below
]


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
    for j in JOBS:
        scrub, vol = j['scrub'], j['volatile']
        if scrub is None:
            scrub, vol = cia_regions(j['src'])
        enc = os.path.join(tmp, 'enc_src.bin'); copy_with_random(j['src'], enc, *scrub)
        xd = os.path.join(OUT, j['name'])
        run(XD, '-e', '-f', '-a', '-A', '-9', '-S', 'djw', '-B', '1073741824', '-s', enc, j['tgt'], xd)
        os.remove(enc)
        hdr = open(xd, 'rb').read(64)
        assert hdr[:3] == b'\xd6\xc3\xc4' and (hdr[4] & 0x04) == 0, 'app header flag (bit 2) still set: %s' % hdr[:8].hex()
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
        print('%-44s %11d bytes  sha256 %s  crc32 %s  (no app header; real + 2 perturbed sources OK)' % (j['name'], n, s, c))
    shutil.rmtree(tmp)


if __name__ == '__main__':
    main()
