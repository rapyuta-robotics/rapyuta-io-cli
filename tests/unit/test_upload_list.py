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

from click.testing import CliRunner

from riocli.database.upload.list import list_uploads


def _run(args: list[str]):
    with (
        patch("riocli.database.upload.list.new_v2_client", return_value=MagicMock()),
        patch("riocli.database.upload.list.walk_pages", return_value=iter([[]])) as walk,
    ):
        result = CliRunner().invoke(list_uploads, args)

    return result, walk


def test_database_filter_reaches_the_api():
    result, walk = _run(["--database", "orders-db"])

    assert result.exit_code == 0
    assert walk.call_args.kwargs["database"] == "orders-db"


def test_no_database_lists_the_whole_project():
    # An archive's database is usually deleted by the time anyone looks for it,
    # so the listing must not require one.
    result, walk = _run([])

    assert result.exit_code == 0
    assert walk.call_args.kwargs["database"] is None
