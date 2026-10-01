"""Cast-vs-shift sanity check for color / contrast metrics.

Before trusting a metric on image pairs that are not perfectly aligned, check two things on your own content:

  1. false signal  = reading for a 1 px shift with no color change / reading for a real change   (small is good)
  2. cast / shift  = reading for a clearly visible color cast / reading for a 1 px shift          (large is good)

A ratio below 1 in (2) means a visible color cast scores lower than a one-pixel misregistration: the metric cannot
see color through misalignment, even if it looks "robust".

    python guide/shift_vs_cast.py                 # built-in test image (scikit-image astronaut)
    python guide/shift_vs_cast.py my_ref.png      # your own reference (sRGB, 8-bit)
    python guide/shift_vs_cast.py --shift 0.5     # other shift sizes (pixels, diagonal)
    python guide/shift_vs_cast.py --pyiqa msswd,fsim,cw_ssim,dists   # add metrics from pyiqa if installed

Needs numpy, scipy and scikit-image. Every metric below is a short function so you can copy it.
"""
from __future__ import annotations

import argparse

import numpy as np
from scipy import ndimage
from skimage import color, data, io, metrics, transform, util

SEED = 0


# ----------------------------------------------------------------------------- test images
def srgb_to_linear(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def shift(img, d):
    """Sub-pixel diagonal shift by d pixels (cubic spline, reflected borders)."""
    s = d / np.sqrt(2)
    return np.clip(np.stack([ndimage.shift(img[..., c], (s, s), order=3, mode='reflect') for c in range(3)], -1), 0, 1)


def color_cast(img, gains=(1.13, 1.00, 0.86)):
    """Pure white-balance cast: per-channel gains in linear light."""
    return linear_to_srgb(srgb_to_linear(img) * np.asarray(gains))


def real_change(img):
    """A mixed color + contrast change: channel gains, a tone curve and a black-level lift."""
    lin = srgb_to_linear(img) * np.array([1.06, 1.0, 0.92])
    lin = 0.02 + 0.98 * np.clip(lin, 0, 1) ** 1.12
    return linear_to_srgb(lin)


# ----------------------------------------------------------------------------- metrics (ref, test) -> float
def lab(img):
    return color.rgb2lab(img)


def de00_pixel(a, b):
    return float(color.deltaE_ciede2000(lab(a), lab(b)).mean())


def de00_block(a, b, w=32):
    """ΔE00 between block-mean Lab colors (average, then compare)."""
    h, wd = (a.shape[0] // w) * w, (a.shape[1] // w) * w
    def means(x):
        L = lab(x[:h, :wd])
        return L.reshape(h // w, w, wd // w, w, 3).mean(axis=(1, 3))
    return float(color.deltaE_ciede2000(means(a), means(b)).mean())


def de00_global(a, b):
    return float(color.deltaE_ciede2000(lab(a).reshape(-1, 3).mean(0), lab(b).reshape(-1, 3).mean(0)))


def _w1(x, y):
    """1-D Wasserstein distance between two samples: sort both and compare quantiles."""
    x, y = np.sort(x), np.sort(y)
    if len(x) != len(y):
        y = np.interp(np.linspace(0, 1, len(x)), np.linspace(0, 1, len(y)), y)
    return float(np.abs(x - y).mean())


def wasserstein_lab(a, b):
    """Sum over L*, a*, b* of the 1-D Wasserstein distance."""
    A, B = lab(a).reshape(-1, 3), lab(b).reshape(-1, 3)
    return sum(_w1(A[:, c], B[:, c]) for c in range(3))


def sliced_wasserstein_lab(a, b, n_dir=64):
    rng = np.random.default_rng(SEED)
    A, B = lab(a).reshape(-1, 3), lab(b).reshape(-1, 3)
    dirs = rng.normal(size=(n_dir, 3))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    pa, pb = np.sort(A @ dirs.T, axis=0), np.sort(B @ dirs.T, axis=0)
    return float(np.abs(pa - pb).mean())


def color_moments(a, b):
    def m(x):
        L = lab(x).reshape(-1, 3)
        mu, sd = L.mean(0), L.std(0)
        sk = np.cbrt(((L - mu) ** 3).mean(0))
        return np.concatenate([mu, sd, sk])
    return float(np.abs(m(a) - m(b)).sum())


def colorfulness(x):
    """Hasler & Süsstrunk (2003) on 0-255 sRGB."""
    R, G, B = (x * 255).transpose(2, 0, 1)
    rg, yb = R - G, 0.5 * (R + G) - B
    return np.hypot(rg.std(), yb.std()) + 0.3 * np.hypot(rg.mean(), yb.mean())


def colorfulness_ratio(a, b):
    return float(abs(colorfulness(b) / colorfulness(a) - 1))


def _hist(x, bins):
    L = lab(x).reshape(-1, 3)
    h, _ = np.histogramdd(L, bins=bins, range=[(0, 100), (-110, 110), (-110, 110)])
    return h / h.sum()


def hist_intersection(a, b, bins=16):
    return float(1 - np.minimum(_hist(a, bins), _hist(b, bins)).sum())


def hist_chi2(a, b, bins=8):
    """sqrt(χ²) so that it scales like the other distances."""
    ha, hb = _hist(a, bins), _hist(b, bins)
    s = ha + hb
    m = s > 0
    return float(np.sqrt(0.5 * ((ha[m] - hb[m]) ** 2 / s[m]).sum()))


def angle_mean(a, b):
    """Angular error (degrees) between the mean linear RGB of the two images."""
    u, v = srgb_to_linear(a).reshape(-1, 3).mean(0), srgb_to_linear(b).reshape(-1, 3).mean(0)
    return float(np.degrees(np.arccos(np.clip(u @ v / np.linalg.norm(u) / np.linalg.norm(v), -1, 1))))


def angle_pixel(a, b):
    u, v = srgb_to_linear(a).reshape(-1, 3) + 1e-6, srgb_to_linear(b).reshape(-1, 3) + 1e-6
    c = (u * v).sum(1) / np.linalg.norm(u, axis=1) / np.linalg.norm(v, axis=1)
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))).mean())


def one_minus_ssim(a, b):
    return float(1 - metrics.structural_similarity(a, b, channel_axis=-1, data_range=1.0))


def luminance(x):
    return lab(x)[..., 0]


def michelson_ratio(a, b):
    def m(x):
        p1, p99 = np.percentile(srgb_to_linear(x) @ [0.2126, 0.7152, 0.0722], [1, 99])
        return (p99 - p1) / (p99 + p1)
    return float(abs(m(b) / m(a) - 1))


def rms_ratio(a, b):
    def r(x):
        y = luminance(x)
        return y.std() / y.mean()
    return float(abs(r(b) / r(a) - 1))


METRICS = [
    ('per-pixel ΔE00', de00_pixel, 'pixel'),
    ('block-mean ΔE00 (32 px)', de00_block, 'shift'),
    ('image-mean ΔE00', de00_global, 'free'),
    ('Lab 1-D Wasserstein', wasserstein_lab, 'free'),
    ('sliced Wasserstein (Lab)', sliced_wasserstein_lab, 'free'),
    ('color moments (L1)', color_moments, 'free'),
    ('colorfulness |ratio-1|', colorfulness_ratio, 'free'),
    ('1 - histogram intersection', hist_intersection, 'free'),
    ('sqrt chi2 histogram', hist_chi2, 'free'),
    ('angle of mean RGB (deg)', angle_mean, 'free'),
    ('per-pixel RGB angle (deg)', angle_pixel, 'pixel'),
    ('1 - SSIM', one_minus_ssim, 'pixel'),
    ('Michelson |ratio-1| *', michelson_ratio, 'free'),
    ('RMS contrast |ratio-1| *', rms_ratio, 'free'),
]


def pyiqa_metrics(names):
    import pyiqa  # noqa: F401  (optional dependency)
    import torch
    out = []
    for n in names:
        m = pyiqa.create_metric(n, device='cpu')
        lower = m.lower_better

        def f(a, b, m=m, lower=lower):
            ta = torch.from_numpy(a.transpose(2, 0, 1)).float()[None]
            tb = torch.from_numpy(b.transpose(2, 0, 1)).float()[None]
            v = float(m(tb, ta))
            return v if lower else 1 - v
        out.append((f'pyiqa {n}' + ('' if lower else ' (1 - x)'), f, '?'))
    return out


# ----------------------------------------------------------------------------- main
def run(ref, d=1.0, extra=()):
    tests = {
        'real': real_change(ref),
        'shift': shift(ref, d),
        'cast': color_cast(ref),
    }
    rows = []
    for name, f, cls in list(METRICS) + list(extra):
        real, sh, ca = f(ref, tests['real']), f(ref, tests['shift']), f(ref, tests['cast'])
        rows.append((name, cls, real, sh, sh / real if real else float('nan'), ca, ca / sh if sh else float('inf')))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('image', nargs='?', help='reference image (sRGB); default: scikit-image astronaut')
    ap.add_argument('--shift', type=float, default=1.0, help='diagonal shift in pixels (default 1)')
    ap.add_argument('--size', type=int, default=512, help='resize the longer side to this many pixels (default 512)')
    ap.add_argument('--pyiqa', default='', help='comma-separated pyiqa metric names to add')
    args = ap.parse_args()
    ref = io.imread(args.image) if args.image else data.astronaut()
    ref = util.img_as_float(ref[..., :3])
    s = args.size / max(ref.shape[:2])
    if s < 1:
        ref = np.clip(transform.rescale(ref, s, channel_axis=-1, anti_aliasing=True), 0, 1)
    extra = pyiqa_metrics([n for n in args.pyiqa.split(',') if n]) if args.pyiqa else []
    rows = run(ref, args.shift, extra)
    print(f'reference {ref.shape[1]}x{ref.shape[0]}, shift {args.shift:g} px, cast = linear gains (1.13, 1.00, 0.86)\n')
    head = f"{'metric':<28}{'class':<7}{'real change':>12}{'shift only':>12}{'false sig.':>11}{'cast only':>11}{'cast/shift':>11}"
    print(head)
    print('-' * len(head))
    for name, cls, real, sh, fs, ca, cs in rows:
        print(f'{name:<28}{cls:<7}{real:>12.4g}{sh:>12.4g}{fs:>11.3f}{ca:>11.4g}{cs:>11.1f}')
    print('\nfalse sig. = shift only / real change (small is good); cast/shift < 1 means the metric cannot see a '
          'visible cast through a shift of this size.\n* contrast metrics: they should ignore the cast, so only the '
          'first three columns matter.')


if __name__ == '__main__':
    main()
