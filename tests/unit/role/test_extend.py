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

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from rapyuta_io_sdk_v2 import BulkRoleBindingUpdate
from rapyuta_io_sdk_v2.exceptions import MethodNotAllowedError

from riocli.role.extend import extend
from tests.unit.role.conftest import NOW, make_binding

ARGS = ["rio-project_admin", "Project:warehouse-prod", "User:engineer@example.com"]

PERMANENT = make_binding("rb-perm")
SHIFT = make_binding(
    "rb-shift", not_before="2026-10-25T23:00:00Z", not_after="2026-10-26T03:00:00Z"
)
LATER = make_binding("rb-later", not_after="2026-10-26T12:00:00Z")


@pytest.fixture
def client():
    client = MagicMock()
    config = MagicMock(organization_guid="org-1")
    config.new_v2_client.return_value = client
    with (
        patch("riocli.role.extend.get_config_from_context", return_value=config),
        patch("riocli.role.window.utcnow", return_value=NOW),
    ):
        yield client


@pytest.fixture
def bindings():
    with patch("riocli.role.extend.find_bindings") as mock:
        yield mock


def test_replaces_window_in_one_request(runner, client, bindings):
    bindings.return_value = [PERMANENT, SHIFT]
    client.update_role_binding.return_value = BulkRoleBindingUpdate(
        newBindings=[
            make_binding(
                "rb-new",
                not_before="2026-10-25T23:00:00Z",
                not_after="2026-10-26T08:00:00Z",
            )
        ]
    )

    result = runner.invoke(extend, [*ARGS, "--not-after", "2026-10-26T17:00:00+09:00"])

    assert result.exit_code == 0, result.output
    assert client.update_role_binding.call_count == 1
    body = client.update_role_binding.call_args.args[0]
    assert [b.metadata.guid for b in body["oldBindings"]] == ["rb-shift"]
    new = body["newBindings"][0]
    assert new["metadata"]["organizationGUID"] == "org-1"
    assert new["spec"]["roleRef"] == {"name": "rio-project_admin"}
    assert new["spec"]["subject"] == {"kind": "User", "name": "engineer@example.com"}
    assert new["spec"]["domain"] == {"kind": "Project", "name": "warehouse-prod"}
    assert new["spec"]["notBefore"] == "2026-10-25T23:00:00+00:00"
    assert new["spec"]["notAfter"] == "2026-10-26T17:00:00+09:00"
    assert "Binding extended. Window:" in result.output
    assert "2026-10-26T17:00:00+09:00 (local)" in result.output


def test_for_counts_from_now(runner, client, bindings):
    bindings.return_value = [SHIFT]

    result = runner.invoke(extend, [*ARGS, "--for", "30m"])

    assert result.exit_code == 0, result.output
    new = client.update_role_binding.call_args.args[0]["newBindings"][0]
    assert new["spec"]["notAfter"] == (NOW + timedelta(minutes=30)).isoformat()


def test_several_time_bound_without_selector(runner, client, bindings):
    bindings.return_value = [PERMANENT, SHIFT, LATER]

    result = runner.invoke(extend, [*ARGS, "--for", "30m"])

    assert result.exit_code == 1
    assert "select one with --current-not-after" in result.output
    assert "2026-10-26T21:00:00+09:00" in result.output
    client.update_role_binding.assert_not_called()


def test_current_not_after_selects_one(runner, client, bindings):
    bindings.return_value = [PERMANENT, SHIFT, LATER]

    result = runner.invoke(
        extend,
        [*ARGS, "--for", "30m", "--current-not-after", "2026-10-26T12:00:00+09:00"],
    )

    assert result.exit_code == 0, result.output
    body = client.update_role_binding.call_args.args[0]
    assert [b.metadata.guid for b in body["oldBindings"]] == ["rb-shift"]


def test_no_time_bound_binding(runner, client, bindings):
    bindings.return_value = [PERMANENT]

    result = runner.invoke(extend, [*ARGS, "--for", "30m"])

    assert result.exit_code == 1
    assert "No time-bound binding matches." in result.output
    client.update_role_binding.assert_not_called()


@pytest.mark.parametrize(
    "options",
    [[], ["--for", "30m", "--not-after", "2026-10-26T17:00:00+09:00"]],
)
def test_needs_exactly_one_end(runner, client, bindings, options):
    result = runner.invoke(extend, [*ARGS, *options])

    assert result.exit_code == 2
    client.update_role_binding.assert_not_called()


def test_server_error_exits_1(runner, client, bindings):
    bindings.return_value = [SHIFT]
    client.update_role_binding.side_effect = MethodNotAllowedError(
        "notAfter must be in the future"
    )

    result = runner.invoke(extend, [*ARGS, "--not-after", "2026-10-25T00:00:00Z"])

    assert result.exit_code == 1
    assert "Failed to extend binding: notAfter must be in the future" in result.output
