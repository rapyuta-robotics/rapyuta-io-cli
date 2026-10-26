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

import json
from unittest.mock import MagicMock, patch

import pytest
import yaml

from riocli.role.list import list_role_bindings
from tests.unit.role.conftest import NOW, make_binding

PERMANENT = make_binding("rb-perm")
ACTIVE = make_binding("rb-active", not_after="2026-10-26T02:10:00Z")
UPCOMING = make_binding(
    "rb-upcoming", not_before="2026-10-26T00:30:00Z", not_after="2026-10-26T08:00:00Z"
)
ENDED = make_binding("rb-ended", not_after="2026-10-25T23:00:00Z")


@pytest.fixture
def listed():
    with (
        patch("riocli.role.list.get_config_from_context", return_value=MagicMock()),
        patch(
            "riocli.role.list.walk_pages",
            return_value=iter([[PERMANENT, ACTIVE, UPCOMING, ENDED]]),
        ),
        patch("riocli.role.window.utcnow", return_value=NOW),
    ):
        yield


def row(output: str, needle: str) -> str:
    return next(line for line in output.splitlines() if needle in line)


def test_table_shows_window_and_status(runner, listed):
    result = runner.invoke(list_role_bindings, [])

    assert result.exit_code == 0, result.output
    header = result.output.splitlines()[0]
    for column in ["Role", "Domain", "Subject", "Not Before", "Not After", "Status"]:
        assert column in header

    lines = [line for line in result.output.splitlines()[2:] if line.strip()]
    assert len(lines) == 4
    assert lines[0].rstrip().endswith("User:engineer@example.com")
    assert "2026-10-26T11:10:00+09:00" in lines[1]
    assert lines[1].rstrip().endswith("2h 10m left")
    assert "2026-10-26T09:30:00+09:00" in lines[2]
    assert lines[2].rstrip().endswith("starts in 30m")
    assert lines[3].rstrip().endswith("ended")


@pytest.mark.parametrize("fmt, load", [("json", json.loads), ("yaml", yaml.safe_load)])
def test_format_outputs_windows_in_utc(runner, listed, fmt, load):
    result = runner.invoke(list_role_bindings, ["--format", fmt])

    assert result.exit_code == 0, result.output
    items = load(result.output)
    assert [i["metadata"]["guid"] for i in items] == [
        "rb-perm",
        "rb-active",
        "rb-upcoming",
        "rb-ended",
    ]
    assert "notAfter" not in items[0]["spec"]
    assert items[2]["spec"]["notBefore"] == "2026-10-26T00:30:00Z"
    assert items[2]["spec"]["notAfter"] == "2026-10-26T08:00:00Z"
