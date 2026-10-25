#!/usr/bin/env python3
"""Resolve planning settings without executing configured commands or writing state.

Stdlib only; shipped beside the skill so both tools run the same resolver.
See ../references/planning-settings.md for the file and consumer contracts.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess

FACTS = ('tracker', 'label_vocabulary', 'spec_location')
PERSONAL = ('user_name', 'review_hosting', 'spec_review_launch')
STEPS = FACTS + PERSONAL
BUILTINS = {'tracker': 'github-issues', 'review_hosting': 'local-html',
            'spec_review_launch': 'fresh-subagent'}


class InvalidSetting(ValueError):
    """A present setting cannot be used; never try its shadowed value."""


def read_settings(path: Path, *, require_tracked: bool = False) -> tuple[dict, str | None]:
    try:
        # Broken symlinks and unreadable files are invalid, not absent.
        if not path.exists() and not path.is_symlink():
            return {}, None
        if require_tracked:
            tracked = subprocess.run(['git', '-C', str(path.parent), 'ls-files',
                                      '--error-unmatch', '-z', '--', f':(top,literal){path.name}'],
                                     text=True, capture_output=True)
            if tracked.returncode or path.name not in tracked.stdout.split('\0'):
                detail = tracked.stderr.strip() or f'git ls-files exited {tracked.returncode} without an exact path match'
                raise ValueError('cannot verify repository planning settings as tracked '
                                 f'in this worktree: {detail}')
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f'duplicate entry {key}')
                result[key] = value
            return result
        data = json.loads(path.read_text(), object_pairs_hook=unique)
        if not isinstance(data, dict):
            raise ValueError('expected a JSON object')
        unknown = set(data) - set(STEPS)
        if unknown:
            raise ValueError('unknown entries: ' + ', '.join(sorted(unknown)))
        return data, None
    except (OSError, ValueError) as exc:
        return {}, str(exc)


def github_repository(repo: Path) -> str:
    result = subprocess.run(['git', '-C', str(repo), 'remote', 'get-url', 'origin'],
                            text=True, capture_output=True)
    remote = result.stdout.strip()
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([\w.-]+/[\w.-]+?)(?:\.git)?/?', remote)
    if result.returncode or not match:
        raise InvalidSetting('origin must name a GitHub repository; configure tracker explicitly')
    return match[1]


def default_value(step: str, repo: Path):
    if step == 'tracker':
        return {'builtin': BUILTINS[step], 'repository': github_repository(repo)}
    if step in BUILTINS:
        return {'builtin': BUILTINS[step]}
    return {'user_name': 'the user', 'label_vocabulary': [], 'spec_location': 'issues'}[step]


def validate(step: str, value, repo: Path, skills: set[str]) -> bool:
    """Return availability; malformed values always raise, including in a profile."""
    if step == 'user_name':
        if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
            raise InvalidSetting('expected a nonempty name without control characters')
    elif step == 'label_vocabulary':
        if value == {'builtin': 'repository-policy'}:
            return True
        if (not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value)
                or len(value) != len(set(value))):
            raise InvalidSetting('expected a list of distinct nonempty label names or '
                                 '{"builtin":"repository-policy"}')
    elif step == 'spec_location':
        # A user can preserve different one-ticket and epic placement policies.
        locations = (list(value.values()) if isinstance(value, dict)
                     and set(value) == {'one_ticket', 'several_tickets'} else [value])
        for location in locations:
            if not isinstance(location, str) or not location.strip():
                raise InvalidSetting('expected issues, a repository-relative directory, or one_ticket/several_tickets destinations')
            if location != 'issues':
                if '\0' in location:
                    raise InvalidSetting('spec directory must not contain NUL characters')
                path = Path(location)
                if path.is_absolute() or '..' in path.parts or path == Path('.'):
                    raise InvalidSetting('spec directory must stay inside the repository')
                parent = repo / path
                # Only missing components may be created; preserve other path errors.
                while True:
                    try:
                        mode = parent.stat().st_mode
                        break
                    except FileNotFoundError:
                        if parent.is_symlink():
                            raise InvalidSetting('spec directory contains a broken symlink')
                        parent = parent.parent
                if not parent.resolve(strict=True).is_relative_to(repo.resolve()):
                    raise InvalidSetting('spec directory resolves outside the repository')
                if not stat.S_ISDIR(mode) or not os.access(parent, os.W_OK | os.X_OK):
                    raise InvalidSetting('spec directory is not usable')
    else:
        if not isinstance(value, dict) or len(value) != 1:
            raise InvalidSetting('expected exactly one of builtin, skill, command')
        kind, handler = next(iter(value.items()))
        if kind == 'builtin':
            if handler != BUILTINS[step]:
                raise InvalidSetting(f'unknown builtin for {step}')
        elif kind == 'skill':
            if not isinstance(handler, str) or not re.fullmatch(r'[\w:./-]+', handler):
                raise InvalidSetting('expected a skill name')
            return handler in skills
        elif kind == 'command':
            if (not isinstance(handler, list) or not handler
                    or any(not isinstance(x, str) or not x or '\0' in x for x in handler)):
                raise InvalidSetting('command must be a nonempty argv array')
            executable = os.path.expanduser(handler[0])
            if '/' in executable:
                target = Path(executable)
                if not target.is_absolute():
                    target = repo / target
                return target.is_file() and os.access(target, os.X_OK)
            return shutil.which(executable) is not None
        else:
            raise InvalidSetting('expected exactly one of builtin, skill, command')
    return True


def resolve(repo: Path, profile_path: Path, skills: set[str], steps: list[str],
            *, in_repository: bool = True) -> dict:
    repository_path = repo / '.planning.json'
    profile, profile_error = read_settings(profile_path)
    local, local_error = (read_settings(repository_path, require_tracked=True)
                          if in_repository else ({}, None))
    output = {'values': {}, 'sources': {}, 'notices': [], 'errors': {}}
    for step in steps:
        path = repository_path
        try:
            if local_error and step in FACTS:
                raise InvalidSetting(local_error)
            if step in PERSONAL and step in local:
                raise InvalidSetting('personal entry is allowed only in the planning profile')
            if step in FACTS and step in local:
                value, source = local[step], 'repository planning settings'
            else:
                path = profile_path
                if profile_error:
                    raise InvalidSetting(profile_error)
                value = profile.get(step)
                source = 'planning profile' if step in profile else 'default'
            reason = 'not configured'
            if source != 'default':
                available = validate(step, value, repo, skills)
                if not available:
                    if source == 'repository planning settings':
                        raise InvalidSetting('configured skill or command is not installed in the running tool')
                    source, reason = 'default', 'configured skill or command is not installed in the running tool'
            if source == 'default':
                value = default_value(step, repo)
                output['notices'].append(f'{step}: {reason}; using default {json.dumps(value, ensure_ascii=False)}')
            elif value == {'builtin': 'github-issues'}:
                value = {**value, 'repository': github_repository(repo)}
            output['values'][step] = value
            output['sources'][step] = source
        except (InvalidSetting, OSError) as exc:
            output['errors'][step] = f'{path}: entry {step}: {exc}; stop this step'
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--tool', choices=['claude', 'codex'], required=True,
                        help='the running tool; available skills come from its current catalog')
    parser.add_argument('--available-skill', action='append', default=[])
    parser.add_argument('--step', choices=STEPS, action='append')
    args = parser.parse_args()
    root = subprocess.run(['git', '-C', str(args.repo), 'rev-parse', '--show-toplevel'],
                          text=True, capture_output=True)
    steps = list(dict.fromkeys(args.step or STEPS))
    if root.returncode and any(step in FACTS for step in steps):
        parser.error('--repo must be inside a git repository for repository facts')
    target = Path(root.stdout.strip()) if not root.returncode else args.repo.resolve()
    if not target.is_dir():
        parser.error('--repo must name a directory')
    profile_path = Path(os.environ.get('PLANNING_PROFILE',
                        str(Path.home() / '.config/development-planning/profile.json'))).expanduser()
    result = resolve(target, profile_path, set(args.available_skill), steps,
                     in_repository=not root.returncode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
