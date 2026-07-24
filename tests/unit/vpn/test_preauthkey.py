# Copyright 2024 Rapyuta Robotics
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

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from riocli.vpn.preauthkey import preauthkey

_FAKE_KEY = "tskey-auth-abc123"
_FAKE_URL = "https://headscale.example.com"
_FAKE_TAG = "tag:rio"

_FAKE_BINDING = {
    "HEADSCALE_PRE_AUTH_KEY": _FAKE_KEY,
    "HEADSCALE_URL": _FAKE_URL,
    "HEADSCALE_ACL_TAG": _FAKE_TAG,
}


def _make_ctx_obj(project_guid: str = "proj-guid-123") -> MagicMock:
    obj = MagicMock()
    obj.project_guid = project_guid
    return obj


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_vpn_enabled():
    with patch("riocli.vpn.preauthkey.is_vpn_enabled_in_project", return_value=True):
        yield


@pytest.fixture
def mock_vpn_disabled():
    with patch("riocli.vpn.preauthkey.is_vpn_enabled_in_project", return_value=False):
        yield


@pytest.fixture
def mock_create_binding():
    with patch("riocli.vpn.preauthkey.create_binding", return_value=_FAKE_BINDING) as m:
        yield m


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.project_guid = "proj-guid-123"
    config.new_v2_client.return_value = MagicMock()
    with patch("riocli.vpn.preauthkey.get_config_from_context", return_value=config) as m:
        yield m, config


class TestPreauthkeyCommand:
    def test_prints_key_only_by_default(
        self, runner, mock_config, mock_vpn_enabled, mock_create_binding
    ):
        result = runner.invoke(preauthkey, obj=_make_ctx_obj())

        assert result.exit_code == 0
        assert result.output.strip() == _FAKE_KEY

    def test_print_all_includes_url_and_tag(
        self, runner, mock_config, mock_vpn_enabled, mock_create_binding
    ):
        result = runner.invoke(preauthkey, ["--print-all"], obj=_make_ctx_obj())

        assert result.exit_code == 0
        assert _FAKE_KEY in result.output
        assert _FAKE_URL in result.output
        assert _FAKE_TAG in result.output

    def test_vpn_not_enabled_exits_nonzero(self, runner, mock_config, mock_vpn_disabled):
        result = runner.invoke(preauthkey, obj=_make_ctx_obj())

        assert result.exit_code != 0

    def test_default_expiry_is_90_days(
        self, runner, mock_config, mock_vpn_enabled, mock_create_binding
    ):
        runner.invoke(preauthkey, obj=_make_ctx_obj())

        _, kwargs = mock_create_binding.call_args
        assert kwargs["delta"] == timedelta(hours=24 * 90)

    def test_custom_expiry_is_forwarded(
        self, runner, mock_config, mock_vpn_enabled, mock_create_binding
    ):
        runner.invoke(preauthkey, ["--expiry", "48"], obj=_make_ctx_obj())

        _, kwargs = mock_create_binding.call_args
        assert kwargs["delta"] == timedelta(hours=48)

    def test_default_is_non_ephemeral(
        self, runner, mock_config, mock_vpn_enabled, mock_create_binding
    ):
        runner.invoke(preauthkey, obj=_make_ctx_obj())

        _, kwargs = mock_create_binding.call_args
        assert kwargs["ephemeral"] is False

    def test_ephemeral_flag_is_forwarded(
        self, runner, mock_config, mock_vpn_enabled, mock_create_binding
    ):
        runner.invoke(preauthkey, ["--ephemeral"], obj=_make_ctx_obj())

        _, kwargs = mock_create_binding.call_args
        assert kwargs["ephemeral"] is True

    def test_missing_key_in_binding_exits_nonzero(
        self, runner, mock_config, mock_vpn_enabled
    ):
        with patch("riocli.vpn.preauthkey.create_binding", return_value={}):
            result = runner.invoke(preauthkey, obj=_make_ctx_obj())

        assert result.exit_code != 0

    def test_create_binding_exception_exits_nonzero(
        self, runner, mock_config, mock_vpn_enabled
    ):
        with patch(
            "riocli.vpn.preauthkey.create_binding",
            side_effect=Exception("network error"),
        ):
            result = runner.invoke(preauthkey, obj=_make_ctx_obj())

        assert result.exit_code != 0
