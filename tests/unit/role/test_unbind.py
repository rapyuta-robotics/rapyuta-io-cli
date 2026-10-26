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
from rapyuta_io_sdk_v2.exceptions import MethodNotAllowedError

from riocli.role.unbind import unbind
from tests.unit.role.conftest import make_binding

ARGS = ["rio-project_admin", "Project:warehouse-prod", "User:engineer@example.com"]

PERMANENT = make_binding("rb-perm")
MORNING = make_binding("rb-am", not_after="2026-10-26T03:00:00Z")
EVENING = make_binding("rb-pm", not_after="2026-10-26T12:00:00Z")


@pytest.fixture
def client():
    client = MagicMock()
    config = MagicMock(organization_guid="org-1")
    config.new_v2_client.return_value = client
    with patch("riocli.role.unbind.get_config_from_context", return_value=config):
        yield client


@pytest.fixture
def bindings():
    with patch("riocli.role.unbind.find_bindings") as mock:
        yield mock


def removed(client: MagicMock) -> list[str]:
    body = client.update_role_binding.call_args.args[0]
    assert body["newBindings"] == []
    return [b.metadata.guid for b in body["oldBindings"]]


def test_one_match_is_removed(runner, client, bindings):
    bindings.return_value = [MORNING]

    result = runner.invoke(unbind, ARGS)

    assert result.exit_code == 0, result.output
    assert removed(client) == ["rb-am"]
    assert "Binding deleted successfully." in result.output


def test_no_match(runner, client, bindings):
    bindings.return_value = []

    result = runner.invoke(unbind, ARGS)

    assert result.exit_code == 0
    assert "Binding does not exist." in result.output
    client.update_role_binding.assert_not_called()


def test_several_without_selector_lists_them(runner, client, bindings):
    bindings.return_value = [PERMANENT, MORNING, EVENING]

    result = runner.invoke(unbind, ARGS)

    assert result.exit_code == 1
    assert (
        "More than one binding matches; select one with --not-after or --permanent."
        in result.output
    )
    assert "2026-10-26T12:00:00+09:00" in result.output
    assert "2026-10-26T21:00:00+09:00" in result.output
    client.update_role_binding.assert_not_called()


def test_not_after_selects_one(runner, client, bindings):
    bindings.return_value = [PERMANENT, MORNING, EVENING]

    result = runner.invoke(unbind, [*ARGS, "--not-after", "2026-10-26T21:00:00+09:00"])

    assert result.exit_code == 0, result.output
    assert removed(client) == ["rb-pm"]


def test_permanent_selects_one(runner, client, bindings):
    bindings.return_value = [PERMANENT, MORNING, EVENING]

    result = runner.invoke(unbind, [*ARGS, "--permanent"])

    assert result.exit_code == 0, result.output
    assert removed(client) == ["rb-perm"]


def test_not_after_with_permanent_is_usage_error(runner, client, bindings):
    result = runner.invoke(
        unbind, [*ARGS, "--permanent", "--not-after", "2026-10-26T21:00:00+09:00"]
    )

    assert result.exit_code == 2
    client.update_role_binding.assert_not_called()


def test_server_error_exits_1(runner, client, bindings):
    bindings.return_value = [MORNING]
    client.update_role_binding.side_effect = MethodNotAllowedError("denied")

    result = runner.invoke(unbind, ARGS)

    assert result.exit_code == 1
    assert "Failed to delete binding: denied" in result.output
