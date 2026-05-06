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

"""Unit, integration, and E2E tests for the ``rio ssh`` command.

Tests cover key generation (via ssh-keygen), certificate parsing
(via ssh-keygen -L), ssh-agent interaction (via ssh-add), SDK signing
call, error paths, CLI flag behaviour, and full end-to-end flows.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from riocli.ssh.certificate import (
    _parse_valid_before_from_output,
    format_cert_expiry,
    is_cert_valid,
    parse_cert_valid_before,
    write_certificate,
)
from riocli.ssh.keys import (
    RIO_KEY_NAME,
    ensure_rio_key_pair,
    get_rio_key_dir,
    get_rio_key_paths,
)
from riocli.ssh.util import add_to_ssh_agent, remove_from_ssh_agent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# keys.py – unit tests
# ---------------------------------------------------------------------------


class TestKeyPaths:
    """Tests for get_rio_key_paths() and get_rio_key_dir()."""

    def test_custom_ssh_dir(self, tmp_path):
        priv, pub, cert = get_rio_key_paths(tmp_path)
        assert priv == tmp_path / "rio_ed25519"
        assert pub == tmp_path / "rio_ed25519.pub"
        assert cert == tmp_path / "rio_ed25519-cert.pub"

    def test_default_key_dir_uses_app_dir(self):
        """Without an override, paths should be under ~/.config/rio-cli/."""
        d = get_rio_key_dir()
        assert d == Path.home() / ".config" / "rio-cli"

    def test_key_name_constant(self, tmp_path):
        priv, pub, cert = get_rio_key_paths(tmp_path)
        assert priv.name == RIO_KEY_NAME
        assert pub.name == f"{RIO_KEY_NAME}.pub"
        assert cert.name == f"{RIO_KEY_NAME}-cert.pub"


class TestEnsureRioKeyPair:
    """Tests for ensure_rio_key_pair()."""

    def test_generates_key_pair_when_missing(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert priv.is_file()
        assert pub.is_file()
        assert pub.read_text().strip().startswith("ssh-ed25519 ")
        assert oct(priv.stat().st_mode & 0o777) == "0o600"

    def test_reuses_existing_key_pair(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        _generate_test_key_pair(ssh_dir)
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is False
        assert priv.is_file()
        assert pub.is_file()

    def test_creates_ssh_dir_if_missing(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert ssh_dir.is_dir()
        assert oct(ssh_dir.stat().st_mode & 0o777) == "0o700"

    def test_deletes_stale_cert_on_new_key_pair(self, tmp_path):
        """When a new key pair is generated, any leftover cert must be removed."""
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("stale-cert-for-old-key")

        priv, pub, returned_cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert not cert.exists(), "Stale cert should have been deleted"

    def test_only_private_key_exists_regenerates(self, tmp_path):
        """If only the private key exists (no public), regenerate both."""
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        priv_path = ssh_dir / "rio_ed25519"
        priv_path.write_text("orphaned-private-key")

        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert priv.is_file()
        assert pub.is_file()
        assert pub.read_text().strip().startswith("ssh-ed25519 ")

    def test_only_public_key_exists_regenerates(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)
        pub_path = ssh_dir / "rio_ed25519.pub"
        pub_path.write_text("orphaned-public-key")

        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert priv.is_file()
        assert pub.is_file()

    def test_generated_key_is_valid_ed25519(self, tmp_path):
        """Generated key should be usable by ssh-keygen."""
        ssh_dir = tmp_path / "ssh"
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        # ssh-keygen -l -f should succeed on the generated public key
        result = subprocess.run(
            ["ssh-keygen", "-l", "-f", str(pub)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "ED25519" in result.stdout

    def test_idempotent_double_generate(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        _, pub1, _, gen1 = ensure_rio_key_pair(ssh_dir)
        pub1_content = pub1.read_text()

        _, pub2, _, gen2 = ensure_rio_key_pair(ssh_dir)
        pub2_content = pub2.read_text()

        assert gen1 is True
        assert gen2 is False
        assert pub1_content == pub2_content

    def test_public_key_permissions(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        _, pub, _, _ = ensure_rio_key_pair(ssh_dir)
        assert oct(pub.stat().st_mode & 0o777) == "0o644"

    def test_creates_nested_dir(self, tmp_path):
        ssh_dir = tmp_path / "a" / "b" / "ssh"
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert ssh_dir.is_dir()
        assert priv.is_file()

    def test_ssh_keygen_failure_raises(self, tmp_path):
        """If ssh-keygen fails, ensure_rio_key_pair raises RuntimeError."""
        ssh_dir = tmp_path / "ssh"
        with patch("riocli.ssh.keys.subprocess.run") as mock_run:
            mock_run.return_value = _make_subprocess_result(
                returncode=1,
                stderr="Permission denied",
            )
            with pytest.raises(RuntimeError, match="ssh-keygen failed"):
                ensure_rio_key_pair(ssh_dir)


# ---------------------------------------------------------------------------
# certificate.py – unit tests
# ---------------------------------------------------------------------------


class TestCertificateParsing:
    """Tests for certificate parsing functions."""

    def test_parse_valid_before_from_output(self):
        """Parse a typical ssh-keygen -L output."""
        output = """\
/tmp/test-cert.pub:
        Type: ssh-ed25519-cert-v01@openssh.com user certificate
        Public key: ED25519-CERT SHA256:abc123
        Signing CA: ED25519 SHA256:def456
        Key ID: "user@host"
        Serial: 1234567890
        Valid: from 2026-04-01T10:00:00 to 2026-04-01T10:05:00
        Principals:
                user
        Critical Options: (none)
        Extensions:
                permit-pty
"""
        dt = _parse_valid_before_from_output(output)
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 4
        assert dt.day == 1

    def test_parse_valid_before_forever(self):
        """Handle 'forever' sentinel."""
        output = "        Valid: from 2026-04-01T10:00:00 to forever\n"
        # The 'forever' keyword contains 'forever' — should return datetime.max
        dt = _parse_valid_before_from_output(output)
        assert dt is not None

    def test_parse_valid_before_no_valid_line(self):
        output = "        Type: some cert\n        Key ID: foo\n"
        assert _parse_valid_before_from_output(output) is None

    def test_parse_valid_before_empty_output(self):
        assert _parse_valid_before_from_output("") is None

    @patch("riocli.ssh.certificate.subprocess.run")
    def test_parse_cert_valid_before_success(self, mock_run, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        mock_run.return_value = _make_subprocess_result(
            stdout="        Valid: from 2026-04-01T10:00:00 to 2026-04-01T10:05:00\n",
        )

        dt = parse_cert_valid_before(cert_path)
        assert dt is not None
        mock_run.assert_called_once()

    @patch("riocli.ssh.certificate.subprocess.run")
    def test_parse_cert_valid_before_failure(self, mock_run, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert")
        mock_run.return_value = _make_subprocess_result(returncode=1)

        assert parse_cert_valid_before(cert_path) is None

    def test_parse_cert_missing_file(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert parse_cert_valid_before(cert_path) is None

    @patch("riocli.ssh.certificate.subprocess.run")
    def test_is_cert_valid_true(self, mock_run, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        future = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + 3600))
        mock_run.return_value = _make_subprocess_result(
            stdout=f"        Valid: from 2026-01-01T00:00:00 to {future}\n",
        )

        assert is_cert_valid(cert_path) is True

    @patch("riocli.ssh.certificate.subprocess.run")
    def test_is_cert_valid_expired(self, mock_run, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        past = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 3600))
        mock_run.return_value = _make_subprocess_result(
            stdout=f"        Valid: from 2020-01-01T00:00:00 to {past}\n",
        )

        assert is_cert_valid(cert_path) is False

    def test_is_cert_valid_missing_file(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert is_cert_valid(cert_path) is False

    @patch("riocli.ssh.certificate.subprocess.run")
    def test_format_cert_expiry(self, mock_run, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        future = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + 3600))
        mock_run.return_value = _make_subprocess_result(
            stdout=f"        Valid: from 2026-01-01T00:00:00 to {future}\n",
        )

        result = format_cert_expiry(cert_path)
        assert result is not None
        assert "T" in result

    def test_format_cert_expiry_missing(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert format_cert_expiry(cert_path) is None

    @patch("riocli.ssh.certificate.subprocess.run")
    def test_is_cert_valid_bad_output(self, mock_run, tmp_path):
        """is_cert_valid returns False when ssh-keygen output is unparseable."""
        cert_path = tmp_path / "cert.pub"
        cert_path.write_text("fake cert")
        mock_run.return_value = _make_subprocess_result(
            stdout="Type: some cert\nKey ID: foo\n",
        )
        assert is_cert_valid(cert_path) is False

    @patch("riocli.ssh.certificate.subprocess.run")
    def test_format_cert_expiry_bad_output(self, mock_run, tmp_path):
        cert_path = tmp_path / "cert.pub"
        cert_path.write_text("fake cert")
        mock_run.return_value = _make_subprocess_result(
            stdout="Type: some cert\n",
        )
        assert format_cert_expiry(cert_path) is None


class TestWriteCertificate:
    """Tests for write_certificate()."""

    def test_writes_with_newline(self, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        write_certificate(cert_path, "cert-content")
        assert cert_path.read_text() == "cert-content\n"

    def test_sets_permissions(self, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        write_certificate(cert_path, "cert-content")
        assert oct(cert_path.stat().st_mode & 0o777) == "0o644"

    def test_overwrites_existing_cert(self, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        write_certificate(cert_path, "old-cert")
        write_certificate(cert_path, "new-cert")
        assert cert_path.read_text() == "new-cert\n"

    def test_creates_file_if_missing(self, tmp_path):
        cert_path = tmp_path / "brand-new-cert.pub"
        assert not cert_path.exists()
        write_certificate(cert_path, "fresh-cert")
        assert cert_path.exists()
        assert cert_path.read_text() == "fresh-cert\n"

    def test_preserves_cert_content_exactly(self, tmp_path):
        cert_content = "ssh-ed25519-cert-v01@openssh.com AAAA+/== user@host"
        cert_path = tmp_path / "exact-cert.pub"
        write_certificate(cert_path, cert_content)
        assert cert_path.read_text() == cert_content + "\n"


# ---------------------------------------------------------------------------
# util.py – ssh-add wrapper tests
# ---------------------------------------------------------------------------


class TestSSHAddWrappers:
    """Tests for add_to_ssh_agent() and remove_from_ssh_agent()."""

    @patch("riocli.ssh.util.subprocess.run")
    def test_add_to_ssh_agent_success(self, mock_run, tmp_path):
        mock_run.return_value = _make_subprocess_result()
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        add_to_ssh_agent(priv, lifetime=120)

        mock_run.assert_called_once_with(
            ["ssh-add", "-t", "120", str(priv)],
            capture_output=True,
            text=True,
        )

    @patch("riocli.ssh.util.subprocess.run")
    def test_add_to_ssh_agent_default_lifetime(self, mock_run, tmp_path):
        mock_run.return_value = _make_subprocess_result()
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        add_to_ssh_agent(priv)

        mock_run.assert_called_once_with(
            ["ssh-add", "-t", "300", str(priv)],
            capture_output=True,
            text=True,
        )

    @patch("riocli.ssh.util.subprocess.run")
    def test_add_to_ssh_agent_failure(self, mock_run, tmp_path):
        mock_run.return_value = _make_subprocess_result(
            returncode=1,
            stderr="Could not open a connection to your agent",
        )
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        with pytest.raises(RuntimeError, match="Failed to add key"):
            add_to_ssh_agent(priv)

    @patch("riocli.ssh.util.subprocess.run")
    def test_remove_from_ssh_agent_success(self, mock_run, tmp_path):
        mock_run.return_value = _make_subprocess_result()
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        remove_from_ssh_agent(priv)

        mock_run.assert_called_once_with(
            ["ssh-add", "-d", str(priv)],
            capture_output=True,
            text=True,
        )

    @patch("riocli.ssh.util.subprocess.run")
    def test_remove_from_ssh_agent_failure_silenced(self, mock_run, tmp_path):
        """remove_from_ssh_agent silently ignores failures."""
        mock_run.return_value = _make_subprocess_result(
            returncode=1,
            stderr="Could not remove identity",
        )
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        # Should NOT raise
        remove_from_ssh_agent(priv)

    @patch("riocli.ssh.util.subprocess.run")
    def test_remove_from_ssh_agent_oserror_silenced(self, mock_run, tmp_path):
        """OSError (e.g. ssh-add not found) should be silently ignored."""
        mock_run.side_effect = OSError("No such file or directory")
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        # Should NOT raise
        remove_from_ssh_agent(priv)


# ---------------------------------------------------------------------------
# CLI command – integration tests (Click CliRunner)
# ---------------------------------------------------------------------------


@pytest.fixture
def ssh_dir(tmp_path):
    """Create a temporary ssh dir with a rio_ed25519 key pair."""
    d = tmp_path / "ssh"
    d.mkdir()
    _generate_test_key_pair(d)
    return d


class TestSSHCommand:
    """Tests for the ``rio ssh`` click command."""

    # ---- Happy paths ----

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_happy_path(self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        mock_config.return_value.new_v2_client.return_value.sign_ssh_public_key.assert_called_once()
        assert cert.exists()
        mock_add.assert_called_once()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_first_run_generates_key(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, True)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Generated dedicated key pair" in result.output

    # ---- Flag behaviour ----

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_no_agent_flag_skips_agent(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_force_re_signs(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client(
            certificate="new-cert"
        )

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force"], catch_exceptions=False)

        assert result.exit_code == 0
        assert cert.read_text().strip() == "new-cert"

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_force_and_no_agent(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        """--force --no-agent: re-sign but skip agent loading."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client(
            certificate="fresh-cert"
        )

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force", "--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        assert cert.read_text().strip() == "fresh-cert"
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_short_force_flag(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        """-f should work the same as --force."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client(
            certificate="new-cert"
        )

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["-f"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_config.return_value.new_v2_client.return_value.sign_ssh_public_key.assert_called_once()

    # ---- Error paths ----

    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_key_generation_error(self, mock_ensure):
        mock_ensure.side_effect = FileNotFoundError("Permission denied")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "Permission denied" in result.output

    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_api_error_exits(self, mock_ensure, mock_config, ssh_dir):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value.sign_ssh_public_key.side_effect = Exception(
            "unauthorized"
        )

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "unauthorized" in result.output

    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_runtime_error_exits(self, mock_ensure, mock_config, ssh_dir):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value.sign_ssh_public_key.side_effect = RuntimeError(
            "timeout"
        )

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "timeout" in result.output

    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_network_error_shows_message(self, mock_ensure, mock_config, ssh_dir):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value.sign_ssh_public_key.side_effect = ConnectionError(
            "Connection refused"
        )

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "Connection refused" in result.output

    # ---- Agent interaction edge cases ----

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_agent_failure_warns_but_succeeds(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        """Agent failure should print a warning, not fail the command."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client()
        mock_add.side_effect = RuntimeError("agent not running")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "agent not running" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_remove_called_before_write(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        """remove_from_ssh_agent must be called BEFORE writing the new cert."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client()

        call_order = []
        mock_remove.side_effect = lambda *a, **k: call_order.append("remove")

        from riocli.ssh import ssh

        with patch("riocli.ssh.write_certificate") as mock_write:
            mock_write.side_effect = lambda *a, **k: call_order.append("write")
            runner = CliRunner()
            result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert call_order.index("remove") < call_order.index("write")

    # ---- Cert reuse paths ----

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_reuse_valid_cert_skips_api(
        self,
        mock_ensure,
        mock_config,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """When a valid cert already exists, skip the API call."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        mock_ensure.return_value = (priv, pub, cert, False)

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        mock_config.return_value.new_v2_client.return_value.sign_ssh_public_key.assert_not_called()
        mock_add.assert_called_once()
        assert "still valid" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_force_overrides_valid_cert(
        self, mock_ensure, mock_config, mock_valid, mock_remove, mock_add, ssh_dir
    ):
        """--force should re-sign even when the existing cert is valid."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client(
            certificate="fresh-cert"
        )

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_config.return_value.new_v2_client.return_value.sign_ssh_public_key.assert_called_once()
        assert cert.read_text().strip() == "fresh-cert"

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_reuse_valid_cert_no_agent(
        self,
        mock_ensure,
        mock_config,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse valid cert with --no-agent should skip agent loading."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        mock_ensure.return_value = (priv, pub, cert, False)

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_config.return_value.new_v2_client.return_value.sign_ssh_public_key.assert_not_called()
        mock_add.assert_not_called()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_reuse_with_agent_failure_warns(
        self,
        mock_ensure,
        mock_config,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse path + agent failure should warn, not fail."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_add.side_effect = RuntimeError("SSH_AUTH_SOCK is not set")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "SSH_AUTH_SOCK" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value=None)
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_reuse_no_expiry_string(
        self,
        mock_ensure,
        mock_config,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse path with unparseable expiry should still succeed."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        mock_ensure.return_value = (priv, pub, cert, False)

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "still valid" in result.output

    # ---- Output content tests ----

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_output_contains_cert_written(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "SSH certificate written" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_output_contains_agent_loaded(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Identity loaded into ssh-agent" in result.output
        assert "5m TTL" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_output_contains_public_key_path(
        self, mock_ensure, mock_config, mock_remove, mock_add, ssh_dir
    ):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_config.return_value.new_v2_client.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Using SSH public key" in result.output

    # ---- user-guid removed ----

    def test_user_guid_flag_not_accepted(self):
        """--user-guid should no longer be accepted."""
        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--user-guid", "test-guid-123"])

        assert result.exit_code != 0
        assert "No such option" in result.output or "no such option" in result.output


# ---------------------------------------------------------------------------
# E2E integration tests – full flow with real ssh-keygen, mocked SDK
# ---------------------------------------------------------------------------


class TestE2ESignFlow:
    """End-to-end tests exercising the full command with real key generation
    via ssh-keygen, mocked SDK API, and mocked ssh-add calls.
    """

    def _run_ssh_e2e(
        self,
        tmp_ssh_dir: Path,
        certificate: str,
        cli_args: list[str] | None = None,
        add_raises: bool = False,
    ):
        """Run rio ssh with real ssh-keygen and mocked SDK/ssh-add."""
        from riocli.ssh import ssh

        if cli_args is None:
            cli_args = []

        mock_client = _mock_v2_client(certificate=certificate)
        mock_config = MagicMock()
        mock_config.new_v2_client.return_value = mock_client

        with (
            patch("riocli.ssh.get_config_from_context", return_value=mock_config),
            patch(
                "riocli.ssh.ensure_rio_key_pair", wraps=ensure_rio_key_pair
            ) as mock_ensure,
            patch("riocli.ssh.add_to_ssh_agent") as mock_add,
            patch("riocli.ssh.remove_from_ssh_agent") as mock_remove,
        ):
            mock_ensure.side_effect = lambda: ensure_rio_key_pair(tmp_ssh_dir)
            if add_raises:
                mock_add.side_effect = RuntimeError("no agent")

            runner = CliRunner()
            result = runner.invoke(ssh, cli_args, catch_exceptions=False)

        return result, mock_client, mock_add, mock_remove

    def test_first_run_full_flow(self, tmp_path):
        """First run: generate key → sign → write cert → load agent."""
        ssh_dir = tmp_path / "ssh"

        result, mock_client, mock_add, mock_remove = self._run_ssh_e2e(
            ssh_dir, "ssh-ed25519-cert-v01@openssh.com AAAA... test"
        )

        assert result.exit_code == 0
        assert (ssh_dir / "rio_ed25519").is_file()
        assert (ssh_dir / "rio_ed25519.pub").is_file()
        assert "Generated dedicated key pair" in result.output

        cert_path = ssh_dir / "rio_ed25519-cert.pub"
        assert cert_path.is_file()

        mock_client.sign_ssh_public_key.assert_called_once()
        mock_add.assert_called_once()

    def test_second_run_reuses_key(self, tmp_path):
        ssh_dir = tmp_path / "ssh"

        result1, _, _, _ = self._run_ssh_e2e(
            ssh_dir, "ssh-ed25519-cert-v01@openssh.com AAAA... test"
        )
        assert result1.exit_code == 0
        pub_content_1 = (ssh_dir / "rio_ed25519.pub").read_text()

        result2, _, _, _ = self._run_ssh_e2e(
            ssh_dir, "ssh-ed25519-cert-v01@openssh.com AAAA... test"
        )
        assert result2.exit_code == 0
        pub_content_2 = (ssh_dir / "rio_ed25519.pub").read_text()

        assert pub_content_1 == pub_content_2
        assert "Generated dedicated key pair" not in result2.output

    def test_force_re_signs(self, tmp_path):
        ssh_dir = tmp_path / "ssh"

        result1, _, _, _ = self._run_ssh_e2e(ssh_dir, "first-cert")
        assert result1.exit_code == 0

        result2, mock_client2, _, _ = self._run_ssh_e2e(
            ssh_dir, "second-cert", cli_args=["--force"]
        )
        assert result2.exit_code == 0
        mock_client2.sign_ssh_public_key.assert_called_once()
        assert (ssh_dir / "rio_ed25519-cert.pub").read_text().strip() == "second-cert"

    def test_no_agent_skips_ssh_add(self, tmp_path):
        ssh_dir = tmp_path / "ssh"

        result, _, mock_add, mock_remove = self._run_ssh_e2e(
            ssh_dir, "cert-content", cli_args=["--no-agent"]
        )

        assert result.exit_code == 0
        mock_add.assert_not_called()
        mock_remove.assert_not_called()
        assert (ssh_dir / "rio_ed25519-cert.pub").is_file()

    def test_cert_file_permissions_after_full_flow(self, tmp_path):
        ssh_dir = tmp_path / "ssh"

        result, _, _, _ = self._run_ssh_e2e(ssh_dir, "cert-content")

        assert result.exit_code == 0
        cert_path = ssh_dir / "rio_ed25519-cert.pub"
        assert oct(cert_path.stat().st_mode & 0o777) == "0o644"

    def test_key_permissions_after_full_flow(self, tmp_path):
        ssh_dir = tmp_path / "ssh"

        result, _, _, _ = self._run_ssh_e2e(ssh_dir, "cert-content")

        assert result.exit_code == 0
        assert oct((ssh_dir / "rio_ed25519").stat().st_mode & 0o777) == "0o600"
        assert oct((ssh_dir / "rio_ed25519.pub").stat().st_mode & 0o777) == "0o644"

    def test_public_key_sent_to_sdk_matches_file(self, tmp_path):
        ssh_dir = tmp_path / "ssh"

        result, mock_client, _, _ = self._run_ssh_e2e(ssh_dir, "cert-content")

        assert result.exit_code == 0
        pub_on_disk = (ssh_dir / "rio_ed25519.pub").read_text().strip()

        sign_call = mock_client.sign_ssh_public_key.call_args
        request = sign_call.kwargs.get("body") or sign_call.args[0]
        assert request.public_key == pub_on_disk

    def test_agent_failure_does_not_affect_cert_on_disk(self, tmp_path):
        ssh_dir = tmp_path / "ssh"

        result, _, _, _ = self._run_ssh_e2e(ssh_dir, "cert-content", add_raises=True)

        assert result.exit_code == 0
        cert_path = ssh_dir / "rio_ed25519-cert.pub"
        assert cert_path.is_file()
        assert cert_path.read_text().strip() == "cert-content"

    def test_stale_cert_removed_on_key_regeneration(self, tmp_path):
        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir(parents=True)

        old_cert = ssh_dir / "rio_ed25519-cert.pub"
        old_cert.write_text("stale-cert-for-old-key")

        result, _, _, _ = self._run_ssh_e2e(ssh_dir, "new-cert-content")

        assert result.exit_code == 0
        cert_on_disk = old_cert.read_text().strip()
        assert cert_on_disk == "new-cert-content"
        assert cert_on_disk != "stale-cert-for-old-key"

    def test_sequential_runs_idempotent(self, tmp_path):
        ssh_dir = tmp_path / "ssh"

        for i in range(3):
            result, _, _, _ = self._run_ssh_e2e(
                ssh_dir, f"cert-{i}", cli_args=["--force"]
            )
            assert result.exit_code == 0

        assert (ssh_dir / "rio_ed25519").is_file()
        assert (ssh_dir / "rio_ed25519.pub").is_file()
        assert (ssh_dir / "rio_ed25519-cert.pub").is_file()

    def test_no_user_guid_in_sdk_call(self, tmp_path):
        """SDK call should NOT include user_guid (option removed)."""
        ssh_dir = tmp_path / "ssh"

        result, mock_client, _, _ = self._run_ssh_e2e(ssh_dir, "cert-content")

        assert result.exit_code == 0
        sign_call = mock_client.sign_ssh_public_key.call_args
        # user_guid should not be in kwargs
        assert "user_guid" not in (sign_call.kwargs or {})
