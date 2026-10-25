"""Release archives: build one, verify it, and pin the published signing key.

The build and verify tests sign with a throwaway key generated in a temporary
GnuPG home. The published key is never used to sign here; its test only checks
that the committed key and fingerprint agree.
"""
import json
from pathlib import Path
import os
import shutil
import subprocess
import tarfile
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "scripts", "build-release.sh")
VERIFY = os.path.join(ROOT, "scripts", "verify-release.sh")
PUBLISHED_KEY = os.path.join(ROOT, "keys", "development-planning-release.asc")
FINGERPRINT_FILE = os.path.join(ROOT, "RELEASE_SIGNING_FINGERPRINT")
# The fingerprint Hippocampus releases are signed with. Continuity releases use the same key.
HIPPOCAMPUS_RELEASE_FINGERPRINT = "09674AFF392661238F4ACBD9F32B3A412CD5EFC5"
SNAPSHOT_IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".DS_Store", "dist", ".worktrees")

@pytest.fixture(autouse=True)
def require_gnupg():
    for tool in ("gpg", "gpgconf"):
        if shutil.which(tool) is None:
            reason = f"{tool} is not installed"
            if os.environ.get("PLANNING_RELEASE_CHECK") == "1":
                pytest.fail(reason, pytrace=False)
            pytest.skip(reason)


def version():
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as handle:
        return json.load(handle)["version"]


def gpg(home, *args, check=True):
    return subprocess.run(["gpg", "--homedir", home, "--batch", *args],
                          text=True, capture_output=True, check=check)


@pytest.fixture
def gnupg_home():
    # A short path: gpg-agent's socket lives in the home, and macOS caps socket paths at 104 bytes.
    home = tempfile.mkdtemp(prefix="gpg")
    os.chmod(home, 0o700)
    yield home
    subprocess.run(["gpgconf", "--homedir", home, "--kill", "gpg-agent"], capture_output=True)
    shutil.rmtree(home, ignore_errors=True)


def generate_key(home, name):
    """A throwaway, unprotected signing key; returns its fingerprint."""
    before = set(fingerprints(home, secret=True))
    params = os.path.join(home, f"{name}.params")
    with open(params, "w", encoding="utf-8") as handle:
        handle.write("%no-protection\nKey-Type: eddsa\nKey-Curve: ed25519\nKey-Usage: sign\n"
                     f"Name-Real: {name}\nName-Email: {name}@example.invalid\nExpire-Date: 0\n%commit\n")
    gpg(home, "--generate-key", params)
    (new,) = set(fingerprints(home, secret=True)) - before
    return new


def fingerprints(home, secret=False):
    """Primary key fingerprints in the keyring."""
    listing = gpg(home, "--with-colons", "--list-secret-keys" if secret else "--list-keys", check=False).stdout
    result, primary = [], False
    for line in listing.splitlines():
        fields = line.split(":")
        if fields[0] in ("pub", "sec"):
            primary = True
        elif fields[0] == "fpr" and primary:
            result.append(fields[9])
            primary = False
        elif fields[0] in ("sub", "ssb"):
            primary = False
    return result


def export(home, key, path):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(gpg(home, "--armor", "--export", key).stdout)
    return path


def sandbox_repo(dest):
    """A git repository holding this checkout's current files, so a test controls its tag and dirty state."""
    shutil.copytree(ROOT, dest, ignore=SNAPSHOT_IGNORE)
    for args in (["init", "--quiet"], ["config", "user.email", "test@example.invalid"],
                 ["config", "user.name", "development-planning test"], ["config", "commit.gpgsign", "false"],
                 ["config", "tag.gpgsign", "false"], ["add", "-A"], ["commit", "--quiet", "-m", "snapshot"]):
        subprocess.run(["git", *args], cwd=dest, check=True, capture_output=True)
    return dest


def build(repo, out, key, home, cwd=None):
    env = dict(os.environ, GNUPGHOME=home)
    result = subprocess.run(["bash", os.path.join(repo, "scripts", "build-release.sh"), out],
                            text=True, capture_output=True, env=env, cwd=cwd)
    if result.returncode == 0:
        archive = os.path.join(os.path.abspath(os.path.join(cwd or os.getcwd(), out)),
                               f"development-planning-{version()}.tar.gz")
        # Only ephemeral test keys sign here; never the published release key.
        gpg(home, "--yes", "--local-user", key, "--detach-sign", "--armor",
            "--output", archive + ".asc", archive + ".sha256")
    return result


def verify(archive, keyring, fingerprint):
    return subprocess.run(["bash", VERIFY, archive, keyring, fingerprint], text=True, capture_output=True)


def test_committed_key_is_the_published_hippocampus_release_key(gnupg_home):
    with open(FINGERPRINT_FILE, encoding="utf-8") as handle:
        committed = handle.read().strip()
    assert committed == HIPPOCAMPUS_RELEASE_FINGERPRINT
    gpg(gnupg_home, "--import", PUBLISHED_KEY)
    assert fingerprints(gnupg_home) == [committed]
    assert fingerprints(gnupg_home, secret=True) == []


def test_built_archive_verifies_and_holds_only_the_tracked_tree(tmp_path, gnupg_home):
    key = generate_key(gnupg_home, "release")
    keyring = export(gnupg_home, key, str(tmp_path / "release.asc"))
    repo = sandbox_repo(str(tmp_path / "checkout-with-another-name"))
    (tmp_path / "checkout-with-another-name" / "untracked.txt").write_text("not shipped\n")

    out = os.path.join(repo, "dist", ".worktrees")
    result = build(repo, out, key, gnupg_home)
    assert result.returncode == 0, result.stderr
    archive = os.path.join(out, f"development-planning-{version()}.tar.gz")

    result = verify(archive, keyring, key.lower())
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout

    tracked = subprocess.run(["git", "ls-files"], cwd=repo, text=True, capture_output=True, check=True)
    with tarfile.open(archive) as tar:
        files = sorted(m.name for m in tar.getmembers() if not m.isdir())
    assert files == sorted("development-planning/" + name for name in tracked.stdout.splitlines())


def test_relative_output_directory_resolves_from_the_caller(tmp_path, gnupg_home):
    key = generate_key(gnupg_home, "release")
    keyring = export(gnupg_home, key, str(tmp_path / "release.asc"))
    repo = sandbox_repo(str(tmp_path / "repo"))
    caller = tmp_path / "caller"
    caller.mkdir()

    result = build(repo, "dist", key, gnupg_home, cwd=str(caller))
    assert result.returncode == 0, result.stderr
    archive = caller / "dist" / f"development-planning-{version()}.tar.gz"
    assert archive.is_file()
    assert not os.path.exists(os.path.join(repo, "dist", ".worktrees"))
    assert verify(str(archive), keyring, key).returncode == 0


def test_verify_rejects_another_key_a_tampered_archive_and_a_swapped_checksum(tmp_path, gnupg_home):
    key = generate_key(gnupg_home, "release")
    other = generate_key(gnupg_home, "other")
    keyring = export(gnupg_home, key, str(tmp_path / "release.asc"))
    both = tmp_path / "both.asc"
    both.write_text(keyring_text(keyring) + keyring_text(export(gnupg_home, other, str(tmp_path / "other.asc"))))
    repo = sandbox_repo(str(tmp_path / "repo"))

    assert build(repo, str(tmp_path / "other-dist"), other, gnupg_home).returncode == 0
    other_archive = str(tmp_path / "other-dist" / f"development-planning-{version()}.tar.gz")
    rejected = verify(other_archive, str(both), key)
    assert rejected.returncode != 0
    assert "fingerprint mismatch" in rejected.stderr

    assert build(repo, str(tmp_path / "dist"), key, gnupg_home).returncode == 0
    archive = str(tmp_path / "dist" / f"development-planning-{version()}.tar.gz")
    renamed = str(tmp_path / "dist" / "development-planning-renamed.tar.gz")
    shutil.copy(archive, renamed)
    shutil.copy(archive + ".sha256", renamed + ".sha256")
    shutil.copy(archive + ".asc", renamed + ".asc")
    assert verify(renamed, keyring, key).returncode != 0

    with open(archive, "ab") as handle:
        handle.write(b"x")
    assert verify(archive, keyring, key).returncode != 0


def keyring_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def test_build_refuses_a_dirty_tree_and_a_commit_past_the_release_tag(tmp_path, gnupg_home):
    key = generate_key(gnupg_home, "release")
    repo = sandbox_repo(str(tmp_path / "repo"))
    readme = os.path.join(repo, "README.md")
    with open(readme, "a", encoding="utf-8") as handle:
        handle.write("\nlocal edit\n")
    dirty = build(repo, str(tmp_path / "dirty"), key, gnupg_home)
    assert dirty.returncode != 0
    assert "dirty" in dirty.stderr
    subprocess.run(["git", "checkout", "--", "README.md"], cwd=repo, check=True)

    tag = f"v{version()}"
    subprocess.run(["git", "tag", "-a", tag, "-m", tag], cwd=repo, check=True)
    assert build(repo, str(tmp_path / "at-tag"), key, gnupg_home).returncode == 0
    subprocess.run(["git", "commit", "--quiet", "--allow-empty", "-m", "past the tag"], cwd=repo, check=True)
    past = build(repo, str(tmp_path / "past-tag"), key, gnupg_home)
    assert past.returncode != 0
    assert tag in past.stderr


@pytest.mark.parametrize("damage,diagnostic", [
    ("archive", "archive checksum"),
    ("checksum", "signature"),
    ("missing-signature", "missing"),
    ("invalid-signature", "signature"),
    ("signed-wrong-name", "checksum names"),
    ("signed-wrong-checksum", "archive checksum"),
    ("wrong-fingerprint", "fingerprint"),
    ("missing-key", "public key"),
])
def test_downloaded_assets_fail_closed(tmp_path, gnupg_home, damage, diagnostic):
    key = generate_key(gnupg_home, "release")
    repo = sandbox_repo(str(tmp_path / "repo"))
    out = tmp_path / "download"
    assert build(repo, str(out), key, gnupg_home).returncode == 0
    public = export(gnupg_home, key, str(out / "development-planning-release.asc"))
    script = out / "verify-release.sh"
    shutil.copy(VERIFY, script)
    archive = out / f"development-planning-{version()}.tar.gz"
    checksum = archive.with_name(archive.name + ".sha256")
    signature = archive.with_name(archive.name + ".asc")
    if damage == "archive":
        archive.write_bytes(archive.read_bytes() + b"changed")
    elif damage == "checksum":
        checksum.write_text("0" * 64 + "  " + archive.name + "\n")
    elif damage == "missing-signature":
        signature.unlink()
    elif damage == "invalid-signature":
        signature.write_text("invalid signature\n")
    elif damage == "signed-wrong-name":
        checksum.write_text("0" * 64 + "  other.tar.gz\n")
        gpg(gnupg_home, "--yes", "--local-user", key, "--detach-sign", "--armor",
            "--output", str(signature), str(checksum))
    elif damage == "signed-wrong-checksum":
        checksum.write_text("0" * 64 + "  " + archive.name + "\n")
        gpg(gnupg_home, "--yes", "--local-user", key, "--detach-sign", "--armor",
            "--output", str(signature), str(checksum))
    elif damage == "wrong-fingerprint":
        key = "0" * 40
    elif damage == "missing-key":
        os.unlink(public)
    result = subprocess.run(["bash", str(script), str(archive), public, key],
                            cwd=out, text=True, capture_output=True)
    assert result.returncode != 0
    assert diagnostic in result.stderr.lower()
    assert "NOT VERIFIED" in result.stderr


def test_build_never_invokes_gpg_and_copies_standalone_assets(tmp_path):
    repo = sandbox_repo(str(tmp_path / "repo"))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    marker = tmp_path / "gpg-called"
    stub = bin_dir / "gpg"
    stub.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\nexit 99\n')
    stub.chmod(0o755)
    out = tmp_path / "release"
    result = subprocess.run(["bash", os.path.join(repo, "scripts/build-release.sh"), str(out)],
                            env=dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"]),
                            text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert not marker.exists()
    assert sorted(p.name for p in out.iterdir()) == sorted([
        f"development-planning-{version()}.tar.gz",
        f"development-planning-{version()}.tar.gz.sha256",
        "development-planning-release.asc", "verify-release.sh"])
    assert (out / "verify-release.sh").read_bytes() == Path(VERIFY).read_bytes()
    assert (out / "development-planning-release.asc").read_bytes() == Path(PUBLISHED_KEY).read_bytes()
