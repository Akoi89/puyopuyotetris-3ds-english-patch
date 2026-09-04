import os,re,json,collections,mtx
JP=re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9d]')
DEBUG=re.compile(r'^[A-Z][A-Z0-9_]{1,10}[_ ]?\d*\s+\d+\s*//|^[A-Z][A-Z0-9_]{1,10}\s+[A-Z]+\uf813?$')
GLYPH=re.compile(r'^[ぁ-んァ-ン０-９5０5]{6,}')
cats=collections.Counter(); per=collections.defaultdict(collections.Counter)
rows=[]
for dp,dn,fn in os.walk('tr_jpvoice'):
    for f in sorted(fn):
        if not f.endswith('.mtx'): continue
        rel=os.path.relpath(os.path.join(dp,f),'tr_jpvoice')
        pp=os.path.join('patch/romfs',rel)
        after=mtx.parse(pp) if os.path.exists(pp) else mtx.parse(os.path.join(dp,f))
        before=mtx.parse(os.path.join(dp,f))
        for sb,sa in zip(before,after):
            for x,y in zip(sb,sa):
                if not (x.strip() and JP.search(x)): continue
                if not JP.search(y): cats['filled']+=1; per[rel]['filled']+=1
                elif DEBUG.match(x): cats['debug table (not shown in game)']+=1; per[rel]['debug']+=1
                else: cats['NEEDS TRANSLATION']+=1; per[rel]['todo']+=1; rows.append((rel,x))
tot=sum(cats.values())
print('Japanese strings in the fan patch : %d'%tot)
for k,v in cats.most_common(): print('  %-34s %5d  (%.1f%%)'%(k,v,100*v/tot))
print()
print('%-52s %6s %6s %6s'%('file','filled','todo','debug'))
for rel,c in sorted(per.items(),key=lambda kv:-kv[1]['todo']):
    if c['todo']: print('%-52s %6d %6d %6d'%(rel,c['filled'],c['todo'],c['debug']))
# todo.json is written by maketodo.py only
