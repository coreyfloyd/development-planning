# Releasing the planning package

This follows [continuity's release contract](https://github.com/coreyfloyd/continuity/blob/main/RELEASING.md).
The verification script is adapted from continuity's `scripts/verify-release.sh`;
it retains its isolated keyring, signer fingerprint and signed checksum checks,
and adds explicit NOT VERIFIED failure diagnostics. The builder deliberately
separates archive creation from manual signing.

## Contract

The version in `.claude-plugin/plugin.json` determines the tag and title,
`v<version>`. Publish exactly these five assets:

```text
development-planning-<version>.tar.gz
development-planning-<version>.tar.gz.sha256
development-planning-<version>.tar.gz.asc
development-planning-release.asc
verify-release.sh
```

The archive is the tracked tree of the tagged commit, under a literal
`development-planning/` root. The armored detached signature signs the checksum,
not the archive. Publish the public key from `keys/` and the verifier from
`scripts/` unmodified. The fingerprint in `RELEASE_SIGNING_FINGERPRINT` is
`09674AFF392661238F4ACBD9F32B3A412CD5EFC5`, shared with continuity and Hippocampus.
Tests pin the public key to that fingerprint. Key rotation is a separate change.

## Prepare the candidate

Wait until the other intended release work is complete and integrated. Requires
Git, Python 3, Bash, GnuPG, `shasum`, uv, and authenticated GitHub CLI. The release
secret key and an interactive pinentry are required only for the human signing
step. From a clean, reviewed commit on main:

```sh
test "$(git branch --show-current)" = main
test -z "$(git status --porcelain --untracked-files=no)"
git fetch origin main --tags
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
VERSION_VALUE="$(python3 -c 'import json; print(json.load(open(".claude-plugin/plugin.json"))["version"])')"
TAG="v$VERSION_VALUE"
FINGERPRINT="$(tr -d '[:space:]' < RELEASE_SIGNING_FINGERPRINT)"
COMMIT="$(git rev-parse HEAD)"
! git rev-parse --verify --quiet "refs/tags/$TAG"
test -z "$(git ls-remote --tags origin "refs/tags/$TAG" "refs/tags/$TAG^{}")"
gh auth status
```

Run the full suite on the exact candidate; do not pipe away its exit status:

```sh
git diff --check
PLANNING_RELEASE_CHECK=1 uv run --with pytest python -m pytest -q -s tests
```

The tests build sandbox repositories, sign with disposable keys, check the
published public key and fingerprint, verify using release assets alone, and
reject altered archives, bad checksums, missing or invalid signatures and wrong
signers. They also check dirty-tree and tag/commit guards, tracked archive
contents, and that the builder never invokes GnuPG.

Check README and skill documentation for renamed names, stale counts, and
absolute claims before tagging. Before **every push**, scan the full pushed
range with `python3 scripts/check-public-range.py <remote-base>` (omit the base
only for a first push). Stop on a match; a clean final tree is insufficient.
For a release tag whose commit is already on remote main, still scan from the
previous published tag, or omit the base for the first release, to cover all
newly released history. Never move or force-push a published tag.

## Build: agent stops here

A feature branch may build an unsigned candidate for handoff. Publication must
use the final reviewed commit. Rebuild and re-sign if the commit changes.

```sh
bash scripts/build-release.sh dist
```

The builder refuses modified tracked files or a HEAD different from an existing
version tag, excludes untracked files, writes the archive and checksum, and
copies the public key and verifier. Rebuilding discards any old candidate
signature, which cannot be assumed valid for rebuilt bytes.

An agent stops after this unsigned build and hands the human the exact signing
command. Agents must never sign with the release key, handle its passphrase,
use loopback pinentry, read passphrase files/environment variables, or configure
a pinentry to bypass the human decision.

## Human signing only

From an interactive terminal, set `GPG_TTY` and sign the built checksum:

```sh
export GPG_TTY="$(tty)"
gpg --local-user 09674AFF392661238F4ACBD9F32B3A412CD5EFC5 \
  --armor --detach-sign \
  --output dist/development-planning-0.1.0.tar.gz.asc \
  dist/development-planning-0.1.0.tar.gz.sha256
```

Use the version being released if later than 0.1.0. Only the human answers
pinentry. A missing signature blocks publication.

## Verify, tag and publish

Safe for an authorized release operator after the signature exists. In the
same shell as the preparation variables:

```sh
set -e
test -s "dist/development-planning-$VERSION_VALUE.tar.gz.asc"
bash dist/verify-release.sh "dist/development-planning-$VERSION_VALUE.tar.gz" \
  dist/development-planning-release.asc "$FINGERPRINT"
# Inspect the listing: every entry must start with development-planning/.
tar -tzf "dist/development-planning-$VERSION_VALUE.tar.gz"
python3 scripts/check-public-range.py
git tag -a "$TAG" "$COMMIT" -m "development-planning $VERSION_VALUE"
git push origin "$TAG"
test "$(git ls-remote origin "refs/tags/$TAG^{}" | awk '{print $1}')" = "$COMMIT"
gh release create "$TAG" \
  "dist/development-planning-$VERSION_VALUE.tar.gz" \
  "dist/development-planning-$VERSION_VALUE.tar.gz.sha256" \
  "dist/development-planning-$VERSION_VALUE.tar.gz.asc" \
  dist/development-planning-release.asc dist/verify-release.sh \
  --verify-tag --title "$TAG" --notes-file /path/to/reviewed-release-notes.md
```

Stop immediately on any failed command. Do not publish after a failed verifier.
Write reviewed release notes outside the checkout before running the command.
The tag must name the exact archived commit; never replace existing assets
silently or move a tag to recover from a mismatch.

## Verify downloaded assets alone

```sh
VERIFY_DIR="$(mktemp -d)"
gh release download "$TAG" --dir "$VERIFY_DIR"
ls -la "$VERIFY_DIR"
test "$(find "$VERIFY_DIR" -maxdepth 1 -type f | wc -l | tr -d ' ')" = 5
cmp "$VERIFY_DIR/development-planning-release.asc" keys/development-planning-release.asc
cmp "$VERIFY_DIR/verify-release.sh" scripts/verify-release.sh
bash "$VERIFY_DIR/verify-release.sh" \
  "$VERIFY_DIR/development-planning-$VERSION_VALUE.tar.gz" \
  "$VERIFY_DIR/development-planning-release.asc" "$FINGERPRINT"
```

Verification uses only those downloaded files and the independently trusted
fingerprint. A missing or invalid signature, wrong signer, mismatched checksum,
or altered archive must fail, name the failed check, and report NOT VERIFIED.
