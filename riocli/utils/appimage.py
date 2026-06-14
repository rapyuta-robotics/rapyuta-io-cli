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


def update_available(channel: str, remote_version: str, current_version: str) -> bool:
    """Whether ``remote_version`` should replace ``current_version``.

    Release channel uses semver precedence (no downgrades). Devel builds
    share a base version and differ only by ignored +build metadata, so
    compare the full string for any change.
    """
    if channel == CHANNEL_DEVEL:
        return remote_version != current_version
    return semver.Version.parse(remote_version).compare(current_version) > 0
