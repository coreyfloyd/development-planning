#!/bin/bash
# Build an unsigned release candidate. Signing is manual; see RELEASING.md.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["version"])' "$ROOT/.claude-plugin/plugin.json")"
OUT="${1:-$ROOT/dist}"

# Only tracked-file changes count as dirty: git archive below never packages
# untracked files, so an in-tree output directory cannot leak into the archive.
if [ -n "$(cd "$ROOT" && git status --porcelain --untracked-files=no)" ]; then
  echo "refusing to build: working tree is dirty" >&2
  exit 1
fi

# If the release tag exists, HEAD must be the commit it points at.
TAG="v$VERSION"
if (cd "$ROOT" && git rev-parse --verify --quiet "refs/tags/$TAG") >/dev/null 2>&1; then
  HEAD_COMMIT="$(cd "$ROOT" && git rev-parse HEAD)"
  TAG_COMMIT="$(cd "$ROOT" && git rev-parse "refs/tags/$TAG^{commit}")"
  if [ "$HEAD_COMMIT" != "$TAG_COMMIT" ]; then
    echo "refusing to build: HEAD ($HEAD_COMMIT) is not tag $TAG ($TAG_COMMIT)" >&2
    exit 1
  fi
fi

mkdir -p "$OUT"
# Absolute, so a relative argument means the caller's directory, not $ROOT.
OUT="$(cd "$OUT" && pwd)"
ARCHIVE="$OUT/development-planning-$VERSION.tar.gz"
# The archive is the tracked tree at HEAD under a literal development-planning/ root,
# whatever the checkout directory is called.
(cd "$ROOT" && git archive --format=tar.gz --prefix=development-planning/ -o "$ARCHIVE" HEAD)
(cd "$OUT" && shasum -a 256 "$(basename "$ARCHIVE")") > "$ARCHIVE.sha256"
# Never invoke GnuPG here: the maintainer signs the checksum separately.
# Remove a prior signature before rebuilding so it cannot describe stale bytes.
rm -f "$ARCHIVE.asc"
cp "$ROOT/keys/development-planning-release.asc" "$OUT/"
cp "$ROOT/scripts/verify-release.sh" "$OUT/"
printf 'Unsigned candidate: %s\nMaintainer signature required before publication.\n' "$ARCHIVE"
