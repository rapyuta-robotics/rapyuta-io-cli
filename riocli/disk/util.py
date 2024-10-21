# Copyright 2024 Rapyuta Robotics
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

from riocli.disk.model import Disk
from riocli.utils import tabulate_data
from riocli.v2client import Client


def fetch_disks(
    client: Client,
    disk_name_or_regex: str,
    include_all: bool,
) -> typing.List[Disk]:
    disks = client.list_disks()

    if include_all:
        return disks

    result = []
    for n in disks:
        if re.search(disk_name_or_regex, n.metadata.name):
            result.append(n)

    return result


def display_disk_list(disks: typing.Any, show_header: bool = True):
    headers = []
    if show_header:
        headers = (
            "Disk ID",
            "Name",
            "Status",
            "Capacity (GB)",
            "Capacity Used (GB)",
            "Used By",
        )

    data = []

    for d in disks:
        capacity = d.status.get("capacityUsed", 0) / (1024 * 1204 * 1024)  # Bytes -> GB

        data.append(
            [
                d.metadata.guid,
                d.metadata.name,
                d.status.get("status"),
                d.spec.capacity,
                capacity,
                d.status.get("diskBound", {}).get("deployment_name"),
            ]
        )

    tabulate_data(data, headers)
