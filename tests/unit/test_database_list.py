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
from rapyuta_io_sdk_v2 import Database

from riocli.database.list import list_databases


@pytest.fixture
def runner():
    return CliRunner()


def _database(standby_devices: int, running: int) -> Database:
    postgres = {
        "version": "17",
        "primary": {"deviceName": "edge-node-01", "port": 5432},
    }
    status = {"phase": "Running", "postgres": {}}

    if standby_devices:
        postgres["standby"] = {
            "primaryInterface": "eth0",
            "devices": [
                {"deviceName": f"edge-node-{i + 2:02d}", "port": 5432}
                for i in range(standby_devices)
            ],
        }
        status["postgres"]["standby"] = [
            {
                "deviceName": f"edge-node-{i + 2:02d}",
                "port": 5432,
                "phase": "running" if i < running else "crashloop",
            }
            for i in range(standby_devices)
        ]

    return Database.model_validate(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Database",
            "metadata": {"name": "orders-db", "guid": "db-aaaaaaaaaaaaaaaaaaaa"},
            "spec": {"type": "postgres", "postgres": postgres},
            "status": status,
        }
    )


def _invoke(runner, databases):
    with (
        patch("riocli.database.list.new_v2_client", return_value=MagicMock()),
        patch("riocli.database.list.walk_pages", return_value=iter([databases])),
    ):
        return runner.invoke(list_databases, [])


def test_standby_column_reports_running_over_desired(runner):
    result = _invoke(runner, [_database(standby_devices=2, running=1)])

    assert result.exit_code == 0
    assert "Standby" in result.output
    assert "1/2" in result.output


def test_standby_column_is_a_dash_without_standbys(runner):
    result = _invoke(runner, [_database(standby_devices=0, running=0)])

    assert result.exit_code == 0
    # A primary-only database must not read as "0 standbys running" — it has none.
    assert "0/0" not in result.output
