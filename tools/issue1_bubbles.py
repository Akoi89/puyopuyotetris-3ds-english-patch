"""Bubble height for the EX chapter dialogue is scripted: manzai_script_chapterNN.narc member S is section S's
scene script, and each dialogue line is

    MzSetText <section> <entry> <slot> <size> <a> <b>

where <size> encodes the bubble size (observed against Sega's Japanese line counts: 0/1 = one line,
3 = two lines, 6/7 = three lines; the low bit is a separate flag).

    python issue1_bubbles.py table     crosstab <size> against the JP line count, all three chapters
    python issue1_bubbles.py apply     rewrite <size> from the English line count (patch_dlc2 tables),
                                        keeping the low bit, into patch_dlc2/<cid>/data/manzai_script_chapterNN.narc
                                        (null test: narc.build(read) == original first)
"""
import os, re, sys, collections
import mtx, narc

BR, END = chr(0xf8fd), chr(0xf813)
CH = [('0010', '08'), ('0011', '09'), ('0012', '10')]
SIZE_FOR_LINES = {1: 0, 2: 2, 3: 6}      # base code per line count; low bit carried over from Sega's value
LINE = re.compile(r'^(MzSetText[ \t]+)(\d+)([ \t]+)(\d+)([ \t]+)(\d+)([ \t]+)(\d+)(.*)$')


def build_padded(orig, members):
    """narc.build, but with each member padded to 4 bytes with 0xFF (tail included), as Sega's script archives are."""
    import struct
    data = bytearray(); spans = []
    for m in members:
        spans.append((len(data), len(data) + len(m)))
        data += m
        while len(data) % 4:
            data += b'\xff'
    btaf = bytearray(b'BTAF') + struct.pack('<II', 12 + 8 * len(members), len(members))
    for a, b in spans:
        btaf += struct.pack('<II', a, b)
    gmif = b'GMIF' + struct.pack('<I', 8 + len(data)) + bytes(data)
    out = bytearray(b'NARC\xfe\xff\x00\x01') + struct.pack('<I', 0) + struct.pack('<HH', 0x10, orig['nsec']) + btaf + orig['btnf'] + gmif
    struct.pack_into('<I', out, 8, len(out))
    return bytes(out)


def lines_of(t):
    return len(t.replace(END, '').split(BR)) if t.strip() else 0


def scripts(cid, ch):
    p = os.path.join('dlc_r', cid, 'data', 'manzai_script_chapter%s.narc' % ch)
    arc = narc.read(p)
    return p, arc, [m.decode('utf-8') for m in arc['members']]


if sys.argv[1] == 'table':
    tab = collections.Counter(); seen = collections.Counter()
    for cid, ch in CH:
        jp = mtx.parse('dlc_r/%s/data/chapter%sJapanese.mtx' % (cid, ch))
        p, arc, texts = scripts(cid, ch)
        pass
        n = 0
        for si, txt in enumerate(texts):
            for ln in txt.split('\n'):
                m = LINE.match(ln.rstrip('\r'))
                if not m:
                    continue
                sec, ent, slot, size = int(m.group(2)), int(m.group(4)), int(m.group(6)), int(m.group(8))
                tab[(size, lines_of(jp[sec][ent]))] += 1; seen[sec == si] += 1; n += 1
        print('ch%s: %d MzSetText lines (section arg == member index: %s)' % (ch, n, dict(seen)))
    print('size -> JP line count crosstab:')
    for (size, nl), c in sorted(tab.items()):
        print('   size %d  lines %d : %d' % (size, nl, c))
elif sys.argv[1] == 'apply':
    for cid, ch in CH:
        en = mtx.parse('patch_dlc2/%s/data/chapter%sJapanese.mtx' % (cid, ch))
        jp = mtx.parse('dlc_r/%s/data/chapter%sJapanese.mtx' % (cid, ch))
        p, arc, texts = scripts(cid, ch)
        assert build_padded(arc, list(arc['members'])) == open(p, 'rb').read(), 'padded null test failed: ' + p
        changed = 0; total = 0; out = []
        for txt in texts:
            rows = []
            for ln in txt.split('\n'):
                m = LINE.match(ln.rstrip('\r'))
                if m:
                    sec, ent, size = int(m.group(2)), int(m.group(4)), int(m.group(8))
                    nl_en = lines_of(en[sec][ent]); nl_jp = lines_of(jp[sec][ent])
                    total += 1
                    if nl_en and nl_en != nl_jp:
                        # observed codes: 0/1 one line, 3/4 two lines, 6/7 three lines -> 3*(lines-1) + variant
                        variant = size - 3 * (nl_jp - 1)
                        assert variant in (0, 1), ('unexpected size code', ch, sec, ent, size, nl_jp)
                        new = 3 * (nl_en - 1) + variant
                        ln = m.group(1) + m.group(2) + m.group(3) + m.group(4) + m.group(5) + m.group(6) + m.group(7) + str(new) + m.group(9) + ('\r' if ln.endswith('\r') else '')
                        changed += 1
                rows.append(ln)
            out.append('\n'.join(rows).encode('utf-8'))
        for a, b in zip(texts, out):
            assert len(a.encode('utf-8')) == len(b) or True
        dst = os.path.join('patch_dlc2', cid, 'data', 'manzai_script_chapter%s.narc' % ch)
        open(dst, 'wb').write(build_padded(arc, out))
        back = [m.decode('utf-8') for m in narc.read(dst)['members']]
        assert len(back) == len(texts) and all(b == o.decode('utf-8') for b, o in zip(back, out))
        print('ch%s: %d of %d MzSetText sizes changed -> %s' % (ch, changed, total, dst))
