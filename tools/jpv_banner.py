"""Japanese-voice edition banner: the shipped banner's models (English logo) with
Sega's original CWAV (the Japanese title call) put back.

banner_new.bin = models + English CWAV (what 1.0.10..1.0.12 ship).
_banner_jp.bin = the banner from the JP decrypted CCI (its CWAV is Sega's).
Output banner_jpv.bin, then exefs_banner.py splices it into the fan decrypted CCI.
"""
import hashlib, struct, subprocess, sys, os
import csar

R = os.environ.get('PUYO_ROOT') or sys.exit('set PUYO_ROOT to the project folder')
FAN_CCI = os.path.join(R, '0004000000101200 Puyopuyo Tetris (English Translated, English Voices) (CTR-P-BPTJ) (v0.0.0) (J).standard-decrypted.cci')

ship = open('banner_new.bin', 'rb').read()
jp = open('_banner_jp.bin', 'rb').read()
cw_s = struct.unpack_from('<I', ship, 0x84)[0]
cw_j = struct.unpack_from('<I', jp, 0x84)[0]
jp_cwav = jp[cw_j:]
assert cw_s % 0x20 == 0, 'CWAV offset must stay 0x20-aligned'
info = csar.cwav_info(jp_cwav)
print('JP CWAV: enc %d rate %d samples %d (%.2f s), %d bytes' % (info['enc'], info['rate'], info['samples'], info['samples'] / info['rate'], len(jp_cwav)))
new = ship[:cw_s] + jp_cwav
open('banner_jpv.bin', 'wb').write(new)
print('banner_jpv.bin %d bytes sha256 %s (models %d bytes from banner_new.bin, CWAV sha %s)' % (
    len(new), hashlib.sha256(new).hexdigest(), cw_s, hashlib.sha256(jp_cwav).hexdigest()[:12]))
# the model region must be exactly the shipped one, the CWAV exactly Sega's
assert new[:cw_s] == ship[:cw_s] and new[cw_s:] == jp[cw_j:]

r = subprocess.run([sys.executable, 'exefs_banner.py', FAN_CCI, 'banner_jpv.bin', 'cci_banner_jpv.cci'], capture_output=True, text=True)
print(r.stdout, r.stderr)
if r.returncode:
    raise SystemExit('exefs_banner failed')
