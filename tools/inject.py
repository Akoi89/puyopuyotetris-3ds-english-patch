import os,re,json,collections,unicodedata,shutil,sys
import mtx
JP=re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9d]')
CTRL=re.compile(r'[\uf800-\uf8ff]')
SRC='tr_jpvoice'; ORIG='jp_orig'; OUT='patch/romfs'
END='\uf813'

def norm(s):
    s=unicodedata.normalize('NFKC',s).replace('\u3000',' ')
    s=CTRL.sub('',s)
    return re.sub(r'\s+',' ',s).strip()
def nospace(s): return re.sub(r'\s+','',norm(s))

PLACEHOLDER=re.compile(r'^\s*(no_text|NO_TEXT|dummy|DUMMY|nodata)')
T=json.load(open('tiers.json',encoding='utf-8'))
import os as _os
T['gen']=json.load(open('gen.json',encoding='utf-8')) if _os.path.exists('gen.json') else {}
T['human']=json.load(open('human.json',encoding='utf-8')) if _os.path.exists('human.json') else {}
TIERS=[('human',lambda s:s),('steam',lambda s:s),('steam_n',norm),('steam_s',nospace),
       ('fan',lambda s:s),('fan_n',norm),('fan_s',nospace),('gen',lambda s:s)]

def fixcodes(src,rep):
    """Carry the original's terminal control code onto the replacement."""
    rep=rep.rstrip(END)
    if src.rstrip().endswith(END): rep+=END
    return rep

# ---- pass 1: positional fill from a paired, already-translated sibling ----
def base_of(fn):
    m=re.match(r'(.+?)_F\d+(Japanese)?\.mtx$',fn)
    if not m: return None
    return m.group(1)+('Japanese' if m.group(2) else '')+'.mtx'

pos_map={}   # relpath -> {(sec,idx): english}
for dp,dn,fn in os.walk(SRC):
    for f in fn:
        if not f.endswith('.mtx'): continue
        b=base_of(f)
        if not b or b not in fn: continue
        rel=os.path.relpath(os.path.join(dp,f),SRC)
        brel=os.path.relpath(os.path.join(dp,b),SRC)
        try:
            Fj=mtx.parse(os.path.join(ORIG,rel)); Bj=mtx.parse(os.path.join(ORIG,brel))
            Bt=mtx.parse(os.path.join(SRC,brel))
        except Exception as e: continue
        if [len(s) for s in Fj]!=[len(s) for s in Bj] or [len(s) for s in Bj]!=[len(s) for s in Bt]:
            print('  [pos] shape mismatch, skipped: %s'%rel); continue
        m={}
        for si,(fs,bs,bt) in enumerate(zip(Fj,Bj,Bt)):
            for i,(a,c,e) in enumerate(zip(fs,bs,bt)):
                if a.strip() and e.strip() and JP.search(a) and not JP.search(e):
                    if nospace(a)==nospace(c): m[(si,i)]=e
        if m: pos_map[rel]=m; print('  [pos] %-52s %d entries from %s'%(rel,len(m),b))

# ---- pass 2: apply ----
if os.path.isdir('patch'): shutil.rmtree('patch')
stats=collections.Counter(); todo=[]; changed=[]
for dp,dn,fn in os.walk(SRC):
    for f in sorted(fn):
        if not f.endswith('.mtx'): continue
        p=os.path.join(dp,f); rel=os.path.relpath(p,SRC)
        raw=open(p,'rb').read()
        try: W=mtx.width(raw); secs=mtx._read(raw,W)
        except Exception: continue
        pm=pos_map.get(rel,{}); n=0; new=[]
        for si,sec in enumerate(secs):
            row=[]
            for i,x in enumerate(sec):
                x=x.replace(chr(0xFEFF),'')            # BOMs left by the fan tool
                if not(x.strip() and JP.search(x)): row.append(x); continue
                en=None; tier=None
                if (si,i) in pm: en=pm[(si,i)]; tier='positional'
                else:
                    for name,fn2 in TIERS:
                        k=fn2(x)
                        if k in T[name]: en=T[name][k]; tier=name; break
                if en is not None and tier != 'human' and PLACEHOLDER.match(en):
                    stats['skipped-placeholder']+=1; row.append(x); continue
                if en is None:
                    todo.append((rel,si,i,x)); row.append(x)
                else:
                    stats[tier]+=1; n+=1; row.append(fixcodes(x,en))
            new.append(row)
        if n:
            out=os.path.join(OUT,rel); os.makedirs(os.path.dirname(out),exist_ok=True)
            open(out,'wb').write(mtx.build(new,W))
            changed.append((rel,n))
print()
print('files written : %d'%len(changed))
print('strings filled: %d  %s'%(sum(stats.values()),dict(stats)))
print('still to do   : %d'%len(todo))
json.dump([{'file':r,'sec':s,'idx':i,'ja':x} for r,s,i,x in todo],
          open('todo.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
