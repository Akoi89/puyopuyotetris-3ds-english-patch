"""Manual row-run boxes for the two textures the detector cannot split:
the glowing green pill buttons in puyo/menu (one connected blob) and the LA4
dialog text in system COMP:5. Appends entries with ids/groups from 1000 to
labels2.json and prints them so labels2_en.json can name them.
"""
import json
import numpy as np
import narc, labels2

L = json.load(open('labels2.json', encoding='utf-8'))
L = [l for l in L if l['id'] < 1000]
nid = 1000


def row_runs(a, thr, x0, x1, y0, y1, minrows=8):
    ink = (a[y0:y1, x0:x1, 3] > thr).sum(axis=1) > 3
    runs, start = [], None
    for i, v in enumerate(list(ink) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= minrows:
                runs.append((y0 + start, y0 + i))
            start = None
    return runs


def add(root, rel, sel, box, mi, fmt):
    global nid
    L.append(dict(id=nid, root=root, narc=rel, member=mi, tex=sel, fmt=fmt, box=list(box), group=nid))
    print(nid, rel, sel, box); nid += 1


arc = narc.read('tr_envoice/puyo/menu/puyo_menu.narc')
for m in range(12, 17):
    sel = 'COMP:%d' % m
    mi, e, img, fmt, hdr = labels2.get_texture(arc, sel)
    a = np.array(img)
    for y0, y1 in row_runs(a, 200, 10, 150, 0, 200):
        cols = np.where((a[y0:y1, :, 3] > 200).any(axis=0))[0]
        add('tr_envoice', 'puyo/menu/puyo_menu.narc', sel, (int(cols.min()), y0, int(cols.max()) + 1, y1), mi, fmt)

arc = narc.read('tr_envoice/system/system.narc')
mi, e, img, fmt, hdr = labels2.get_texture(arc, 'COMP:5')
a = np.array(img)
for y0, y1 in row_runs(a, 128, 0, 256, 0, 256):
    cols = np.where((a[y0:y1, :, 3] > 128).any(axis=0))[0]
    add('tr_envoice', 'system/system.narc', 'COMP:5', (int(cols.min()), y0, int(cols.max()) + 1, y1), mi, fmt)

json.dump(L, open('labels2.json', 'w', encoding='utf-8'), indent=0)
print('total labels', len(L))
