import os,re,mtx
JP=re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9d]')
bad=0; n=0; jp_left=0
for dp,dn,fn in os.walk('patch/romfs'):
    for f in fn:
        if not f.endswith('.mtx'): continue
        p=os.path.join(dp,f); rel=os.path.relpath(p,'patch/romfs')
        src=mtx.parse(os.path.join('tr_jpvoice',rel))
        try: new=mtx.parse(p)
        except Exception as e: print('PARSE FAIL',rel,e); bad+=1; continue
        if [len(s) for s in src]!=[len(s) for s in new]:
            print('SHAPE CHANGED',rel,[len(s) for s in src],[len(s) for s in new]); bad+=1; continue
        for a,b in zip(src,new):
            for x,y in zip(a,b):
                n+=1
                if JP.search(y): jp_left+=1
                # untouched entries must be byte-identical
                if not JP.search(x) and x!=y:
                    print('CORRUPTED untouched entry in',rel,repr(x),repr(y)); bad+=1
print('files verified: %d, entries: %d, problems: %d, Japanese remaining in patched files: %d'%(
    sum(len(f) for _,_,f in os.walk('patch/romfs')),n,bad,jp_left))
