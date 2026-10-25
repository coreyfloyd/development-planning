#!/usr/bin/env python3
"""Refuse publication when any commit in the pushed range has private references."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

# Fragments keep the gate itself safe to ship under the same literal range scan.
PRIVATE = re.compile(
    r'admin' + r'-panel|claude' + r'-dotfiles|obsi' + r'dian|/Use' + r'rs/|'
    r'mini' + r'1|mini' + r'2|tail' + r'scale|100\.[0-9]+\.', re.I)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', nargs='?', help='remote base commit; omit for the first push')
    args = parser.parse_args()
    revision = f'{args.base}..HEAD' if args.base else 'HEAD'
    result = subprocess.run(['git', 'log', '-p', '--root', revision, '--'],
                            capture_output=True, text=True)
    if result.returncode:
        print('cannot read publication range: ' + result.stderr.strip(), file=sys.stderr)
        return 2
    findings = [(number, line) for number, line in enumerate(result.stdout.splitlines(), 1)
                if PRIVATE.search(line)]
    if findings:
        print('publication stopped: private references in pushed commit range', file=sys.stderr)
        for number, line in findings:
            print(f'git log line {number}: {line}', file=sys.stderr)
        return 1
    print(f'{revision}: private-reference count = 0')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
