"""Where does the speech bubble's height come from? Hypothesis: a per-entry line count stored in the scene
script (chapter_08.pss or manzai_script_chapter08.narc), matching Sega's Japanese line counts.

    python issue1_bubble.py 08
Prints file sizes/heads and searches both files for the sequence of JP line counts (section 0, then all
sections) encoded as u8 / u16 / u32, and for the entry count.
"""
import os, struct, sys
import mtx, narc

ch = sys.argv[1] if len(sys.argv) > 1 else '08'
cid = {'08': '0010', '09': '0011', '10': '0012'}[ch]
BR, END = chr(0xf8fd), chr(0xf813)
jp = mtx.parse('dlc_r/%s/data/chapter%sJapanese.mtx' % (cid, ch))
counts = [[len(t.replace(END, '').split(BR)) if t.strip() else 0 for t in s] for s in jp]
print('sections', len(jp), 'entries per section', [len(s) for s in jp])
print('JP line counts sec0:', counts[0])

pss = open('dlc_r/%s/data/chapter_%s.pss' % (cid, ch), 'rb').read()
print('pss size', len(pss), 'head', pss[:64].hex())
arc = narc.read('dlc_r/%s/data/manzai_script_chapter%s.narc' % (cid, ch))
ms = arc['members']
print('manzai narc members', len(ms), [(i, len(m), m[:4]) for i, m in enumerate(ms)][:40])
naix = open('dlc_r/%s/data/manzai_script_chapter%s.naix' % (cid, ch), 'rb').read()
print('naix size', len(naix), 'head', naix[:200])


def find_seq(blob, seq, name):
    hits = []
    for fmt, w in (('<B', 1), ('<H', 2), ('<I', 4)):
        pat = b''.join(struct.pack(fmt, v) for v in seq)
        j = blob.find(pat)
        while j >= 0:
            hits.append((fmt, j)); j = blob.find(pat, j + 1)
    print('  %s: sequence of %d values found at %s' % (name, len(seq), hits[:10] if hits else 'nowhere'))


for name, blob in (('pss', pss), ('naix', naix)) + tuple(('manzai m%d' % i, m) for i, m in enumerate(ms)):
    find_seq(blob, counts[0][:8], name)
    find_seq(blob, [c for s in counts for c in s][:12], name + ' (all sections)')
