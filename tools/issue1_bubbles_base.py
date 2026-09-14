"""Base-game counterpart of issue1_bubbles.py, with a narrower rule and an in-place edit.

In the DLC the size argument of `MzSetText sec entry slot SIZE 0 0` matched Sega's Japanese line count
in all 763 lines, so rewriting it from the English line count was safe. In the BASE it does not:
Sega's own Japanese violates size//3+1 in 167 of about 2,700 lines (including 3 drawn lines in a
size 0 bubble), so the field cannot be read here as "lines the bubble holds".

What is still certain is the relative case: where our English needs MORE lines than Sega's Japanese had
in the same bubble, the bubble was sized for fewer lines than we now draw. That is the failure the
reporter photographed in the DLC. Only those entries are raised, only by the difference, never past 3
lines, and never in a debug table entry.

The size is a single ASCII digit, and the replacement is a single ASCII digit, so the edit is done on
the archive's raw bytes: every offset, length and pad byte in the file stays exactly as Sega wrote it,
and the result differs from the original in precisely one byte per changed bubble.

    python issue1_bubbles_base.py list      what would change, with Sega's line count beside ours
    python issue1_bubbles_base.py apply     write the changed archives into patch/romfs/script/adventure/
"""
import os, re, struct, sys
import mtx, narc

BR, END = chr(0xf8fd), chr(0xf813)
LINE = re.compile(rb'^MzSetText[ \t]+(\d+)[ \t]+(\d+)[ \t]+(\d+)[ \t]+(\d+)', re.M)
DEBUG = re.compile(r'^[A-Z][A-Z0-9_]{1,10}[_ ]?\d*\s+\d+\s*//')
JOBS = [('chapter%02d' % i, 'script/adventure/chapter%02d/manzai_script_chapter%02d.narc' % (i, i)) for i in range(0, 8)]
JOBS.append(('general', 'script/adventure/general/manzai_script_general.narc'))


def drawn(t):
    ls = t.replace(END, '').split(BR)
    while ls and not ls[-1].strip():
        ls.pop()
    return len(ls)


def textfile(stem, root):
    rel = 'tenp/text/adventure/%sJapanese.mtx' % stem
    p = os.path.join('patch', 'romfs', rel)
    return p if (root == 'en' and os.path.exists(p)) else os.path.join('romfs_110_tree' if root == 'en' else 'jp_orig', rel)


def member_spans(raw):
    """[(start, end)] of each member inside the whole file, from BTAF + GMIF."""
    hs, nsec = struct.unpack_from('<HH', raw, 12)
    off, files, img = hs, [], None
    while off < len(raw):
        tag = raw[off:off + 4]; size = struct.unpack_from('<I', raw, off + 4)[0]
        if size == 0:
            break
        if tag == b'BTAF':
            n = struct.unpack_from('<I', raw, off + 8)[0]
            files = [struct.unpack_from('<II', raw, off + 12 + 8 * i) for i in range(n)]
        elif tag == b'GMIF':
            img = off + 8
        off += size
    return [(img + a, img + b) for a, b in files]


def scan(stem, scr):
    """-> (source path, raw bytes, [(absolute offset of the size digit, sec, ent, old, new, jp lines, en lines, text)])"""
    src = os.path.join('romfs_110_tree', scr)
    raw = open(src, 'rb').read()
    en = mtx.parse(textfile(stem, 'en')); jp = mtx.parse(textfile(stem, 'jp'))
    hits = []
    for a, b in member_spans(raw):
        for m in LINE.finditer(raw[a:b]):
            sec, ent, size = int(m.group(1)), int(m.group(2)), int(m.group(4))
            t = en[sec][ent]
            if DEBUG.match(t):
                continue
            ne, nj = drawn(t), drawn(jp[sec][ent])
            if ne > nj and ne > size // 3 + 1:
                new = min(6, size + 3 * (ne - (size // 3 + 1)))
                assert len(str(new)) == len(m.group(4)) == 1
                hits.append((a + m.start(4), sec, ent, size, new, nj, ne, t.replace(BR, ' / ').replace(END, '')))
    return src, raw, hits


if __name__ == '__main__':
    mode = sys.argv[1]
    total = 0
    for stem, scr in JOBS:
        src, raw, hits = scan(stem, scr)
        total += len(hits)
        if hits:
            print('%s: %d bubble(s) to enlarge' % (stem, len(hits)))
            for off, sec, ent, size, new, nj, ne, t in hits:
                print('   sec%d #%d  size %d -> %d   Japanese %d line(s), English %d:  %s' % (sec, ent, size, new, nj, ne, t))
        if mode == 'apply' and hits:
            out = bytearray(raw)
            for off, sec, ent, size, new, nj, ne, t in hits:
                assert out[off:off + 1] == str(size).encode()
                out[off:off + 1] = str(new).encode()
            dst = os.path.join('patch', 'romfs', scr.replace('/', os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'wb').write(bytes(out))
            back = open(dst, 'rb').read()
            diff = [i for i in range(len(raw)) if raw[i] != back[i]]
            assert len(back) == len(raw) and diff == sorted(h[0] for h in hits), (len(back), diff)
            # and the archive still parses with the same member sizes
            assert [len(m) for m in narc.read(dst)['members']] == [len(m) for m in narc.read(src)['members']]
            print('   wrote %s  (%d byte(s) differ from Sega\'s file, each one a size digit)' % (dst, len(diff)))
    print('TOTAL bubbles enlarged: %d' % total)
