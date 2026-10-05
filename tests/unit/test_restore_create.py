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
from rapyuta_io_sdk_v2 import Restore

from riocli.database.restore.create import create_restore


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, args):
    client = MagicMock()
    client.create_restore.return_value = Restore.model_validate(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Restore",
            "metadata": {"name": "orders-restore", "guid": "restore-aaaaaaaaaaaaaaaa"},
            "spec": {
                "database": "orders-db",
                "source": {"type": "backup", "fileUpload": "fileupload-abc123"},
            },
            "status": {"phase": "Running"},
        }
    )
    with patch("riocli.database.restore.create.new_v2_client", return_value=client):
        result = runner.invoke(create_restore, args)

    return result, client


def test_target_time_is_sent_on_the_source(runner):
    result, client = _invoke(
        runner,
        [
            "orders-restore",
            "-d",
            "orders-db",
            "-u",
            "fileupload-abc123",
            "--target-time",
            "2026-01-01T02:00:00Z",
        ],
    )

    assert result.exit_code == 0
    body = client.create_restore.call_args.kwargs["body"]
    assert body["spec"]["source"]["targetTime"] == "2026-01-01T02:00:00Z"


def test_target_time_is_refused_for_a_data_directory(runner):
    # An old data directory is a fixed snapshot with no WAL to replay, so a
    # point in time would silently mean nothing.
    result, client = _invoke(
        runner,
        [
            "orders-migrate",
            "-d",
            "orders-db-v18",
            "--source",
            "dataDirectory",
            "--old-data-directory",
            "/opt/rapyuta/volumes/orders-db/17",
            "--source-version",
            "17",
            "--target-time",
            "2026-01-01T02:00:00Z",
        ],
    )

    assert result.exit_code == 1
    assert "only supported when --source is backup" in result.output
    client.create_restore.assert_not_called()


def test_no_target_time_leaves_the_key_out(runner):
    result, client = _invoke(
        runner, ["orders-restore", "-d", "orders-db", "-u", "fileupload-abc123"]
    )

    assert result.exit_code == 0
    assert (
        "targetTime"
        not in client.create_restore.call_args.kwargs["body"]["spec"]["source"]
    )
