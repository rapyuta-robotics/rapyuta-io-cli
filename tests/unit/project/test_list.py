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

from riocli.project.list import list_projects


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def ctx_obj():
    """A minimal stand-in for the CLI config object the command reads the
    current organization and project out of."""
    obj = MagicMock()
    obj.data = {
        "organization_id": "org-guid",
        "project_id": "project-guid",
    }
    return obj


@pytest.fixture
def walk_pages():
    """Patch the clients and pagination, yielding the walk_pages mock so tests
    can assert on the filters the command forwards to the API."""
    with (
        patch("riocli.project.list.new_v2_client", return_value=MagicMock()),
        patch("riocli.organization.util.new_v2_client", return_value=MagicMock()),
        patch("riocli.project.list.walk_pages", return_value=iter(())) as mock,
    ):
        yield mock


class TestLabelFilter:
    def test_label_flag_is_forwarded_to_the_api(self, runner, ctx_obj, walk_pages):
        # The flag used to be accepted and dropped, so the API returned every
        # project in the organization regardless of the label passed.
        result = runner.invoke(list_projects, ["--label", "release=3.0"], obj=ctx_obj)

        assert result.exit_code == 0
        assert list(walk_pages.call_args.kwargs["label_selector"]) == ["release=3.0"]

    def test_repeated_label_flags_are_all_forwarded(self, runner, ctx_obj, walk_pages):
        result = runner.invoke(
            list_projects, ["-l", "release=3.0", "-l", "team=io"], obj=ctx_obj
        )

        assert result.exit_code == 0
        assert list(walk_pages.call_args.kwargs["label_selector"]) == [
            "release=3.0",
            "team=io",
        ]

    def test_no_label_flag_sends_no_label_filter(self, runner, ctx_obj, walk_pages):
        result = runner.invoke(list_projects, [], obj=ctx_obj)

        assert result.exit_code == 0
        assert list(walk_pages.call_args.kwargs["label_selector"]) == []

    def test_organization_is_still_forwarded(self, runner, ctx_obj, walk_pages):
        result = runner.invoke(list_projects, ["--label", "release=3.0"], obj=ctx_obj)

        assert result.exit_code == 0
        assert walk_pages.call_args.kwargs["organizations"] == ["org-guid"]
