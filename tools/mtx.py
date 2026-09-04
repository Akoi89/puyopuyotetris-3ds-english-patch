import struct

TERM='\uf8ff'

def _read(d, W):
    F='<Q' if W==8 else '<I'
    tbl=struct.unpack_from(F,d,W)[0]
    assert tbl==2*W, 'bad section table offset %d'%tbl
    first_sec=struct.unpack_from(F,d,2*W)[0]
    nsec=(first_sec-2*W)//W
    secs=[struct.unpack_from(F,d,2*W+W*i)[0] for i in range(nsec)]
    # string data begins right after all pointer tables == first offset of section 0
    data_start=struct.unpack_from(F,d,secs[0])[0]
    out=[]
    for si,s in enumerate(secs):
        end = secs[si+1] if si+1<len(secs) else data_start
        n=(end-s)//W
        strs=[]
        for i in range(n):
            off=struct.unpack_from(F,d,s+W*i)[0]
            j=off; buf=bytearray()
            while j+1<len(d):
                w=d[j]|(d[j+1]<<8)
                if w==0xf8ff or w==0: break
                buf+=d[j:j+2]; j+=2
            strs.append(buf.decode('utf-16-le',errors='replace'))
        out.append(strs)
    return out

def width(path_or_bytes):
    d=path_or_bytes if isinstance(path_or_bytes,bytes) else open(path_or_bytes,'rb').read()
    if struct.unpack_from('<I',d,0)[0]==len(d) and struct.unpack_from('<I',d,4)[0]==8: return 4
    if struct.unpack_from('<Q',d,0)[0]==len(d) and struct.unpack_from('<Q',d,8)[0]==16: return 8
    raise ValueError('unrecognised mtx header')

def parse(path):
    d=open(path,'rb') .read()
    return _read(d, width(d))

def parse_bytes(d):
    return _read(d, width(d))

def build(secs, W=4):
    """Rebuild an .mtx. Identical strings share one blob, matching the originals."""
    F='<Q' if W==8 else '<I'
    ntbl=sum(len(s) for s in secs)
    data_start = 2*W + W*len(secs) + W*ntbl
    blobs={}; data=bytearray(); offs=[]
    for s in secs:
        row=[]
        for t in s:
            o=data_start+len(data)
            row.append(o)
            data += (t+TERM).encode('utf-16-le')
        offs.append(row)
    out=bytearray()
    out += struct.pack(F,0)          # size, patched below
    out += struct.pack(F,2*W)
    p = 2*W + W*len(secs)
    for row in offs:
        out += struct.pack(F,p); p += W*len(row)
    for row in offs:
        for o in row: out += struct.pack(F,o)
    out += data
    struct.pack_into(F,out,0,len(out))
    return bytes(out)
