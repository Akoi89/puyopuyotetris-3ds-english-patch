"""patch_dlc2_jpv = patch_dlc2 without the adv_sound folders (the imported English
story voices). Everything else (text, atlases, plates, shop icons) is kept."""
import os, shutil

SRC, DST = 'patch_dlc2', 'patch_dlc2_jpv'
if os.path.exists(DST):
    shutil.rmtree(DST)
kept = dropped = 0
for dp, dn, fn in os.walk(SRC):
    rel = os.path.relpath(dp, SRC)
    parts = rel.split(os.sep)
    if len(parts) >= 2 and parts[1] == 'adv_sound':
        dropped += len(fn)
        continue
    for f in fn:
        d = os.path.join(DST, rel, f)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(os.path.join(dp, f), d)
        kept += 1
print('kept %d files, dropped %d voice clips' % (kept, dropped))
for c in sorted(os.listdir(DST)):
    n = sum(len(f) for _, _, f in os.walk(os.path.join(DST, c)))
    print('  %s: %d files' % (c, n))
