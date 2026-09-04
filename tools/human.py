"""Build human.json {exact japanese: english} from tr_batch*.json + tr_extra.json.

Batches carry (file, sec, idx, en). The Japanese key is read from the SOURCE
tree (tr_jpvoice), never from todo.json, so applied translations are never lost
when the to-do list is regenerated. todo.json is left untouched here.
"""
import glob, json, io, os, sys
sys.path.insert(0, '.')
import mtx
BR = chr(0xf8fd); END = chr(0xf813); NL = chr(10); CR = chr(13)
cache = {}
def src(rel):
    rel = rel.replace('/', os.sep)
    if rel not in cache:
        cache[rel] = mtx.parse(os.path.join('tr_jpvoice', rel))
    return cache[rel]
human = {}; n = miss = 0
for b in sorted(glob.glob('tr_batch*.json')):
    for e in json.load(io.open(b, encoding='utf-8')):
        S = src(e['file'])
        try: ja = S[e['sec']][e['idx']]
        except IndexError: miss += 1; print('  bad index', e['file'], e['sec'], e['idx']); continue
        en = e['en'].replace(CR + NL, BR).replace(NL, BR)
        if ja.rstrip().endswith(END) and not en.endswith(END): en += END
        human[ja] = en; n += 1
if os.path.exists('tr_extra.json'):
    for k, v in json.load(io.open('tr_extra.json', encoding='utf-8')).items():
        human[k] = v + (END if k.rstrip().endswith(END) and not v.endswith(END) else '')
json.dump(human, io.open('human.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('human.json: %d translations from %d batch entries (%d bad) + extras' % (len(human), n, miss))
