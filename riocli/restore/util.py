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


def fetch_restores(
    client: Client,
    database: str,
    restore_name_or_regex: str,
    include_all: bool,
) -> list:
    restores = []
    for page in walk_pages(client.list_restores, database=database):
        restores.extend(page)

    if include_all:
        return restores

    result = []
    for restore in restores:
        if re.search(restore_name_or_regex, restore.metadata.name):
            result.append(restore)

    return result


def display_restore_list(restores: typing.Any, show_header: bool = True):
    headers = []
    if show_header:
        headers = ("GUID", "Name", "Source", "Databases", "Phase", "Restored")

    data = []
    for restore in restores:
        status = restore.status
        # The phase and the restored list come from the device's result pointer,
        # which is the only record of what actually landed.
        phase = getattr(status, "phase", None) if status else None
        restored = getattr(status, "restored_databases", None) if status else None
        requested = restore.spec.databases

        data.append(
            [
                restore.metadata.guid,
                restore.metadata.name,
                _source_summary(restore.spec.source),
                ", ".join(requested) if requested else "all",
                phase or "Unknown",
                ", ".join(restored) if restored else "-",
            ]
        )

    tabulate_data(data, headers)


def _source_summary(source: typing.Any) -> str:
    """Describe where a restore reads from, in one column."""
    if source.type == "dataDirectory":
        return f"dataDirectory: {source.old_data_directory}"

    # The archive is what the restore actually reads, so it is what the column
    # shows; the backup name is provenance and may be absent.
    return f"backup: {source.file_upload}"
