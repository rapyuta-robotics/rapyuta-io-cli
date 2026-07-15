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
import tempfile
from hashlib import sha256
from pathlib import Path

import click
import requests
import semver

from riocli.constants import Colors, Symbols

CHANNEL_RELEASE = "release"
CHANNEL_DEVEL = "devel"

# Public-read Azure Blob account (OKD4 Prod) hosting the rio AppImages.
# Containers: release / devel / dev. Override via RIO_APPIMAGE_BASE_URL for
# staging/testing.
DEFAULT_ACCOUNT_URL = "https://riocliartifacts.blob.core.windows.net"


def base_url() -> str:
    """Base URL of the AppImage blob account (env-overridable)."""
    return os.environ.get("RIO_APPIMAGE_BASE_URL", DEFAULT_ACCOUNT_URL)


def channel_for_version(version: str) -> str | None:
    """Map a CLI version to its update channel.

    The channel is carried in the version's local/build segment so the
    stamped version stays PEP 440-valid for ``uv build`` (a semver-style
    ``-prerelease`` would fail the wheel build). Examples:

    - ``10.6.0`` (no build metadata) -> release
    - ``10.6.0+devel.<sha>`` -> devel
    - ``10.6.0+dev.<branch>.<sha>`` (or any other build label) -> None
      (development build, not auto-updatable)
    """
    try:
        build = semver.Version.parse(version).build
    except ValueError as e:
        raise ValueError(f"Invalid version string: {version!r}") from e
    if build is None:
        return CHANNEL_RELEASE
    if build == CHANNEL_DEVEL or build.startswith(f"{CHANNEL_DEVEL}."):
        return CHANNEL_DEVEL
    return None


def manifest_url(channel: str) -> str:
    return f"{base_url()}/{channel}/latest.json"


def appimage_url(channel: str, filename: str) -> str:
    return f"{base_url()}/{channel}/{filename}"


def update_available(channel: str, remote_version: str, current_version: str) -> bool:
    """Whether ``remote_version`` should replace ``current_version``.

    Release channel uses semver precedence (no downgrades). Devel builds
    share a base version and differ only by ignored +build metadata, so
    compare the full string for any change (but never downgrade base version).
    """
    if channel == CHANNEL_DEVEL:
        if semver.Version.parse(remote_version).compare(current_version) < 0:
            return False
        return remote_version != current_version
    return semver.Version.parse(remote_version).compare(current_version) > 0


_REQUIRED_MANIFEST_KEYS = ("version", "file", "sha256")


def fetch_manifest(channel: str) -> dict:
    """Fetch, parse and validate the channel's latest.json (anonymous GET).

    Raises ValueError with an actionable message if the manifest is not a
    JSON object carrying the required keys, so callers get a clear error
    instead of a downstream KeyError/TypeError.
    """
    resp = requests.get(manifest_url(channel), timeout=10)
    resp.raise_for_status()
    manifest = resp.json()
    if not isinstance(manifest, dict) or not all(
        k in manifest for k in _REQUIRED_MANIFEST_KEYS
    ):
        raise ValueError(
            f"Malformed manifest for channel {channel!r}: "
            f"expected a JSON object with keys {_REQUIRED_MANIFEST_KEYS}"
        )
    return manifest


def _unlink_quietly(path: str | None) -> None:
    if path is not None:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


def download_and_replace(channel: str, manifest: dict, target: str | None = None) -> None:
    """Stream the AppImage named in the manifest into a sibling temp file,
    verify its sha256, then atomically replace ``target``.

    ``target`` defaults to the AppImage path (``APPIMAGE`` env var, set by the
    AppImage runtime) and falls back to the running interpreter.
    """
    if target is None:
        target = os.environ.get("APPIMAGE") or sys.executable

    expected = manifest.get("sha256")
    if not expected:
        raise ValueError(
            "Manifest missing 'sha256' — refusing to install unverified binary"
        )

    target_path = Path(target)
    tmp_path = None
    digest = sha256()
    try:
        # Temp file in the target's own directory so os.replace is an atomic
        # same-filesystem rename. Stream the download (AppImages are tens of
        # MB) and hash incrementally to bound peak memory.
        fd, tmp_path = tempfile.mkstemp(dir=target_path.parent, prefix=".rio-update-")
        with os.fdopen(fd, "wb") as f:
            with requests.get(
                appimage_url(channel, manifest["file"]),
                timeout=(10, 300),
                stream=True,
            ) as resp:
                resp.raise_for_status()
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
                    digest.update(chunk)
        if digest.hexdigest() != expected:
            raise ValueError("Checksum mismatch for the downloaded AppImage")
        os.chmod(tmp_path, 0o755)
        os.replace(tmp_path, target)
    except OSError:
        _unlink_quietly(tmp_path)
        click.secho(
            f"{Symbols.WARNING} Please consider running as a root user.",
            fg=Colors.YELLOW,
        )
        raise
    except Exception:
        # Any non-OS failure (checksum mismatch, network error) must still
        # clean up the partial temp file and leave the original untouched.
        _unlink_quietly(tmp_path)
        raise
