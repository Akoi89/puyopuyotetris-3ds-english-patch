import os,sys,mtx
for root in ['jp_orig','tr_jpvoice',r'G:/Claude/PuyoPuyo/PuyoPuyoTetris/data_steam/data']:
    ok=bad=err=0; bl=[]
    for dp,dn,fn in os.walk(root):
        for f in fn:
            if not f.endswith('.mtx'): continue
            p=os.path.join(dp,f); d=open(p,'rb').read()
            try:
                W=mtx.width(d); s=mtx._read(d,W); r=mtx.build(s,W)
            except Exception as e:
                err+=1; bl.append((p,'ERR '+str(e))); continue
            if r==d: ok+=1
            else: bad+=1; bl.append((p,'DIFF %d vs %d'%(len(r),len(d))))
    print('%-20s exact:%d differ:%d error:%d'%(os.path.basename(root),ok,bad,err))
    for p,m in bl[:6]: print('   ',m,p)
