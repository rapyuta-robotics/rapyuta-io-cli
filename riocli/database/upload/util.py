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


from rapyuta_io_sdk_v2.models import BackupArchive

from riocli.utils import tabulate_data


def display_archive_list(archives: list[BackupArchive], show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ("Upload ID", "Backup ID", "Size")

    data = []
    for a in archives:
        data.append([a.guid, a.backup_run_id or "-", human_size(a.total_size)])

    tabulate_data(data, headers)


def human_size(size: int | None) -> str:
    """Render a byte count in MB or GB; archives are never smaller than that."""
    if not size:
        return "-"

    mb = size / (1024 * 1024)

    return f"{mb / 1024:.2f} GB" if mb >= 1024 else f"{mb:.2f} MB"
