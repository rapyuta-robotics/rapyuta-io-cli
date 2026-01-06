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

from munch import Munch
from rapyuta_io_sdk_v2 import Client

from riocli.utils import process_errors, tabulate_data
from riocli.utils.enums import DeploymentPhaseConstants
from riocli.utils.error import DeploymentNotRunning, ImagePullError, RetriesExhausted


def fetch_networks(
    client: Client,
    network_name_or_regex: str,
    network_type: str,
    include_all: bool,
) -> list:
    if network_type:
        networks = client.list_networks(network_type=network_type)
    else:
        networks = client.list_networks()

    if include_all:
        return list(networks.items)

    result = []
    for n in networks.items:
        if re.search(network_name_or_regex, n.metadata.name):
            result.append(n)

    return result


def print_networks_for_confirmation(networks: list[Munch]) -> None:
    headers = ["Name", "Type"]
    data = [[n.metadata.name, n.spec.type] for n in networks]
    tabulate_data(data, headers)


def poll_network(
    client: Client,
    name: str,
    retry_count: int = 50,
    sleep_interval: int = 6,
    ready_phases: list[str] = None,
):
    if ready_phases is None:
        ready_phases = []

    network = client.get_network(name=name)
    status = network.status

    for _ in range(retry_count):
        if status.phase in ready_phases:
            return network

        if status.phase == DeploymentPhaseConstants.DeploymentPhaseProvisioning.value:
            errors = status.errorCodes or []
            if "DEP_E153" in errors:
                raise ImagePullError(
                    f"Network not running. Phase: Provisioning Status: {status.phase}"
                )
        elif status.phase == DeploymentPhaseConstants.DeploymentPhaseSucceeded.value:
            return network
        elif status.phase == DeploymentPhaseConstants.DeploymentPhaseStopped.value:
            raise DeploymentNotRunning(
                f"Network not running. Phase: Stopped  Status: {status.phase}"
            )

        time.sleep(sleep_interval)
        network = client.get_network(name)
        status = network.status

    msg = (
        f"Retries exhausted: Tried {retry_count} times with {sleep_interval}s interval. "
        f"Network: phase={status.phase} status={status.status} \n"
        f"{process_errors(status.errorCodes or [])}"
    )
    raise RetriesExhausted(msg)
