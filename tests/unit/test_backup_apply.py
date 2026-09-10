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
from rapyuta_io_sdk_v2.exceptions import HttpAlreadyExistsError

from riocli.backup.model import Backup
from riocli.constants import ApplyResult

_MANIFEST = {
    "apiVersion": "api.rapyuta.io/v2",
    "kind": "Backup",
    "metadata": {"name": "ondemand-db-adhoc"},
    "spec": {"type": "onDemand", "database": "ondemand-db"},
}

_REASON = "an on-demand backup requires a healthy scheduled backup for this database"


def _apply(backup: Backup) -> ApplyResult:
    return backup.apply(
        client=MagicMock(),
        v2_client=MagicMock(),
        config=MagicMock(),
        retry_count=1,
        retry_interval=1,
    )


def test_refused_create_carries_the_server_reason():
    # The SDK maps every 409 to HttpAlreadyExistsError, so a create refused on a
    # precondition looks like a name collision. Reporting it as a bare "already
    # exists" turned a refusal into a silent no-op.
    backup = Backup(_MANIFEST)

    with patch.object(
        Backup, "create_object", side_effect=HttpAlreadyExistsError(_REASON)
    ):
        assert _apply(backup) == ApplyResult.EXISTS

    assert backup.exists_reason == _REASON
    # A real attribute, not a manifest key: the reason must never reach the wire.
    assert "exists_reason" not in backup


def test_a_created_backup_reports_no_reason():
    backup = Backup(_MANIFEST)

    with patch.object(Backup, "create_object", return_value=MagicMock()):
        assert _apply(backup) == ApplyResult.CREATED

    assert backup.exists_reason is None


def test_update_is_refused_because_backups_are_immutable():
    with pytest.raises(NotImplementedError):
        Backup(_MANIFEST).update_object(v2_client=MagicMock())
