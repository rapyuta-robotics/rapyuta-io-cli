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

import munch

from riocli.deployment.list import DEFAULT_PHASES
from riocli.utils import tabulate_data
from riocli.v2client import Client
from riocli.v2client.enums import DeploymentPhaseConstants

ALL_PHASES = [
    DeploymentPhaseConstants.DeploymentPhaseInProgress,
    DeploymentPhaseConstants.DeploymentPhaseProvisioning,
    DeploymentPhaseConstants.DeploymentPhaseSucceeded,
    DeploymentPhaseConstants.DeploymentPhaseStopped,
]


def fetch_deployments(
    client: Client,
    deployment_name_or_regex: str,
    include_all: bool,
) -> typing.List[munch.Munch]:
    deployments = client.list_deployments(query={"phases": DEFAULT_PHASES})
    result = []
    for deployment in deployments:
        if (
            include_all
            or deployment_name_or_regex == deployment.metadata.name
            or deployment_name_or_regex == deployment.metadata.guid
            or (
                deployment_name_or_regex not in deployment.metadata.name
                and re.search(
                    r"^{}$".format(deployment_name_or_regex), deployment.metadata.name
                )
            )
        ):
            result.append(deployment)

    return result


def print_deployments_for_confirmation(deployments: typing.List[munch.Munch]):
    headers = ["Name", "GUID", "Phase", "Status"]

    data = []
    for deployment in deployments:
        data.append(
            [
                deployment.metadata.name,
                deployment.metadata.guid,
                deployment.status.phase,
                deployment.status.status,
            ]
        )

    tabulate_data(data, headers)
