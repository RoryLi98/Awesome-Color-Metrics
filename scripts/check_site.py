"""Check bilingual publication identity, offline pages, links and translation failures.

Run after scripts/build.py: python scripts/check_site.py
Browser interactions and responsive layout still need a browser check.
"""
from __future__ import annotations

import copy
from html.parser import HTMLParser
import json
import re
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import color_data
import localization

ROOT = color_data.ROOT


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links = []
        self.ids = []
        self.dependencies = []
        self.payload_text = ''
        self.in_payload = False
        self.feed(path.read_text(encoding='utf-8'))
        self.payload = json.loads(self.payload_text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag in ('script', 'img', 'iframe') and attrs.get('src'):
            self.dependencies.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.dependencies.append(attrs.get('href', ''))
        if tag == 'script':
            self.in_payload = attrs.get('id') == 'library-data'

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_payload = False

    def handle_data(self, data):
        if self.in_payload:
            self.payload_text += data


class SiteContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = color_data.load()
        cls.pages = [Page(ROOT / 'docs' / name) for name in ('index.html', 'zh-CN.html')]

    def test_bilingual_identity_and_implementation_parity(self):
        en, zh = self.pages
        self.assertEqual(len(en.payload['papers']), sum(len(x) for x in self.source['metrics'].values()))
        fields = ('name', 'title', 'venue', 'year', 'category', 'paper', 'code', 'status', 'align', 'color', 'output')
        for a, b in zip(en.payload['papers'], zh.payload['papers'], strict=True):
            self.assertEqual({k: a[k] for k in fields}, {k: b[k] for k in fields})
            self.assertRegex(b['translation'], r'[\u3400-\u9fff]')
            self.assertRegex(b['summary'], r'[\u3400-\u9fff]')
            if a['note']:
                self.assertRegex(b['note'], r'[\u3400-\u9fff]')
            self.assertEqual([(x['package'], x['url']) for x in a['implementations']],
                             [(x['package'], x['url']) for x in b['implementations']])
        for section in ('datasets', 'tools'):
            self.assertEqual([(x['name'], x['url']) for x in en.payload[section]],
                             [(x['name'], x['url']) for x in zh.payload[section]])

    def test_offline_shell_and_document_links(self):
        base = f"https://github.com/{self.source['config']['owner']}/{self.source['config']['repo']}/blob/main/"
        for page in self.pages:
            self.assertFalse(page.dependencies)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            for url in page.links:
                if url.startswith('#'):
                    self.assertIn(url[1:], page.ids)
                elif url.startswith(base):
                    self.assertTrue((ROOT / unquote(urlsplit(url[len(base):]).path)).exists(), url)
                elif not urlsplit(url).scheme:
                    self.assertTrue((ROOT / 'docs' / urlsplit(url).path).exists(), url)
        for path in ROOT.glob('*.md'):
            for target in re.findall(r'\]\(([^)\s]+)\)', path.read_text(encoding='utf-8')):
                if target.startswith('#') or urlsplit(target).scheme:
                    continue
                self.assertTrue((path.parent / unquote(urlsplit(target).path)).exists(), f'{path.name}: {target}')
        for path in (ROOT / 'docs').glob('*.html'):
            self.assertNotRegex(path.read_text(encoding='utf-8'), r'__[A-Za-z][A-Za-z0-9_]*__')

    def test_translation_is_required_and_source_is_unchanged(self):
        before = copy.deepcopy(self.source)
        localization.chinese(self.source)
        self.assertEqual(self.source, before)
        original_load = localization._load
        translations = copy.deepcopy(original_load(ROOT / 'data/i18n/metrics.zh-CN.yaml'))
        first = next(iter(translations))
        del translations[first]['tldr']

        def load_with_gap(path):
            return translations if path.name == 'metrics.zh-CN.yaml' else original_load(path)

        with patch.object(localization, '_load', side_effect=load_with_gap):
            with self.assertRaisesRegex(ValueError, 'missing Chinese tldr'):
                localization.chinese(self.source)


if __name__ == '__main__':
    unittest.main()
