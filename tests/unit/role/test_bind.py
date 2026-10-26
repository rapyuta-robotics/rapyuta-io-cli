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

from riocli.role.bind import bind
from tests.unit.role.conftest import NOW, make_binding

ARGS = ["rio-project_admin", "Project:warehouse-prod", "User:engineer@example.com"]


@pytest.fixture
def client():
    client = MagicMock()
    config = MagicMock(organization_guid="org-1")
    config.new_v2_client.return_value = client
    with (
        patch("riocli.role.bind.get_config_from_context", return_value=config),
        patch("riocli.role.window.utcnow", return_value=NOW),
    ):
        yield client


def created(**window) -> BulkRoleBindingUpdate:
    return BulkRoleBindingUpdate(newBindings=[make_binding("rb-new", **window)])


def sent_spec(client: MagicMock, call: int = 0) -> dict:
    body = client.update_role_binding.call_args_list[call].args[0]
    return body["newBindings"][0]["spec"]


class TestWindowOptions:
    def test_for_sends_end_from_now(self, runner, client):
        client.update_role_binding.return_value = created(
            not_after="2026-10-26T08:00:00Z"
        )

        result = runner.invoke(bind, [*ARGS, "--for", "8h"])

        assert result.exit_code == 0, result.output
        spec = sent_spec(client)
        assert spec["notAfter"] == (NOW + timedelta(hours=8)).isoformat()
        assert "notBefore" not in spec

    def test_not_before_and_not_after_are_sent_with_offset(self, runner, client):
        client.update_role_binding.return_value = created(
            not_before="2026-10-27T00:00:00Z", not_after="2026-10-27T08:00:00Z"
        )

        result = runner.invoke(
            bind,
            [
                *ARGS,
                "--not-before",
                "2026-10-27T09:00:00+09:00",
                "--not-after",
                "2026-10-27T17:00:00+09:00",
            ],
        )

        assert result.exit_code == 0, result.output
        spec = sent_spec(client)
        assert spec["notBefore"] == "2026-10-27T09:00:00+09:00"
        assert spec["notAfter"] == "2026-10-27T17:00:00+09:00"

    def test_no_options_send_no_window(self, runner, client):
        client.update_role_binding.return_value = created()

        result = runner.invoke(bind, ARGS)

        assert result.exit_code == 0, result.output
        spec = sent_spec(client)
        assert "notBefore" not in spec
        assert "notAfter" not in spec
        assert "Binding created successfully." in result.output
        assert "Window" not in result.output

    @pytest.mark.parametrize(
        "options",
        [
            ["--not-after", "2026-10-27T17:00:00+09:00", "--for", "8h"],
            ["--not-before", "2026-10-27T09:00:00+09:00"],
            ["--for", "8x"],
            ["--not-after", "next friday"],
        ],
    )
    def test_usage_errors_send_nothing(self, runner, client, options):
        result = runner.invoke(bind, [*ARGS, *options])

        assert result.exit_code == 2
        client.update_role_binding.assert_not_called()

    def test_success_shows_window_in_local_time_and_utc(self, runner, client):
        client.update_role_binding.return_value = created(
            not_after="2026-10-26T08:00:00Z"
        )

        result = runner.invoke(bind, [*ARGS, "--for", "8h"])

        assert "Binding created successfully." in result.output
        assert "2026-10-26T17:00:00+09:00 (local)" in result.output
        assert "2026-10-26T08:00:00Z UTC" in result.output

    def test_server_error_is_shown_and_exits_1(self, runner, client):
        client.update_role_binding.side_effect = MethodNotAllowedError(
            "notAfter must be in the future"
        )

        result = runner.invoke(bind, [*ARGS, "--not-after", "2026-10-25T00:00:00Z"])

        assert result.exit_code == 1
        assert "Failed to create binding: notAfter must be in the future" in result.output


class TestSafetyCheck:
    def test_window_dropped_by_server_removes_binding(self, runner, client):
        client.update_role_binding.side_effect = [created(), BulkRoleBindingUpdate()]

        result = runner.invoke(bind, [*ARGS, "--for", "8h"])

        assert result.exit_code == 1
        assert client.update_role_binding.call_count == 2
        removal = client.update_role_binding.call_args_list[1].args[0]
        assert removal["newBindings"] == []
        assert [b.metadata.guid for b in removal["oldBindings"]] == ["rb-new"]
        assert (
            "This environment does not support time-bound role bindings; "
            "no binding was kept." in result.output
        )

    def test_failed_removal_reports_binding(self, runner, client):
        client.update_role_binding.side_effect = [
            created(),
            MethodNotAllowedError("boom"),
        ]

        result = runner.invoke(bind, [*ARGS, "--for", "8h"])

        assert result.exit_code == 1
        assert (
            "A permanent binding may exist: rio-project_admin Project:warehouse-prod "
            "User:engineer@example.com (rb-new)" in result.output
        )

    def test_permanent_bind_skips_check(self, runner, client):
        client.update_role_binding.return_value = created()

        result = runner.invoke(bind, ARGS)

        assert result.exit_code == 0
        assert client.update_role_binding.call_count == 1
