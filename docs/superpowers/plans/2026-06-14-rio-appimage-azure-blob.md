# rio AppImage on Azure Blob — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AppImage `rio update` download from public-read Azure Blob containers (channel-keyed) instead of the rate-limited `api.github.com` path; leave the pip/PyPI path untouched.

**Architecture:** A new focused module `riocli/utils/appimage.py` holds pure, unit-testable helpers (channel-from-version, URL builders, update-available check) plus the network fetch/replace. `bootstrap.py`'s `update` command branches: pip → existing PyPI flow; AppImage → new module. CI (`build-rio-appimage.sh`, `upload-appimage.yml`, `release.yml`) stamps a channel suffix into `__version__` for non-release builds and uploads the AppImage + a `latest.json` manifest to the matching container via azcopy.

**Tech Stack:** Python 3.13, Click, `requests`, `semver`, pytest (unit, no network). Bash + GitHub Actions + azcopy for CI. Azure Blob Storage (public-read containers).

**Spec:** `docs/superpowers/specs/2026-06-14-rio-appimage-azure-blob-design.md`

---

## File Structure

**New:**
- `riocli/utils/appimage.py` — channel detection, manifest/URL builders, update-available check, manifest fetch, download + executable swap. One responsibility: AppImage self-update against Azure Blob.
- `tests/unit/utils/test_appimage.py` — unit tests (pure functions + mocked network).

**Modified:**
- `riocli/utils/__init__.py` — remove the old GitHub-based `update_appimage` (lines 213-261). Keep `check_for_updates`, `is_pip_installation`, `pip_install_cli`.
- `riocli/bootstrap.py` — swap the `update_appimage` import for the new module; rewrite the `update` command's AppImage branch (lines 130-149, 52-58).
- `scripts/build-rio-appimage.sh` — stamp channel suffix for non-release builds; after build, compute sha256, write `latest.json`, azcopy-upload to the channel container.
- `.github/workflows/upload-appimage.yml` — PR → `dev/<branch>/`; push `devel` → `devel`; drop `main` trigger; pass `CHANNEL` + Azure secrets; PR comment links to blob URL.
- `.github/workflows/release.yml` — pass `CHANNEL=release` + Azure secrets to semantic-release env.

**Reference (do not change):** `riocli/chart/util.py` (Azure access pattern), `scripts/bump-version.sh` (sed stamping pattern), `tests/unit/test_chart_branch_util.py` (URL test pattern).

---

## Task 1: Channel detection + URL builders (pure functions)

**Files:**
- Create: `riocli/utils/appimage.py`
- Test: `tests/unit/utils/test_appimage.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/utils/test_appimage.py
# Copyright 2026 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from riocli.utils import appimage


@pytest.mark.parametrize(
    "version,expected",
    [
        ("10.6.0", appimage.CHANNEL_RELEASE),
        ("10.6.0-devel+abc1234", appimage.CHANNEL_DEVEL),
        ("10.6.0-devel.3+abc1234", appimage.CHANNEL_DEVEL),
        ("10.6.0-dev.feature-x+abc1234", None),
        ("10.6.0-rc.1+abc1234", None),
    ],
)
def test_channel_for_version(version, expected):
    assert appimage.channel_for_version(version) == expected


def test_manifest_url_default_account():
    assert appimage.manifest_url("devel") == (
        f"{appimage.DEFAULT_ACCOUNT_URL}/devel/latest.json"
    )


def test_appimage_url_default_account():
    assert appimage.appimage_url("release", "rio-10.6.0-x86_64.AppImage") == (
        f"{appimage.DEFAULT_ACCOUNT_URL}/release/rio-10.6.0-x86_64.AppImage"
    )


def test_base_url_env_override(monkeypatch):
    monkeypatch.setenv("RIO_APPIMAGE_BASE_URL", "https://staging.example.com")
    assert appimage.manifest_url("devel") == (
        "https://staging.example.com/devel/latest.json"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/utils/test_appimage.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'riocli.utils.appimage'`

- [ ] **Step 3: Write the module**

```python
# riocli/utils/appimage.py
# Copyright 2026 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
from hashlib import sha256
from pathlib import Path
from shutil import move
from tempfile import TemporaryDirectory

import click
import requests
import semver

from riocli.constants import Colors, Symbols

CHANNEL_RELEASE = "release"
CHANNEL_DEVEL = "devel"

# Public-read Azure Blob account that hosts the rio AppImages.
# NOTE: confirm the final account name with infra before the first
# blob-aware release (spec open question #1). Overridable via env for
# staging/testing.
DEFAULT_ACCOUNT_URL = "https://riocliartifacts.blob.core.windows.net"


def base_url() -> str:
    """Base URL of the AppImage blob account (env-overridable)."""
    return os.environ.get("RIO_APPIMAGE_BASE_URL", DEFAULT_ACCOUNT_URL)


def channel_for_version(version: str) -> str | None:
    """Map a CLI version to its update channel.

    Plain semver -> release. A ``devel``/``devel.N`` prerelease -> devel.
    Anything else (``dev.<branch>``, ``rc.N``, etc.) is not an
    auto-updatable channel and returns None.
    """
    pre = semver.Version.parse(version).prerelease
    if pre is None:
        return CHANNEL_RELEASE
    if pre == CHANNEL_DEVEL or pre.startswith(f"{CHANNEL_DEVEL}."):
        return CHANNEL_DEVEL
    return None


def manifest_url(channel: str) -> str:
    return f"{base_url()}/{channel}/latest.json"


def appimage_url(channel: str, filename: str) -> str:
    return f"{base_url()}/{channel}/{filename}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/utils/test_appimage.py -v`
Expected: PASS (all parametrized cases + URL tests)

- [ ] **Step 5: Commit**

```bash
git add riocli/utils/appimage.py tests/unit/utils/test_appimage.py
git commit -m "feat(update): add AppImage channel detection and blob URL builders"
```

---

## Task 2: Update-available check

**Files:**
- Modify: `riocli/utils/appimage.py`
- Test: `tests/unit/utils/test_appimage.py`

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/unit/utils/test_appimage.py

def test_update_available_release_newer():
    assert appimage.update_available("release", "10.7.0", "10.6.0") is True


def test_update_available_release_same():
    assert appimage.update_available("release", "10.6.0", "10.6.0") is False


def test_update_available_release_older_is_false():
    # never offer a downgrade on the release channel
    assert appimage.update_available("release", "10.5.0", "10.6.0") is False


def test_update_available_devel_differs():
    # devel builds differ only by +build metadata, which semver ignores;
    # any difference in the full version string means a newer commit.
    assert appimage.update_available(
        "devel", "10.6.0-devel+bbb2222", "10.6.0-devel+aaa1111"
    ) is True


def test_update_available_devel_same():
    assert appimage.update_available(
        "devel", "10.6.0-devel+aaa1111", "10.6.0-devel+aaa1111"
    ) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/utils/test_appimage.py -k update_available -v`
Expected: FAIL — `AttributeError: module 'riocli.utils.appimage' has no attribute 'update_available'`

- [ ] **Step 3: Implement**

```python
# append to riocli/utils/appimage.py

def update_available(channel: str, remote_version: str, current_version: str) -> bool:
    """Whether ``remote_version`` should replace ``current_version``.

    Release channel uses semver precedence (no downgrades). Devel builds
    share a base version and differ only by ignored +build metadata, so
    compare the full string for any change.
    """
    if channel == CHANNEL_DEVEL:
        return remote_version != current_version
    return semver.Version.parse(remote_version).compare(current_version) > 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/utils/test_appimage.py -k update_available -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add riocli/utils/appimage.py tests/unit/utils/test_appimage.py
git commit -m "feat(update): add channel-aware update-available check"
```

---

## Task 3: Manifest fetch + download/replace with checksum

**Files:**
- Modify: `riocli/utils/appimage.py`
- Test: `tests/unit/utils/test_appimage.py`

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/unit/utils/test_appimage.py
from hashlib import sha256
from unittest.mock import MagicMock


def _fake_response(content=b"", json_data=None):
    resp = MagicMock()
    resp.content = content
    resp.raise_for_status = MagicMock()
    if json_data is not None:
        resp.json = MagicMock(return_value=json_data)
    return resp


def test_fetch_manifest(monkeypatch):
    manifest = {"version": "10.6.0-devel+abc", "file": "rio.AppImage", "sha256": "x"}
    monkeypatch.setattr(
        appimage.requests, "get", lambda url, **kw: _fake_response(json_data=manifest)
    )
    assert appimage.fetch_manifest("devel") == manifest


def test_download_and_replace_writes_target(monkeypatch, tmp_path):
    payload = b"APPIMAGE-BYTES"
    digest = sha256(payload).hexdigest()
    manifest = {"version": "10.6.0", "file": "rio.AppImage", "sha256": digest}
    monkeypatch.setattr(
        appimage.requests, "get", lambda url, **kw: _fake_response(content=payload)
    )
    target = tmp_path / "rio"
    target.write_bytes(b"OLD")
    appimage.download_and_replace("release", manifest, target=str(target))
    assert target.read_bytes() == payload


def test_download_and_replace_checksum_mismatch(monkeypatch, tmp_path):
    manifest = {"version": "10.6.0", "file": "rio.AppImage", "sha256": "deadbeef"}
    monkeypatch.setattr(
        appimage.requests, "get", lambda url, **kw: _fake_response(content=b"bytes")
    )
    target = tmp_path / "rio"
    target.write_bytes(b"OLD")
    with pytest.raises(Exception, match="[Cc]hecksum"):
        appimage.download_and_replace("release", manifest, target=str(target))
    # original must be untouched on mismatch
    assert target.read_bytes() == b"OLD"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/utils/test_appimage.py -k "fetch_manifest or download_and_replace" -v`
Expected: FAIL — attributes `fetch_manifest` / `download_and_replace` do not exist

- [ ] **Step 3: Implement**

```python
# append to riocli/utils/appimage.py

def fetch_manifest(channel: str) -> dict:
    """Fetch and parse the channel's latest.json (anonymous GET)."""
    resp = requests.get(manifest_url(channel))
    resp.raise_for_status()
    return resp.json()


def download_and_replace(channel: str, manifest: dict, target: str | None = None) -> None:
    """Download the AppImage named in the manifest, verify its sha256,
    then atomically replace ``target`` (defaults to the running executable).
    """
    if target is None:
        target = sys.executable

    resp = requests.get(appimage_url(channel, manifest["file"]))
    resp.raise_for_status()
    content = resp.content

    expected = manifest.get("sha256")
    if expected and sha256(content).hexdigest() != expected:
        raise Exception("Checksum mismatch for the downloaded AppImage")

    with TemporaryDirectory() as tmp:
        save_to = Path(tmp) / "rio"
        save_to.write_bytes(content)
        os.chmod(save_to, 0o755)
        try:
            os.remove(target)
            move(save_to, target)
        except OSError as e:
            click.secho(
                f"{Symbols.WARNING} Please consider running as a root user.",
                fg=Colors.YELLOW,
            )
            raise e
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/utils/test_appimage.py -v`
Expected: PASS (whole file)

- [ ] **Step 5: Commit**

```bash
git add riocli/utils/appimage.py tests/unit/utils/test_appimage.py
git commit -m "feat(update): fetch manifest and replace AppImage with checksum verify"
```

---

## Task 4: Wire the new module into the `update` command

**Files:**
- Modify: `riocli/bootstrap.py` (imports lines 52-58; `update` command lines 130-149)
- Modify: `riocli/utils/__init__.py` (remove old `update_appimage`, lines 213-261)
- Test: `tests/unit/test_update_command.py` (new)

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_update_command.py
# Copyright 2026 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import patch

from click.testing import CliRunner

from riocli.bootstrap import cli


def test_update_devel_appimage_uses_blob():
    """A devel AppImage runs the blob path, not the GitHub path."""
    manifest = {
        "version": "10.9.9-devel+newsha",
        "file": "rio-10.9.9-devel+newsha-x86_64.AppImage",
        "sha256": "x",
    }
    with (
        patch("riocli.bootstrap.__version__", "10.6.0-devel+oldsha"),
        patch("riocli.bootstrap.is_pip_installation", return_value=False),
        patch("riocli.bootstrap.appimage.fetch_manifest", return_value=manifest) as fm,
        patch("riocli.bootstrap.appimage.download_and_replace") as dr,
    ):
        result = CliRunner().invoke(cli, ["update", "--silent"])
    assert result.exit_code == 0
    fm.assert_called_once_with("devel")
    dr.assert_called_once_with("devel", manifest)


def test_update_dev_build_is_not_updatable():
    """A feature-branch (dev.*) build refuses to auto-update."""
    with (
        patch("riocli.bootstrap.__version__", "10.6.0-dev.feature-x+sha"),
        patch("riocli.bootstrap.is_pip_installation", return_value=False),
        patch("riocli.bootstrap.appimage.fetch_manifest") as fm,
    ):
        result = CliRunner().invoke(cli, ["update", "--silent"])
    assert result.exit_code == 0
    assert "development build" in result.output.lower()
    fm.assert_not_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_update_command.py -v`
Expected: FAIL — `riocli.bootstrap` has no attribute `appimage` (import not yet added)

- [ ] **Step 3: Edit `riocli/bootstrap.py` imports**

Replace the util import block (lines 52-58) — drop `update_appimage`, add the module import:

```python
from riocli.utils import (
    AliasedGroup,
    check_for_updates,
    is_pip_installation,
    pip_install_cli,
)
from riocli.utils import appimage
```

- [ ] **Step 4: Rewrite the `update` command body**

Replace lines 130-149 (from `available, latest = check_for_updates(...)` through the `try/except`) with:

```python
    if is_pip_installation():
        available, latest = check_for_updates(__version__)
        if not available:
            click.secho("🎉 You are using the latest version", fg=Colors.GREEN)
            return
        click.secho(f"🎉 A newer version ({latest}) is available.", fg=Colors.GREEN)
        if not silent:
            _ = click.confirm("Do you want to update?", abort=True, default=False)
        try:
            _ = pip_install_cli(version=latest)
        except Exception as e:
            click.secho(f"{Symbols.ERROR} Failed to update: {e}", fg=Colors.RED)
            raise SystemExit(1) from e
        click.secho(f"{Symbols.SUCCESS} Update successful!", fg=Colors.GREEN)
        return

    # AppImage installation: update from our Azure Blob channel.
    channel = appimage.channel_for_version(__version__)
    if channel is None:
        click.secho(
            f"{Symbols.WARNING} This is a development build; auto-update is "
            "disabled. Rebuild from your branch or install a release.",
            fg=Colors.YELLOW,
        )
        return

    try:
        manifest = appimage.fetch_manifest(channel)
    except Exception as e:
        click.secho(f"{Symbols.ERROR} Failed to update: {e}", fg=Colors.RED)
        raise SystemExit(1) from e

    if not appimage.update_available(channel, manifest["version"], __version__):
        click.secho("🎉 You are using the latest version", fg=Colors.GREEN)
        return

    click.secho(
        f"🎉 A newer version ({manifest['version']}) is available.", fg=Colors.GREEN
    )
    if not silent:
        _ = click.confirm("Do you want to update?", abort=True, default=False)

    try:
        appimage.download_and_replace(channel, manifest)
    except Exception as e:
        click.secho(f"{Symbols.ERROR} Failed to update: {e}", fg=Colors.RED)
        raise SystemExit(1) from e

    click.secho(f"{Symbols.SUCCESS} Update successful!", fg=Colors.GREEN)
```

- [ ] **Step 5: Remove the old `update_appimage` from `riocli/utils/__init__.py`**

Delete the entire `def update_appimage(version: str):` function (lines 213-261). Leave `check_for_updates`, `pip_install_cli`, `is_pip_installation` intact.

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_update_command.py tests/unit/utils/test_appimage.py -v`
Expected: PASS

- [ ] **Step 7: Lint + verify nothing else imports the removed symbol**

Run: `grep -rn "update_appimage" riocli/ tests/`
Expected: no matches (the import in bootstrap was removed)

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: clean (run `uv run ruff format .` if format check fails)

- [ ] **Step 8: Commit**

```bash
git add riocli/bootstrap.py riocli/utils/__init__.py tests/unit/test_update_command.py
git commit -m "feat(update): route AppImage updates through Azure Blob channels"
```

---

## Task 5: Stamp channel suffix into `__version__` for non-release builds

**Files:**
- Modify: `scripts/build-rio-appimage.sh`

Context: For `release`, `bump-version.sh` already set a plain semver `__version__` before this script runs, so `channel_for_version` returns `release` — no stamping needed. For `devel`/`dev`, the binary must report a channel-tagged version so the installed AppImage is self-describing.

- [ ] **Step 1: Add a stamping block near the top of the build (before `uv build`)**

Insert after the `mc` download lines (after line 14, before `# Creating rio-cli wheel`):

```bash
# Stamp a channel suffix into __version__ for non-release builds so the
# installed AppImage knows which Azure Blob container to update from.
# CHANNEL is set by the calling workflow (release|devel|dev). Release
# builds are versioned upstream by bump-version.sh and are left as-is.
CHANNEL="${CHANNEL:-dev}"
if [[ "$CHANNEL" != "release" ]]; then
  BASE_VERSION=$(grep -m1 '^__version__' riocli/bootstrap.py | sed -E 's/.*"([^"]+)".*/\1/')
  SHORT_SHA=$(git rev-parse --short "${GITHUB_SHA:-HEAD}")
  if [[ "$CHANNEL" == "devel" ]]; then
    STAMP="${BASE_VERSION}-devel+${SHORT_SHA}"
  else
    # dev / PR build: include a semver-safe branch identifier
    RAW_BRANCH="${GITHUB_HEAD_REF:-${GITHUB_REF_NAME:-local}}"
    SAFE_BRANCH=$(echo "$RAW_BRANCH" | tr -c '0-9A-Za-z' '-' | sed -E 's/-+/-/g; s/^-|-$//g')
    STAMP="${BASE_VERSION}-dev.${SAFE_BRANCH}+${SHORT_SHA}"
  fi
  sed -i -E "0,/^__version__.*/s/^__version__.*/__version__ = \"${STAMP}\"/" riocli/bootstrap.py
fi
```

- [ ] **Step 2: Shellcheck the script**

Run: `shellcheck scripts/build-rio-appimage.sh || true`
Expected: no new errors introduced by the added block (pre-existing warnings acceptable).

- [ ] **Step 3: Local dry-run of the stamping logic (no full build)**

Run:
```bash
cp riocli/bootstrap.py /tmp/bootstrap.bak
CHANNEL=devel GITHUB_SHA=$(git rev-parse HEAD) bash -c '
  BASE_VERSION=$(grep -m1 "^__version__" riocli/bootstrap.py | sed -E "s/.*\"([^\"]+)\".*/\1/")
  SHORT_SHA=$(git rev-parse --short "${GITHUB_SHA:-HEAD}")
  echo "would stamp: ${BASE_VERSION}-devel+${SHORT_SHA}"'
cp /tmp/bootstrap.bak riocli/bootstrap.py
```
Expected: prints `would stamp: <current-version>-devel+<sha>` and restores the file.

- [ ] **Step 4: Commit**

```bash
git add scripts/build-rio-appimage.sh
git commit -m "ci: stamp channel suffix into version for devel/dev AppImage builds"
```

---

## Task 6: Upload AppImage + manifest to Azure Blob in the build script

**Files:**
- Modify: `scripts/build-rio-appimage.sh`

- [ ] **Step 1: Append an upload stage at the end of the script (after `./appimagetool-x86_64.AppImage -n squashfs-root/`)**

```bash
# Upload the built AppImage to the channel's Azure Blob container.
# Download stays anonymous (public-read); upload authenticates with a
# write-scoped SAS token. Required env: CHANNEL, AZURE_STORAGE_ACCOUNT,
# AZURE_SAS_TOKEN. dev/PR builds land under dev/<branch>/ and carry no
# manifest (not an update channel).
APPIMAGE_FILE=$(ls rio*.AppImage | head -n1)

if [[ -n "${AZURE_STORAGE_ACCOUNT:-}" && -n "${AZURE_SAS_TOKEN:-}" ]]; then
  if [[ "$CHANNEL" == "dev" ]]; then
    RAW_BRANCH="${GITHUB_HEAD_REF:-${GITHUB_REF_NAME:-local}}"
    DEST="https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/dev/${RAW_BRANCH}/${APPIMAGE_FILE}?${AZURE_SAS_TOKEN}"
    azcopy copy "${APPIMAGE_FILE}" "${DEST}"
  else
    SHA256=$(sha256sum "${APPIMAGE_FILE}" | cut -d' ' -f1)
    VERSION=$(grep -m1 '^__version__' ../riocli/bootstrap.py | sed -E 's/.*"([^"]+)".*/\1/')
    cat > latest.json <<EOF
{"version": "${VERSION}", "file": "${APPIMAGE_FILE}", "sha256": "${SHA256}"}
EOF
    BASE="https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/${CHANNEL}"
    azcopy copy "${APPIMAGE_FILE}" "${BASE}/${APPIMAGE_FILE}?${AZURE_SAS_TOKEN}"
    azcopy copy "latest.json" "${BASE}/latest.json?${AZURE_SAS_TOKEN}"
  fi
else
  echo "AZURE_STORAGE_ACCOUNT / AZURE_SAS_TOKEN not set — skipping blob upload"
fi
```

Note: the script `cd scripts` earlier (line ~`cd scripts`), so `riocli/bootstrap.py` is referenced as `../riocli/bootstrap.py` here. Confirm the relative path against the `cd` in the script before running.

- [ ] **Step 2: Ensure azcopy is available — add install near the `mc` install (top of script)**

```bash
# Install azcopy for Azure Blob uploads
wget -q https://aka.ms/downloadazcopy-v10-linux -O azcopy.tar.gz
tar -xzf azcopy.tar.gz --strip-components=1 --wildcards '*/azcopy'
chmod +x azcopy
export PATH="$PWD:$PATH"
```

- [ ] **Step 3: Shellcheck**

Run: `shellcheck scripts/build-rio-appimage.sh || true`
Expected: no new errors.

- [ ] **Step 4: Commit**

```bash
git add scripts/build-rio-appimage.sh
git commit -m "ci: upload AppImage and latest.json manifest to Azure Blob"
```

---

## Task 7: Update `upload-appimage.yml` (devel + dev channels)

**Files:**
- Modify: `.github/workflows/upload-appimage.yml`

- [ ] **Step 1: Change triggers — drop `main`**

```yaml
on:
  push:
    branches:
    - devel
  pull_request:
```

- [ ] **Step 2: Set `CHANNEL` + Azure secrets on the build step**

Replace the `Create AppImage` step's `env:` block:

```yaml
      - name: Create AppImage
        run: ./scripts/build-rio-appimage.sh
        shell: bash
        env:
          CHANNEL: ${{ github.event_name == 'pull_request' && 'dev' || 'devel' }}
          MINIO_URL: ${{ secrets.MINIO_URL }}
          MINIO_ACCESS_KEY: ${{ secrets.MINIO_ACCESS_KEY }}
          MINIO_SECRET: ${{ secrets.MINIO_SECRET }}
          AZURE_STORAGE_ACCOUNT: ${{ secrets.AZURE_STORAGE_ACCOUNT }}
          AZURE_SAS_TOKEN: ${{ secrets.AZURE_SAS_TOKEN }}
```

- [ ] **Step 3: Point the PR comment at the blob URL**

Replace the body of the `Edit the last bot comment` and `Artifact Comment on PR` steps so the link is the blob path (the existing GitHub-Actions-artifact link is removed). Use:

```yaml
      - name: Comment blob link on PR
        if: github.event_name == 'pull_request'
        run: |
          BRANCH="${{ github.head_ref }}"
          ACCOUNT="${{ secrets.AZURE_STORAGE_ACCOUNT }}"
          FILE=$(ls scripts/rio*.AppImage | xargs -n1 basename | head -n1)
          URL="https://${ACCOUNT}.blob.core.windows.net/dev/${BRANCH}/${FILE}"
          gh pr comment "$PR_NUMBER" --edit-last -b "**🤖 PR AppImage:** [$FILE]($URL)" \
            || gh pr comment "$PR_NUMBER" -b "**🤖 PR AppImage:** [$FILE]($URL)"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.number }}
```

Delete the now-obsolete `Edit the last bot comment`, `Delete existing bot comments`, and `Artifact Comment on PR` steps. The `Upload AppImage artifact` (`actions/upload-artifact`) step may be kept as a secondary or removed — keeping it adds a GitHub fallback at no cost; recommended to keep.

- [ ] **Step 4: Validate workflow YAML**

Run: `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/upload-appimage.yml'))"`
Expected: no exception (valid YAML).

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/upload-appimage.yml
git commit -m "ci: upload devel/PR AppImages to Azure Blob, link blob URL on PRs"
```

---

## Task 8: Update `release.yml` (release channel)

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: Add `CHANNEL=release` + Azure secrets to the semantic-release step env**

Add to the `Run semantic-release` step's `env:` block (alongside the existing `MINIO_*`):

```yaml
          CHANNEL: release
          AZURE_STORAGE_ACCOUNT: ${{ secrets.AZURE_STORAGE_ACCOUNT }}
          AZURE_SAS_TOKEN: ${{ secrets.AZURE_SAS_TOKEN }}
```

(`.releaserc.json` already calls `build-rio-appimage.sh ${nextRelease.version}` as a `prepareCmd`; with `CHANNEL=release` it now also uploads the versioned AppImage + `latest.json` to the `release` container. The `@semantic-release/github` asset attach stays — GitHub Release remains the transition fallback.)

- [ ] **Step 2: Validate workflow YAML**

Run: `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"`
Expected: no exception.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: upload release AppImage to Azure Blob via semantic-release"
```

---

## Task 9: Document required secrets + infra prerequisites

**Files:**
- Create: `docs/update-channels.md` (keep it out of CLAUDE.md to avoid bloat)

- [ ] **Step 1: Write the doc**

```markdown
# rio update channels

`rio update` updates an AppImage install from Azure Blob Storage (public-read),
keyed by the running binary's version:

| Version pattern | Channel | Source |
|---|---|---|
| `X.Y.Z` | release | `https://<account>.blob.core.windows.net/release/latest.json` |
| `X.Y.Z-devel+<sha>` | devel | `.../devel/latest.json` |
| `X.Y.Z-dev.<branch>+<sha>` | none | not auto-updatable (dev build) |

pip installs are unaffected — they continue to upgrade from PyPI.

Override the blob base URL for testing: `RIO_APPIMAGE_BASE_URL=https://staging... rio update`.

## CI prerequisites (GitHub secrets)

- `AZURE_STORAGE_ACCOUNT` — storage account name (public-read containers `release`, `devel`, `dev`).
- `AZURE_SAS_TOKEN` — write-scoped, container-scoped, time-bound SAS used by CI uploads.

## Infra checklist (one-time)

1. Provision the storage account in the OKD4 Prod subscription.
2. Create containers `release` (permanent), `devel` (30d lifecycle), `dev` (15d lifecycle), all with anonymous blob read.
3. Issue a write SAS; store it as `AZURE_SAS_TOKEN`. Set `AZURE_STORAGE_ACCOUNT`.
4. Set `DEFAULT_ACCOUNT_URL` in `riocli/utils/appimage.py` to the real account before the first blob-aware release.
```

- [ ] **Step 2: Commit**

```bash
git add docs/update-channels.md
git commit -m "docs: document rio update channels and CI secrets"
```

---

## Final verification

- [ ] Run the full unit suite: `uv run pytest tests/unit/ -v` — Expected: PASS
- [ ] Lint/format: `uv run ruff check . && uv run ruff format --check .` — Expected: clean
- [ ] Confirm no dangling reference: `grep -rn "update_appimage\|api.github.com/repos/rapyuta-robotics/rapyuta-io-cli/releases" riocli/` — Expected: no matches
- [ ] Manual end-to-end (staging): build a devel AppImage, host `devel/latest.json` + file on a staging container, run `RIO_APPIMAGE_BASE_URL=<staging> ./rio update` from an older devel build, confirm it downloads, verifies sha256, and swaps the binary.

## Notes for the implementer

- **Backwards compat:** AppImages already in the field run the old GitHub-based updater. They keep working only because the GitHub Release asset is retained. The first blob-aware version must also ship as a normal GitHub Release so existing users can reach it; only after the field rolls past the last GitHub-only version may the GitHub asset attach be dropped (future cleanup, out of scope here).
- **Account name:** `DEFAULT_ACCOUNT_URL` in `appimage.py` and `AZURE_STORAGE_ACCOUNT` in CI must match the real provisioned account (spec open question #1). `riocliartifacts` is a placeholder default.
- **Do not touch** the pip path, `check_for_updates`, `pip_install_cli`, the MinIO build-input cache, or PyPI publishing.
