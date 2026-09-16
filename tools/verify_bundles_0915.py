"""Re-verify the two rebuilt 1.0.14 bundles: apply every xdelta out of the zip
against the real source and hash-match the result against the shipped CIA."""
import os, sys, zipfile, hashlib, shutil, subprocess, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
W = os.path.join(R, 'work')
os.chdir(R)
BASE_SRC = os.path.join(R, '0004000000101200 Jap-ORG-Base (CTR-P-BPTJ) (v0.1.0) (J).piratelegit-decrypted.cci')
DLC_SRC = os.path.join(W, 'dlc_shell.cia')
CUR = os.path.join(R, 'Final', '_CURRENT')


def fsha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


for p in (BASE_SRC, DLC_SRC):
    if not os.path.exists(p):
        sys.exit('MISSING SOURCE: %s' % p)

JOBS = [
    ('PuyoPuyoTetris-xdelta-patches-1.0.14.zip', [
        (BASE_SRC, 'PuyoPuyoTetris-EN-voices-1.0.14.xdelta',
         os.path.join(CUR, 'PuyoPuyoTetris-EN-voices-1.0.14.cia')),
        (DLC_SRC, 'PuyoPuyoTetris-DLC-0.2.8.xdelta',
         os.path.join(CUR, 'PuyoPuyoTetris-DLC-0.2.8.cia')),
    ]),
    ('PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip', [
        (BASE_SRC, 'PuyoPuyoTetris-JP-voices-1.0.14.xdelta',
         os.path.join(CUR, 'PuyoPuyoTetris-JP-voices-1.0.14.cia')),
        (DLC_SRC, 'PuyoPuyoTetris-DLC-JP-voices-0.2.8.xdelta',
         os.path.join(CUR, 'PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia')),
    ]),
]

fails = 0
for zname, jobs in JOBS:
    bundle = os.path.join(CUR, zname)
    print('== %s (%d B)' % (zname, os.path.getsize(bundle)))
    z = zipfile.ZipFile(bundle)
    bad = z.testzip()
    print('   zip integrity: %s' % ('OK' if bad is None else 'CORRUPT ' + bad))
    tmp = os.path.join(W, '_verify_zip_0915')
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    open(os.path.join(tmp, 'xdelta3.exe'), 'wb').write(z.read('xdelta3.exe'))
    for src, xd, want_file in jobs:
        blob = z.read(xd)
        if not (blob[:3] == b'\xd6\xc3\xc4' and (blob[4] & 0x04) == 0):
            print('   %s CARRIES AN APP HEADER' % xd)
            fails += 1
        open(os.path.join(tmp, xd), 'wb').write(blob)
        out = os.path.join(tmp, 'out.bin')
        r = subprocess.run([os.path.join(tmp, 'xdelta3.exe'), '-d', '-f',
                            '-B', '1073741824', '-s', src,
                            os.path.join(tmp, xd), out],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print('   %s FAILED TO APPLY: %s' % (xd, r.stderr.strip()[:200]))
            fails += 1
            continue
        got, want = fsha(out), fsha(want_file)
        ok = got == want
        fails += 0 if ok else 1
        print('   %-44s -> %s  %s' % (xd, got[:16], 'OK' if ok else 'MISMATCH want ' + want[:16]))
        os.remove(out)
    rm = z.read('README.md').decode('utf-8')
    dashes = [c for c in rm if ord(c) in (0x2013, 0x2014)]
    print('   README.md %d B, dashes %d, non-ascii %d'
          % (len(rm.encode()), len(dashes), sum(ord(c) > 126 for c in rm)))
    z.close()
    shutil.rmtree(tmp, ignore_errors=True)

print('\nFAILS: %d' % fails)
sys.exit(1 if fails else 0)
