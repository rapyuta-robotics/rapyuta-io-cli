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
import time
import typing

from rapyuta_io_sdk_v2 import Client

from riocli.utils import tabulate_data
from riocli.utils.enums import DiskStatusConstants
from riocli.utils.error import DeploymentNotRunning, RetriesExhausted


def fetch_disks(
    client: Client,
    disk_name_or_regex: str,
    include_all: bool,
) -> list:
    disks = client.list_disks()

    if include_all:
        return disks.items

    result = []
    for n in disks.items:
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
        capacity_used = getattr(d.status, "capacity_used", 0) or 0

        capacity = capacity_used / (1024 * 1204 * 1024)  # Bytes -> GB

        data.append(
            [
                d.metadata.guid,
                d.metadata.name,
                d.status.status,
                d.spec.capacity,
                capacity,
                getattr(d.status.disk_bound, "deployment_name", None),
            ]
        )

    tabulate_data(data, headers)


def poll_disk(
    client: Client,
    name: str,
    retry_count: int = 50,
    sleep_interval: int = 6,
):
    disk = client.get_disk(name)
    status = disk.status

    for _ in range(retry_count):
        if status.status in [
            DiskStatusConstants.DiskStatusAvailable.value,
            DiskStatusConstants.DiskStatusReleased.value,
        ]:
            return disk
        elif status.status == DiskStatusConstants.DiskStatusFailed.value:
            raise DeploymentNotRunning(f"Disk not running. Status: {status.status}")

        time.sleep(sleep_interval)
        disk = client.get_disk(name)
        status = disk.status

    raise RetriesExhausted(
        f"Retries exhausted: Tried {retry_count} times with {sleep_interval}s interval. Disk: status={status.status}"
    )
