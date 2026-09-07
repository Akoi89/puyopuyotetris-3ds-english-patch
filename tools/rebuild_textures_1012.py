"""Re-render every patch texture from its sources through work/tex.py (1.0.12: etcpak ETC1A4).

    python rebuild_textures_1012.py snapshot            copy patch -> patch_1011_ref, patch_dlc2 -> patch_dlc2_1011_ref (once)
    python rebuild_textures_1012.py run legacy "ENG 1.0.11"   reset the texture archives and re-run the chain with the
                                                        pre-1.0.12 encoder (null test: overlay must equal the snapshot)
    python rebuild_textures_1012.py run etcpak "ENG 1.0.12"   the real 1.0.12 render
    python rebuild_textures_1012.py compare             list overlay files that differ from the snapshot

The chain is the recorded texture part of the rebuild order (CONTINUE_HERE): labels.py apply, labels2.py apply,
record_card.py, prefectures.py, notice.py, swap_logos.py, steam_text.py apply, steam_manual.py apply, dlc_plates.py,
stamp_title.py. Font-atlas steps (atlas_fix2 / atlas_compact) do not go through the texture encoder and are left alone.
Every archive any of these scripts writes is deleted from the overlay first, because steam_text.py and steam_manual.py
layer onto whatever archive already sits in the overlay. PUYO_TEX_STATS=<file> gets one line per ETC1A4 texture
(w h PSNR) so the two encoders can be compared texture by texture.
"""
import hashlib, json, os, re, shutil, subprocess, sys, time

REF = {'patch': 'patch_1011_ref', 'patch_dlc2': 'patch_dlc2_1011_ref'}
OUT = {'tr_envoice': 'patch/romfs', 'tr_jpvoice': 'patch/romfs', 'dlc_r': 'patch_dlc2'}


def write_set():
    """Every overlay path the chain writes, derived from the scripts' own tables."""
    paths = set()
    for js in ('labels.json', 'labels2.json', 'steam_text.json'):
        for l in json.load(open(js, encoding='utf-8')):
            if js == 'steam_text.json' and not l.get('ok'):
                continue
            paths.add(os.path.join(OUT[l['root']], l['narc']))
    src = open('steam_manual.py', encoding='utf-8').read()
    for rel in re.findall(r"\('([^']+\.narc)'", src):
        paths.add(os.path.join('patch/romfs', rel))
    for rel in ('toko/toko.narc', 'mydata/option/option.narc', 'logo/Attention.narc',
                'tenp/swap/swap2p/swap2p.narc', 'title/title.narc'):
        paths.add(os.path.join('patch/romfs', rel))
    for content, n in (('0010', 1), ('0011', 2), ('0012', 3)):
        for kind in ('adv_DL1_0%d' % n, 'adv_DL2_0%d' % n):
            paths.add('patch_dlc2/%s/data/%s.narc' % (content, kind))
    return sorted(p.replace('\\', '/') for p in paths)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def snapshot():
    for src, dst in REF.items():
        if os.path.exists(dst):
            print(dst, 'exists, kept'); continue
        shutil.copytree(src, dst); print('copied', src, '->', dst)


def run(mode, stamp):
    assert mode in ('legacy', 'etcpak', 'search')
    for dst in REF.values():
        assert os.path.isdir(dst), 'run snapshot first'
    ws = write_set()
    gone = 0
    for p in ws:
        if os.path.exists(p):
            os.remove(p); gone += 1
    print('reset: %d of %d chain outputs removed from the overlays' % (gone, len(ws)), flush=True)
    env = dict(os.environ, PUYO_ETC1=mode, PUYO_TEX_STATS='tex_stats_%s.txt' % mode, PYTHONIOENCODING='utf-8')
    if os.path.exists(env['PUYO_TEX_STATS']):
        os.remove(env['PUYO_TEX_STATS'])
    chain = [['labels.py', 'apply'], ['labels2.py', 'apply'], ['record_card.py'], ['prefectures.py'], ['notice.py'],
             ['swap_logos.py'], ['steam_text.py', 'apply'], ['steam_manual.py', 'apply'], ['dlc_plates.py'],
             ['stamp_title.py', stamp, REF['patch'] + '/romfs/title/title.narc']]
    log = open('rebuild_textures_%s.log' % mode, 'w', encoding='utf-8')
    for step in chain:
        t = time.time()
        print('== %s' % ' '.join(step), flush=True)
        r = subprocess.run([sys.executable] + step, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        txt = r.stdout.decode('utf-8', 'replace')
        log.write('== %s\n%s\n' % (' '.join(step), txt)); log.flush()
        print('   exit %d, %.0f s, %d lines' % (r.returncode, time.time() - t, txt.count('\n')), flush=True)
        if r.returncode:
            print(txt[-3000:]); raise SystemExit('step failed: %s' % ' '.join(step))
    missing = [p for p in ws if not os.path.exists(p)]
    print('chain done; outputs missing:', missing or 'none')
    compare()


def compare():
    ws = set(write_set())
    for src, ref in REF.items():
        same = diff = 0; changed = []
        for root, _, fs in os.walk(ref):
            for f in fs:
                rp = os.path.join(root, f); rel = os.path.relpath(rp, ref)
                p = os.path.join(src, rel)
                if not os.path.exists(p):
                    changed.append(('MISSING', rel)); continue
                if sha(p) == sha(rp):
                    same += 1
                else:
                    diff += 1; changed.append(('DIFF', rel))
        extra = [os.path.relpath(os.path.join(r, f), src) for r, _, fs in os.walk(src) for f in fs
                 if not os.path.exists(os.path.join(ref, os.path.relpath(os.path.join(r, f), src)))]
        print('%s vs %s: %d identical, %d differ, %d extra' % (src, ref, same, diff, len(extra)))
        for kind, rel in changed:
            tag = 'chain' if os.path.join(src, rel).replace('\\', '/') in ws else 'NOT IN CHAIN'
            print('   %-8s %-60s %s' % (kind, rel, tag))
        for rel in extra:
            print('   EXTRA    %s' % rel)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'snapshot':
        snapshot()
    elif cmd == 'run':
        run(sys.argv[2], sys.argv[3])
    elif cmd == 'compare':
        compare()
    elif cmd == 'writeset':
        print('\n'.join(write_set()))
