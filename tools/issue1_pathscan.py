"""Scan the four 1.0.13 xdelta files for local paths (the specific strings, not bare words that also
occur inside the game's own data)."""
import os, glob
USER = os.environ.get('USERNAME', 'nobody').encode()
NEEDLES = [b'G:\\Claude', b'G:/Claude', b'Users\\' + USER, b'Users/' + USER, b'PuyoPuyo\\work', b'PuyoPuyo/work', b'C:\\Users', b'scratch-workspaces']
for p in sorted(glob.glob('rhdn_xdelta_v5/*.xdelta') + glob.glob('rhdn_xdelta_jpv_113/*.xdelta')):
    b = open(p, 'rb').read()
    hits = {n.decode('latin1'): b.count(n) for n in NEEDLES if n in b}
    loose = {w: b.count(w.encode()) for w in (USER.decode(), 'Claude')}
    print('%-60s %11d bytes  app-header flag %s  path strings: %s  (loose words, expected inside game data: %s)' % (
        p, len(b), 'SET' if b[4] & 0x04 else 'clear', hits or 'none', loose))
for d in ('rhdn_xdelta_v5/_tmp', 'rhdn_xdelta_jpv_113/_tmp'):
    if os.path.isdir(d):
        import shutil; shutil.rmtree(d); print('removed', d)
