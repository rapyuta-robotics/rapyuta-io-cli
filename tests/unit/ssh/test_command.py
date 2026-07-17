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

"""Integration and E2E tests for the ``rio ssh`` Click command."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

if TYPE_CHECKING:
    from pathlib import Path

from click.testing import CliRunner

from riocli.config.config import Configuration

from .conftest import _make_config_for_dir, _mock_v2_client, _real_config_for_dir


class TestResolveKeyPaths:
    """Unit tests for the _resolve_key_paths() helper."""

    def test_no_flags_returns_managed_key(self, ssh_dir):
        from riocli.ssh.cert import _resolve_key_paths

        config = _make_config_for_dir(ssh_dir)
        priv, pub, cert, should_generate = _resolve_key_paths(None, False, config)

        assert priv == config.ssh_private_key
        assert pub == config.ssh_public_key
        assert cert == config.ssh_certificate
        assert should_generate is True

    def test_use_system_key_finds_ed25519(self, tmp_path):
        from riocli.ssh.cert import _resolve_key_paths

        fake_home = tmp_path / "home"
        ssh_dir = fake_home / ".ssh"
        ssh_dir.mkdir(parents=True)
        (ssh_dir / "id_ed25519").write_text("priv")
        (ssh_dir / "id_ed25519.pub").write_text("pub")

        config = MagicMock()
        with patch("riocli.ssh.Path.home", return_value=fake_home):
            priv, pub, cert, should_generate = _resolve_key_paths(None, True, config)

        assert priv == ssh_dir / "id_ed25519"
        assert pub == ssh_dir / "id_ed25519.pub"
        assert cert == ssh_dir / "id_ed25519-cert.pub"
        assert should_generate is False

    def test_use_system_key_skips_to_ecdsa_when_ed25519_missing(self, tmp_path):
        from riocli.ssh.cert import _resolve_key_paths

        fake_home = tmp_path / "home"
        ssh_dir = fake_home / ".ssh"
        ssh_dir.mkdir(parents=True)
        # Only ecdsa exists
        (ssh_dir / "id_ecdsa").write_text("priv")
        (ssh_dir / "id_ecdsa.pub").write_text("pub")

        config = MagicMock()
        with patch("riocli.ssh.Path.home", return_value=fake_home):
            priv, pub, cert, should_generate = _resolve_key_paths(None, True, config)

        assert priv == ssh_dir / "id_ecdsa"
        assert should_generate is False

    def test_use_system_key_falls_back_when_no_system_key(self, tmp_path):
        from riocli.ssh.cert import _resolve_key_paths

        fake_home = tmp_path / "home"
        (fake_home / ".ssh").mkdir(parents=True)

        config = _make_config_for_dir(tmp_path)
        with patch("riocli.ssh.Path.home", return_value=fake_home):
            priv, pub, cert, should_generate = _resolve_key_paths(None, True, config)

        assert priv == config.ssh_private_key
        assert should_generate is True

    def test_explicit_key_path_derives_pub_and_cert(self, tmp_path):
        from riocli.ssh.cert import _resolve_key_paths

        key = tmp_path / "mykey"
        config = MagicMock()
        priv, pub, cert, should_generate = _resolve_key_paths(str(key), False, config)

        assert priv == key.resolve()
        assert pub == priv.parent / "mykey.pub"
        assert cert == priv.parent / "mykey-cert.pub"
        assert should_generate is False


class TestSSHCommand:
    """Tests for the ``rio ssh`` click command."""

    # ---- Happy paths ----

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_happy_path(
        self, mock_get_config, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        config.ensure_ssh_keys.assert_called_once()
        config.new_v2_client.return_value.sign_ssh_public_key.assert_called_once()
        assert config.ssh_certificate.exists()
        mock_add.assert_called_once()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_first_run_generates_key(
        self, mock_get_config, mock_remove, mock_add, ssh_dir
    ):
        config = _make_config_for_dir(ssh_dir)
        config.ensure_ssh_keys.return_value = True
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Generated dedicated key pair" in result.output

    # ---- Flag behaviour ----

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_no_agent_flag_skips_agent(
        self, mock_get_config, mock_remove, mock_add, ssh_dir
    ):
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_force_re_signs(self, mock_get_config, mock_remove, mock_add, ssh_dir):
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        config = _make_config_for_dir(ssh_dir)
        config.new_v2_client.return_value = _mock_v2_client(certificate="new-cert")
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force"], catch_exceptions=False)

        assert result.exit_code == 0
        assert cert.read_text().strip() == "new-cert"

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_force_and_no_agent(self, mock_get_config, mock_remove, mock_add, ssh_dir):
        """--force --no-agent: re-sign but skip agent loading."""
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        config = _make_config_for_dir(ssh_dir)
        config.new_v2_client.return_value = _mock_v2_client(certificate="fresh-cert")
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force", "--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        assert cert.read_text().strip() == "fresh-cert"
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_short_force_flag(self, mock_get_config, mock_remove, mock_add, ssh_dir):
        """-f should work the same as --force."""
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        config = _make_config_for_dir(ssh_dir)
        config.new_v2_client.return_value = _mock_v2_client(certificate="new-cert")
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["-f"], catch_exceptions=False)

        assert result.exit_code == 0
        config.new_v2_client.return_value.sign_ssh_public_key.assert_called_once()

    # ---- Error paths ----

    @patch("riocli.ssh.get_config_from_context")
    def test_key_generation_error(self, mock_get_config):
        config = MagicMock(spec=Configuration)
        config.ensure_ssh_keys.side_effect = RuntimeError(
            "ssh-keygen failed: Permission denied"
        )
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "Permission denied" in result.output

    @patch("riocli.ssh.get_config_from_context")
    def test_api_error_exits(self, mock_get_config, ssh_dir):
        config = _make_config_for_dir(ssh_dir)
        config.new_v2_client.return_value.sign_ssh_public_key.side_effect = Exception(
            "unauthorized"
        )
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "unauthorized" in result.output

    @patch("riocli.ssh.get_config_from_context")
    def test_runtime_error_exits(self, mock_get_config, ssh_dir):
        config = _make_config_for_dir(ssh_dir)
        config.new_v2_client.return_value.sign_ssh_public_key.side_effect = RuntimeError(
            "timeout"
        )
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "timeout" in result.output

    @patch("riocli.ssh.get_config_from_context")
    def test_network_error_shows_message(self, mock_get_config, ssh_dir):
        config = _make_config_for_dir(ssh_dir)
        config.new_v2_client.return_value.sign_ssh_public_key.side_effect = (
            ConnectionError("Connection refused")
        )
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "Connection refused" in result.output

    @patch("riocli.ssh.get_config_from_context")
    def test_missing_private_key_errors(self, mock_get_config, ssh_dir):
        """--key-path pointing to a non-existent file is rejected by Click (exit 2)."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--key-path", str(ssh_dir / "nonexistent_key")])

        # click.Path(exists=True) validates the path before our code runs.
        assert result.exit_code == 2
        assert "does not exist" in result.output

    @patch("riocli.ssh.get_config_from_context")
    def test_missing_public_key_errors(self, mock_get_config, ssh_dir):
        """--key-path where only the private key exists (no .pub) must error."""
        priv = ssh_dir / "only_private"
        priv.write_text("fake private key")
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--key-path", str(priv)])

        assert result.exit_code == 1
        assert "SSH public key not found" in result.output

    @patch("riocli.ssh.is_ssh_agent_available", return_value=False)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_no_agent_socket_logs_info(
        self, mock_get_config, mock_add, _mock_agent, ssh_dir
    ):
        """When SSH_AUTH_SOCK is absent, an info message is printed and agent is skipped."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "No ssh-agent detected" in result.output
        mock_add.assert_not_called()

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.get_config_from_context")
    def test_cert_expiry_shown_after_sign(
        self, mock_get_config, mock_expiry, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        """Certificate expiry line must appear in output after a successful sign."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Certificate valid until: 2026-12-31T23:59:59" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh._resolve_key_paths")
    @patch("riocli.ssh.get_config_from_context")
    def test_use_system_key_fallback_logs_message(
        self, mock_get_config, mock_resolve, mock_remove, mock_add, ssh_dir
    ):
        """--use-system-key with no system keys found must log the fallback message."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config
        # should_generate=True signals the fallback path was taken
        mock_resolve.return_value = (
            config.ssh_private_key,
            config.ssh_public_key,
            config.ssh_certificate,
            True,
        )

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--use-system-key"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "falling back to rio-cli managed key" in result.output

    # ---- Agent interaction edge cases ----

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_agent_failure_warns_but_succeeds(
        self, mock_get_config, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        """Agent failure should print a warning, not fail the command."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config
        mock_add.side_effect = RuntimeError("agent not running")

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "agent not running" in result.output

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_remove_called_before_write(
        self, mock_get_config, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        """remove_from_ssh_agent must be called BEFORE writing the new cert."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        call_order = []
        mock_remove.side_effect = lambda *a, **k: call_order.append("remove")

        from riocli.ssh.cert import ssh

        with patch("riocli.ssh.write_certificate") as mock_write:
            mock_write.side_effect = lambda *a, **k: call_order.append("write")
            runner = CliRunner()
            result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert call_order.index("remove") < call_order.index("write")

    # ---- Cert reuse paths ----

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.get_config_from_context")
    def test_reuse_valid_cert_skips_api(
        self,
        mock_get_config,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        _mock_agent,
        ssh_dir,
    ):
        """When a valid cert already exists, skip the API call."""
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        config.new_v2_client.return_value.sign_ssh_public_key.assert_not_called()
        mock_add.assert_called_once()
        assert "still valid" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.get_config_from_context")
    def test_force_overrides_valid_cert(
        self, mock_get_config, mock_valid, mock_remove, mock_add, ssh_dir
    ):
        """--force should re-sign even when the existing cert is valid."""
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        config = _make_config_for_dir(ssh_dir)
        config.new_v2_client.return_value = _mock_v2_client(certificate="fresh-cert")
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force"], catch_exceptions=False)

        assert result.exit_code == 0
        config.new_v2_client.return_value.sign_ssh_public_key.assert_called_once()
        assert cert.read_text().strip() == "fresh-cert"

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.get_config_from_context")
    def test_reuse_valid_cert_no_agent(
        self,
        mock_get_config,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse valid cert with --no-agent should skip agent loading."""
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        config.new_v2_client.return_value.sign_ssh_public_key.assert_not_called()
        mock_add.assert_not_called()

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.get_config_from_context")
    def test_reuse_with_agent_failure_warns(
        self,
        mock_get_config,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse path + agent failure should warn, not fail."""
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config
        mock_add.side_effect = RuntimeError("SSH_AUTH_SOCK is not set")

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "SSH_AUTH_SOCK" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value=None)
    @patch("riocli.ssh.get_config_from_context")
    def test_reuse_no_expiry_string(
        self,
        mock_get_config,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse path with unparseable expiry should still succeed."""
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "still valid" in result.output

    # ---- Output content tests ----

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_output_contains_cert_written(
        self, mock_get_config, mock_remove, mock_add, ssh_dir
    ):
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "SSH certificate written" in result.output

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_output_contains_agent_loaded(
        self, mock_get_config, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Identity loaded into ssh-agent" in result.output
        assert "5m TTL" in result.output

    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_output_contains_public_key_path(
        self, mock_get_config, mock_remove, mock_add, ssh_dir
    ):
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Using SSH public key" in result.output

    # ---- --use-system-key and --key-path agent behaviour ----

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_key_path_explicit_skips_agent_by_default(
        self, mock_get_config, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        """--key-path PATH without --agent must not load the key into ssh-agent."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(
            ssh, ["--key-path", str(ssh_dir / "rio_ed25519")], catch_exceptions=False
        )

        assert result.exit_code == 0
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh.get_config_from_context")
    def test_key_path_explicit_with_agent_flag_loads_agent(
        self, mock_get_config, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        """--key-path PATH --agent must load the key into ssh-agent."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(
            ssh,
            ["--key-path", str(ssh_dir / "rio_ed25519"), "--agent"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        mock_add.assert_called_once()

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh._resolve_key_paths")
    @patch("riocli.ssh.get_config_from_context")
    def test_use_system_key_skips_agent_by_default(
        self, mock_get_config, mock_resolve, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        """--use-system-key without --agent must not load into ssh-agent."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config
        mock_resolve.return_value = (
            ssh_dir / "rio_ed25519",
            ssh_dir / "rio_ed25519.pub",
            ssh_dir / "rio_ed25519-cert.pub",
            False,
        )

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--use-system-key"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    @patch("riocli.ssh.is_ssh_agent_available", return_value=True)
    @patch("riocli.ssh.add_to_ssh_agent")
    @patch("riocli.ssh.remove_from_ssh_agent")
    @patch("riocli.ssh._resolve_key_paths")
    @patch("riocli.ssh.get_config_from_context")
    def test_use_system_key_with_agent_flag_loads_agent(
        self, mock_get_config, mock_resolve, mock_remove, mock_add, _mock_agent, ssh_dir
    ):
        """--use-system-key --agent must load the key into ssh-agent."""
        config = _make_config_for_dir(ssh_dir)
        mock_get_config.return_value = config
        mock_resolve.return_value = (
            ssh_dir / "rio_ed25519",
            ssh_dir / "rio_ed25519.pub",
            ssh_dir / "rio_ed25519-cert.pub",
            False,
        )

        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(
            ssh, ["--use-system-key", "--agent"], catch_exceptions=False
        )

        assert result.exit_code == 0
        mock_add.assert_called_once()

    # ---- mutually exclusive flags ----

    def test_use_system_key_and_key_path_together_errors(self, ssh_dir):
        """--use-system-key and --key-path together must be rejected."""
        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(
            ssh, ["--use-system-key", "--key-path", str(ssh_dir / "rio_ed25519")]
        )

        assert result.exit_code != 0
        assert "mutually exclusive" in result.output

    # ---- user-guid removed ----

    def test_user_guid_flag_not_accepted(self):
        """--user-guid should no longer be accepted."""
        from riocli.ssh.cert import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--user-guid", "test-guid-123"])

        assert result.exit_code != 0
        assert "No such option" in result.output or "no such option" in result.output


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
        from riocli.ssh.cert import ssh

        if cli_args is None:
            cli_args = []

        mock_client = _mock_v2_client(certificate=certificate)
        config = _real_config_for_dir(tmp_ssh_dir)

        with (
            patch.object(config, "new_v2_client", return_value=mock_client),
            patch("riocli.ssh.get_config_from_context", return_value=config),
            patch("riocli.ssh.is_ssh_agent_available", return_value=True),
            patch("riocli.ssh.add_to_ssh_agent") as mock_add,
            patch("riocli.ssh.remove_from_ssh_agent") as mock_remove,
        ):
            if add_raises:
                mock_add.side_effect = RuntimeError("no agent")

            runner = CliRunner()
            result = runner.invoke(ssh, cli_args, catch_exceptions=False)

        return result, mock_client, mock_add, mock_remove

    def test_first_run_full_flow(self, tmp_path):
        """First run: generate key -> sign -> write cert -> load agent."""
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

    def test_key_path_explicit_skips_agent_by_default(self, tmp_path):
        """E2E: --key-path PATH without --agent must not call ssh-add."""
        from .conftest import _generate_test_key_pair

        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir()
        _generate_test_key_pair(ssh_dir)

        result, _, mock_add, mock_remove = self._run_ssh_e2e(
            ssh_dir,
            "cert-content",
            cli_args=["--key-path", str(ssh_dir / "rio_ed25519")],
        )

        assert result.exit_code == 0
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    def test_key_path_explicit_with_agent_flag_loads_agent(self, tmp_path):
        """E2E: --key-path PATH --agent must call ssh-add."""
        from .conftest import _generate_test_key_pair

        ssh_dir = tmp_path / "ssh"
        ssh_dir.mkdir()
        _generate_test_key_pair(ssh_dir)

        result, _, mock_add, _ = self._run_ssh_e2e(
            ssh_dir,
            "cert-content",
            cli_args=["--key-path", str(ssh_dir / "rio_ed25519"), "--agent"],
        )

        assert result.exit_code == 0
        mock_add.assert_called_once()

    def test_no_user_guid_in_sdk_call(self, tmp_path):
        """SDK call should NOT include user_guid (option removed)."""
        ssh_dir = tmp_path / "ssh"

        result, mock_client, _, _ = self._run_ssh_e2e(ssh_dir, "cert-content")

        assert result.exit_code == 0
        sign_call = mock_client.sign_ssh_public_key.call_args
        # user_guid should not be in kwargs
        assert "user_guid" not in (sign_call.kwargs or {})
