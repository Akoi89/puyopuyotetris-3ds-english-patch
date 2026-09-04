"""Emit the list of strings that still need a human translation."""
import os, re, json, mtx

JP = re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9d]')
# voice-index / glyph-test tables that the game never displays
DEBUG = re.compile(r'^[A-Z][A-Z0-9_]{1,10}[_ ]?\d*\s+\d+\s*//|^[A-Z][A-Z0-9_]{1,10}\s+[A-Z]+\uf813?$')

BR = '\uf8fd'   # in-game line break
END = '\uf813'  # end-of-message

items = []
for dp, dn, fn in os.walk('tr_jpvoice'):
    for f in sorted(fn):
        if not f.endswith('.mtx'):
            continue
        rel = os.path.relpath(os.path.join(dp, f), 'tr_jpvoice').replace(os.sep, '/')
        pp = os.path.join('patch/romfs', rel)
        cur = mtx.parse(pp) if os.path.exists(pp) else mtx.parse(os.path.join(dp, f))
        for si, sec in enumerate(cur):
            for i, x in enumerate(sec):
                if x.strip() and JP.search(x) and not DEBUG.match(x):
                    items.append({'file': rel, 'sec': si, 'idx': i, 'ja': x, 'en': ''})

json.dump(items, open('todo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

with open('todo.tsv', 'w', encoding='utf-8', newline='') as o:
    o.write('file\tsec\tidx\tjapanese\tenglish\n')
    for it in items:
        ja = it['ja'].replace(END, '').replace(BR, '\\n').replace('\u3000', ' ')
        o.write('%s\t%d\t%d\t%s\t\n' % (it['file'], it['sec'], it['idx'], ja))

print('to-do entries:', len(items))
