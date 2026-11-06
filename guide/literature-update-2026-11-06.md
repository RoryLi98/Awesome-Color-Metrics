# Literature update — 2026-11-06

[English](literature-update-2026-11-06.md) · [简体中文](literature-update-2026-11-06.zh-CN.md)

This refresh adds **9 publications and 2 datasets** to Awesome Color Metrics: **164 entries**,
**91 with runnable implementations**, **58 labeled shift-tolerant or alignment-free**, and **15 datasets**.
The table structure follows Awesome Neural ISP: concise problem–method–evaluation summaries, explicit release
status, and separate dates for a literature refresh and the full link audit. The full audit date remains
**2026-10-11**; only the sources described below were checked for this refresh.

本次补充 **9 篇论文、2 个数据集**，采用 Awesome Neural ISP 的简洁摘要与来源记录方式。
重点区分局部颜色判别阈值、整图色差、属性相似度、风格匹配与颜色真实感；文献更新日期不代表重新检查了全库链接。

## Added publications and primary sources

| Entry | Primary source checked | Placement and interpretation |
|:--|:--|:--|
| Conformally-Euclidean line element | [arXiv:2606.12588, v2](https://arxiv.org/abs/2606.12588v2) | Formulas; a luminance-scaled local line element and derived coordinates, not a whole-image score. |
| V1 Fisher color metric | [arXiv:2603.24356](https://arxiv.org/abs/2603.24356) and its [full text](https://arxiv.org/html/2603.24356v1) | Formulas; a 17-parameter threshold model fitted to four datasets. Retained as a preprint, without inferring photographic validation from its reported fit. |
| IPT-LCs | [Optics Express, DOI 10.1364/OE.609373](https://doi.org/10.1364/OE.609373); publisher abstract deposited with [Crossref](https://api.crossref.org/works/10.1364/OE.609373) | Formulas; 980 highlight pairs, 194–977 cd/m², with a 203 cd/m² D65 adapting white. |
| EDOKS | [Discover Artificial Intelligence, DOI 10.1007/s44163-026-02424-4](https://doi.org/10.1007/s44163-026-02424-4), [arXiv full text](https://arxiv.org/html/2601.19680v1), and [official implementation](https://github.com/antdimarino/EDOKS) | Color-aware FR-IQA; Gabor-signature EMD plus per-pixel Oklab distance. The color term requires alignment even though the texture term uses distributions. Journal publication is dated 2026-10-17. |
| TPIPS | [arXiv:2607.18237](https://arxiv.org/abs/2607.18237), [author project](https://peterwang512.github.io/TPIPS/), and [official repository](https://github.com/adobe-research/TPIPS) | Deep-feature similarity; NeurIPS 2026 is stated by both the author page and repository citation. Text-conditioned subject-color or lighting similarity is not calibrated ΔE. |
| Color-difference model evaluation review | [arXiv:2601.13402, v3](https://arxiv.org/abs/2601.13402v3) | Studies; compares measures for assessing discrimination models, including coordinate invariance and scale optimization. |
| Empirical 3D color metric field | [Journal of Vision, DOI 10.1167/jov.26.9.3](https://doi.org/10.1167/jov.26.9.3) and [publisher full text](https://jov.arvojournals.org/article.aspx?doi=10.1167/jov.26.9.3) | Studies; eight observers, 35 colors and seven orientations provide local ellipsoids and an interpolated metric field. |
| Texture-dependent color tolerances | [JOSA A, DOI 10.1364/JOSAA.588315](https://doi.org/10.1364/JOSAA.588315); publisher abstract deposited with [Crossref](https://api.crossref.org/works/10.1364/JOSAA.588315) | Studies; ten textures, 11 color centers, 18 directions and 26 observers. The paper describes a dataset; a separate downloadable release was not confirmed. |
| Metamer mismatching and discrimination | [Color Research & Application, DOI 10.1002/col.22976](https://doi.org/10.1002/col.22976); publisher abstract deposited with [Crossref](https://api.crossref.org/works/10.1002/col.22976) | Studies; tests an explanation for variation in color-discrimination ellipsoids, rather than proposing an image-quality score. |

Publisher metadata and abstracts were reconciled with Crossref where available. An arXiv identifier is retained
for a preprint unless a journal record or an explicit official acceptance statement establishes a venue.
`no-code` means no public implementation was confirmed in this search, not that an implementation cannot exist.
Optica's pages redirected to an automated-access challenge and Wiley returned HTTP 403; the corresponding
descriptions use the publisher-deposited Crossref abstracts linked above, rather than claiming full-text access.

## Code and dataset evidence

- **EDOKS:** the official repository contains `edoks/edoks.py`, `edoks/oklab.py`, `edoks/emd.py`,
  the clustering implementation and a C EMD core, with installation and inference instructions.
  These files establish a released implementation rather than a placeholder README. The package is labeled Python / C.
- **TPIPS:** the official repository contains the embedding, early-fusion and activation-distance implementations,
  `tpips/load.py`, and inference, evaluation, training and data-download scripts. Its README links model checkpoints
  and documents the released [`tpips` package](https://pypi.org/project/tpips/).
- **TPIPS Odd-One-Out:** the official README links the [train/validation/test dataset](https://huggingface.co/datasets/sywang/tpips-odd-one-out)
  and lists 26 GB. Five annotators judge synthetic triplets for specified visual attributes.
- **TPIPS Cross-Algorithm 2AFC:** the README separately links the [held-out algorithm test set](https://huggingface.co/datasets/sywang/tpips-2afc)
  and lists 1.7 GB. It covers editing, compositing, novel-view synthesis and image-to-3D outputs.

Repository file trees and release instructions were checked. The metrics were not installed or benchmarked,
and the datasets and model checkpoints were not downloaded. Dataset sizes above are the authors' listed sizes.

## Existing entries and label corrections

- **CD-Attention:** already present; retained one record and revised its title and summary from the publisher's
  [abstract](https://api.crossref.org/works/10.3390/app15052704). The summary connects local CNN features,
  global ViT context, deformable attention and high/low-frequency prediction.
- **MIS acceptability:** already present under white-balance error; revised from the
  [official CIC abstract](https://library.imaging.org/cic/articles/33/1/6). The 3,465 observations are trials,
  and the two proposed corrections concern appearance weighting and spatial/illuminance factors.
  Acceptability is distinct from difference magnitude or aesthetic preference. Its WB-protocol alignment label
  does not establish invariance to arbitrary viewpoint changes.
- **Photo CD (Niu 2026):** the [Crossref record](https://api.crossref.org/works/10.1117/12.3117003)
  identifies CVAR 2026 as the proceedings title; clarified the venue as **CVAR (Proc SPIE)**.
- **MRFEM-KL:** changed `shift` to `pixel`. The previous record itself noted that misalignment tolerance was not
  stated; distribution comparison in spatially corresponding sliding windows is insufficient evidence for a
  shift-tolerant label. Retained as a comparison baseline with an explicit note. This conservative correction
  offsets the additional alignment-free TPIPS entry, leaving the tolerant total at 58.
- **Partial color sensitivity:** clarified that the label means the method is not validated as a dedicated
  color-difference measure. This accommodates semantic color-attribute judgments without implying calibrated
  sensitivity to white-balance casts or other low-level chromatic changes.
- **Release labels:** the Markdown generator now visibly labels a linked placeholder repository “coming soon,”
  consistent with the distinction between released implementations and announced code in Awesome Neural ISP.

The research-thread summaries now distinguish correspondence relaxation from geometric invariance, local
threshold models from photographic difference, and text-conditioned similarity from style or realism scores.

## Search scope

Searches covered arXiv titles/abstracts and Crossref titles for color/colour difference, perceptual color metrics,
color image quality, HDR quality and perceptual similarity with misaligned references, through **2026-11-06**.
Results were deduplicated against existing names and DOI/arXiv links, then checked against publisher abstracts,
author pages and official repository contents. Earlier missing publications directly relevant to the color
metric taxonomy were included alongside 2026 work. The 2025 spatial-grating paper
[DOI 10.1002/jsid.2100](https://doi.org/10.1002/jsid.2100) was checked but not added as an independent metric:
the existing 2024 Riemannian sinusoidal entry already covers that model family.

This is a scoped literature refresh, not an exhaustive search of all journal and conference proceedings.
Generic no-reference IQA without a color component, colorization/color-transfer algorithms themselves,
unrelated mathematical graph-coloring results and video-only temporal metrics were excluded.

## Validation

Run `python scripts/build.py` and `python scripts/build.py --check` to validate the YAML and reproduce
`README.md`, `README.zh-CN.md`, `CODE.md`, `CODE.zh-CN.md`, `docs/index.html` and `docs/zh-CN.html`.
Counts and paper/code links are generated from the data files;
the generated pages are not edited by hand.
