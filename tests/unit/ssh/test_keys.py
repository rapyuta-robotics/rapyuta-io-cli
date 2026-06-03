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

"""Tests for SSH key generation and Configuration SSH properties."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from riocli.config.config import Configuration

from .conftest import _make_subprocess_result, _real_config_for_dir


class TestSSHProperties:
    """Tests for Configuration.ssh_private_key, ssh_public_key, ssh_certificate."""

    def test_paths_in_app_dir(self):
        """SSH paths should live in the CLI's config directory."""
        config = Configuration.__new__(Configuration)
        priv = config.ssh_private_key
        pub = config.ssh_public_key
        cert = config.ssh_certificate

        app_dir = Path.home() / ".config" / "rio-cli"
        assert priv == app_dir / "rio_ed25519"
        assert pub == app_dir / "rio_ed25519.pub"
        assert cert == app_dir / "rio_ed25519-cert.pub"

    def test_key_name_constant(self):
        assert Configuration._SSH_KEY_NAME == "rio_ed25519"


class TestEnsureSSHKeys:
    """Tests for Configuration.ensure_ssh_keys()."""

    def test_generates_key_pair_when_missing(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        config = _real_config_for_dir(ssh_dir)

        generated = config.ensure_ssh_keys()

        assert generated is True
        assert config.ssh_private_key.is_file()
        assert config.ssh_public_key.is_file()
        assert config.ssh_public_key.read_text().strip().startswith("ssh-ed25519 ")
        assert oct(config.ssh_private_key.stat().st_mode & 0o777) == "0o600"

    def test_reuses_existing_key_pair(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        from .conftest import _generate_test_key_pair

        _generate_test_key_pair(ssh_dir)
        config = _real_config_for_dir(ssh_dir)

        generated = config.ensure_ssh_keys()

        assert generated is False
        assert config.ssh_private_key.is_file()
        assert config.ssh_public_key.is_file()

    def test_creates_dir_if_missing(self, tmp_path):
        ssh_dir = tmp_path / "newdir"
        config = _real_config_for_dir(ssh_dir)

        generated = config.ensure_ssh_keys()

        assert generated is True
        assert ssh_dir.is_dir()
        assert oct(ssh_dir.stat().st_mode & 0o777) == "0o700"

    def test_deletes_stale_cert_on_new_key_pair(self, tmp_path):
        """When a new key pair is generated, any leftover cert must be removed."""
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("stale-cert-for-old-key")
        config = _real_config_for_dir(ssh_dir)

        generated = config.ensure_ssh_keys()

        assert generated is True
        assert not cert.exists(), "Stale cert should have been deleted"

    def test_only_private_key_exists_regenerates(self, tmp_path):
        """If only the private key exists (no public), regenerate both."""
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        (ssh_dir / "rio_ed25519").write_text("orphaned-private-key")
        config = _real_config_for_dir(ssh_dir)

        generated = config.ensure_ssh_keys()

        assert generated is True
        assert config.ssh_public_key.read_text().strip().startswith("ssh-ed25519 ")

    def test_only_public_key_exists_regenerates(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        (ssh_dir / "rio_ed25519.pub").write_text("orphaned-public-key")
        config = _real_config_for_dir(ssh_dir)

        generated = config.ensure_ssh_keys()

        assert generated is True
        assert config.ssh_private_key.is_file()
        assert config.ssh_public_key.is_file()

    def test_generated_key_is_valid_ed25519(self, tmp_path):
        """Generated key should be usable by ssh-keygen."""
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        config = _real_config_for_dir(ssh_dir)
        config.ensure_ssh_keys()

        result = subprocess.run(
            ["ssh-keygen", "-l", "-f", str(config.ssh_public_key)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "ED25519" in result.stdout

    def test_idempotent_double_generate(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        config = _real_config_for_dir(ssh_dir)

        gen1 = config.ensure_ssh_keys()
        pub1 = config.ssh_public_key.read_text()
        gen2 = config.ensure_ssh_keys()
        pub2 = config.ssh_public_key.read_text()

        assert gen1 is True
        assert gen2 is False
        assert pub1 == pub2

    def test_public_key_permissions(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        config = _real_config_for_dir(ssh_dir)
        config.ensure_ssh_keys()

        assert oct(config.ssh_public_key.stat().st_mode & 0o777) == "0o644"

    def test_creates_nested_dir(self, tmp_path):
        ssh_dir = tmp_path / "a" / "b" / "ssh"
        config = _real_config_for_dir(ssh_dir)

        generated = config.ensure_ssh_keys()

        assert generated is True
        assert ssh_dir.is_dir()
        assert config.ssh_private_key.is_file()

    def test_ssh_keygen_failure_raises(self, tmp_path):
        """If ssh-keygen fails, ensure_ssh_keys raises RuntimeError."""
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        config = _real_config_for_dir(ssh_dir)

        with patch("riocli.config.config.subprocess.run") as mock_run:
            mock_run.return_value = _make_subprocess_result(
                returncode=1,
                stderr="Permission denied",
            )
            with pytest.raises(RuntimeError, match="ssh-keygen failed"):
                config.ensure_ssh_keys()
