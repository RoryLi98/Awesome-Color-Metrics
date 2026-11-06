# 参与贡献

[English](CONTRIBUTING.md) · [简体中文](CONTRIBUTING.zh-CN.md)

条目以 `data/` 下的英文 YAML 为唯一文献源，中文内容由 `data/i18n/` 覆盖。中英文 README、实现索引与网页均自动生成，请修改源数据后重新构建。

## 快速开始

1. Fork 仓库并创建分支。
2. 在 `data/metrics/` 的相应文件添加或修订条目，同时更新 `data/i18n/metrics.zh-CN.yaml` 中同名条目的中文标题、摘要与备注。
3. 安装依赖并构建、校验：

   ```bash
   pip install -r requirements.txt
   python scripts/build.py
   python scripts/build.py --check
   ```

4. 一起提交数据与六个生成文件：`README.md`、`README.zh-CN.md`、`CODE.md`、`CODE.zh-CN.md`、`docs/index.html`、`docs/zh-CN.html`。CI 会检查数据合法性、翻译完整性及生成文件是否过期。

也可以通过 [添加指标](https://github.com/RoryLi98/Awesome-Color-Metrics/issues/new?template=add-metric.yml)或[报告错误](https://github.com/RoryLi98/Awesome-Color-Metrics/issues/new?template=broken-link.yml)提交来源与修改建议。

## 文件位置

| 文件 | 内容 |
|:--|:--|
| `data/metrics/formula.yaml` | 色差公式与均匀色空间 |
| `data/metrics/spatial.yaml` | 空间色差与可见差异模型 |
| `data/metrics/friqa.yaml` | 彩色全参考图像质量指标 |
| `data/metrics/contrast.yaml` | 对比度、色调与动态范围 |
| `data/metrics/photo.yaml` | 摄影图像感知色差 |
| `data/metrics/global.yaml` | 全局统计与颜色直方图 |
| `data/metrics/patch.yaml` | 图像块分布与平移容忍结构 |
| `data/metrics/deep.yaml` | 深度特征与错位比较 |
| `data/metrics/protocol.yaml` | 非配准真值的评测协议 |
| `data/metrics/wb.yaml` | 白平衡与光源误差 |
| `data/metrics/chart.yaml` | 测试图卡与相机标准 |
| `data/metrics/study.yaml` | 基准、心理物理研究与综述 |
| `data/datasets.yaml` | 数据集 |
| `data/tools.yaml` | 工具与程序库 |
| `data/resources.yaml` | 教程、书籍与相关列表 |
| `data/trends.yaml` | 研究脉络 |
| `data/categories.yaml`、`data/navigation.yaml` | 分类说明与侧栏分组 |

每篇文献只有一个主分类。选择其主要贡献所在的文件，构建程序负责排序；侧栏分组必须完整覆盖各分类且不得重复。

## 条目字段

```yaml
- name: MS-SWD
  title: Multiscale Sliced Wasserstein Distances as Perceptual Color Difference Measures
  venue: ECCV
  year: 2024
  paper: https://doi.org/10.1007/978-3-031-73668-1_25
  code: https://github.com/real-hjq/MS-SWD
  status: code
  impl:
    - label: pyiqa · `msswd`
      url: https://github.com/chaofengc/IQA-PyTorch
  framework: PyTorch
  align: free
  color: dedicated
  output: score
  tldr: One neutral sentence describing the method and its evaluation.
  note: Optional practical limitation.
```

`name` 是稳定的指标名或缩写，也是中文翻译的键。`title` 使用正式英文标题；`paper` 优先 DOI、CVF 或 ECVA，否则使用 arXiv 摘要页。`impl` 列出额外实现，标签建议采用“程序包 · `函数名`”。`framework`、`output` 和 `note` 可选；输出标签为 `score`（分数）、`map`（差异图）、`components`（分项）、`params`（参数）、`text`（文字与分数）。

### 配准要求 `align`

| 值 | 使用条件 |
|:--|:--|
| `pixel` | 比较相同像素或窗口，如逐像素 ΔE、SSIM、LPIPS、可见差异模型 |
| `shift` | 方法设计或实验支持亚像素至数像素错位容忍，如局部搜索、抗混叠、区域均值 |
| `free` | 比较全局统计、分布或单幅图像特征，舍弃位置 |
| `chart` | 在已知测试目标上读取色块并与参考值比较 |
| `pair` | 比较两个颜色或一个刺激；图像配准要求取决于聚合方式 |

标签描述方法需要什么，不能仅依据测试数据集推断。若机制需要空间对应且论文未讨论错位，标为 `pixel` 并在备注说明。`free` 也不代表对任意视角、裁剪或内容变化不变。

### 颜色敏感性 `color`

| 值 | 使用条件 |
|:--|:--|
| `dedicated` | 针对色差设计，且在色差数据上验证 |
| `chromatic` | 显式使用颜色通道或颜色数值，如直方图、FSIMc、FLIP |
| `partial` | 输入彩色图像，但未作为专用色差指标验证，包括多数深度指标与语义属性相似度 |
| `luminance` | 只比较亮度，如 GMSD、TMQI、CW-SSIM |

### 开放状态 `status`

| 值 | 使用条件 |
|:--|:--|
| `code` | 官方实现已公开，`code` 指向该实现 |
| `toolbox` | 无官方代码，但有维护中的工具箱或程序包，须在 `impl` 列出 |
| `unofficial` | 仅有第三方实现，`code` 指向该实现 |
| `spec` | 标准或建议，按文档自行实现 |
| `coming-soon` | 仓库仍是占位页，或明确表示代码待发布 |
| `no-code` | 本次检索未确认公开实现 |

检查实际实现文件与发布说明，不能仅凭仓库存在就标为 `code`。构建会拒绝 `toolbox` 没有 `impl`、`no-code` 却带 `code` 等不一致记录。可用实现统计包含 `code`、`toolbox`、`unofficial`，不包含待发布仓库。

## 翻译与写作

- 英文源与中文覆盖应同时更新。`data/i18n/metrics.zh-CN.yaml` 以原始 `name` 为键，提供 `title`、`tldr`，以及英文存在时的 `note`。
- 分类、数据集、工具、研究脉络与学习资源的中文位于 `data/i18n/resources.zh-CN.yaml`；导航组名位于 `data/navigation.yaml`。资源 URL 与顺序必须对应。
- 中英文网页都以正式英文标题为主标题，中文页另列译名。指标缩写、作者姓名、文献身份及资源链接保持一致。
- 用一两句中性文字连接问题、方法与评价，避免“首创”“最先进”等宣传。训练代码缺失、仅在阈值数据验证、领域特定判断等限制写入备注。
- 区分颜色差异、风格相似度、颜色真实感与偏好；通用嵌入不能自动视为经过标定的色差指标。
- 一篇文献一条记录，变体写入备注。构建会拒绝缺失或过期的翻译键。

收录色差公式、HDR 与宽色域、含颜色或对比度成分的全参考指标、错位参考比较、白平衡误差、图卡与相机标准，以及相关评测、心理物理研究和数据集。不收录无颜色成分的无参考 IQA、颜色恒常/上色/颜色迁移算法本身，以及仅衡量视频时间失真的指标。

## 维护说明

`config.yaml` 控制仓库地址、网页地址及日期。GitHub Pages 可从 `main` 分支的 `docs/` 发布。两份网页均内嵌样式、脚本和数据，不依赖 CDN 或服务端 API。

定向文献更新使用 `literature_updated`，并新增中英文 `guide/literature-update-YYYY-MM-DD*.md`，记录一手来源、代码证据与分类理由。`checked` 仅用于全库链接检查；定向更新不能替代全库审计。链接工作流使用 [lychee](https://github.com/lycheeverse/lychee)，配置位于 `lychee.toml`。

布局和本地预览方式见[设计说明](guide/design-notes.md)。
