import os,re,json,collections,unicodedata
from mtx import parse
JP=re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9d]')
STEAM=r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data'
def trim(s):
    i=len(s)
    while i>0 and not s[i-1].strip(): i-=1
    return s[:i]
def norm(s):
    s=unicodedata.normalize('NFKC',s).replace('\u3000',' ').replace('\uf813','')
    return re.sub(r'\s+',' ',s).strip()
def nospace(s): return re.sub(r'\s+','',norm(s))

def add(tm,J,E,require_jp=False):
    if len(J)!=len(E): return 0
    n=0
    for sj,se in zip(J,E):
        a=trim(sj); b=trim(se)
        # Steam's DLC English files carry one junk trailing entry per section
        if len(b)==len(a)+1 and len(b[-1].strip())<=2: b=b[:-1]
        if len(a)!=len(b): continue
        for x,y in zip(a,b):
            if not(x.strip() and y.strip()): continue
            if require_jp and (not JP.search(x) or JP.search(y)): continue
            tm[x][y]+=1; n+=1
    return n

steam=collections.defaultdict(collections.Counter)
for dp,dn,fn in os.walk(STEAM):
    for f in fn:
        if f.endswith('English.mtx'):
            j=f[:-11]+'Japanese.mtx'
            if j in fn:
                try: add(steam,parse(os.path.join(dp,j)),parse(os.path.join(dp,f)))
                except Exception as e: pass
fan=collections.defaultdict(collections.Counter)
for line in open('diff.txt',encoding='utf-8'):
    p=line.strip()
    if not p.endswith('.mtx'): continue
    try: add(fan,parse(os.path.join('jp_orig',p)),parse(os.path.join('tr_jpvoice',p)),require_jp=True)
    except Exception as e: pass

def flat(tm): return {k:v.most_common(1)[0][0] for k,v in tm.items()}
S=flat(steam); F=flat(fan)
print('steam TM:',len(S),' fan TM:',len(F))
tiers={}
for name,d in (('steam',S),('fan',F)):
    tiers[name]=d
    tiers[name+'_n']={}; tiers[name+'_s']={}
    for k,v in d.items():
        tiers[name+'_n'].setdefault(norm(k),v)
        tiers[name+'_s'].setdefault(nospace(k),v)
json.dump(tiers,open('tiers.json','w',encoding='utf-8'),ensure_ascii=False)
