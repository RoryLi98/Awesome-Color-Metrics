# Color Metrics 101: Measuring Color and Contrast Change, Aligned or Not

You have a reference image and a test image (an ISP output, a re-capture, a compressed or edited version) and want
to know **how much the color and contrast changed**. If every pixel of the test image sits exactly on its
counterpart in the reference, almost any metric works. If the two are off by even one pixel, most of them start
measuring edges instead of color. This page explains why, what to use instead, and how to check a metric on your
own images. Metrics named here are listed with papers and code in the [main list](../README.md).

A runnable check is in [`shift_vs_cast.py`](shift_vs_cast.py) (NumPy + scikit-image, about 250 lines).

## 1. The problem in one formula

```
I2(x) = P[ I1( T(x) ) ] + n
```

| Symbol | Meaning | You want it? |
|:--|:--|:--|
| `I1`, `I2` | reference and test image | |
| `T` | geometric transform between them (shift, homography, lens distortion, parallax) | no, it is a nuisance |
| `P` | photometric change: gains, color matrix, tone curve, saturation, local contrast | **yes, this is what you measure** |
| `n` | noise | no |

"Aligned" means `T` has been removed so completely that `x` points to the same scene point in both images.
Registration (SIFT + RANSAC, ECC, optical flow) usually leaves a residual of a fraction of a pixel to a pixel, and
more near depth edges.

## 2. First decide what you are asking

There are two different questions, and metrics are built for one or the other:

1. **"How different do they look?"** One perceptual number. FLIP, ColorVideoVDP, LPIPS, DISTS, MS-SWD, CD-Net
   answer this.
2. **"How much did color change, and how?"** A quantity with units that you can attribute: ΔE00, its split into
   lightness / chroma / hue, a fitted tone curve and color matrix. This is what an ISP engineer usually needs.

A single score cannot tell a white-balance error from a saturation change from a contrast change. Use score metrics
as sentinels, and attributable quantities as the main result.

## 3. Color difference: CIELAB and ΔE

- Convert both images from sRGB to linear RGB, then to XYZ and CIELAB with the same white point (sRGB is D65; chart
  data are often D50, so adapt with Bradford).
- **ΔE\*ab (CIE76)** is Euclidean distance in CIELAB. **CIEDE2000 (ΔE00)** reweights lightness, chroma and hue and
  is the standard today; always say which one you report, the numbers differ a lot on saturated colors.
- Split the difference: **ΔL\*** (lightness, e.g. exposure), **ΔC\*** (chroma, e.g. saturation), **ΔH\*** (hue,
  e.g. white balance or a hue twist). Very different errors can give the same ΔE00; the split tells them apart and
  points to different fixes.
- **ΔE vs ΔC**: chart reports often give ΔC00 (ΔE without the lightness term) because small exposure errors inflate
  ΔE. Note that ΔC00 still contains hue.
- For HDR or wide-gamut content use ΔE ITP, Jzazbz or CAM16-UCS; no HDR color-difference model is settled yet.

Rough reading of ΔE00 between uniform patches: below 1 is hard to see side by side, 2–3 is noticeable, above 5 is an
obvious difference. These thresholds do not transfer directly to whole images, where content, background and the
spatial pattern of the error all matter.

## 4. Contrast is a family, not one number

| Kind | How | Notes |
|:--|:--|:--|
| Global | RMS (std / mean of luminance), Michelson with 1st / 99th percentiles | RMS also counts noise and sharpening as contrast |
| Local, per band | Peli band-limited contrast: band-pass / low-pass one octave below | gives a map per scale |
| Tone curve | scatter of test vs reference luminance, fitted curve: slopes in shadows / mid-tones / highlights, black level, clipping | the most interpretable |
| SSIM contrast term | `c = 2σxσy / (σx² + σy²)` | symmetric: a contrast ratio of 0.6 and of 1/0.6 give the same 0.88, so it cannot say up or down |
| Visibility | DRIM: loss, amplification and reversal of visible contrast | only reports changes in visibility, not mild tone-curve changes |

## 5. Aligned pairs: what to report

With exact correspondence every pixel is a sample pair, and the strongest tools are available.

**Color**

- ΔE00 map with mean, median, **p95**, max and the fraction of pixels above a threshold (the mean hides local
  problems).
- ΔL\* / ΔC\* / ΔH\* maps or means.
- A fitted model `test ≈ curve(M · ref)` in linear RGB (3×3 matrix then per-channel monotone curve, the order of a
  camera's CCM and gamma). Fit by alternating: fix the curve, fit the matrix; fix the matrix, fit the curve; 3–4
  rounds. Report the parameters and the **residual ΔE00**.

**Contrast**

- Tone-curve slopes, black level and clipping.
- Local contrast ratio maps `σ_test / σ_ref` per band (mask flat regions where σ is near 0).

**Pitfalls that remain even when aligned**

1. *Warping removes contrast.* Interpolation is a low-pass filter; one bicubic warp can cut the finest band by a few
   percent, as much as the effect you may be measuring. Put both images through the same resampling, or measure it.
2. *Color space.* Decode sRGB to linear before fitting matrices; keep white points consistent.
3. *Clipping.* Mask blown highlights and crushed shadows; ΔE and slopes are meaningless there.
4. *Noise and sharpening look like contrast.* Report the finest band separately.
5. *Gauge freedom.* Curve and matrix can trade off against each other. Report their combined effect (ΔE00 on a set
   of standard colors), not individual matrix entries.

## 6. Misaligned pairs: why per-pixel metrics fail

With a one-pixel residual, every edge becomes a color difference: the ΔE00 map of a shifted copy of the same image
looks like an edge map. Two facts make this worse than it sounds:

- It is a **bias, not noise**. Distances are never negative, so misregistration only pushes the mean up (Jensen's
  inequality), and the same shift does the same thing every time. Averaging more images does not remove it.
- It scales with the image content, not with the color change. The subtler the real difference, the larger the
  share of the reading that is fake.

**The rule: average, then compare.** Compute block means (or distributions) first, the difference second. A block of
width `W` shifted by `d` exchanges only about `d / W` of its content, so the false signal falls quickly with block
size. Measured on the scikit-image astronaut (512 px) with the mixed color + contrast change of the script:

| Shift | per-pixel ΔE00 | W = 4 | W = 16 | W = 32 | W = 128 | image mean |
|--:|--:|--:|--:|--:|--:|--:|
| 0.25 px | 0.153 | 0.080 | 0.042 | 0.030 | 0.012 | 0.008 |
| 0.5 px | 0.311 | 0.160 | 0.083 | 0.060 | 0.024 | 0.016 |
| 1 px | 0.602 | 0.318 | 0.167 | 0.119 | 0.048 | 0.032 |
| 2 px | 0.930 | 0.609 | 0.331 | 0.238 | 0.096 | 0.062 |

*False signal = ΔE00 reading for the shift alone ÷ reading for the real change on aligned images. Same formula
everywhere; only the order of averaging changes.*

Rule of thumb: blocks of **16–32× the expected residual** keep the false signal near or below 0.1. You lose spatial
detail, so report block p95 as well as the mean. You lose little information about the change itself when it is
global or slowly varying (gains, matrices and global tone curves are a handful of parameters). For linear parts the
block mean in linear RGB is exact; for a nonlinear tone curve, prefer low-variance blocks when fitting.

**Five ways to cope with misalignment, and what each costs**

| Strategy | Example | Cost |
|:--|:--|:--|
| A. Align, then measure | warp + any pixel metric | interpolation loss and residual bias |
| B. Aggregate, then compare | block means, histograms, distributions, MS-SWD | loses localization |
| C. Tolerant matching | neighborhood-minimum ΔE, shift search (cPSNR), contextual matching | also hides genuine small differences |
| D. Fit a parametric model | curve + matrix on block means | changes outside the model go into the residual |
| E. Joint estimation | ECC-style registration invariant to `P` | photometric change is cancelled, not measured |

To answer "how much did color change" use **B + D**: aggregate to clean sample pairs, then fit the model on them.

## 7. Two traps

**Blind is not robust.** SSIM normalizes local mean and variance, so a pure channel-gain cast that is clearly visible
(ΔE00 ≈ 3.4) moves 1 − SSIM by only 0.0024, about 1/56 of what a 1 px shift does. In a misalignment test SSIM looks
wonderfully stable, because it sees almost nothing of the cast. CW-SSIM, texture statistics and deep Gram-matrix
metrics share this property. Always report two numbers for a metric: its response to a real change and its reading
under misalignment alone.

**Sampling is not misalignment.** Photographing a display or print adds display grid → lens blur → sensor grid. The
resulting moiré and aliasing create color errors that registration cannot remove. Low-pass optically or digitally,
or avoid high-frequency regions. CameraVDP is a worked example of correcting and quantifying the camera's own
geometry, MTF, vignetting and color before judging a display.

**The only strictly immune option** is a test chart in a controlled scene: read only the central part of each patch,
cropping inward by at least the expected misregistration.

## 8. The cast-vs-shift test

Run the script on your own reference image:

```bash
pip install numpy scipy scikit-image
python guide/shift_vs_cast.py my_reference.png            # 1 px diagonal shift
python guide/shift_vs_cast.py my_reference.png --shift 0.5
```

It builds three test images (a mixed real change, a 1 px shift with no color change, and a pure white-balance cast
with linear gains 1.13 / 1.00 / 0.86) and prints, for each metric, the false signal and **cast ÷ shift**. Output on
the built-in astronaut image:

| Metric | Class | False signal (shift ÷ real) | Cast ÷ shift |
|:--|:--|--:|--:|
| per-pixel ΔE00 | pixel | 0.602 | 1.2 |
| per-pixel RGB angle | pixel | 0.542 | 1.3 |
| 1 − SSIM | pixel | 0.718 | 0.02 |
| block-mean ΔE00 (32 px) | shift | 0.119 | 6.9 |
| 1 − histogram intersection (Lab 16³) | free | 0.127 | 3.9 |
| √χ² histogram (Lab 8³) | free | 0.223 | 2.2 |
| image-mean ΔE00 | free | 0.032 | 35 |
| sliced Wasserstein (Lab) | free | 0.021 | 41 |
| Lab 1-D Wasserstein | free | 0.022 | 43 |
| color moments | free | 0.011 | 42 |
| colorfulness ratio | free | 0.010 | 204 |
| angle of mean RGB | free | 0.005 | 384 |

Read it like this: cast ÷ shift below 1 means a visible cast scores lower than a 1 px misregistration, so the
metric cannot see color through that much misalignment. Histogram distances depend strongly on the bin size.
Numbers change with the image; the ordering is what matters.

An earlier single-image run (640×640 natural image, 1 px shift, official code or pyiqa) placed other metrics as
follows: MS-SWD 37, DeepDC (substitute VGG weights) 1.7–9.8 across four images, FLIP 1.8, DeepSSIM (substitute
weights) 0.65–1.6 across four images, ColorVideoVDP 0.5, VSI 0.18, FSIMc 0.08 and CW-SSIM 0.07. Use
`--pyiqa msswd,fsim,vsi,cw_ssim,dists` to repeat this for pyiqa metrics on your data. FLIP and ColorVideoVDP are
not wrong here; a 1 px shift *is* a visible difference to a visible-difference model, which is why such models need
aligned input.

## 9. What to report

For a comparison of two ISPs (or an ISP against a reference), six numbers say more than one:

1. **ΔE00 of the fitted transform** on a set of standard colors (e.g. the 24 ColorChecker colors): the systematic
   color change, immune to misalignment when fitted on block means.
2. **Block-mean ΔE00, mean and p95**, with block size stated: where it changed.
3. **ΔL\* / ΔC\* / ΔH\*** of the block means: what kind of change.
4. **Tone-curve parameters** (slopes, black level, clipping) and a contrast-distribution distance per band: how
   contrast changed.
5. **One perceptual cross-check** that tolerates misalignment, such as MS-SWD.
6. **The noise floor** of every metric: its reading on two captures with no change, or on a shifted copy. Do not
   claim differences below it.

## 10. Choosing a metric

- Exact alignment and you need attribution → ΔE00 map + decomposition, curve + matrix fit, local contrast ratios
  ([Spatial](../README.md#spatial--visibility-based-color-difference), [Formulas](../README.md#color-difference-formulas--uniform-color-spaces)).
- Exact alignment and you need "how visible" → ColorVideoVDP, FLIP, HDR-VDP-3.
- Residual around a pixel → block means with the same formulas; MS-SWD or CD-Flow as the perceptual number
  ([Photographs](../README.md#perceptual-color-difference-of-photographs)).
- Different viewpoints or cameras → distributions only: Lab Wasserstein, MS-SWD, CD-Net; deep metrics such as DISTS
  or DeepSSIM only as sentinels ([Deep](../README.md#deep-feature-metrics-robust-to-misalignment)).
- Controlled scene → test charts ([Charts](../README.md#test-charts--camera-standards)).
- Before using any metric on misaligned data → run the cast-vs-shift test.
