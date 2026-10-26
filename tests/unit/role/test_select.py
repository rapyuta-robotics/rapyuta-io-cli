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
from unittest.mock import MagicMock

import pytest
from rapyuta_io_sdk_v2 import RoleBindingList

from riocli.role.select import AmbiguousBindingError, find_bindings, select_binding
from tests.unit.role.conftest import make_binding

PERMANENT = make_binding("rb-perm")
MORNING = make_binding("rb-am", not_after="2026-10-26T03:00:00Z")
EVENING = make_binding(
    "rb-pm", not_before="2026-10-26T09:00:00Z", not_after="2026-10-26T12:00:00Z"
)


def mock_client(items: list) -> MagicMock:
    client = MagicMock()
    client.list_role_bindings.return_value = RoleBindingList(
        metadata={"continue": None}, items=items
    )
    return client


class TestFindBindings:
    def test_filters_are_sent_as_lists_and_exact_matches_kept(self):
        other_role = make_binding("rb-x", role="rio-project_viewer")
        client = mock_client([PERMANENT, other_role])

        found = find_bindings(
            client,
            "rio-project_admin",
            ("User", "engineer@example.com"),
            ("Project", "warehouse-prod"),
        )

        kwargs = client.list_role_bindings.call_args.kwargs
        assert kwargs["role_names"] == ["rio-project_admin"]
        assert kwargs["subject_kinds"] == ["User"]
        assert kwargs["subject_names"] == ["engineer@example.com"]
        assert kwargs["domain_kinds"] == ["Project"]
        assert kwargs["domain_names"] == ["warehouse-prod"]
        assert [b.metadata.guid for b in found] == ["rb-perm"]

    def test_kinds_match_case_insensitively(self):
        client = mock_client([PERMANENT])

        found = find_bindings(
            client,
            "rio-project_admin",
            ("user", "engineer@example.com"),
            ("project", "warehouse-prod"),
        )

        assert found == [PERMANENT]


class TestSelectBinding:
    def test_no_match(self):
        assert select_binding([]) is None

    def test_one_match(self):
        assert select_binding([MORNING]) is MORNING

    def test_several_without_selector(self):
        with pytest.raises(AmbiguousBindingError) as exc:
            select_binding([PERMANENT, MORNING, EVENING])

        assert exc.value.candidates == [PERMANENT, MORNING, EVENING]

    def test_not_after_selects_by_end_to_the_second(self):
        end = datetime(2026, 10, 26, 12, 0, 0, 400000, tzinfo=timezone.utc)

        assert select_binding([PERMANENT, MORNING, EVENING], not_after=end) is EVENING

    def test_not_after_without_match(self):
        end = datetime(2026, 10, 26, 13, 0, tzinfo=timezone.utc)

        assert select_binding([PERMANENT, MORNING], not_after=end) is None

    def test_permanent_selects_binding_without_window(self):
        assert select_binding([PERMANENT, MORNING, EVENING], permanent=True) is PERMANENT
