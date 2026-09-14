"""Dump every DDS texture in Steam's party2p.narc and party2p_e.narc (fast: bytes.find)."""
import io, os, sys
import narc
from PIL import Image

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def textures(member):
    if member[:4] == b'DDS ':
        yield member
    elif member[:4] == b'tppk':
        offs = []
        j = member.find(b'DDS ')
        while j >= 0:
            offs.append(j); j = member.find(b'DDS ', j + 4)
        for k, j in enumerate(offs):
            end = offs[k + 1] if k + 1 < len(offs) else len(member)
            yield member[j:end]


for tag in ['party2p_e', 'party2p']:
    ms = narc.read('G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data/tenp/party/party2p/%s.narc' % tag)['members']
    print(tag, 'members', len(ms), [m[:4] for m in ms])
    for i, m in enumerate(ms):
        for k, b in enumerate(textures(m)):
            try:
                im = Image.open(io.BytesIO(b)); im.load(); im = im.convert('RGBA')
            except Exception as e:
                print(tag, i, k, 'ERR', e); continue
            print(tag, i, k, im.size)
            im.save('%s/%s_%02d_%d.png' % (OUT, tag, i, k))
