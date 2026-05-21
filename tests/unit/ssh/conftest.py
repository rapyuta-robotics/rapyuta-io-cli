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

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, PropertyMock

import pytest

from riocli.config.config import Configuration

if TYPE_CHECKING:
    from pathlib import Path


def _generate_test_key_pair(ssh_dir: Path) -> tuple[Path, Path]:
    """Generate a real ed25519 key pair in *ssh_dir* via ssh-keygen."""
    priv_path = ssh_dir / "rio_ed25519"
    pub_path = ssh_dir / "rio_ed25519.pub"

    subprocess.run(
        [
            "ssh-keygen",
            "-t",
            "ed25519",
            "-f",
            str(priv_path),
            "-N",
            "",
            "-C",
            "rio-ssh",
            "-q",
        ],
        check=True,
        capture_output=True,
    )
    return priv_path, pub_path


def _mock_v2_client(certificate: str = "ssh-ed25519-cert-v01@openssh.com AAAA..."):
    """Return a mock v2 client with sign_ssh_public_key wired up."""
    client = MagicMock()
    response = MagicMock()
    response.certificate = certificate
    client.sign_ssh_public_key.return_value = response
    return client


def _make_subprocess_result(returncode: int = 0, stdout: str = "", stderr: str = ""):
    """Create a mock subprocess.CompletedProcess."""
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def _make_config_for_dir(d: Path) -> MagicMock:
    """Build a mock Configuration whose SSH properties point at *d*."""
    config = MagicMock(spec=Configuration)
    type(config).ssh_private_key = PropertyMock(return_value=d / "rio_ed25519")
    type(config).ssh_public_key = PropertyMock(return_value=d / "rio_ed25519.pub")
    type(config).ssh_certificate = PropertyMock(
        return_value=d / "rio_ed25519-cert.pub",
    )
    # By default, ensure_ssh_keys returns False (existing key pair).
    config.ensure_ssh_keys.return_value = False
    config.new_v2_client.return_value = _mock_v2_client()
    return config


def _real_config_for_dir(d: Path) -> Configuration:
    """Create a real Configuration whose SSH properties point at *d*.

    Uses a dynamic subclass so the base Configuration class is never
    mutated, preventing property-override leaks across tests.
    """

    class _TestConfig(Configuration):
        @property
        def ssh_private_key(self):
            return d / "rio_ed25519"

        @property
        def ssh_public_key(self):
            return d / "rio_ed25519.pub"

        @property
        def ssh_certificate(self):
            return d / "rio_ed25519-cert.pub"

    config = _TestConfig.__new__(_TestConfig)
    config.data = {}
    config.exists = False
    config._filepath = None
    return config


@pytest.fixture
def ssh_dir(tmp_path):
    """Create a temporary ssh dir with a rio_ed25519 key pair."""
    d = tmp_path / "ssh"
    d.mkdir()
    _generate_test_key_pair(d)
    return d
