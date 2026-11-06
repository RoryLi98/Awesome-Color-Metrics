# Research library design / 文献库设计说明

The structure follows [Awesome Neural ISP](https://github.com/RoryLi98/Awesome-Neural-ISP): grouped navigation, a compact introduction, four statistics, resource tabs, composable filters and full-width publication cards. The color-metrics taxonomy keeps its own alignment, color-sensitivity, output and implementation fields.

布局参考 Awesome Neural ISP：分组侧栏、紧凑导言、四项统计、资源标签页、组合筛选和通栏论文卡片。颜色指标保留自己的配准要求、颜色敏感性、输出形式与实现来源。

## Information hierarchy / 信息层级

- Four navigation groups cover all 12 categories once. Publications have one primary category. / 四个导航组完整覆盖 12 个分类，每篇文献只计一次。
- Publications, datasets, tools and learning resources have separate tabs with a shared search field. / 论文、数据集、工具和学习资料各有标签页，共用搜索入口。
- Official English titles lead the cards in both languages; Chinese translations appear underneath. Metadata, implementation status and code links share one compact row, with expandable notes for limits. / 两种语言均以正式英文标题为主，中文页另列译名；元数据、开放状态和代码链接紧凑排列，使用局限可展开阅读。
- Results start at 24 entries and expand in batches of 24. Research threads and audit dates sit below the library. / 首批显示 24 条，可继续展开；研究脉络和审计日期位于文献库下方。

## Interaction / 交互

Venue selections use OR; topic, search, alignment, color, release status, year, output and implementation filters combine with AND. Search matches every whitespace-separated term against the record, including canonical English text on the Chinese page. The CVPR + ICCV + ECCV preset selects those venues together.

发表场所多选取并集；分类、关键词、配准、颜色、开放状态、年份、输出、实现来源之间取交集。空格分隔的关键词须全部匹配。中文页同时检索原始英文文献文本。会议快捷选项一次选中 CVPR、ICCV、ECCV。

The query string preserves view and filters on reload and language switch. Pagination resets when filters change. Dataset/tool/resource tabs use the search term; publication-only filters apply when returning to publications. `/` focuses search, Escape closes the venue panel or mobile navigation. Unsupported query values fall back to defaults.

URL 参数保存标签页与筛选，刷新或切换语言后保持选择；筛选改变时恢复首批结果。资源页只使用搜索条件，返回论文时恢复论文筛选。`/` 聚焦搜索，Escape 收起会议面板或手机导航；无效参数回退到默认值。

## Visual system / 视觉与响应式

The independent Color Metrics mark is a segmented hue ring with two color samples joined by a distance vector: color space and measurable color difference. Its editable vector source is `docs/assets/color-metrics.svg`, embedded in both pages and reused as the favicon.

Color Metrics 使用独立标志：分段色环代表色空间，两枚颜色样本和距离向量代表可测量的色差。矢量源文件为 `docs/assets/color-metrics.svg`，内嵌于中英文页面，也用于浏览器页签图标。

Muted gray and blue, system fonts, thin rules and compact metadata support a dense research index. The fixed desktop sidebar becomes a drawer below 800 px; grids and filters wrap at smaller widths. Focus outlines, a skip link, native form controls and reduced-motion rules support keyboard use.

灰蓝配色、系统字体、细分隔线和紧凑元数据服务于文献浏览。桌面固定侧栏在 800 px 以下变为抽屉，资源网格与筛选随宽度换行。保留焦点边框、跳至内容链接、原生表单控件及减少动效规则。

## Sources and build / 数据与构建

English records in `data/` are canonical. `data/i18n/metrics.zh-CN.yaml` supplies all translated titles, summaries and notes; `data/i18n/resources.zh-CN.yaml` supplies supporting content. The validator rejects missing translations, obsolete keys and mismatched resource URLs. `data/navigation.yaml` defines groups and validates unique coverage.

英文 YAML 为文献源，中文覆盖提供全部标题、摘要、备注与配套资源说明。校验拒绝缺失翻译、过期键、资源 URL 不一致或重复导航。

`scripts/build.py` produces the English/Chinese README, CODE index and HTML pages. `scripts/site_build.py`, `site_template.html`, `site_style.css` and `site_script.js` build the interface. CSS, JavaScript and JSON are embedded in each HTML file; there are no remote fonts, CDN scripts or fetch calls. External paper/resource links still require connectivity.

构建输出六份成果；每份网页内嵌 CSS、JavaScript 与 JSON，无远程字体、CDN 脚本或数据请求。论文与资源外链仍需联网访问。

```bash
python scripts/build.py
python scripts/build.py --check
python scripts/check_site.py
node --check scripts/site_script.js
python -m http.server 8773 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:8773/` or `http://127.0.0.1:8773/zh-CN.html`. Browser QA should cover desktop and mobile, venue union + other-filter intersection, search in both languages, language-state persistence, pagination, resource tabs, notes, no-results and invalid query values.

预览时分别打开上述中英文地址。页面检查应覆盖桌面与手机、多选并集和组合交集、中英文搜索、语言切换保留状态、分页、资源页、备注、无结果与无效参数。
