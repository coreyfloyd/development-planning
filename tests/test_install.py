"""Exercise real package discovery and installation into isolated tool homes."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {'dev-plan', 'strawman', 'grilling', 'grill-me', 'grill-with-docs',
          'to-spec', 'spec-review', 'to-tickets', 'domain-modeling',
          'visual-review', 'diagramming'}


def install(home, *args):
    return subprocess.run([sys.executable, str(ROOT / 'scripts/install-codex.py'),
                           '--codex-home', str(home), *args], capture_output=True, text=True)


def test_plugin_discovers_exactly_eleven_skills():
    plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
    assert plugin['name'] == 'development-planning'
    assert plugin['license'] == 'Apache-2.0'
    assert {p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')} == SKILLS


def test_installer_links_all_skills_and_reinstall_is_idempotent(tmp_path):
    home = tmp_path / 'codex'
    for _ in range(2):
        result = install(home)
        assert result.returncode == 0, result.stderr
        assert {p.name for p in (home / 'skills').iterdir()} == SKILLS
        for name in SKILLS:
            assert (home / 'skills' / name).is_symlink()
            assert (home / 'skills' / name / 'SKILL.md').read_bytes() == (ROOT / 'skills' / name / 'SKILL.md').read_bytes()
    assert not (home / 'hooks.json').exists()
    assert not (home / 'config.toml').exists()


def test_collision_is_reported_before_any_links_are_written(tmp_path):
    skills = tmp_path / 'skills'
    skills.mkdir()
    (skills / 'to-spec').mkdir()
    result = install(tmp_path)
    assert result.returncode != 0
    assert 'to-spec' in result.stderr
    assert {p.name for p in skills.iterdir()} == {'to-spec'}


def test_dangling_foreign_link_is_preserved(tmp_path):
    skills = tmp_path / 'skills'
    skills.mkdir()
    link = skills / 'grilling'
    link.symlink_to(tmp_path / 'missing')
    result = install(tmp_path)
    assert result.returncode != 0
    assert os.readlink(link) == str(tmp_path / 'missing')
    assert len(list(skills.iterdir())) == 1


def test_incomplete_source_stops_before_installation(tmp_path):
    import shutil
    package = tmp_path / 'package'
    shutil.copytree(ROOT / 'scripts', package / 'scripts')
    result = subprocess.run([sys.executable, str(package / 'scripts/install-codex.py'),
                             '--codex-home', str(tmp_path / 'home')], capture_output=True, text=True)
    assert result.returncode != 0
    assert not (tmp_path / 'home').exists()
