# 文献更新 — 2026-11-06

[English](literature-update-2026-11-06.md) · [简体中文](literature-update-2026-11-06.zh-CN.md)

本次新增 **9 篇论文、2 个数据集**。现有 **164 条记录、91 项可用实现、58 条容忍小幅错位或无需像素配准的记录、15 个数据集**。摘要与状态记录参考 Awesome Neural ISP 的组织方式，分别记录定向文献更新与全库链接检查。全库检查日期仍为 **2026-10-11**；本次仅核对下列变更条目的来源。

## 新增论文与一手来源

| 条目 | 核对来源 | 分类与解释 |
|:--|:--|:--|
| Conformally-Euclidean line element | [arXiv:2606.12588 v2](https://arxiv.org/abs/2606.12588v2) | 色差公式。依赖亮度的局部线元及推导坐标，不是整图评分。 |
| V1 Fisher color metric | [arXiv:2603.24356](https://arxiv.org/abs/2603.24356)、[全文](https://arxiv.org/html/2603.24356v1) | 色差公式。以四组阈值数据拟合 17 参数模型，保留预印本身份，不能据拟合成绩推断摄影图像验证。 |
| IPT-LCs | [Optics Express，DOI 10.1364/OE.609373](https://doi.org/10.1364/OE.609373)、出版方提交至 [Crossref 的摘要](https://api.crossref.org/works/10.1364/OE.609373) | 色差公式。980 对高光刺激，亮度 194–977 cd/m²，适应白为 203 cd/m² 的 D65。 |
| EDOKS | [Discover Artificial Intelligence，DOI 10.1007/s44163-026-02424-4](https://doi.org/10.1007/s44163-026-02424-4)、[arXiv 全文](https://arxiv.org/html/2601.19680v1)、[官方实现](https://github.com/antdimarino/EDOKS) | 彩色全参考 IQA。Gabor 特征 EMD 加逐像素 Oklab 距离。纹理项使用分布，但颜色项仍需配准。期刊出版日期为 2026-10-17。 |
| TPIPS | [arXiv:2607.18237](https://arxiv.org/abs/2607.18237)、[作者项目页](https://peterwang512.github.io/TPIPS/)、[官方仓库](https://github.com/adobe-research/TPIPS) | 深度特征相似度。作者页与仓库引用均注明 NeurIPS 2026。文字条件下的主体颜色或光照相似度不等同于标定的 ΔE。 |
| Color-difference model evaluation review | [arXiv:2601.13402 v3](https://arxiv.org/abs/2601.13402v3) | 基准与综述。比较颜色判别模型的评价方式，包括坐标不变性与尺度优化。 |
| Empirical 3D color metric field | [Journal of Vision，DOI 10.1167/jov.26.9.3](https://doi.org/10.1167/jov.26.9.3)、[出版方全文](https://jov.arvojournals.org/article.aspx?doi=10.1167/jov.26.9.3) | 基准与研究。八位观察者、35 个参考色、七种方向，用局部椭球构建插值度量场。 |
| Texture-dependent color tolerances | [JOSA A，DOI 10.1364/JOSAA.588315](https://doi.org/10.1364/JOSAA.588315)、出版方提交至 [Crossref 的摘要](https://api.crossref.org/works/10.1364/JOSAA.588315) | 基准与研究。十种纹理、11 个颜色中心、18 个方向及 26 位观察者。论文描述了数据集，但未确认独立下载版本。 |
| Metamer mismatching and discrimination | [Color Research & Application，DOI 10.1002/col.22976](https://doi.org/10.1002/col.22976)、出版方提交至 [Crossref 的摘要](https://api.crossref.org/works/10.1002/col.22976) | 基准与研究。检验颜色判别椭球变化的解释，不是图像质量评分。 |

有可用记录时，将出版方元数据与摘要和 Crossref 对照。没有期刊记录或官方接收声明时保留 arXiv 身份。`no-code` 表示本次检索未确认公开实现，不能理解为实现绝不存在。

Optica 页面跳转至自动访问验证，Wiley 返回 HTTP 403；相关描述依据上列出版方提交的 Crossref 摘要，不声称已读取这些出版方全文。

## 实现与数据集证据

- **EDOKS：** 官方仓库包含 `edoks/edoks.py`、`edoks/oklab.py`、`edoks/emd.py`、聚类实现与 C EMD 核心，并有安装和推理说明，因此标为已发布实现，语言为 Python / C。
- **TPIPS：** 官方仓库含嵌入、早期融合、激活距离实现、`tpips/load.py`，以及推理、评测、训练、数据下载脚本。README 链接模型权重并说明已发布的 [`tpips` 程序包](https://pypi.org/project/tpips/)。
- **TPIPS Odd-One-Out：** 官方 README 链接[训练/验证/测试数据集](https://huggingface.co/datasets/sywang/tpips-odd-one-out)，作者列出大小为 26 GB。每个合成三元组由五位标注者按指定视觉属性判断。
- **TPIPS Cross-Algorithm 2AFC：** README 独立链接[保留算法测试集](https://huggingface.co/datasets/sywang/tpips-2afc)，作者列出大小为 1.7 GB，覆盖编辑、合成、新视角合成与图像到三维的输出。

本次核对了仓库文件树与发布说明，没有安装或跑分这些指标，也没有下载数据集和模型权重。数据大小采用作者列出的数值。

## 既有记录与标签修订

- **CD-Attention：** 原列表已有，保留单条记录，依据[出版方摘要](https://api.crossref.org/works/10.3390/app15052704)修正标题与摘要，说明局部 CNN、全局 ViT、可变形注意力及高低频预测的关系。
- **MIS acceptability：** 原白平衡误差分类已有，依据 [CIC 官方摘要](https://library.imaging.org/cic/articles/33/1/6)修订。3,465 是实验判断次数；两种修正涉及外观权重及空间/照度因素。可接受性不同于差异幅度或审美偏好，白平衡协议标签也不能证明对任意视角不变。
- **Photo CD（Niu 2026）：** [Crossref](https://api.crossref.org/works/10.1117/12.3117003)注明论文集为 CVAR 2026，因此将发表场所明确为 **CVAR (Proc SPIE)**。
- **MRFEM-KL：** 从 `shift` 改为 `pixel`。原备注已说明论文未声称错位容忍，空间对应滑窗中的分布比较不足以支持 `shift`。保留为基线并加注限制。此修正与新增无需配准的 TPIPS 抵消，相关合计仍为 58。
- **部分颜色敏感：** 明确表示未作为专用色差指标验证，以容纳语义颜色属性判断，同时避免暗示对白平衡色偏等低层变化具有经过标定的敏感性。
- **待发布：** Markdown 中的占位仓库链接显式标记“待发布”，区分已发布实现与代码公告。
- **研究脉络：** 区分放宽对应与几何不变、局部阈值与摄影色差，以及文字条件相似度、风格和真实感。

## 检索范围

截至 **2026-11-06**，检索覆盖 arXiv 标题/摘要与 Crossref 标题中的 color/colour difference、perceptual color metrics、color image quality、HDR quality，以及非配准参考的感知相似度。按指标名、DOI、arXiv 链接去重，再核对出版方摘要、作者页与官方仓库内容。除 2026 年工作，也补入与本分类直接相关的早期遗漏。

2025 年空间光栅论文 [DOI 10.1002/jsid.2100](https://doi.org/10.1002/jsid.2100)已核对但未作为独立指标新增，因为已有的 2024 年 Riemannian sinusoidal 条目覆盖该模型族。

这是限定范围的文献更新，不是所有期刊与会议的穷尽检索。排除无颜色成分的通用无参考 IQA、颜色迁移或上色算法本身、无关的数学图着色及仅描述时间失真的视频指标。

## 数据校验与复现

运行 `python scripts/build.py` 与 `python scripts/build.py --check`，校验 YAML 并生成六份中英文成果：`README.md`、`README.zh-CN.md`、`CODE.md`、`CODE.zh-CN.md`、`docs/index.html`、`docs/zh-CN.html`。计数、论文与实现链接均由数据生成，不手工修改生成文件。
