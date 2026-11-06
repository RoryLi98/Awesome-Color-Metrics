"""Build the English and Chinese research library without client dependencies."""
from __future__ import annotations

import html
import json
import re
import copy
from urllib.parse import quote

from color_data import ROOT, ALIGN, COLOR, _load, all_metrics
from localization import ALIGN_ZH, COLOR_ZH, OUT_ZH, STATUS_ZH

UI = {
 'en': dict(skip='Skip to the library', directory='An open research library', browse='Browse research',
    all='All entries', resources='Resources', guide='Color metrics, explained', contribute='Contribute',
    menu='Browse', about='About', language='简体中文', breadcrumb='Research libraries', codeIndex='Implementation index', ownRepo='This repository', codeLink='Code',
    eyebrow='COLOR SCIENCE / COMPUTATIONAL PHOTOGRAPHY', hero1='Color differences,', hero2='organized for research.',
    intro='Find the right metric for your images. Explore color, contrast and perceptual difference across reference conditions.',
    readGuide='Start with Color Metrics 101 ↗', entries='metrics, protocols & studies', code='with implementations',
    tolerant='shift-tolerant or alignment-free', datasets='datasets', library='Research library',
    libraryDesc='Browse a research area, then combine alignment, color sensitivity and release filters.',
    papersTab='Publications', datasetsTab='Datasets', toolsTab='Tools', learnTab='Learn',
    search='Search titles, metrics, topics or functions…', searchLabel='Search the research library',
    venues='All venues', selectedVenues='venues selected', vision='CVPR + ICCV + ECCV', clear='Clear',
    venueHelp='Combine venues with OR; other filters narrow the result.', alignment='Any alignment',
    color='Any color sensitivity', status='Any release status', runnable='With implementations',
    standard='Standards', unreleased='Without released implementations', newest='Newest first', ready='Code first', az='Title A–Z',
    reset='Reset', advanced='More filters & label definitions', year='Any year', output='Any output',
    package='Any implementation', official='Official repository', active='Active filters', remove='Remove filter',
    classification='Reading the labels', results='entries', more='Show more', empty='No matching entries',
    emptyHelp='Try a broader search or remove a filter.', notes='Notes & limitations', tools='Tools & libraries',
    learn='Learning resources', tutorials='Tutorials & references', books='Books', related='Related lists',
    threads='Research threads', threadsDesc='Connections between methods, evidence and practical evaluation.',
    aboutText='A curated library of color-difference formulas, visual models, photographic metrics, alignment-aware comparisons and camera measurement protocols.',
    coverage='Each publication has one primary category. Navigation groups organize browsing; they do not add duplicate entries. Source titles and resource URLs remain canonical in both languages.',
    updated='Literature updated', checked='Full link audit', audit='A literature refresh checks changed entries; it is separate from a complete link audit.',
    updateLog='Sources & update notes', footer='Open knowledge for image evaluation', noscript='Enable JavaScript for filters, or read the complete list in',
    content='Content', size='Size', use='Used for', download='Dataset ↗', source='Source',
    signal='Geometry tolerance does not establish color sensitivity. Test a real color change against a shift-only control.',
    viewPapers='View publications',
 ),
 'zh-CN': dict(skip='跳至文献库', directory='开放研究文献库', browse='浏览研究方向',
    all='全部条目', resources='资源', guide='色差指标入门', contribute='参与贡献',
    menu='浏览目录', about='关于', language='English', breadcrumb='研究文献库', codeIndex='实现索引', ownRepo='本仓库', codeLink='代码',
    eyebrow='颜色科学 / 计算摄影', hero1='看懂色彩差异，', hero2='找到合适的指标。',
    intro='按图像对应关系选择色差、对比度与感知质量指标。将论文、实现、数据集和测量条件放在一起阅读。',
    readGuide='从色差指标入门开始 ↗', entries='指标、评测协议与研究', code='项可用实现',
    tolerant='容忍错位或无需像素配准', datasets='个数据集', library='研究文献库',
    libraryDesc='先选择研究方向，再组合配准要求、颜色敏感性与开放状态进行筛选。',
    papersTab='论文与指标', datasetsTab='数据集', toolsTab='工具库', learnTab='学习资料',
    search='搜索论文、指标、研究主题或函数名…', searchLabel='搜索研究文献库',
    venues='全部会议与期刊', selectedVenues='个发表场所', vision='CVPR + ICCV + ECCV', clear='清空',
    venueHelp='多个发表场所取并集，其他条件进一步缩小范围。', alignment='全部配准要求',
    color='全部颜色敏感性', status='全部开放状态', runnable='有可用实现',
    standard='标准文档', unreleased='尚无公开实现', newest='按年份降序', ready='实现优先', az='按英文标题排序',
    reset='重置', advanced='更多筛选与标签说明', year='全部年份', output='全部输出形式',
    package='全部实现来源', official='官方仓库', active='已选筛选条件', remove='移除筛选条件',
    classification='如何理解标签', results='条结果', more='显示更多', empty='没有匹配的条目',
    emptyHelp='尝试更宽泛的关键词，或移除部分筛选条件。', notes='使用备注与局限', tools='工具与程序库',
    learn='学习资料', tutorials='教程与参考资料', books='参考书籍', related='相关文献列表',
    threads='研究脉络', threadsDesc='联系方法、实验证据与实际评测需求。',
    aboutText='收录色差公式、视觉模型、摄影图像指标、非配准比较方法，以及相机色彩与对比度测量协议。',
    coverage='每篇文献只有一个主分类，侧栏分组只组织导航，不重复计数。中英文共用正式英文标题、文献身份和资源链接。',
    updated='文献更新', checked='全库链接检查', audit='文献更新只核对变更条目，与全库链接检查分开记录。',
    updateLog='来源与更新说明', footer='面向图像评测的开放知识', noscript='启用 JavaScript 可使用筛选，也可阅读完整的',
    content='内容', size='规模', use='用途', download='访问数据集 ↗', source='来源',
    signal='容忍几何错位不等于对颜色变化敏感。请同时测试真实色彩变化和仅发生错位的对照组。',
    viewPapers='查看相关文献',
 ),
}
STATUS_EN = {'code':'Official code', 'toolbox':'Toolbox', 'unofficial':'Third-party', 'spec':'Standard',
             'coming-soon':'Coming soon', 'no-code':'No code found'}


def site(d, english, lang='en'):
    ui = dict(UI[lang])
    cfg = d['config']
    zh = lang == 'zh-CN'
    base = f"https://github.com/{cfg['owner']}/{cfg['repo']}"
    suffix = '.zh-CN' if zh else ''
    original = {p['name']:p for _,p in all_metrics(english)}
    papers = []
    for cat, p in all_metrics(d):
        o = original[p['name']]
        papers.append(dict(name=p['name'], title=o['title'], translation=p['title'] if zh else '',
            summary=p['tldr'], note=p.get('note',''), venue=p['venue'], year=p['year'], category=cat['id'],
            paper=p['paper'], code=p.get('code',''), status=p['status'], align=p.get('align',''),
            color=p.get('color',''), output=p.get('output',''),
            implementations=[dict(label=w['label'].replace('this repo','本仓库') if zh else w['label'],
                package=w['label'].split(' · ')[0].split(' (')[0].strip(),
                url=w['url'] if re.match(r'https?://',w['url']) else f'{base}/blob/main/{w["url"]}') for w in p.get('impl',[])],
            search=' '.join(str(o.get(k,'')) for k in ('name','title','tldr','note'))))
    nav = _load(ROOT / 'data/navigation.yaml')
    ids = [cid for g in nav for cid in g['categories']]
    if len(ids) != len(set(ids)) or set(ids) != {c['id'] for c in d['categories']}:
        raise ValueError('Navigation must cover every category exactly once')
    align = ALIGN_ZH if zh else ALIGN
    color = COLOR_ZH if zh else COLOR
    ui['statuses'] = STATUS_ZH if zh else STATUS_EN
    ui['outputs'] = OUT_ZH if zh else {'score':'Score','map':'Difference map','components':'Components','params':'Parameters','text':'Text + score'}
    ui['alignments'] = align
    ui['colors'] = color
    payload = dict(papers=papers, categories=d['categories'],
        navigation=[dict(title=g['title_zh'] if zh else g['title'], categories=g['categories']) for g in nav],
        datasets=d['datasets'], tools=d['tools'], resources=copy.deepcopy(d['resources']), trends=d['trends'])
    for items in payload['resources'].values():
        for item in items:
            url = item['url']
            if not re.match(r'https?://',url):
                if zh:
                    url = url.replace('color-metrics-101.md','color-metrics-101.zh-CN.md')
                item['url'] = f'{base}/blob/main/{url}'
    encode = lambda x: json.dumps(x, ensure_ascii=False, separators=(',',':')).replace('<','\\u003c')
    logo = (ROOT/'docs/assets/color-metrics.svg').read_text(encoding='utf-8').strip()
    rep = {'LANG':lang, 'TITLE':cfg['title'] + (' · 中文' if zh else ''), 'REPO':base,
        'LOGO':logo, 'FAVICON':'data:image/svg+xml,' + quote(logo, safe=''),
        'STYLE':(ROOT/'scripts/site_style.css').read_text(encoding='utf-8'),
        'SCRIPT':(ROOT/'scripts/site_script.js').read_text(encoding='utf-8'),
        'DATA':encode(payload), 'UI':encode(ui), 'ALT':'index.html' if zh else 'zh-CN.html',
        'GUIDE':f'{base}/blob/main/guide/color-metrics-101{suffix}.md',
        'README':f'{base}/blob/main/README{suffix}.md',
        'CODE':f'{base}/blob/main/CODE{suffix}.md',
        'CONTRIBUTE':f'{base}/blob/main/CONTRIBUTING{suffix}.md',
        'LOG':f'{base}/blob/main/guide/literature-update-{cfg["literature_updated"]}{suffix}.md',
        'UPDATED':cfg['literature_updated'], 'CHECKED':cfg['checked'],
        'NP':str(len(papers)), 'NCODE':str(sum(p['status'] in ('code','toolbox','unofficial') for p in papers)),
        'NT':str(sum(p['align'] in ('shift','free') for p in papers)), 'ND':str(len(d['datasets']))}
    template = (ROOT/'scripts/site_template.html').read_text(encoding='utf-8')
    rep.update({k:html.escape(v,quote=True) for k,v in ui.items() if isinstance(v,str)})
    return re.sub(r'__([A-Za-z0-9_]+)__', lambda m:rep.get(m[1],m[0]), template)
