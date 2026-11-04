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

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
import yaml
from rapyuta_io_sdk_v2.exceptions import HttpNotFoundError

from riocli.apply.parse import Applier
from riocli.backup.model import Backup
from riocli.database.model import Database
from riocli.database.util import wait_until_deleted, wait_until_listed

if TYPE_CHECKING:
    from pathlib import Path

_SECRET = {
    "apiVersion": "api.rapyuta.io/v2",
    "kind": "Secret",
    "metadata": {"name": "db-secret"},
    "spec": {"type": "Opaque", "data": {"U": "u", "P": "p"}},
}
_DATABASE = {
    "apiVersion": "api.rapyuta.io/v2",
    "kind": "Database",
    "metadata": {"name": "db"},
    "spec": {
        "type": "postgres",
        "postgres": {
            "version": "17",
            "primary": {"deviceName": "dev", "dataDirectory": "/d", "port": 5432},
            "users": {
                "primary": {
                    "username": {"name": "db-secret", "key": "U"},
                    "password": {"name": "db-secret", "key": "P"},
                }
            },
        },
    },
}
_BACKUP = {
    "apiVersion": "api.rapyuta.io/v2",
    "kind": "Backup",
    "metadata": {"name": "bk"},
    "spec": {"type": "scheduled", "database": "db", "schedule": "*/5 * * * *"},
}


def test_apply_orders_secret_then_database_then_backup(tmp_path: Path):
    f = tmp_path / "all.yaml"
    f.write_text(yaml.safe_dump_all([_BACKUP, _DATABASE, _SECRET]))

    with patch.object(Applier, "_load_values_and_secrets", return_value={}):
        applier = Applier([str(f)], [], [], MagicMock())

    assert applier._get_apply_order() == [
        ("secret:db-secret",),
        ("database:db",),
        ("backup:bk",),
    ]


def test_database_waits_for_its_secret_before_create():
    client = MagicMock()
    client.get_secret.side_effect = [HttpNotFoundError("nf"), MagicMock()]

    with patch("riocli.database.util.time.sleep"):
        Database(_DATABASE).create_object(v2_client=client)

    assert client.get_secret.call_count == 2
    client.create_database.assert_called_once()


def test_backup_waits_for_its_database_before_create():
    client = MagicMock()
    client.get_database.side_effect = [HttpNotFoundError("nf"), MagicMock()]

    with patch("riocli.database.util.time.sleep"):
        Backup(_BACKUP).create_object(v2_client=client)

    client.get_database.assert_called_with("db")
    client.create_backup.assert_called_once()


def test_wait_gives_up_after_timeout():
    get = MagicMock(side_effect=HttpNotFoundError("nf"))

    with (
        patch("riocli.database.util.time.sleep"),
        patch("riocli.database.util.time.monotonic", side_effect=[0, 10, 61]),
    ):
        with pytest.raises(Exception, match="database db not found after 60s"):
            wait_until_listed(get, "database", "db")

    assert get.call_count == 2


@pytest.mark.parametrize(
    ("model", "manifest", "getter"),
    [(Backup, _BACKUP, "get_backup"), (Database, _DATABASE, "get_database")],
)
def test_delete_returns_only_once_the_resource_is_gone(model, manifest, getter):
    # The server keeps the row until the device acks, and refuses to delete the
    # parent (database, then secret) while it is still there.
    client = MagicMock()
    getattr(client, getter).side_effect = [MagicMock(), HttpNotFoundError("nf")]

    with patch("riocli.database.util.time.sleep"):
        model(manifest).delete_object(v2_client=client)

    assert getattr(client, getter).call_count == 2


def test_delete_wait_gives_up_after_timeout():
    get = MagicMock(return_value=MagicMock())

    with (
        patch("riocli.database.util.time.sleep"),
        patch("riocli.database.util.time.monotonic", side_effect=[0, 10, 61]),
        pytest.raises(Exception, match="backup bk still present 60s after delete"),
    ):
        wait_until_deleted(get, "backup", "bk")

    assert get.call_count == 2
