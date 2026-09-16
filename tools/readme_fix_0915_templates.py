"""Apply the same 2026-09-15 readme corrections to the template sources, so the
next rebuild does not reintroduce them. The JP template still carries its
{BASE_XD_MB} placeholder; none of the anchors touch that line."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(r'G:\Claude\PuyoPuyo')

import importlib.util
spec = importlib.util.spec_from_file_location('fix', r'G:\Claude\PuyoPuyo\work\_readme_fix_0915.py')

# import the strings without running the zip rebuild
src = open(r'G:\Claude\PuyoPuyo\work\_readme_fix_0915.py', encoding='utf-8').read()
ns = {}
exec(src.split('def edit(')[0].replace('import zipfile, hashlib, io, os, re, sys',
                                       'import os, re, sys'), ns)


def edit(text, pairs):
    for old, new in pairs:
        pat = re.compile(r"\r?\n".join(re.escape(l) for l in old.split("\n")))
        n = len(pat.findall(text))
        if n != 1:
            sys.exit("TEMPLATE ANCHOR FAIL count=%d for: %r" % (n, old[:60]))
        text = pat.sub(lambda m: new.replace("\n", "\r\n"), text, count=1)
    return text


JOBS = [
    (r'work\readmes_jpv_114\README_rhdn.md',
     [(ns['JP_OLD'], ns['JP_NEW']), (ns['JP_OLD2'], ns['JP_NEW2']),
      (ns['JP_OLD3'], ns['JP_NEW3'])]),
    (r'work\readmes_1014\README_rhdn.md',
     [(ns['EN_OLD'], ns['EN_NEW'])]),
]

for path, pairs in JOBS:
    b = open(path, 'rb').read()
    t2 = edit(b.decode('utf-8'), pairs)
    bad = sorted({hex(ord(c)) for c in t2 if ord(c) > 126})
    if bad:
        sys.exit('NON-ASCII in %s: %s' % (path, bad))
    open(path, 'wb').write(t2.encode('utf-8'))
    print('%s  %d -> %d bytes  (placeholder kept: %s)'
          % (path, len(b), len(t2.encode()), '{BASE_XD_MB}' in t2))
print('OK')
