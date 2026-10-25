#!/usr/bin/env python3
"""Assemble authored review content with the kit and deliver via resolved settings.

Content, headings, diagrams and decisions belong to the calling skill. This helper
only wraps its HTML body in the shared stylesheet and performs the delivery step.
It consumes a resolver result, never resolves or announces settings a second time.
"""
from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import subprocess
import sys

KIT = Path(__file__).resolve().parents[1]
FACTS = ('tracker', 'label_vocabulary', 'spec_location')


def assemble(body: str, title: str) -> str:
    css = (KIT / 'assets/review-page.css').read_text()
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>{css}</style></head>'
            f'<body><main>{body}</main></body></html>\n')


def deliver(page: Path, repo: Path, settings: dict, settings_file: Path,
            *, render_only: bool = False) -> dict:
    request = {'step': 'review_hosting', 'local_html_path': str(page),
               'repo': str(repo),
               'repo_facts': {key: settings['values'][key] for key in FACTS
                              if key in settings['values']}}
    if render_only:
        return {**request, 'render_only': True}
    binding = settings['values']['review_hosting']
    if binding == {'builtin': 'local-html'}:
        return {**request, 'approval': 'chat'}
    if 'skill' in binding:
        # Native skill execution belongs to the running agent. It must read the
        # named skill, then pass this request without re-entering the renderer.
        return {**request, 'skill': binding['skill']}
    argv = list(binding['command'])
    argv[0] = os.path.expanduser(argv[0])
    if '/' in argv[0] and not Path(argv[0]).is_absolute():
        argv[0] = str(repo / argv[0])
    try:
        result = subprocess.run(argv, cwd=repo, input=json.dumps(request),
                                text=True, capture_output=True)
    except OSError as exc:
        raise ValueError(f'{settings_file}: entry review_hosting: {exc}; stop hosting') from exc
    if result.returncode:
        raise ValueError(f'{settings_file}: entry review_hosting: command exited '
                         f'{result.returncode}: {result.stderr.strip() or result.stdout.strip()}; stop hosting')
    handler_result = result.stdout.strip()
    if not handler_result:
        raise ValueError(f'{settings_file}: entry review_hosting: command stdout is empty; '
                         'expected a description of the delivery result; stop hosting')
    return {**request, 'handler_result': handler_result}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--body', type=Path, required=True,
                        help='authored HTML body following the calling skill structure')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--title', default='Spec review')
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--settings', type=Path, required=True,
                        help='JSON result from the shared planning settings resolver')
    parser.add_argument('--settings-file', type=Path, required=True,
                        help='originating planning profile path for binding error reports')
    parser.add_argument('--render-only', action='store_true',
                        help='return the local page to an already active hosting handler')
    args = parser.parse_args()
    try:
        settings = json.loads(args.settings.read_text())
        if settings.get('errors', {}).get('review_hosting'):
            raise ValueError(settings['errors']['review_hosting'])
        # Require an actual resolver result; missing resolution never defaults here.
        if 'review_hosting' not in settings.get('values', {}):
            raise ValueError(f'{args.settings_file}: entry review_hosting: missing resolved binding; stop hosting')
        page = args.out.resolve()
        page.write_text(assemble(args.body.read_text(), args.title))
        result = deliver(page, args.repo.resolve(), settings, args.settings_file,
                         render_only=args.render_only)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
