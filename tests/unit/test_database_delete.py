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

from riocli.database.delete import delete_database


@pytest.fixture
def runner():
    return CliRunner()


def _database() -> Database:
    return Database.model_validate(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Database",
            "metadata": {"name": "orders-db", "guid": "db-aaaaaaaaaaaaaaaaaaaa"},
            "spec": {
                "type": "postgres",
                "postgres": {
                    "version": "17",
                    "primary": {"deviceName": "edge-node-01", "port": 5432},
                },
            },
            "status": {"phase": "Running"},
        }
    )


def _invoke(runner, args):
    client = MagicMock()
    client.list_databases.return_value.items = [_database()]

    with patch("riocli.database.delete.new_v2_client", return_value=client):
        result = runner.invoke(delete_database, [*args, "--force", "orders-db"])

    return result, client


@pytest.mark.parametrize(
    ("args", "force"),
    [([], False), (["--skip-device-ack"], True)],
)
def test_skip_device_ack_maps_to_force_delete(runner, args, force):
    result, client = _invoke(runner, args)

    assert result.exit_code == 0, result.output
    client.delete_database.assert_called_once_with(name="orders-db", force=force)
