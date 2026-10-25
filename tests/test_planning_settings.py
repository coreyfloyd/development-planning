"""Exercise the shipped planning entrypoint with isolated user and repository settings."""
import json
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/dev-plan/scripts/planning_settings.py'


@pytest.fixture(params=['claude', 'codex'])
def planning(request, tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    subprocess.run(['git', '-C', str(repo), 'remote', 'add', 'origin',
                    'git@github.com:example/product.git'], check=True)
    profile = tmp_path / 'profile.json'
    settings = repo / '.planning.json'

    def run(user=None, local=None, skills=(), step=None, *, tracked=True, target_repo=None):
        target_repo = target_repo or repo
        if user is not None:
            profile.write_text(user if isinstance(user, str) else json.dumps(user))
        if local is not None:
            (target_repo / '.planning.json').write_text(local if isinstance(local, str) else json.dumps(local))
            if tracked:
                subprocess.run(['git', '-C', str(target_repo), 'add', '--', '.planning.json'], check=True)
        args = ['python3', str(SCRIPT), '--repo', str(target_repo), '--tool', request.param]
        for skill in skills:
            args += ['--available-skill', skill]
        if step:
            args += ['--step', step]
        result = subprocess.run(args, env={**os.environ, 'HOME': str(tmp_path),
                                'PLANNING_PROFILE': str(profile)}, capture_output=True, text=True)
        assert result.returncode in (0, 2), result.stderr
        return result.returncode, json.loads(result.stdout)
    return run, profile, settings


def test_no_setup_uses_remote_and_generic_defaults(planning):
    run, _, _ = planning
    code, result = run()
    assert code == 0
    assert result['values']['tracker'] == {'builtin': 'github-issues', 'repository': 'example/product'}
    assert result['values']['user_name'] == 'the user'
    assert result['values']['spec_location'] == 'issues'
    assert result['values']['label_vocabulary'] == []
    assert len(result['notices']) == len(set(result['notices'])) == 6
    assert all(result['sources'][key] == 'default' for key in result['values'])


def test_partial_repository_settings_resolve_each_fact(planning):
    run, _, _ = planning
    code, result = run({'user_name': 'Taylor', 'tracker': {'skill': 'tracker'},
                        'label_vocabulary': ['feature'], 'spec_location': 'specs'},
                       {'spec_location': 'docs/proposals'}, skills=['tracker'])
    assert code == 0
    assert result['values']['tracker'] == {'skill': 'tracker'}
    assert result['values']['label_vocabulary'] == ['feature']
    assert result['values']['spec_location'] == 'docs/proposals'
    assert result['values']['user_name'] == 'Taylor'
    assert result['sources']['tracker'] == 'planning profile'
    assert result['sources']['spec_location'] == 'repository planning settings'


@pytest.mark.parametrize('ignored', [False, True])
@pytest.mark.parametrize('with_profile', [False, True])
def test_untracked_repository_settings_stop_without_fallback(planning, ignored, with_profile):
    run, _, settings = planning
    if ignored:
        (settings.parent / '.gitignore').write_text('.planning.json\n')
    marker = settings.parent / 'executed'
    command = {'command': ['python3', '-c', f"open({str(marker)!r}, 'w').close()"]}
    user = {'tracker': {'builtin': 'github-issues'}} if with_profile else None
    code, result = run(user, {'tracker': command}, step='tracker', tracked=False)
    assert code == 2
    assert not result['values'] and not result['sources'] and not result['notices']
    assert str(settings) in result['errors']['tracker']
    assert 'entry tracker:' in result['errors']['tracker']
    assert 'cannot verify repository planning settings as tracked' in result['errors']['tracker']
    assert 'stop this step' in result['errors']['tracker']
    assert not marker.exists()
    index = subprocess.run(['git', '-C', str(settings.parent), 'ls-files', '--', '.planning.json'],
                           capture_output=True, text=True, check=True)
    assert not index.stdout


def test_untracked_repository_settings_are_rejected_before_parsing(planning):
    run, _, settings = planning
    code, result = run(local='{', step='tracker', tracked=False)
    assert code == 2
    assert str(settings) in result['errors']['tracker']
    assert 'cannot verify repository planning settings as tracked' in result['errors']['tracker']


def test_tracked_directory_children_do_not_make_settings_file_tracked(planning):
    run, _, settings = planning
    settings.mkdir()
    (settings / 'tracked-child').write_text('a tracked child, not the settings file')
    subprocess.run(['git', '-C', str(settings.parent), 'add', '--', '.planning.json'], check=True)
    settings.rename(settings.parent / 'old-directory')
    code, result = run(local={'tracker': {'builtin': 'github-issues'}}, step='tracker', tracked=False)
    assert code == 2
    assert not result['values'] and not result['notices']
    assert str(settings) in result['errors']['tracker']
    assert 'cannot verify repository planning settings as tracked' in result['errors']['tracker']


def test_repository_settings_stop_when_git_cannot_verify_tracking(planning):
    run, _, settings = planning
    (settings.parent / '.git/index').write_text('invalid index')
    code, result = run(local={'tracker': {'builtin': 'github-issues'}}, step='tracker', tracked=False)
    assert code == 2
    assert not result['values'] and not result['notices']
    assert str(settings) in result['errors']['tracker']
    assert 'cannot verify repository planning settings as tracked' in result['errors']['tracker']
    assert 'index' in result['errors']['tracker']


@pytest.mark.parametrize('tracked', [False, True])
def test_linked_worktree_uses_its_own_tracking_and_working_file(planning, tracked):
    run, _, settings = planning
    run(local={'label_vocabulary': ['main-label']}, step='label_vocabulary')
    subprocess.run(['git', '-C', str(settings.parent), '-c', 'core.hooksPath=/dev/null',
                    '-c', 'commit.gpgsign=false', '-c', 'user.name=Planning settings test',
                    '-c', 'user.email=planning@example.invalid', 'commit', '-qm', 'Track settings'], check=True)
    linked = settings.parent.parent / 'linked'
    subprocess.run(['git', '-C', str(settings.parent), 'worktree', 'add', '--quiet',
                    '--detach', str(linked), 'HEAD'], check=True)
    if not tracked:
        subprocess.run(['git', '-C', str(linked), 'rm', '--cached', '--quiet', '.planning.json'], check=True)
    code, result = run(local={'label_vocabulary': ['worktree-label']}, step='label_vocabulary',
                       tracked=False, target_repo=linked)
    if tracked:
        assert code == 0
        assert result['values']['label_vocabulary'] == ['worktree-label']
        assert result['sources']['label_vocabulary'] == 'repository planning settings'
    else:
        assert code == 2
        assert not result['values'] and not result['notices']
        assert str(linked / '.planning.json') in result['errors']['label_vocabulary']
        assert 'cannot verify repository planning settings as tracked' in result['errors']['label_vocabulary']
    code, result = run(step='label_vocabulary')
    assert code == 0
    assert result['values']['label_vocabulary'] == ['main-label']


@pytest.mark.parametrize('entry,value', [('tracker', {'skill': 'missing'}),
    ('label_vocabulary', 'bug'), ('spec_location', '../outside'),
    ('user_name', 'Injected'), ('review_hosting', {'builtin': 'local-html'}),
    ('spec_review_launch', {'builtin': 'fresh-subagent'})])
def test_invalid_repository_value_stops_affected_step_without_fallback(planning, entry, value):
    run, _, settings = planning
    code, result = run({'tracker': {'skill': 'installed'}}, {entry: value}, skills=['installed'])
    assert code == 2
    assert entry not in result['values']
    assert str(settings) in result['errors'][entry]
    assert entry in result['errors'][entry]
    assert not any(entry + ':' in notice for notice in result['notices'])


@pytest.mark.parametrize('handler', [{'skill': 'missing'}, {'command': ['missing-planning-command']}])
def test_uninstalled_profile_handler_uses_default_with_one_notice(planning, handler):
    run, _, _ = planning
    code, result = run({'tracker': handler}, step='tracker')
    assert code == 0
    assert result['values']['tracker']['builtin'] == 'github-issues'
    assert len(result['notices']) == 1
    assert 'tracker' in result['notices'][0] and 'github-issues' in result['notices'][0]


@pytest.mark.parametrize('value', ['{', '[]', '{"tracker": false}', '{"tracker": null}'])
def test_invalid_profile_is_not_absent(planning, value):
    run, profile, _ = planning
    code, result = run(value, step='tracker')
    assert code == 2
    assert not result['values']
    assert str(profile) in result['errors']['tracker']


def test_shadowed_invalid_profile_fact_does_not_block_valid_repo_fact(planning):
    run, _, _ = planning
    code, result = run({'label_vocabulary': False}, {'label_vocabulary': ['feature']}, step='label_vocabulary')
    assert code == 0
    assert result['values']['label_vocabulary'] == ['feature']


def test_unusable_spec_directory_does_not_fall_back(planning):
    run, _, settings = planning
    (settings.parent / 'blocked').write_text('a file')
    code, result = run({'spec_location': 'docs/specs'}, {'spec_location': 'blocked/specs'}, step='spec_location')
    assert code == 2
    assert not result['values']


@pytest.mark.parametrize('source', ['repository', 'profile'])
@pytest.mark.parametrize('destination', ['directory', 'one_ticket', 'several_tickets'])
@pytest.mark.parametrize('failure', ['symlink-loop', 'nul', 'broken-symlink', 'long-component'])
def test_invalid_spec_path_reports_file_and_entry_without_fallback(planning, source, destination, failure):
    run, profile, settings = planning
    repo = settings.parent
    if failure == 'symlink-loop':
        (repo / 'loop').symlink_to('loop')
        location = 'loop/specs'
    elif failure == 'nul':
        location = 'docs/\0specs'
    elif failure == 'broken-symlink':
        (repo / 'broken').symlink_to('missing')
        location = 'broken/specs'
    else:
        location = 's' * (os.pathconf(repo, 'PC_NAME_MAX') + 1)
    if destination != 'directory':
        location = {'one_ticket': 'issues', 'several_tickets': 'issues', destination: location}
    if source == 'repository':
        code, result = run({'spec_location': 'docs/specs'}, {'spec_location': location})
        settings_file = settings
    else:
        code, result = run({'spec_location': location})
        settings_file = profile
    assert code == 2
    assert set(result['errors']) == {'spec_location'}
    assert str(settings_file) in result['errors']['spec_location']
    assert 'entry spec_location:' in result['errors']['spec_location']
    assert 'stop this step' in result['errors']['spec_location']
    assert 'spec_location' not in result['values']
    assert 'spec_location' not in result['sources']
    assert not any(notice.startswith('spec_location:') for notice in result['notices'])
    assert result['values']['tracker']['repository'] == 'example/product'
    assert not (repo / 'docs').exists()
    assert not (repo / 'missing').exists()


@pytest.mark.parametrize('symlink', [False, True])
@pytest.mark.parametrize('existing', [False, True])
def test_usable_spec_directory_resolves_without_creating_it(planning, symlink, existing):
    run, _, settings = planning
    repo = settings.parent
    (repo / 'docs').mkdir()
    if symlink:
        (repo / 'alias').symlink_to('docs')
    location = ('alias' if symlink else 'docs') + '/nested/specs'
    if existing:
        (repo / location).mkdir(parents=True)
    code, result = run(local={'spec_location': location}, step='spec_location')
    assert code == 0
    assert result['values']['spec_location'] == location
    assert result['sources']['spec_location'] == 'repository planning settings'
    assert not result['notices']
    assert (repo / location).exists() == existing


def test_installed_command_is_resolved_without_executing_it(planning):
    run, _, settings = planning
    marker = settings.parent / 'executed'
    code, result = run({'tracker': {'command': ['python3', '-c', f"open({str(marker)!r}, 'w').close()"]}}, step='tracker')
    assert code == 0
    assert result['values']['tracker']['command'][0] == 'python3'
    assert not marker.exists()


def test_repository_tracker_overrides_profile_tracker(planning):
    run, _, _ = planning
    code, result = run({'tracker': {'skill': 'personal-tracker'}},
                       {'tracker': {'skill': 'repo-tracker'}},
                       skills=['personal-tracker', 'repo-tracker'], step='tracker')
    assert code == 0
    assert result['values']['tracker'] == {'skill': 'repo-tracker'}
    assert result['notices'] == []


@pytest.mark.parametrize('step,builtin', [('review_hosting', 'local-html'),
                                        ('spec_review_launch', 'fresh-subagent')])
def test_uninstalled_personal_step_uses_its_own_default(planning, step, builtin):
    run, _, _ = planning
    code, result = run({step: {'skill': 'not-in-this-tools-catalog'}}, step=step)
    assert code == 0
    assert result['values'][step] == {'builtin': builtin}
    assert len(result['notices']) == 1


def test_malformed_repository_file_blocks_even_with_valid_profile(planning):
    run, _, settings = planning
    code, result = run({'tracker': {'skill': 'installed'}}, '{', skills=['installed'], step='tracker')
    assert code == 2
    assert not result['values']
    assert str(settings) in result['errors']['tracker']
    assert not result['notices']


def test_duplicate_entry_is_invalid_not_last_value_wins(planning):
    run, _, settings = planning
    code, result = run(local='{"spec_location":"first", "spec_location":"second"}', step='spec_location')
    assert code == 2
    assert str(settings) in result['errors']['spec_location']
    assert 'duplicate entry spec_location' in result['errors']['spec_location']


def test_spec_location_can_preserve_ticket_count_dependent_placement(planning):
    run, _, _ = planning
    location = {'one_ticket': 'issues', 'several_tickets': 'docs/specs'}
    code, result = run({'spec_location': location}, step='spec_location')
    assert code == 0
    assert result['values']['spec_location'] == location
    assert result['notices'] == []


@pytest.mark.parametrize('step,default,configured', [
    ('review_hosting', {'builtin': 'local-html'}, {'skill': 'review-host'}),
    ('spec_review_launch', {'builtin': 'fresh-subagent'}, {'skill': 'review-launch'}),
    ('user_name', 'the user', 'Taylor'),
])
@pytest.mark.parametrize('use_profile', [False, True])
def test_malformed_repository_does_not_block_personal_steps(planning, step, default, configured, use_profile):
    run, _, settings = planning
    code, result = run({step: configured} if use_profile else {}, '{',
                       skills=['review-host', 'review-launch'], step=step)
    assert code == 0, result['errors']
    assert result['values'] == {step: configured if use_profile else default}
    assert result['sources'] == {step: 'planning profile' if use_profile else 'default'}
    assert len(result['notices']) == (0 if use_profile else 1)
    # The same malformed file still blocks the repo facts that it could override.
    code, result = run(step='tracker')
    assert code == 2 and str(settings) in result['errors']['tracker']
    assert not result['values'] and not result['notices']


@pytest.mark.parametrize('tool', ['claude', 'codex'])
@pytest.mark.parametrize('configured', [False, True])
def test_personal_review_resolution_works_outside_git(tmp_path, tool, configured):
    standalone = tmp_path / 'standalone'
    standalone.mkdir()
    # This file is not repository settings and must not be consulted.
    (standalone / '.planning.json').write_text('{')
    profile = tmp_path / 'profile.json'
    values = {'user_name': 'Taylor', 'review_hosting': {'skill': 'review-host'},
              'spec_review_launch': {'skill': 'review-launch'}}
    if configured:
        profile.write_text(json.dumps(values))
    args = ['python3', str(SCRIPT), '--repo', str(standalone), '--tool', tool,
            '--available-skill', 'review-host', '--available-skill', 'review-launch']
    for step in values:
        args += ['--step', step]
    env = {**os.environ, 'HOME': str(tmp_path), 'PLANNING_PROFILE': str(profile)}
    result = subprocess.run(args, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert not data['errors']
    assert data['values'] == (values if configured else {
        'user_name': 'the user', 'review_hosting': {'builtin': 'local-html'},
        'spec_review_launch': {'builtin': 'fresh-subagent'}})
    assert len(data['notices']) == (0 if configured else 3)
    # Outside Git, facts still require a real planning target repository.
    result = subprocess.run(args + ['--step', 'tracker'], env=env, capture_output=True, text=True)
    assert result.returncode == 2
    assert 'git repository' in result.stderr


@pytest.mark.parametrize('source', ['profile', 'repository'])
def test_explicit_repository_label_policy_resolves_without_fallback(planning, source):
    run, _, _ = planning
    configured = {'label_vocabulary': {'builtin': 'repository-policy'}}
    code, result = run(configured if source == 'profile' else {'label_vocabulary': ['feature']},
                       configured if source == 'repository' else None, step='label_vocabulary')
    assert code == 0
    assert result['values'] == configured
    assert result['sources'] == {'label_vocabulary': (
        'planning profile' if source == 'profile' else 'repository planning settings')}
    assert not result['errors'] and not result['notices']


@pytest.mark.parametrize('vocabulary', [
    {'builtin': 'unknown'}, {'builtin': 'repository-policy', 'labels': []},
    {'skill': 'issue-workflow'}, 'repository-policy',
])
def test_invalid_repository_label_policy_does_not_use_profile(planning, vocabulary):
    run, _, settings = planning
    code, result = run({'label_vocabulary': {'builtin': 'repository-policy'}},
                       {'label_vocabulary': vocabulary}, step='label_vocabulary')
    assert code == 2
    assert not result['values'] and not result['notices']
    assert str(settings) in result['errors']['label_vocabulary']
