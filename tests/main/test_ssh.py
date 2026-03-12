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

"""Unit tests for the ``rio ssh`` command.

Tests cover key discovery, SDK signing call, certificate writing,
ssh-agent loading, error paths, and CLI flag behaviour.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from riocli.ssh.util import (
    derive_cert_path,
    derive_private_key_path,
    discover_ssh_public_key,
)

# ---------------------------------------------------------------------------
# util.py – unit tests
# ---------------------------------------------------------------------------


class TestDiscoverSSHPublicKey:
    """Tests for discover_ssh_public_key()."""

    def test_prefers_ed25519(self, tmp_path, monkeypatch):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        (ssh_dir / "id_ed25519.pub").write_text("ssh-ed25519 AAAA...")
        (ssh_dir / "id_rsa.pub").write_text("ssh-rsa AAAA...")

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        result = discover_ssh_public_key()
        assert result.name == "id_ed25519.pub"

    def test_falls_back_to_rsa(self, tmp_path, monkeypatch):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        (ssh_dir / "id_rsa.pub").write_text("ssh-rsa AAAA...")

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        result = discover_ssh_public_key()
        assert result.name == "id_rsa.pub"

    def test_raises_when_no_key(self, tmp_path, monkeypatch):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        with pytest.raises(FileNotFoundError, match="No SSH public key found"):
            discover_ssh_public_key()


class TestDerivePaths:
    """Tests for path derivation helpers."""

    def test_cert_path(self, tmp_path):
        pub = tmp_path / "id_ed25519.pub"
        assert derive_cert_path(pub) == tmp_path / "id_ed25519-cert.pub"

    def test_private_key_path(self, tmp_path):
        pub = tmp_path / "id_ed25519.pub"
        priv = tmp_path / "id_ed25519"
        priv.write_text("PRIVATE")
        assert derive_private_key_path(pub) == priv

    def test_private_key_missing(self, tmp_path):
        pub = tmp_path / "id_ed25519.pub"
        with pytest.raises(FileNotFoundError, match="Private key not found"):
            derive_private_key_path(pub)


# ---------------------------------------------------------------------------
# CLI command – integration tests (Click CliRunner)
# ---------------------------------------------------------------------------


@pytest.fixture
def ssh_dir(tmp_path):
    """Create a temporary ~/.ssh with an ed25519 key pair."""
    d = tmp_path / ".ssh"
    d.mkdir()
    (d / "id_ed25519.pub").write_text(
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@host"
    )
    (d / "id_ed25519").write_text("-----BEGIN OPENSSH PRIVATE KEY-----\n...\n")
    (d / "id_ed25519").chmod(0o600)
    return d


def _mock_v2_client(certificate: str = "ssh-ed25519-cert-v01@openssh.com AAAA..."):
    """Return a mock v2 client with sign_ssh_public_key wired up."""
    client = MagicMock()
    response = MagicMock()
    response.certificate = certificate
    client.sign_ssh_public_key.return_value = response
    return client


class TestSSHCommand:
    """Tests for the ``rio ssh`` click command."""

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.discover_ssh_public_key")
    def test_happy_path_auto_discover(self, mock_discover, mock_v2, mock_agent, ssh_dir):
        pub = ssh_dir / "id_ed25519.pub"
        mock_discover.return_value = pub
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], input="y\n", catch_exceptions=False)

        assert result.exit_code == 0
        mock_v2.return_value.sign_ssh_public_key.assert_called_once()
        # Certificate file should have been written.
        cert = ssh_dir / "id_ed25519-cert.pub"
        assert cert.exists()
        mock_agent.assert_called_once()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.new_v2_client")
    def test_explicit_key_flag(self, mock_v2, mock_agent, ssh_dir):
        pub = ssh_dir / "id_ed25519.pub"
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--key", str(pub)], catch_exceptions=False)

        assert result.exit_code == 0
        cert = ssh_dir / "id_ed25519-cert.pub"
        assert cert.exists()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.discover_ssh_public_key")
    def test_no_agent_flag_skips_agent(self, mock_discover, mock_v2, mock_agent, ssh_dir):
        mock_discover.return_value = ssh_dir / "id_ed25519.pub"
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_agent.assert_not_called()

    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.discover_ssh_public_key")
    def test_force_overwrites_without_prompt(self, mock_discover, mock_v2, ssh_dir):
        pub = ssh_dir / "id_ed25519.pub"
        cert = ssh_dir / "id_ed25519-cert.pub"
        cert.write_text("old-cert")

        mock_discover.return_value = pub
        mock_v2.return_value = _mock_v2_client(certificate="new-cert")

        from riocli.ssh import ssh

        runner = CliRunner()
        with patch("riocli.ssh.add_to_ssh_agent"):
            result = runner.invoke(ssh, ["--force"], catch_exceptions=False)

        assert result.exit_code == 0
        assert cert.read_text().strip() == "new-cert"

    @patch("riocli.ssh.discover_ssh_public_key")
    def test_no_key_found_exits_with_error(self, mock_discover):
        mock_discover.side_effect = FileNotFoundError("No SSH public key found")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "No SSH public key found" in result.output

    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.discover_ssh_public_key")
    def test_api_error_exits_with_error(self, mock_discover, mock_v2, ssh_dir):
        mock_discover.return_value = ssh_dir / "id_ed25519.pub"
        mock_v2.return_value.sign_ssh_public_key.side_effect = Exception("unauthorized")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "unauthorized" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.discover_ssh_public_key")
    def test_agent_failure_warns_but_succeeds(
        self, mock_discover, mock_v2, mock_agent, ssh_dir
    ):
        """ssh-agent failure should print a warning but not fail the command."""
        mock_discover.return_value = ssh_dir / "id_ed25519.pub"
        mock_v2.return_value = _mock_v2_client()
        mock_agent.side_effect = RuntimeError("agent not running")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "agent not running" in result.output
