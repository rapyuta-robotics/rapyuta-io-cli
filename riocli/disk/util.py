# Copyright 2023 Rapyuta Robotics
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
import typing
import re

from rapyuta_io import Client
from rapyuta_io.clients.persistent_volumes import DiskCapacity, DiskType
from rapyuta_io.utils.rest_client import RestClient, HttpMethod

from riocli.config import Configuration, new_client
from riocli.constants import Colors, Symbols
from riocli.disk.model import Disk
from riocli.utils import tabulate_data

class DiskNotFound(Exception):
    def __init__(self):
        super().__init__('Disk not found')


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

def is_disk_ready(client: Client , name: str) -> bool:
    disk = client.get_disk(name)
    return disk.status.get("status", "") == "Available"

def display_disk_list(disks: typing.Any, show_header: bool = True):
    headers = []
    if show_header:
        headers = (
            'Disk ID', 'Name', 'Status', 'Capacity',
            'Used', 'Available', 'Used By',
        )

    data = [[d.metadata.guid,
             d.metadata.name,
             d.status.get("status"),
             d.spec.capacity,
             d.spec.get("CapacityUsed"),
             d.spec.get("CapacityAvailable"),
             d.get("diskBound", {}).get("DeploymentName")]
            for d in disks]

    tabulate_data(data, headers)