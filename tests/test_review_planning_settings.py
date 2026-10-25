"""Portable review skills must ship without private setup in any asset."""
from html.parser import HTMLParser
import re

import pytest

from test_planning_skill_setup_refs import ROOT, setup_references


def test_review_package_has_no_setup_references_including_assets():
    offenders = []
    for skill in ("visual-review", "spec-review"):
        offenders.extend(setup_references(ROOT / 'skills' / skill))
    assert not offenders, "\n".join(offenders)


class KitPage(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.classes = set()
        self.resources = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.classes.update(attrs.get('class', '').split())
        if tag in ('img', 'iframe', 'link', 'source', 'video', 'audio') or (tag == 'script' and 'src' in attrs):
            self.resources.append((tag, attrs))


def test_kit_is_standalone_and_has_all_six_reusable_blocks():
    kit = ROOT / 'skills/visual-review'
    html = (kit / 'kit.html').read_text()
    page = KitPage(html)
    assert not page.resources, page.resources
    assert not re.search(r'@import|url\s*\(\s*["\']?(?!#)[a-z/]', html, re.I)
    assert {'approval-bar', 'review-section', 'diagram-frame', 'decision-card',
            'ticket-graph', 'review-footer'} <= page.classes
    assert all(code in html for code in ('APPROVE', 'APPROVE Q1A', 'CHANGES:'))
    css = (kit / 'assets/review-page.css').read_text()
    assert re.search(r'<style>\s*' + re.escape(css) + r'\s*</style>', html)
    assert not (kit / 'example.html').exists()


def test_kit_extends_the_neutral_diagram_base_verbatim():
    base = (ROOT / 'skills/diagramming/assets/atlas-base.css').read_text()
    css = (ROOT / 'skills/visual-review/assets/review-page.css').read_text()
    assert css.startswith(base)
    assert '@media print' in css


def test_worked_examples_are_complete_offline_kit_pages():
    directory = ROOT / 'skills/visual-review'
    examples = sorted((directory / 'examples').glob('*.html'))
    assert {p.name for p in examples} == {'continuity-spec.html', 'channel-agents.html'}
    css = (directory / 'assets/review-page.css').read_text()
    for path in examples:
        html = path.read_text()
        page = KitPage(html)
        assert not page.resources
        assert not re.search(r'@import|url\s*\(\s*["\']?(?!#)[a-z/]', html, re.I)
        assert re.search(r'<style>\s*' + re.escape(css) + r'\s*</style>', html)
        assert {'approval-bar', 'diagram-frame', 'decision-card', 'review-footer'} <= page.classes
        assert html.count('class="decision-card"') == 3
        assert html.count('data-clear=') == 3
        assert 'checked' not in re.sub(r'<style>.*?</style>', '', html, flags=re.S).split('<script>')[0]
        assert 'fetch(' not in html and 'XMLHttpRequest' not in html
        assert 'Acceptance criteria' in html
    continuity = (directory / 'examples/continuity-spec.html').read_text()
    assert all(f'<td>S{i}</td>' in continuity for i in range(11))
    agents = (directory / 'examples/channel-agents.html').read_text()
    assert all(word in agents for word in ('reply_owner', 'flipping', 'cold-start', 'draining', '60-minute'))


@pytest.mark.parametrize('name', ['continuity-spec.html', 'channel-agents.html'])
def test_example_starts_with_doctype(name):
    html = (ROOT / 'skills/visual-review/examples' / name).read_text()
    assert html.startswith('<!DOCTYPE html>\n'), name
