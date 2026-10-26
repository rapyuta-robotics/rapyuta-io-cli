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

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from rapyuta_io_sdk_v2.exceptions import HttpAlreadyExistsError

from riocli.constants import ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.role.model import RoleBinding
from tests.unit.role.conftest import make_binding, tokyo  # noqa: F401

START = "2026-10-26T00:00:00Z"
END = "2026-10-26T08:00:00Z"


def manifest(not_before=None, not_after=None) -> dict:
    spec = {
        "roleRef": {"kind": "Role", "name": "rio-project_admin"},
        "subject": {"kind": "User", "name": "engineer@example.com"},
        "domain": {"kind": "Project", "name": "warehouse-prod"},
    }
    if not_before is not None:
        spec["notBefore"] = not_before
    if not_after is not None:
        spec["notAfter"] = not_after

    return {
        "apiVersion": "api.rapyuta.io/v2",
        "kind": "RoleBinding",
        "metadata": {"name": "engineer-warehouse-admin", "labels": {"team": "ops"}},
        "spec": spec,
    }


@pytest.fixture
def existing():
    with patch("riocli.role.model.find_bindings", return_value=[]) as mock:
        yield mock


def apply(obj: RoleBinding, client: MagicMock) -> ApplyResult:
    return obj.apply(
        client=None, v2_client=client, config=None, retry_count=0, retry_interval=0
    )


def delete(obj: RoleBinding, client: MagicMock) -> None:
    obj.delete(
        client=None, v2_client=client, config=None, retry_count=0, retry_interval=0
    )


def body(client: MagicMock, call: int = -1) -> dict:
    return client.update_role_binding.call_args_list[call].args[0]


class TestApply:
    def test_create_sends_bulk_shape(self, existing):
        client = MagicMock()
        obj = RoleBinding(manifest(START, END))

        assert apply(obj, client) == ApplyResult.CREATED

        sent = body(client)
        assert sent["oldBindings"] == []
        assert len(sent["newBindings"]) == 1
        spec = sent["newBindings"][0].spec
        assert spec.not_before == datetime(2026, 10, 26, 0, 0, tzinfo=timezone.utc)
        assert spec.not_after == datetime(2026, 10, 26, 8, 0, tzinfo=timezone.utc)
        assert sent["newBindings"][0].metadata.labels == {"team": "ops"}

    def test_create_permanent(self, existing):
        client = MagicMock()

        assert apply(RoleBinding(manifest()), client) == ApplyResult.CREATED
        assert body(client)["newBindings"][0].spec.not_after is None

    def test_duplicate_permanent_exists(self, existing):
        existing.return_value = [
            make_binding("rb-perm"),
            make_binding("rb-tb", not_after=END),
        ]
        client = MagicMock()

        assert apply(RoleBinding(manifest()), client) == ApplyResult.EXISTS
        client.update_role_binding.assert_not_called()

    def test_identical_window_exists(self, existing):
        existing.return_value = [make_binding("rb-tb", not_before=START, not_after=END)]
        client = MagicMock()

        assert apply(RoleBinding(manifest(START, END)), client) == ApplyResult.EXISTS
        client.update_role_binding.assert_not_called()

    def test_server_conflict_exists(self, existing):
        client = MagicMock()
        client.update_role_binding.side_effect = HttpAlreadyExistsError("exists")
        existing.side_effect = [
            [],
            [make_binding("rb-tb", not_before=START, not_after=END)],
        ]

        assert apply(RoleBinding(manifest(START, END)), client) == ApplyResult.EXISTS

    def test_same_start_is_replaced(self, existing):
        existing.return_value = [
            make_binding("rb-perm"),
            make_binding("rb-old", not_before=START, not_after=END),
            make_binding("rb-other", not_after="2026-10-27T08:00:00Z"),
        ]
        client = MagicMock()

        later = "2026-10-26T11:00:00Z"
        assert apply(RoleBinding(manifest(START, later)), client) == ApplyResult.UPDATED

        assert client.update_role_binding.call_count == 1
        sent = body(client)
        assert [b.metadata.guid for b in sent["oldBindings"]] == ["rb-old"]
        assert sent["newBindings"][0].spec.not_after == datetime(
            2026, 10, 26, 11, 0, tzinfo=timezone.utc
        )

    def test_both_starts_empty_count_as_equal(self, existing):
        existing.return_value = [make_binding("rb-old", not_after=END)]
        client = MagicMock()

        later = "2026-10-26T11:00:00Z"
        assert apply(RoleBinding(manifest(None, later)), client) == ApplyResult.UPDATED
        assert [b.metadata.guid for b in body(client)["oldBindings"]] == ["rb-old"]

    def test_different_start_creates(self, existing):
        existing.return_value = [make_binding("rb-old", not_after=END)]
        client = MagicMock()

        assert apply(RoleBinding(manifest(START, END)), client) == ApplyResult.CREATED
        assert body(client)["oldBindings"] == []

    def test_several_with_same_start_fail_and_change_nothing(self, existing):
        existing.return_value = [
            make_binding("rb-a", not_before=START, not_after=END),
            make_binding("rb-b", not_before=START, not_after="2026-10-26T10:00:00Z"),
        ]
        client = MagicMock()

        with pytest.raises(Exception, match="2 time-bound bindings") as exc:
            apply(RoleBinding(manifest(START, "2026-10-26T11:00:00Z")), client)

        assert "2026-10-26T17:00:00+09:00" in str(exc.value)
        assert "2026-10-26T19:00:00+09:00" in str(exc.value)
        client.update_role_binding.assert_not_called()


class TestDelete:
    def test_removes_binding_with_same_window(self, existing):
        existing.return_value = [
            make_binding("rb-perm"),
            make_binding("rb-tb", not_before=START, not_after=END),
        ]
        client = MagicMock()

        delete(RoleBinding(manifest(START, END)), client)

        sent = body(client)
        assert sent["newBindings"] == []
        assert [b.metadata.guid for b in sent["oldBindings"]] == ["rb-tb"]

    def test_removes_permanent_binding(self, existing):
        existing.return_value = [
            make_binding("rb-perm"),
            make_binding("rb-tb", not_after=END),
        ]
        client = MagicMock()

        delete(RoleBinding(manifest()), client)

        assert [b.metadata.guid for b in body(client)["oldBindings"]] == ["rb-perm"]

    def test_not_found(self, existing):
        existing.return_value = [make_binding("rb-tb", not_after=END)]
        client = MagicMock()

        with pytest.raises(ResourceNotFound):
            delete(RoleBinding(manifest(START, END)), client)

        client.update_role_binding.assert_not_called()
