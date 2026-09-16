# Copyright 2025 Rapyuta Robotics
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

import re
import typing

from rapyuta_io_sdk_v2 import Client, walk_pages

from riocli.utils import tabulate_data


def fetch_backups(
    client: Client,
    backup_name_or_regex: str,
    include_all: bool,
) -> list:
    backups = []
    for page in walk_pages(client.list_backups):
        backups.extend(page)

    if include_all:
        return backups

    result = []
    for backup in backups:
        if re.search(backup_name_or_regex, backup.metadata.name):
            result.append(backup)

    return result


def display_backup_list(backups: typing.Any, show_header: bool = True):
    headers = []
    if show_header:
        headers = ("GUID", "Name", "Type", "Database", "Schedule", "Phase")

    data = []
    for backup in backups:
        phase = getattr(backup.status, "phase", None) if backup.status else None
        data.append(
            [
                backup.metadata.guid,
                backup.metadata.name,
                backup.spec.type,
                backup.spec.database,
                backup.spec.schedule or "-",
                phase or "Unknown",
            ]
        )

    tabulate_data(data, headers)
