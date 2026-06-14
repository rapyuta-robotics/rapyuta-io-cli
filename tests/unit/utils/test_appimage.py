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
