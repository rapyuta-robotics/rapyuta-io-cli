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

import re
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.backup.create import create_backup, generated_backup_name

# The apiserver's name rule (v2/databases/constants.go _databaseNameRegexPattern).
SERVER_NAME = re.compile(r"^[a-zA-Z][a-zA-Z0-9-_]{2,74}$")


def _run(args: list[str]) -> tuple[object, MagicMock]:
    client = MagicMock()
    with (
        patch("riocli.backup.create.new_v2_client", return_value=client),
        patch("riocli.backup.create.display_backup_list"),
    ):
        result = CliRunner().invoke(create_backup, args)
    return result, client


def _body(client: MagicMock) -> dict:
    return client.create_backup.call_args.kwargs["body"]


def test_database_alone_creates_an_on_demand_backup_with_a_generated_name():
    result, client = _run(["--database", "orders-db"])

    assert result.exit_code == 0, result.output
    body = _body(client)
    assert body["spec"] == {"type": "onDemand", "database": "orders-db"}
    assert re.fullmatch(r"orders-db-ondemand-\d{8}-\d{6}", body["metadata"]["name"])


def test_a_given_name_is_kept_for_an_on_demand_backup():
    result, client = _run(["orders-adhoc", "--database", "orders-db"])

    assert result.exit_code == 0, result.output
    assert _body(client)["metadata"]["name"] == "orders-adhoc"
    assert _body(client)["spec"]["type"] == "onDemand"


def test_a_schedule_makes_the_backup_scheduled():
    result, client = _run(
        ["orders-nightly", "--database", "orders-db", "--schedule", "0 2 * * *"]
    )

    assert result.exit_code == 0, result.output
    assert _body(client)["spec"] == {
        "type": "scheduled",
        "database": "orders-db",
        "schedule": "0 2 * * *",
    }


def test_a_scheduled_backup_still_needs_a_name():
    result, client = _run(["--database", "orders-db", "--schedule", "0 2 * * *"])

    assert result.exit_code == 1
    assert "BACKUP_NAME is required" in result.output
    client.create_backup.assert_not_called()


def test_explicit_scheduled_type_still_needs_a_schedule():
    result, client = _run(
        ["orders-nightly", "--database", "orders-db", "--type", "scheduled"]
    )

    assert result.exit_code == 1
    assert "--schedule is required" in result.output
    client.create_backup.assert_not_called()


def test_generated_name_carries_the_utc_datetime():
    now = datetime(2026, 10, 22, 9, 5, 3, tzinfo=timezone.utc)

    assert generated_backup_name("orders-db", now) == "orders-db-ondemand-20261022-090503"


def test_generated_name_fits_the_server_limit_for_the_longest_database_name():
    database = "d" + "b" * 74
    name = generated_backup_name(database, datetime(2026, 10, 22, tzinfo=timezone.utc))

    assert len(name) == 75
    assert SERVER_NAME.fullmatch(name)
    assert name.endswith("-ondemand-20261022-000000")
