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


def test_update_devel_appimage_uses_blob(monkeypatch):
    """A devel AppImage (APPIMAGE env set) updates from the blob, replacing
    the AppImage file (not sys.executable)."""
    monkeypatch.setenv("APPIMAGE", "/opt/rio.AppImage")
    manifest = {
        "version": "10.9.9+devel.newsha",
        "file": "rio-10.9.9-x86_64.AppImage",
        "sha256": "x",
    }
    with (
        patch("riocli.bootstrap.__version__", "10.6.0+devel.oldsha"),
        patch("riocli.bootstrap.appimage.fetch_manifest", return_value=manifest) as fm,
        patch("riocli.bootstrap.appimage.download_and_replace") as dr,
    ):
        result = CliRunner().invoke(cli, ["update", "--silent"])
    assert result.exit_code == 0
    fm.assert_called_once_with("devel")
    dr.assert_called_once_with("devel", manifest, target="/opt/rio.AppImage")


def test_update_appimage_already_latest(monkeypatch):
    monkeypatch.setenv("APPIMAGE", "/opt/rio.AppImage")
    manifest = {"version": "10.6.0", "file": "rio-10.6.0-x86_64.AppImage", "sha256": "x"}
    with (
        patch("riocli.bootstrap.__version__", "10.6.0"),
        patch("riocli.bootstrap.appimage.fetch_manifest", return_value=manifest),
        patch("riocli.bootstrap.appimage.download_and_replace") as dr,
    ):
        result = CliRunner().invoke(cli, ["update", "--silent"])
    assert result.exit_code == 0
    assert "latest version" in result.output
    dr.assert_not_called()


def test_update_dev_build_is_not_updatable(monkeypatch):
    """A feature-branch (dev.*) AppImage build refuses to auto-update."""
    monkeypatch.setenv("APPIMAGE", "/opt/rio.AppImage")
    with (
        patch("riocli.bootstrap.__version__", "10.6.0+dev.feature-x.sha"),
        patch("riocli.bootstrap.appimage.fetch_manifest") as fm,
    ):
        result = CliRunner().invoke(cli, ["update", "--silent"])
    assert result.exit_code == 0
    assert "development build" in result.output.lower()
    fm.assert_not_called()


def test_update_pip_install_uses_pypi(monkeypatch):
    """Without APPIMAGE env it is a pip install: uses PyPI, never the blob."""
    monkeypatch.delenv("APPIMAGE", raising=False)
    with (
        patch("riocli.bootstrap.__version__", "10.6.0"),
        patch("riocli.bootstrap.check_for_updates", return_value=(True, "10.7.0")) as cfu,
        patch("riocli.bootstrap.pip_install_cli") as pip,
        patch("riocli.bootstrap.appimage.fetch_manifest") as fm,
    ):
        result = CliRunner().invoke(cli, ["update", "--silent"])
    assert result.exit_code == 0
    cfu.assert_called_once()
    pip.assert_called_once()
    fm.assert_not_called()
