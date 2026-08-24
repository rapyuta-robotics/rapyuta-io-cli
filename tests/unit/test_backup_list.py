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

from rapyuta_io_sdk_v2 import Backup

from riocli.backup.util import display_backup_list


def _backup(status: dict | None) -> Backup:
    return Backup.model_validate(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Backup",
            "metadata": {"name": "orders-nightly", "guid": "backup-aaaaaaaaaaaaaaaaaa"},
            "spec": {
                "type": "scheduled",
                "database": "orders-db",
                "schedule": "0 2 * * *",
            },
            "status": status,
        }
    )


def test_step_is_shown(capsys):
    backup = _backup({"phase": "Ready", "step": "archiving base backup"})

    display_backup_list([backup])
    out = capsys.readouterr().out

    # The recover dominates a run, so the step is what separates a slow backup
    # from a stuck one.
    assert "archiving base backup" in out
    assert "Ready" in out


def test_missing_status_does_not_break_the_table(capsys):
    display_backup_list([_backup(None)])
    out = capsys.readouterr().out

    assert "Unknown" in out
