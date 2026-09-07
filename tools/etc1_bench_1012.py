"""Compare ETC1A4 colour encoders on the 8 drawn textures the 1.0.12 chain produces (tex_dump_1012/*.png).

    python etc1_bench_1012.py            table of PSNR (dB, visible pixels only) per texture per encoder

Encoders:
  legacy   etc1_enc.encode_rgba          individual mode, base = rounded mean, brute-force table/index (1.0.11)
  etcpak   etc1_enc.encode_rgba_etcpak   etcpak 0.9.15 compress_etc1_rgb
  search   individual mode, base colour searched in a +-R cube around the rounded mean (R below)
  hybrid   per 4x4 block, whichever of the above gives the lowest visible-pixel error
"""
import glob, os, struct, sys, time
import numpy as np
from PIL import Image
sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
import etc1a4, etc1_enc
from etc1a4 import MOD

R = 1
MODS = np.array([[a, b, -a, -b] for a, b in MOD])                     # 8 x 4


def _pack(flip, bases, tables, idxs):
    hi = ((bases[0][0] << 28) | (bases[1][0] << 24) | (bases[0][1] << 20) | (bases[1][1] << 16)
          | (bases[0][2] << 12) | (bases[1][2] << 8) | (tables[0] << 5) | (tables[1] << 2) | flip)
    lo = 0
    for i in range(16):
        x, y = i // 4, i % 4
        if flip == 0:
            si = 0 if x < 2 else 1; j = y * 2 + (x % 2)
        else:
            si = 0 if y < 2 else 1; j = (y % 2) * 4 + x
        k = int(idxs[si][j])
        lo |= ((k >> 1) & 1) << (i + 16)
        lo |= (k & 1) << i
    return hi, lo


def _sub_search(px, wt, radius):
    """px n x 3 float, wt n weights (0 for invisible). Returns (err, base4, table, idx)."""
    mean = (px * wt[:, None]).sum(0) / max(wt.sum(), 1e-9)
    c = np.clip(np.round(mean / 17), 0, 15).astype(int)
    rng = np.arange(-radius, radius + 1)
    cand = np.array([[c[0] + a, c[1] + b, c[2] + d] for a in rng for b in rng for d in rng])
    cand = np.unique(np.clip(cand, 0, 15), axis=0)                    # k x 3
    b255 = cand[:, None, :] * 17 + MODS.reshape(1, 32, 1)              # k x 32 x 3  (table*4+mod)
    b255 = np.clip(b255, 0, 255)
    e = ((b255[:, None, :, :] - px[None, :, None, :]) ** 2).sum(-1)    # k x n x 32
    e = e.reshape(len(cand), len(px), 8, 4)
    ids = e.argmin(-1)                                                 # k x n x 8
    best = np.take_along_axis(e, ids[..., None], -1)[..., 0]           # k x n x 8
    tot = (best * wt[None, :, None]).sum(1)                            # k x 8
    ki, ti = np.unravel_index(tot.argmin(), tot.shape)
    return float(tot[ki, ti]), [int(v) for v in cand[ki]], int(ti), ids[ki, :, ti]


def enc_block_search(rgb, alpha, radius):
    best = None
    for flip in (0, 1):
        subs = (rgb[:, :2], rgb[:, 2:]) if flip == 0 else (rgb[:2, :], rgb[2:, :])
        asubs = (alpha[:, :2], alpha[:, 2:]) if flip == 0 else (alpha[:2, :], alpha[2:, :])
        bases, tables, idxs, tot = [], [], [], 0.0
        for sub, asub in zip(subs, asubs):
            wt = (asub.reshape(-1) > 0).astype(float)
            if wt.sum() == 0:
                wt[:] = 1.0
            e, b, t, i = _sub_search(sub.reshape(-1, 3), wt, radius)
            bases.append(b); tables.append(t); idxs.append(i); tot += e
        if best is None or tot < best[0]:
            best = (tot, flip, bases, tables, idxs)
    _, flip, bases, tables, idxs = best
    return _pack(flip, bases, tables, idxs)


def encode_search(rgba, w, h, radius=R):
    out = bytearray(); f = rgba.astype(np.float32)
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for by, bx in ((0, 0), (0, 4), (4, 0), (4, 4)):
                blk = f[ty + by:ty + by + 4, tx + bx:tx + bx + 4]
                hi, lo = enc_block_search(blk[..., :3], blk[..., 3], radius)
                av = 0
                for x in range(4):
                    for y in range(4):
                        av |= (int(blk[y, x, 3]) >> 4) << (4 * (x * 4 + y))
                out += struct.pack('<Q', av) + struct.pack('<Q', (hi << 32) | lo)
    return bytes(out)


def block_errors(data, rgba, w, h):
    rgb, _ = etc1a4.decode(data, w, h)
    e = ((rgb.astype(float) - rgba[..., :3]) ** 2).sum(-1) * (rgba[..., 3] > 0)
    # per 4x4 block in file order
    out = []
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for by, bx in ((0, 0), (0, 4), (4, 0), (4, 4)):
                out.append(e[ty + by:ty + by + 4, tx + bx:tx + bx + 4].sum())
    return np.array(out)


def hybrid(datas, rgba, w, h):
    errs = np.stack([block_errors(d, rgba, w, h) for d in datas])
    pick = errs.argmin(0); out = bytearray()
    for i, p in enumerate(pick):
        out += datas[p][i * 16:i * 16 + 16]
    return bytes(out), np.bincount(pick, minlength=len(datas))


def psnr(data, rgba, w, h):
    rgb, _ = etc1a4.decode(data, w, h)
    vis = rgba[..., 3] > 0
    mse = ((rgb.astype(float) - rgba[..., :3]) ** 2)[vis].mean()
    return 99.0 if mse == 0 else 10 * np.log10(255.0 ** 2 / mse)


if __name__ == '__main__':
    files = sorted(glob.glob('tex_dump_1012/*.png'))
    rows = []
    for fn in files:
        rgba = np.array(Image.open(fn).convert('RGBA')); h, w = rgba.shape[:2]
        base = bytes(w * h); mask = np.ones((h, w), bool)
        t = time.time(); L = etc1_enc.encode_rgba(rgba, base, w, h, touch_mask=mask); tl = time.time() - t
        t = time.time(); E = etc1_enc.encode_rgba_etcpak(rgba, base, w, h, touch_mask=mask); te = time.time() - t
        t = time.time(); S = encode_search(rgba, w, h); ts = time.time() - t
        H, picks = hybrid([L, E, S], rgba, w, h)
        r = (os.path.basename(fn), psnr(L, rgba, w, h), psnr(E, rgba, w, h), psnr(S, rgba, w, h), psnr(H, rgba, w, h), tl, te, ts, picks)
        rows.append(r)
        print('%-20s legacy %6.2f  etcpak %6.2f  search %6.2f  hybrid %6.2f   (s: %.0f %.1f %.0f)  picks L/E/S %s' % r, flush=True)
