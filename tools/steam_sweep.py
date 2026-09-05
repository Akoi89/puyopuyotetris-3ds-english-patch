"""Sweep Steam's *_e.narc archives for localised textures.

For every X_e.narc with a sibling X.narc under the Steam data, decode every
DDS texture in both (plain DDS members and DDS files inside 'tppk'
containers), compare pixel by pixel, and save the textures that differ to
steam_sweep/<archive>/<member>_<k>_{jp,en}.png with a side-by-side contact
sheet steam_sweep/<archive>.png. Writes steam_sweep/INDEX.md listing each
archive with the count of differing textures.
"""
import io, os, glob, struct, sys
import numpy as np
from PIL import Image, ImageDraw
import narc

D = 'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/'
OUT = 'steam_sweep'
os.makedirs(OUT, exist_ok=True)


def textures(member):
    """Yield DDS blobs inside a narc member (plain or tppk-wrapped)."""
    if member[:4] == b'DDS ':
        yield member
    elif member[:4] == b'tppk':
        offs = [i for i in range(len(member) - 4) if member[i:i + 4] == b'DDS ']
        for k, j in enumerate(offs):
            end = offs[k + 1] if k + 1 < len(offs) else len(member)
            yield member[j:end]


def decode(blob):
    try:
        im = Image.open(io.BytesIO(blob)); im.load(); return im.convert('RGBA')
    except Exception:
        return None


rows = []
files = sorted(glob.glob(D + '**/*_e.narc', recursive=True))
for pe in files:
    pj = pe[:-7] + '.narc'
    rel = os.path.relpath(pe, D).replace(os.sep, '/')
    if 'sound' in rel or not os.path.exists(pj):
        continue
    try:
        je = narc.read(pe)['members']; jj = narc.read(pj)['members']
    except Exception as ex:
        print('ERR', rel, ex); continue
    tag = rel[:-5].replace('/', '__')
    diffs = []
    for i, m in enumerate(je):
        mj = jj[i] if i < len(jj) else b''
        te = list(textures(m)); tj = list(textures(mj))
        for k, be in enumerate(te):
            ie = decode(be)
            if ie is None: continue
            ij = decode(tj[k]) if k < len(tj) else None
            same = ij is not None and ij.size == ie.size and np.array_equal(np.array(ij), np.array(ie))
            if same: continue
            diffs.append((i, k, ij, ie))
    if not diffs:
        continue
    od = os.path.join(OUT, tag); os.makedirs(od, exist_ok=True)
    cell = 320
    sheet = Image.new('RGBA', (cell * 2 + 8, cell * len(diffs)), (40, 40, 60, 255)); d = ImageDraw.Draw(sheet)
    for r, (i, k, ij, ie) in enumerate(diffs):
        ie.save('%s/%d_%d_en.png' % (od, i, k))
        if ij is not None: ij.save('%s/%d_%d_jp.png' % (od, i, k))
        for c, im in enumerate((ij, ie)):
            if im is None: continue
            s = min((cell - 16) / im.width, (cell - 16) / im.height); t = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))))
            x, y = c * (cell + 8), r * cell; sheet.paste(t, (x, y + 14), t)
            d.text((x + 2, y), '%s m%d k%d %s %dx%d' % ('jp' if c == 0 else 'EN', i, k, '', im.width, im.height), fill=(255, 220, 0, 255))
    sheet.save('%s/%s.png' % (OUT, tag))
    rows.append((rel, len(diffs)))
    print('%-60s %d differing textures' % (rel, len(diffs)))
with open(os.path.join(OUT, 'INDEX.md'), 'w', encoding='utf-8') as f:
    f.write('# Steam _e.narc sweep: textures that differ between Japanese and English\n\n')
    for rel, n in rows:
        f.write('- `%s`: %d\n' % (rel, n))
print(len(rows), 'archives with localised textures')
