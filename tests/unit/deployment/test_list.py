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

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from riocli.deployment.list import list_deployments


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def walk_pages():
    """Patch the client and pagination, yielding the walk_pages mock so tests
    can assert on the filters the command forwards to the API."""
    with (
        patch("riocli.deployment.list.new_v2_client", return_value=MagicMock()),
        patch("riocli.deployment.list.walk_pages", return_value=iter(())) as mock,
    ):
        yield mock


class TestDeviceFilter:
    def test_device_flag_is_forwarded_to_the_api(self, runner, walk_pages):
        # The flag used to be accepted and dropped, so the API returned every
        # deployment in the project regardless of the device passed.
        result = runner.invoke(list_deployments, ["--device", "my-device"])

        assert result.exit_code == 0
        assert walk_pages.call_args.kwargs["device_name"] == "my-device"

    def test_no_device_flag_sends_no_device_filter(self, runner, walk_pages):
        result = runner.invoke(list_deployments, [])

        assert result.exit_code == 0
        assert walk_pages.call_args.kwargs["device_name"] is None

    def test_other_filters_are_still_forwarded(self, runner, walk_pages):
        result = runner.invoke(
            list_deployments,
            ["--device", "my-device", "--phase", "Stopped", "-l", "key=value"],
        )

        assert result.exit_code == 0
        kwargs = walk_pages.call_args.kwargs
        assert kwargs["device_name"] == "my-device"
        assert list(kwargs["phases"]) == ["Stopped"]
        assert list(kwargs["label_selector"]) == ["key=value"]
