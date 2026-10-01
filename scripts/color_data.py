"""Load and validate the YAML data under data/.

Everything the README, CODE.md and the interactive page show comes from here.
"""
from __future__ import annotations

import datetime as _dt
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

STATUSES = {
    'code': 'official code is public',
    'toolbox': 'no official code; implemented in a maintained toolbox (or in this repository\'s guide script)',
    'unofficial': 'third-party implementation only',
    'spec': 'standard or recommendation; implement from the document',
    'coming-soon': 'repository is a placeholder or says code is coming',
    'no-code': 'no public code found',
}
CODE_STATUSES = ('code', 'toolbox', 'unofficial')

# Alignment requirement: the main axis of this list.
ALIGN = {
    'pixel': ('Needs pixel alignment',
              'compares values at the same pixel or window; any residual misalignment adds a positive bias'),
    'shift': ('Tolerates small shifts',
              'designed or shown to tolerate sub-pixel to few-pixel misalignment (coarse scales, anti-aliasing, local search)'),
    'free': ('Alignment-free',
             'compares global statistics or distributions, or a per-image measure; position is discarded'),
    'chart': ('Known target',
              'measured on a test chart against reference values; immune to small shifts when only patch centers are read'),
    'pair': ('Per color pair',
             'a formula for two colors or one stimulus; whether it needs alignment depends on how you aggregate it'),
}
ALIGN_ORDER = ('pixel', 'shift', 'free', 'chart', 'pair')
TOLERANT = ('shift', 'free')

# Does the metric see color?
COLOR = {
    'dedicated': ('dedicated', 'built and validated for color difference'),
    'chromatic': ('chromatic', 'models chromatic channels or color values explicitly'),
    'partial': ('partial', 'takes color input but was not designed or tested for color; may miss casts'),
    'luminance': ('luminance only', 'works on luminance; blind to color casts'),
}
OUTPUTS = {
    'score': 'one number',
    'map': 'per-pixel map (plus a pooled number)',
    'components': 'several interpretable numbers or maps',
    'params': 'fitted parameters (e.g. a curve or matrix)',
    'text': 'text explanation plus a score',
}
# Sections where `align` and `color` may be omitted (papers about metrics rather than metrics).
OPTIONAL_PROPS = ('study',)

METRIC_KEYS = ('name', 'title', 'venue', 'year', 'paper', 'code', 'status', 'impl', 'framework',
               'align', 'color', 'output', 'tldr', 'note')
REQUIRED = ('name', 'title', 'venue', 'year', 'paper', 'status', 'tldr')
URL = re.compile(r'^https?://\S+$')
LOCAL = re.compile(r'^(guide|data|docs)/\S+$')


class DataError(Exception):
    pass


def _load(path: pathlib.Path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f) or []


def load():
    """Return a dict with config, categories, metrics (by category), datasets, tools, resources, trends."""
    cfg = _load(ROOT / 'config.yaml')
    cats = _load(DATA / 'categories.yaml')
    metrics = {c['id']: _load(DATA / 'metrics' / f"{c['id']}.yaml") for c in cats}
    return dict(
        config=cfg,
        categories=cats,
        metrics=metrics,
        datasets=_load(DATA / 'datasets.yaml'),
        tools=_load(DATA / 'tools.yaml'),
        resources=_load(DATA / 'resources.yaml'),
        trends=_load(DATA / 'trends.yaml'),
    )


def validate(d) -> list[str]:
    """Return a list of human-readable problems; empty means the data is valid."""
    errs: list[str] = []
    ids = [c['id'] for c in d['categories']]
    files = sorted(p.stem for p in (DATA / 'metrics').glob('*.yaml'))
    for extra in set(files) - set(ids):
        errs.append(f'data/metrics/{extra}.yaml is not listed in data/categories.yaml')
    this_year = _dt.date.today().year
    seen: dict[str, str] = {}
    for cid, items in d['metrics'].items():
        if not isinstance(items, list):
            errs.append(f'data/metrics/{cid}.yaml must be a YAML list')
            continue
        for i, p in enumerate(items):
            where = f"data/metrics/{cid}.yaml #{i + 1} ({p.get('name', '?')})"
            for k in REQUIRED:
                if p.get(k) in (None, ''):
                    errs.append(f'{where}: missing "{k}"')
            for k in p:
                if k not in METRIC_KEYS:
                    errs.append(f'{where}: unknown key "{k}"')
            st = p.get('status')
            if st not in STATUSES:
                errs.append(f'{where}: status "{st}" must be one of {", ".join(STATUSES)}')
            if st in ('code', 'unofficial') and not p.get('code'):
                errs.append(f'{where}: status "{st}" needs a "code" URL')
            if st == 'toolbox' and not p.get('impl'):
                errs.append(f'{where}: status "toolbox" needs at least one entry under "impl"')
            if st == 'no-code' and (p.get('code') or p.get('impl')):
                errs.append(f'{where}: has code or impl links but status is "no-code"')
            if cid not in OPTIONAL_PROPS or p.get('align') or p.get('color'):
                if p.get('align') not in ALIGN:
                    errs.append(f'{where}: align "{p.get("align")}" must be one of {", ".join(ALIGN)}')
                if p.get('color') not in COLOR:
                    errs.append(f'{where}: color "{p.get("color")}" must be one of {", ".join(COLOR)}')
            if p.get('output') and p['output'] not in OUTPUTS:
                errs.append(f'{where}: output "{p["output"]}" must be one of {", ".join(OUTPUTS)}')
            y = p.get('year')
            if not isinstance(y, int) or not 1900 <= y <= this_year + 1:
                errs.append(f'{where}: year "{y}" is not a plausible integer year')
            for k in ('paper', 'code'):
                if p.get(k) and not URL.match(p[k]):
                    errs.append(f'{where}: "{k}" is not an http(s) URL')
            for w in p.get('impl') or []:
                ok = isinstance(w, dict) and w.get('label') and (URL.match(str(w.get('url', ''))) or LOCAL.match(str(w.get('url', ''))))
                if not ok:
                    errs.append(f'{where}: each impl entry needs "label" and an http(s) or repository-relative "url"')
                elif LOCAL.match(w['url']) and not (ROOT / w['url']).exists():
                    errs.append(f'{where}: impl path "{w["url"]}" does not exist in the repository')
            name = str(p.get('name', '')).lower()
            if name in seen:
                errs.append(f'{where}: name duplicates {seen[name]}')
            seen[name] = where
    for i, ds in enumerate(d['datasets']):
        for k in ('name', 'year', 'url', 'use'):
            if not ds.get(k):
                errs.append(f'data/datasets.yaml #{i + 1}: missing "{k}"')
        if ds.get('task') and ds['task'] not in ids:
            errs.append(f'data/datasets.yaml #{i + 1}: task "{ds["task"]}" is not a category id')
    for i, t in enumerate(d['tools']):
        for k in ('name', 'url', 'description'):
            if not t.get(k):
                errs.append(f'data/tools.yaml #{i + 1}: missing "{k}"')
    return errs


def all_metrics(d):
    """Yield (category, metric) in README order."""
    for c in d['categories']:
        for p in d['metrics'][c['id']]:
            yield c, p
