# Contributing

Thanks for helping keep this list complete and its labels honest. Every entry lives in a YAML file under
[`data/`](data/); `README.md`, `CODE.md` and the interactive page in `docs/` are generated from those files, so
please **do not edit the generated files by hand**.

## Quick start

1. Fork the repository and create a branch.
2. Edit the right file under `data/metrics/` (see the table below).
3. Regenerate and validate:

   ```bash
   pip install -r requirements.txt
   python scripts/build.py
   ```

4. Commit the YAML change together with the regenerated `README.md`, `CODE.md` and `docs/index.html`, and open a
   pull request. CI runs `python scripts/build.py --check` and fails if the data is invalid or the generated files are
   out of date.

Not comfortable with a PR? Open an issue with the [Add a metric](../../issues/new?template=add-metric.yml) or
[Report a broken link or wrong label](../../issues/new?template=broken-link.yml) form instead.

## Which file?

| File | Section |
|:--|:--|
| `data/metrics/formula.yaml` | Color-difference formulas & uniform color spaces |
| `data/metrics/spatial.yaml` | Spatial & visibility-based color difference |
| `data/metrics/friqa.yaml` | Color-aware full-reference IQA |
| `data/metrics/contrast.yaml` | Contrast, tone & dynamic range |
| `data/metrics/photo.yaml` | Perceptual color difference of photographs |
| `data/metrics/global.yaml` | Global statistics & color histograms |
| `data/metrics/patch.yaml` | Patch distributions & shift-tolerant structure |
| `data/metrics/deep.yaml` | Deep-feature metrics robust to misalignment |
| `data/metrics/protocol.yaml` | Evaluation protocols for misaligned ground truth |
| `data/metrics/wb.yaml` | White balance & illuminant error |
| `data/metrics/chart.yaml` | Test charts & camera standards |
| `data/metrics/study.yaml` | Benchmarks, psychophysics & surveys |
| `data/datasets.yaml` | Datasets |
| `data/tools.yaml` | Tools & libraries |
| `data/resources.yaml` | Tutorials, books, related lists |

If an entry fits several sections, put it where its main contribution is. Entry order inside a file does not matter;
the build sorts them.

## Entry format

```yaml
- name: MS-SWD                          # short name shown in bold (metric name or acronym)
  title: Multiscale Sliced Wasserstein Distances as Perceptual Color Difference Measures
  venue: ECCV                           # CVPR, ECCV, IEEE TIP, Color Res Appl, JOSA A, ISO, arXiv, ...
  year: 2024
  paper: https://doi.org/10.1007/978-3-031-73668-1_25   # prefer DOI / CVF / ECVA, else arXiv abs page
  code: https://github.com/real-hjq/MS-SWD              # official repository, if any
  status: code                          # see below
  impl:                                 # other implementations: toolboxes, pip packages
    - label: pyiqa · `msswd`            # "package · `function or metric name`"
      url: https://github.com/chaofengc/IQA-PyTorch
  framework: PyTorch                    # optional
  align: free                           # pixel | shift | free | chart | pair (see below)
  color: dedicated                      # dedicated | chromatic | partial | luminance (see below)
  output: score                         # score | map | components | params | text (optional)
  tldr: One neutral sentence on what the metric computes, ideally 12-28 words.
  note: Optional practical remark (e.g. "fix the random seed").
```

### `align`: what the metric needs from the image pair

| Value | Use when |
|:--|:--|
| `pixel` | it compares values at the same pixel or window (per-pixel ΔE, SSIM, LPIPS, visible-difference predictors) |
| `shift` | the paper designs for or demonstrates tolerance to sub-pixel to few-pixel shifts (anti-aliasing, coarse scales, local search, block means) |
| `free` | it compares global statistics or distributions, or is a per-image measure, so position is discarded |
| `chart` | it is measured on a test chart against known reference values |
| `pair` | it is a formula for two colors or one stimulus |

Label what the method *needs*, not what it was evaluated on. If the paper does not discuss misalignment and the
mechanism compares positions, use `pixel` and say so in `note`.

### `color`: does the metric see color?

| Value | Use when |
|:--|:--|
| `dedicated` | it was built and validated for color difference (on color-difference data) |
| `chromatic` | it has explicit chromatic channels or operates on color values (histograms, FSIMc, FLIP) |
| `partial` | it takes color input but was not designed or tested for color (most deep metrics) |
| `luminance` | it works on luminance only (GMSD, TMQI, CW-SSIM) |

### `status`

| `status` | Use when |
|:--|:--|
| `code` | official code is public (`code` points to it) |
| `toolbox` | no official code, but a maintained toolbox or package implements it (list it under `impl`) |
| `unofficial` | only a third-party implementation exists (`code` points to it) |
| `spec` | the entry is a standard or recommendation that you implement from the document |
| `coming-soon` | the repository is a placeholder or says code will be released |
| `no-code` | no public code was found |

The build refuses entries that break these rules (for example `status: toolbox` without any `impl`, or a `code`
URL on a `no-code` entry).

## What belongs here

Included:

- formulas and spaces for color difference, including HDR / wide gamut;
- full-reference image metrics with a color or contrast component, or validated on color-difference data;
- metrics designed to tolerate misaligned or geometrically different references, even when color is not their focus
  (label them `partial`);
- white-balance / illuminant error measures, test-chart metrics and camera standards for color and tone;
- evaluation protocols that show how misaligned ground truth is handled in practice;
- psychophysical studies, benchmarks and surveys of these metrics, plus datasets.

Out of scope:

- no-reference quality models without a color component;
- color constancy, colorization or color-transfer methods themselves (cite them in Related Lists instead);
- video-only temporal metrics.

## Style

- English only, neutral tone: no "novel", "state-of-the-art" or "outperforms". Describe what the metric computes.
- Use the paper's own capitalization for titles and method names.
- One entry per paper; if a paper defines several variants, mention them in `note`.

## For maintainers

- Suggested GitHub repository settings (the **About** box): description `A curated list of color and contrast metrics for images, sorted by whether they need a pixel-aligned reference: ΔE formulas, S-CIELAB, FLIP, ColorVideoVDP, MS-SWD, CD-Flow, misalignment-robust deep metrics, white-balance error and camera chart standards.`; topics `color-difference`, `color-science`, `image-quality-assessment`, `perceptual-metrics`, `ciede2000`, `misalignment`, `camera-isp`, `low-level-vision`, `awesome-list`; website: the GitHub Pages URL.
- `config.yaml` holds the GitHub owner and repository name used in badges and in the link to the interactive page.
  After changing it, run `python scripts/build.py`.
- The interactive page is `docs/index.html`. Enable it once under **Settings → Pages → Build and deployment →
  Deploy from a branch → `main` / `docs`**.
- `.github/workflows/ci.yml` validates every push and pull request. `.github/workflows/links.yml` runs
  [lychee](https://github.com/lycheeverse/lychee) every Monday and opens an issue if links are broken; its settings
  are in `lychee.toml`.
- When you re-check links by hand, update `checked` in `config.yaml`.
