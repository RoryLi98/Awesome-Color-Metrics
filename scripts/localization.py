"""Validated Chinese overlays. Bibliographic identity and resource URLs stay canonical."""
from __future__ import annotations

import copy
import re

from color_data import ROOT, _load


ALIGN_ZH = {
    'pixel': ('需要像素配准', '比较相同像素或窗口的数值，残留错位会影响读数。'),
    'shift': ('容忍小幅错位', '设计或实验支持亚像素至数像素范围的错位容忍能力。'),
    'free': ('无需像素配准', '比较全局统计、分布或单幅图像特征，不依赖逐像素对应。'),
    'chart': ('已知测试目标', '在测试图卡上与已知参考值比较，读取色块中心可减少错位影响。'),
    'pair': ('逐颜色对', '比较两个颜色或单个刺激，图像配准要求取决于如何聚合。'),
}
COLOR_ZH = {
    'dedicated': ('专用色差', '针对色差设计并经过相关数据验证。'),
    'chromatic': ('显式颜色建模', '显式使用色度通道或颜色数值。'),
    'partial': ('部分颜色敏感', '接收彩色输入，但未经专用色差验证，可能忽略色偏。'),
    'luminance': ('仅亮度', '只使用亮度信息，无法测量纯色度变化。'),
}
OUT_ZH = {'score': '分数', 'map': '差异图', 'components': '分项结果', 'params': '变换参数', 'text': '文字解释与分数'}
STATUS_ZH = {'code': '官方代码', 'toolbox': '工具箱实现', 'unofficial': '第三方实现',
             'spec': '标准文档', 'coming-soon': '待发布', 'no-code': '未找到代码'}


def chinese(d):
    out = copy.deepcopy(d)
    papers = _load(ROOT / 'data/i18n/metrics.zh-CN.yaml')
    content = _load(ROOT / 'data/i18n/resources.zh-CN.yaml')
    errors = []

    def overlay(target, trans, fields, where):
        for field in fields:
            if not target.get(field):
                continue
            value = trans.get(field)
            if not isinstance(value, str) or not value.strip() or not re.search(r'[\u3400-\u9fff]', value):
                errors.append(f'{where}: missing Chinese {field}')
            else:
                target[field] = value

    names = {p['name'] for ps in d['metrics'].values() for p in ps}
    for extra in papers.keys() - names:
        errors.append(f'Obsolete Chinese metric: {extra}')
    for ps in out['metrics'].values():
        for p in ps:
            p['original_title'] = p['title']
            overlay(p, papers.get(p['name'], {}), ('title', 'tldr', 'note'), p['name'])
    for section, identity, fields in [
        ('categories', 'id', ('title', 'short', 'description')),
        ('datasets', 'name', ('capture', 'size', 'use')),
        ('tools', 'name', ('description',)),
    ]:
        translations = content.get(section, {})
        expected = {x[identity] for x in out[section]}
        for extra in translations.keys() - expected:
            errors.append(f'Obsolete Chinese {section}: {extra}')
        for item in out[section]:
            overlay(item, translations.get(item[identity], {}), fields, f'{section}/{item[identity]}')
    if len(content.get('trends', [])) != len(out['trends']):
        errors.append('Chinese research thread count differs')
    else:
        for i, (item, trans) in enumerate(zip(out['trends'], content['trends'])):
            overlay(item, trans, ('title', 'text'), f'trends/{i}')
    for kind, items in out['resources'].items():
        trans = content.get('resources', {}).get(kind, [])
        if len(trans) != len(items):
            errors.append(f'Chinese resources.{kind} count differs')
            continue
        for item, t in zip(items, trans):
            if t.get('url') != item['url']:
                errors.append(f'resources.{kind}: URL/order differs')
            overlay(item, t, ('name', 'description'), f'resources/{item["name"]}')
    overlay(out['config'], content.get('config', {}), ('tagline',), 'config')
    if errors:
        raise ValueError('Incomplete Chinese content:\n  ' + '\n  '.join(errors))
    return out
