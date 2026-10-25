"""A final clean tree must not hide a private identifier in an earlier commit."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/check-public-range.py'


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def commit(repo, content):
    (repo / 'text.txt').write_text(content)
    git(repo, 'add', 'text.txt')
    git(repo, '-c', 'user.name=Test', '-c', 'user.email=test@example.org',
        '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Snapshot')
    return git(repo, 'rev-parse', 'HEAD')


def scan(repo, *args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=repo,
                          capture_output=True, text=True)


def test_scan_checks_intermediate_commits_and_first_push(tmp_path):
    git(tmp_path, 'init', '-q')
    base = commit(tmp_path, 'public text')
    assert scan(tmp_path).returncode == 0
    commit(tmp_path, 'mini' + '1')
    commit(tmp_path, 'public text again')
    result = scan(tmp_path, base)
    assert result.returncode == 1
    assert 'publication stopped' in result.stderr
    assert scan(tmp_path).returncode == 1
    clean_base = git(tmp_path, 'rev-parse', 'HEAD')
    commit(tmp_path, 'clean newest change')
    assert scan(tmp_path, clean_base).returncode == 0


def test_invalid_base_is_an_error(tmp_path):
    git(tmp_path, 'init', '-q')
    commit(tmp_path, 'public text')
    result = scan(tmp_path, 'missing-base')
    assert result.returncode != 0
    assert 'cannot read' in result.stderr
