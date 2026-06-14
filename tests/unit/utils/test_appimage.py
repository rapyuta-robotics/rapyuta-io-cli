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

from hashlib import sha256
from unittest.mock import MagicMock

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


def test_channel_for_version_invalid():
    with pytest.raises(ValueError):
        appimage.channel_for_version("notaversion")


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
    assert (
        appimage.update_available("devel", "10.6.0-devel+bbb2222", "10.6.0-devel+aaa1111")
        is True
    )


def test_update_available_devel_same():
    assert (
        appimage.update_available("devel", "10.6.0-devel+aaa1111", "10.6.0-devel+aaa1111")
        is False
    )


def test_update_available_devel_no_downgrade():
    # remote base version older than current → no update even on devel
    assert (
        appimage.update_available("devel", "10.5.0-devel+aaa1111", "10.6.0-devel+bbb2222")
        is False
    )


def _fake_response(content=b"", json_data=None):
    resp = MagicMock()
    resp.content = content
    resp.raise_for_status = MagicMock()
    if json_data is not None:
        resp.json = MagicMock(return_value=json_data)
    return resp


def test_fetch_manifest(monkeypatch):
    manifest = {"version": "10.6.0-devel+abc", "file": "rio.AppImage", "sha256": "x"}
    monkeypatch.setattr(
        appimage.requests, "get", lambda url, **kw: _fake_response(json_data=manifest)
    )
    assert appimage.fetch_manifest("devel") == manifest


def test_download_and_replace_writes_target(monkeypatch, tmp_path):
    payload = b"APPIMAGE-BYTES"
    digest = sha256(payload).hexdigest()
    manifest = {"version": "10.6.0", "file": "rio.AppImage", "sha256": digest}
    monkeypatch.setattr(
        appimage.requests, "get", lambda url, **kw: _fake_response(content=payload)
    )
    target = tmp_path / "rio"
    target.write_bytes(b"OLD")
    appimage.download_and_replace("release", manifest, target=str(target))
    assert target.read_bytes() == payload


def test_download_and_replace_missing_sha256(monkeypatch, tmp_path):
    # manifest without sha256 must raise ValueError and leave target untouched
    payload = b"APPIMAGE-BYTES"
    manifest = {"version": "10.6.0", "file": "rio.AppImage"}
    monkeypatch.setattr(
        appimage.requests, "get", lambda url, **kw: _fake_response(content=payload)
    )
    target = tmp_path / "rio"
    target.write_bytes(b"OLD")
    with pytest.raises(ValueError, match="sha256"):
        appimage.download_and_replace("release", manifest, target=str(target))
    assert target.read_bytes() == b"OLD"


def test_download_and_replace_checksum_mismatch(monkeypatch, tmp_path):
    manifest = {"version": "10.6.0", "file": "rio.AppImage", "sha256": "deadbeef"}
    monkeypatch.setattr(
        appimage.requests, "get", lambda url, **kw: _fake_response(content=b"bytes")
    )
    target = tmp_path / "rio"
    target.write_bytes(b"OLD")
    with pytest.raises(Exception, match="[Cc]hecksum"):
        appimage.download_and_replace("release", manifest, target=str(target))
    # original must be untouched on mismatch
    assert target.read_bytes() == b"OLD"
