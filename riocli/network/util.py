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
from typing import List

from munch import Munch

from riocli.network.model import Network
from riocli.utils import tabulate_data
from riocli.v2client import Client


def fetch_networks(
    client: Client,
    network_name_or_regex: str,
    network_type: str,
    include_all: bool,
) -> List[Network]:
    if network_type:
        networks = client.list_networks(query={"network_type": network_type})
    else:
        networks = client.list_networks()

    if include_all:
        return list(networks)

    result = []
    for n in networks:
        if re.search(network_name_or_regex, n.metadata.name):
            result.append(n)

    return result


def print_networks_for_confirmation(networks: List[Munch]) -> None:
    headers = ["Name", "Type"]
    data = [[n.metadata.name, n.spec.type] for n in networks]
    tabulate_data(data, headers)
