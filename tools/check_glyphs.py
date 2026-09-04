"""Does every character in the patched text exist in that file's font atlas?

The *_F<n>Japanese.narc archives beside each .mtx hold FONTDATF glyph atlases
carrying only the glyphs that file's text actually uses. Putting a character
into a .mtx whose atlas lacks it renders blank or wrong.

Record layout (16 bytes, after a 56-byte header, sorted by codepoint):
    +0x0C  u16  codepoint
    +0x0E  u16  glyph index
Glyph count is u32 at header +0x10.
"""
import os, re, struct, collections, sys
import mtx


CTRL = re.compile('[\ue000-\uf8ff]')


def narc_members(path):
    d = open(path, 'rb').read()
    if d[:4] != b'NARC':
        return []
    off = struct.unpack_from('<H', d, 12)[0]
    files, img = [], None
    while off < len(d):
        m, s = d[off:off + 4], struct.unpack_from('<I', d, off + 4)[0]
        if m == b'BTAF':
            n = struct.unpack_from('<I', d, off + 8)[0]
            files = [struct.unpack_from('<II', d, off + 12 + 8 * i) for i in range(n)]
        elif m == b'GMIF':
            img = off + 8
        if s == 0:
            break
        off += s
    return [d[img + a:img + b] for a, b in files]


def charset(narc_path):
    """Union of every codepoint in every FONTDATF member of this archive."""
    cs = set()
    for blob in narc_members(narc_path):
        if blob[:8] != b'FONTDATF':
            continue
        n = struct.unpack_from('<I', blob, 0x10)[0]
        if 56 + n * 16 > len(blob):
            continue
        for r in range(n):
            cs.add(struct.unpack_from('<H', blob, 56 + r * 16 + 12)[0])
    return cs


def companions(rel, root='jp_orig'):
    """Font atlases that render this .mtx.

    A difficulty-variant file (X_F1Japanese.mtx) draws through its PARENT's
    atlases: on the untouched ROM every such variant is fully covered by the
    parent's set and none by its own namesake .narc, which is the parent's
    font tier, not the variant's atlas.
    """
    d = os.path.dirname(rel)
    base = os.path.basename(rel)[:-4]
    parent = re.sub(r'_F\d+(Japanese)$', r'\1', base)
    if parent != base and os.path.exists(os.path.join(root, d, parent + '.mtx')):
        base = parent
    stem = base[:-8] if base.endswith('Japanese') else base
    lang = 'Japanese' if base.endswith('Japanese') else ''
    out = []
    for f in sorted(os.listdir(os.path.join(root, d))):
        if not f.endswith('.narc'):
            continue
        n = f[:-5]
        if n == stem + lang or re.match(re.escape(stem) + r'_F\d+' + lang + '$', n):
            out.append(os.path.join(d, f))
    return out


if __name__ == "__main__":
    problems = []
    print('%-50s %-34s %s' % ('patched .mtx', 'atlas', 'missing glyphs'))
    print('-' * 110)
    for dp, dn, fn in os.walk('patch/romfs'):
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), 'patch/romfs')
            before = mtx.parse(os.path.join('tr_jpvoice', rel))
            after = mtx.parse(os.path.join(dp, f))
            need = set()
            for sb, sa in zip(before, after):
                for x, y in zip(sb, sa):
                    if x != y:                       # only what this pass changed
                        need |= set(CTRL.sub('', y))
            if not need:
                continue
            for c in companions(rel):
                # the shipping atlas is the translated one where the fan patch made it
                src = 'tr_jpvoice' if os.path.exists(os.path.join('tr_jpvoice', c)) else 'jp_orig'
                cs = charset(os.path.join(src, c))
                miss = sorted(ch for ch in need if ord(ch) not in cs)
                if miss:
                    shown = ''.join(miss)[:40]
                    print('%-50s %-34s %d: %r' % (rel, os.path.basename(c), len(miss), shown))
                    problems.append((rel, c, miss))
                else:
                    print('%-50s %-34s ok' % (rel, os.path.basename(c)))
    print()
    print('atlases missing glyphs the patched text needs: %d' % len(problems))
    
