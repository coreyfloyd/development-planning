#!/usr/bin/env python3
"""Link the planning package's eleven skills into a Codex skills directory."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('dev-plan', 'strawman', 'grilling', 'grill-me', 'grill-with-docs',
          'to-spec', 'spec-review', 'to-tickets', 'domain-modeling',
          'visual-review', 'diagramming')


def install(home: Path) -> None:
    """Preflight the full inventory and collisions before creating any links."""
    sources = ROOT / 'skills'
    found = {p.name for p in sources.iterdir()} if sources.is_dir() else set()
    if found != set(SKILLS) or any(not (sources / n / 'SKILL.md').is_file() for n in SKILLS):
        raise ValueError('incomplete planning package: expected exactly eleven skills')
    destination = home / 'skills'
    for name in SKILLS:
        link = destination / name
        if os.path.lexists(link) and not (link.is_symlink() and link.resolve() == sources / name):
            raise ValueError(f'existing skill {link} is not owned by this planning package; move it aside explicitly before installing')
    destination.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    try:
        for name in SKILLS:
            link = destination / name
            if not link.is_symlink():
                link.symlink_to(sources / name, target_is_directory=True)
                created.append(link)
    except OSError:
        for link in reversed(created):
            link.unlink()
        raise
    print('Installed all 11 planning package skills in Codex: ' + str(destination))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path,
                        default=Path(os.environ.get('CODEX_HOME') or '~/.codex'))
    args = parser.parse_args()
    try:
        install(args.codex_home.expanduser().resolve())
    except (OSError, ValueError) as error:
        print(f'planning package install: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
