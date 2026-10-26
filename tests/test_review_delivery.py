"""Exercise kit assembly and delivery using a retained, approved spec review."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from html.parser import HTMLParser

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/review-delivery'
DELIVERY = ROOT / 'skills/visual-review/scripts/review_delivery.py'
RESOLVER = ROOT / 'skills/dev-plan/scripts/planning_settings.py'


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.text = []
        self.headings = []
        self.resources = []
        self.heading = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h2':
            self.heading = True
        if tag in ('link', 'img', 'iframe', 'source', 'video', 'audio') or (tag == 'script' and 'src' in attrs):
            self.resources.append((tag, attrs))

    def handle_endtag(self, tag):
        if tag == 'h2':
            self.heading = False

    def handle_data(self, data):
        self.text.append(data)
        if self.heading:
            self.headings.append(data)


@pytest.fixture(params=['claude', 'codex'])
def delivery(request, tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    profile = tmp_path / 'profile.json'
    output = tmp_path / 'review.html'

    def run(binding=None, *, render_only=False, skills=()):
        if binding is not None:
            profile.write_text(json.dumps({'review_hosting': binding}))
        resolver_args = [sys.executable, str(RESOLVER), '--tool', request.param,
                         '--repo', str(repo), '--step', 'review_hosting']
        for skill in skills:
            resolver_args += ['--available-skill', skill]
        resolved = subprocess.run(resolver_args, env={**os.environ, 'PLANNING_PROFILE': str(profile)},
            text=True, capture_output=True, check=True)
        settings = tmp_path / 'resolved.json'
        settings.write_text(resolved.stdout)
        cmd = [sys.executable, str(DELIVERY), '--repo', str(repo),
               '--body', str(FIXTURE / 'spec-review-body.html'), '--out', str(output),
               '--settings', str(settings), '--settings-file', str(profile)]
        if render_only:
            cmd.append('--render-only')
        result = subprocess.run(cmd, text=True, capture_output=True)
        return result, output

    return run, profile, repo, tmp_path


def test_local_file_renders_real_approved_spec_verbatim(delivery):
    run, _, _, _ = delivery
    result, output = run()
    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response['local_html_path'] == str(output)
    assert response['approval'] == 'chat'
    html = output.read_text()
    page = Page(html)
    text = '\n'.join(page.text)
    source = (FIXTURE / 'approved-spec.md').read_text()
    criteria = re.findall(r'^- \[ \] (.+)$', source, re.M)
    stories = re.findall(r'^### (S\d+ — .+)$', source, re.M)
    stops = source.split('### What stops working\n', 1)[1].split('\n## ', 1)[0]
    assert len(criteria) == 34  # Exact count from the approved source, not sample data.
    for line in stories + criteria + re.findall(r'^- (.+)$', stops, re.M):
        assert line in text
    assert page.headings == ['Why this exists', 'User Stories', 'What stops working',
                             'The shape', 'Testing Decisions', 'Out of Scope', 'Evaluator Rubric']
    assert not page.resources
    assert not re.search(r'@import|url\s*\(\s*["\']?(?!#)[a-z/]', html, re.I)
    assert all(code in text for code in ('APPROVE', 'CHANGES: <notes>'))
    css = (ROOT / 'skills/visual-review/assets/review-page.css').read_text()
    assert f'<style>{css}</style>' in html


def test_configured_command_receives_local_page_and_repo_facts(delivery):
    run, _, repo, tmp = delivery
    capture = tmp / 'received.json'
    host = tmp / 'host.py'
    host.write_text('import json, pathlib, sys\n'
                    'request = json.load(sys.stdin)\n'
                    'assert pathlib.Path(request["local_html_path"]).is_file()\n'
                    'pathlib.Path(sys.argv[1]).write_text(json.dumps(request))\n'
                    'print("https://review.example/spec — use the host approval controls")\n')
    result, output = run({'command': [sys.executable, str(host), str(capture)]})
    assert result.returncode == 0, result.stderr
    received = json.loads(capture.read_text())
    assert received['local_html_path'] == str(output)
    assert received['step'] == 'review_hosting'
    assert received['repo'] == str(repo)
    assert received['repo_facts'] == {}
    assert 'use the host approval controls' in result.stdout
    assert '"approval": "chat"' not in result.stdout


def test_failing_binding_stops_and_names_settings_entry(delivery):
    run, profile, _, tmp = delivery
    host = tmp / 'failed.py'
    host.write_text('import sys\nprint("hosting refused", file=sys.stderr)\nsys.exit(7)\n')
    result, output = run({'command': [sys.executable, str(host)]})
    assert result.returncode != 0
    assert str(profile) in result.stderr
    assert 'entry review_hosting' in result.stderr
    assert 'hosting refused' in result.stderr
    assert '7' in result.stderr
    assert not result.stdout  # No fallback success or second hosting attempt.
    assert output.is_file()  # Retain the page for retry.


def test_render_only_returns_local_page_without_recursive_dispatch(delivery):
    run, _, _, tmp = delivery
    capture = tmp / 'must-not-run'
    result, output = run({'command': [sys.executable, '-c',
                         f'from pathlib import Path; Path({str(capture)!r}).touch()']}, render_only=True)
    assert result.returncode == 0, result.stderr
    assert output.is_file()
    assert not capture.exists()
    assert json.loads(result.stdout)['render_only'] is True


def test_spec_mapping_includes_approval_contract_and_retains_question_limit():
    spec = (ROOT / 'skills/to-spec/SKILL.md').read_text()
    review = (ROOT / 'skills/visual-review/SKILL.md').read_text()
    assert '| User Stories |' in spec
    assert '| What stops working |' in spec
    for text in (spec, review):
        assert 'verbatim' in text
        assert 'nothing stops working' in text.lower()
        assert 'at most five' in text.lower()
    assert spec.index('| User Stories |') < spec.index('| What stops working |') < spec.index('| Data Model,')
    assert 'review_delivery.py' in review


def test_skill_binding_hands_local_page_to_native_agent(delivery):
    run, profile, repo, tmp = delivery
    result, output = run({'skill': 'team-review-host'}, skills=('team-review-host',))
    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response['skill'] == 'team-review-host'
    assert response['local_html_path'] == str(output)
    assert response['settings'] == json.loads((tmp / 'resolved.json').read_text())
    assert response['settings_file'] == str(profile)
    assert 'approval' not in response
    assert 'handler_result' not in response

    # A hosting skill can reuse the handoff without resolving or hosting again.
    settings = tmp / 'host-settings.json'
    settings.write_text(json.dumps(response['settings']))
    hosted_page = tmp / 'host-review.html'
    rendered = subprocess.run([
        sys.executable, str(DELIVERY), '--repo', str(repo),
        '--body', str(FIXTURE / 'spec-review-body.html'), '--out', str(hosted_page),
        '--settings', str(settings), '--settings-file', response['settings_file'],
        '--render-only',
    ], text=True, capture_output=True)
    assert rendered.returncode == 0, rendered.stderr
    rendered_response = json.loads(rendered.stdout)
    assert rendered_response['render_only'] is True
    assert rendered_response['local_html_path'] == str(hosted_page)
    assert 'skill' not in rendered_response
    assert hosted_page.read_text() == output.read_text()


@pytest.mark.parametrize('stdout', ['', ' \t\n'])
def test_successful_binding_with_empty_result_stops_hosting(delivery, stdout):
    run, profile, _, tmp = delivery
    host = tmp / 'empty-result.py'
    host.write_text('import sys\n'
                    f'sys.stdout.write({stdout!r})\n'
                    'print("status only on stderr", file=sys.stderr)\n')
    result, output = run({'command': [sys.executable, str(host)]})
    assert result.returncode != 0
    assert str(profile) in result.stderr
    assert 'entry review_hosting' in result.stderr
    assert 'stdout' in result.stderr
    assert 'empty' in result.stderr
    assert 'stop hosting' in result.stderr
    assert not result.stdout  # No successful delivery or fallback reply.
    assert output.is_file()  # Preserve the page for correction and retry.
