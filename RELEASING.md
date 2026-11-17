# Releasing the planning package

The package uses the same signed-checksum contract as [Hippocampus](https://github.com/coreyfloyd/hippocampus/blob/main/RELEASING.md).
The verification script is adapted from continuity's `scripts/verify-release.sh`;
it retains its isolated keyring, signer fingerprint and signed checksum checks,
and adds explicit NOT VERIFIED failure diagnostics. The builder deliberately
separates archive creation from approved checksum signing.

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
signing subkey is held by the configured managed-secret signing node; the
maintainer approves the exact candidate with **SIGN** and runs no signing command. From a clean, reviewed commit on main:

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

## Build the unsigned candidate

A feature branch may build an unsigned candidate for handoff. Publication must
use the final reviewed commit. Rebuild and re-sign if the commit changes.

```sh
bash scripts/build-release.sh dist
```

The builder refuses modified tracked files or a HEAD different from an existing
version tag, excludes untracked files, writes the archive and checksum, and
copies the public key and verifier. Rebuilding discards any old candidate
signature, which cannot be assumed valid for rebuilt bytes.

After this unsigned build, post the immutable candidate's repository, version,
commit, archive and checksum digests, checksum selection, and exact upload list
including the detached signature. Say **SIGN signs and publishes exactly this
release.** The maintainer replies exactly **SIGN** in that request's approval
thread; the signing operation reads that human reply within its deadline. An
agent then signs the approved checksum with the dedicated expiring signing-only
subkey and publishes exactly the approved files plus signature. Any change to
bytes, checksum selection or upload names needs a new summary and SIGN.

Operators invoke the signing operation without reading or relaying private-key
bytes or the passphrase. No standing permission, ticket state, agent interpretation
or unrelated reply substitutes for exact-release approval. The maintainer is
never asked to run signing commands, answer pinentry or provide a passphrase.

The published public key includes the dedicated signing subkey. The pinned primary
fingerprint and verifier remain unchanged. Consumers with an older public-key copy
must update it to verify new subkey-signed releases. Existing published releases,
tags and assets remain untouched.

## Agent signing and recovery

Use the delivered deterministic signing operation on the configured signing node.
Confirm its installed help and delivery receipt before invoking it; an unmerged
candidate is not an installed command. The normal signing operation is being
completed; this runbook does not imply it is already installed.

When that operation is unavailable, the fallback is the already approved
agent-operated managed-subkey method used for the companion package's 0.15.5
release. No retained reusable helper has been identified for that earlier inline
process. Obtain its recorded deterministic procedure and safe signing receipt
from the operation owner; confirm its inputs and exact release approval before
use. Delivery of the reusable signing command remains the operation owner's work. Do not recreate credential handling in an ad-hoc
shell command or hand the maintainer a manual signing command.

That process reads the provisioned signing subkey and passphrase inside the
process, imports only the dedicated subkey into a temporary mode-0700 GnuPG home,
and passes the passphrase through a file descriptor. Credentials never enter
model context, argv, output or logs. Sign only the approved checksum with the
configured subkey, verify the unchanged pinned primary fingerprint and authorized
signing subkey, and remove the temporary keyring. No primary private key belongs
on the signing node. An empty default GnuPG keyring does not establish missing
managed credentials.

A missing approved procedure, expired secret or signing failure is the operator's repair to
coordinate. Preserve the candidate and report the concrete failure; never ask
the maintainer to execute a recovery command, bypass SIGN, export a primary key,
provision new credentials, or weaken verification. A missing signature blocks
publication. Installation and restarts require their own authorization.

## Verify, tag and publish

Continue as the authorized release operator after the approved signature exists. In the
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

If publication already exists but downloaded verification failed, the release is
incomplete. Reconcile the existing approved assets and finish fresh-download
verification without replacing a tag or asset; remote existence alone is not
success.
