#!/bin/bash
# Verify a release archive: its checksum carries a signature by the expected key,
# and the archive matches the checksum. Usage:
#   verify-release.sh development-planning-<version>.tar.gz development-planning-release.asc <fingerprint>
set -euo pipefail

fail() {
  echo "verify-release.sh: $*; archive NOT VERIFIED" >&2
  exit 1
}
ARCHIVE="${1:-}"
[ -n "$ARCHIVE" ] || fail "archive argument missing"
KEYRING="${2:-}"
[ -n "$KEYRING" ] || fail "public key argument missing"
EXPECTED_FINGERPRINT="${3:-}"
[ -n "$EXPECTED_FINGERPRINT" ] || fail "signing fingerprint argument missing"
for tool in gpg shasum; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    fail "$tool is required but was not found on PATH"
  fi
done
for file in "$ARCHIVE" "$ARCHIVE.sha256" "$ARCHIVE.asc"; do
  if [ ! -f "$file" ]; then
    fail "missing $file"
  fi
done
[ -f "$KEYRING" ] || fail "public key missing: $KEYRING"
GNUPGHOME="$(mktemp -d)" || fail "temporary keyring creation failed"
trap 'gpgconf --kill gpg-agent >/dev/null 2>&1 || true; rm -rf "$GNUPGHOME"' EXIT
export GNUPGHOME
gpg --batch --import "$KEYRING" >/dev/null 2>&1 || fail "public key import failed"
NORMALIZED_EXPECTED="$(printf '%s' "$EXPECTED_FINGERPRINT" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')"
VERIFY_STATUS="$(gpg --batch --status-fd 1 --verify "$ARCHIVE.asc" "$ARCHIVE.sha256" 2>/dev/null || true)"
# VALIDSIG's last field is the primary key fingerprint of the signer.
SIGNING_FINGERPRINT="$(printf '%s\n' "$VERIFY_STATUS" | awk '$1 == "[GNUPG:]" && $2 == "VALIDSIG" {print $NF; exit}')"
if [ -z "$SIGNING_FINGERPRINT" ] || [ "$SIGNING_FINGERPRINT" != "$NORMALIZED_EXPECTED" ]; then
  fail "signature verification failed or signing fingerprint mismatch"
fi
# The signed checksum must name this archive, not another file beside it.
CHECKSUM_NAME="$(awk '{print $2; exit}' "$ARCHIVE.sha256" | sed 's/^\*//')"
if [ "$CHECKSUM_NAME" != "$(basename "$ARCHIVE")" ]; then
  fail "checksum names $CHECKSUM_NAME, not $(basename "$ARCHIVE")"
fi
(cd "$(dirname "$ARCHIVE")" && shasum -a 256 -c "$(basename "$ARCHIVE").sha256") || fail "archive checksum mismatch"
printf 'Archive VERIFIED: %s\n' "$ARCHIVE"
