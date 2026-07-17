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

"""Tests for ``rio ssh-cert install-wrapper``."""

from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner

from riocli.ssh.install_wrapper import _inject_include, install_wrapper

_ENSURE_PATH = "/usr/local/bin/rio-ssh-ensure-cert"


def _run(args: list[str], rio: str | None = _ENSURE_PATH) -> object:
    """Invoke install_wrapper with shutil.which mocked."""
    runner = CliRunner()
    with patch("riocli.ssh.install_wrapper.shutil.which", return_value=rio):
        return runner.invoke(install_wrapper, args, catch_exceptions=False)


class TestInstallWrapper:
    def test_happy_path_writes_conf_and_config(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir(mode=0o700)

        with (
            patch("riocli.ssh.install_wrapper.Path.home", return_value=tmp_path),
            patch(
                "riocli.ssh.install_wrapper.shutil.which",
                return_value=_ENSURE_PATH,
            ),
            patch(
                "riocli.ssh.install_wrapper.click.get_app_dir",
                return_value=str(tmp_path / ".config" / "rio-cli"),
            ),
        ):
            result = CliRunner().invoke(
                install_wrapper, ["--ssh-user", "rr"], catch_exceptions=False
            )

        assert result.exit_code == 0

        conf_file = ssh_dir / "config.d" / "rio-ssh.conf"
        assert conf_file.exists()
        content = conf_file.read_text()
        assert "Match user rr" in content
        assert f"exec \"'{_ENSURE_PATH}'\"" in content
        assert "IdentityFile" in content
        assert "CertificateFile" in content

        ssh_config = ssh_dir / "config"
        assert ssh_config.exists()
        assert "Include config.d/rio-ssh.conf" in ssh_config.read_text()

    def test_creates_config_d_dir_when_missing(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir(mode=0o700)

        with (
            patch("riocli.ssh.install_wrapper.Path.home", return_value=tmp_path),
            patch(
                "riocli.ssh.install_wrapper.shutil.which",
                return_value=_ENSURE_PATH,
            ),
            patch(
                "riocli.ssh.install_wrapper.click.get_app_dir", return_value=str(tmp_path)
            ),
        ):
            CliRunner().invoke(install_wrapper, [], catch_exceptions=False)

        assert (ssh_dir / "config.d").is_dir()

    def test_wrapper_not_on_path_exits_1(self, tmp_path):
        result = _run([], rio=None)
        assert result.exit_code == 1
        assert "rio-ssh-ensure-cert not found" in result.output

    def test_existing_conf_skipped_without_force(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        conf_dir = ssh_dir / "config.d"
        conf_dir.mkdir(parents=True, mode=0o700)
        conf_file = conf_dir / "rio-ssh.conf"
        conf_file.write_text("# existing content")

        with (
            patch("riocli.ssh.install_wrapper.Path.home", return_value=tmp_path),
            patch(
                "riocli.ssh.install_wrapper.shutil.which",
                return_value=_ENSURE_PATH,
            ),
            patch(
                "riocli.ssh.install_wrapper.click.get_app_dir", return_value=str(tmp_path)
            ),
        ):
            result = CliRunner().invoke(install_wrapper, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "already exists" in result.output
        assert conf_file.read_text() == "# existing content"

    def test_force_overwrites_existing_conf(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        conf_dir = ssh_dir / "config.d"
        conf_dir.mkdir(parents=True, mode=0o700)
        conf_file = conf_dir / "rio-ssh.conf"
        conf_file.write_text("# old content")

        with (
            patch("riocli.ssh.install_wrapper.Path.home", return_value=tmp_path),
            patch(
                "riocli.ssh.install_wrapper.shutil.which",
                return_value=_ENSURE_PATH,
            ),
            patch(
                "riocli.ssh.install_wrapper.click.get_app_dir", return_value=str(tmp_path)
            ),
        ):
            result = CliRunner().invoke(
                install_wrapper, ["--force"], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "# old content" not in conf_file.read_text()
        assert "Match user" in conf_file.read_text()

    def test_custom_ssh_user(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir(mode=0o700)

        with (
            patch("riocli.ssh.install_wrapper.Path.home", return_value=tmp_path),
            patch(
                "riocli.ssh.install_wrapper.shutil.which",
                return_value=_ENSURE_PATH,
            ),
            patch(
                "riocli.ssh.install_wrapper.click.get_app_dir", return_value=str(tmp_path)
            ),
        ):
            CliRunner().invoke(
                install_wrapper, ["--ssh-user", "robot"], catch_exceptions=False
            )

        conf = (ssh_dir / "config.d" / "rio-ssh.conf").read_text()
        assert "Match user robot" in conf

    def test_conf_file_permissions(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir(mode=0o700)

        with (
            patch("riocli.ssh.install_wrapper.Path.home", return_value=tmp_path),
            patch(
                "riocli.ssh.install_wrapper.shutil.which",
                return_value=_ENSURE_PATH,
            ),
            patch(
                "riocli.ssh.install_wrapper.click.get_app_dir", return_value=str(tmp_path)
            ),
        ):
            CliRunner().invoke(install_wrapper, [], catch_exceptions=False)

        conf_file = ssh_dir / "config.d" / "rio-ssh.conf"
        assert oct(conf_file.stat().st_mode & 0o777) == "0o600"


class TestInjectInclude:
    def test_creates_new_config(self, tmp_path):
        ssh_config = tmp_path / "config"
        _inject_include(ssh_config)

        assert ssh_config.exists()
        text = ssh_config.read_text()
        assert "Include config.d/rio-ssh.conf" in text
        assert "# >>> rio ssh-cert (managed) >>>" in text

    def test_prepends_to_existing_config(self, tmp_path):
        ssh_config = tmp_path / "config"
        ssh_config.write_text("Host myserver\n    User deploy\n")
        _inject_include(ssh_config)

        text = ssh_config.read_text()
        assert text.index("Include") < text.index("Host myserver")

    def test_idempotent_when_block_already_present(self, tmp_path):
        ssh_config = tmp_path / "config"
        ssh_config.write_text(
            "# >>> rio ssh-cert (managed) >>>\n"
            "Include config.d/rio-ssh.conf\n"
            "# <<< rio ssh-cert (managed) <<<\n"
        )
        original = ssh_config.read_text()
        _inject_include(ssh_config)

        assert ssh_config.read_text() == original

    def test_new_config_permissions(self, tmp_path):
        ssh_config = tmp_path / "config"
        _inject_include(ssh_config)
        assert oct(ssh_config.stat().st_mode & 0o777) == "0o600"
