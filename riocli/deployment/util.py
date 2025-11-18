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

from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2.models import Deployment

from riocli.deployment.list import DEFAULT_PHASES
from riocli.utils import process_errors, tabulate_data
from riocli.utils.enums import DeploymentPhaseConstants
from riocli.utils.error import DeploymentNotRunning, ImagePullError, RetriesExhausted

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
) -> list:
    deployments = client.list_deployments(phases=DEFAULT_PHASES)
    result = []
    for deployment in deployments.items:
        if (
            include_all
            or deployment_name_or_regex == deployment.metadata.name
            or deployment_name_or_regex == deployment.metadata.guid
            or (
                deployment_name_or_regex not in deployment.metadata.name
                and re.search(rf"^{deployment_name_or_regex}$", deployment.metadata.name)
                and re.search(rf"^{deployment_name_or_regex}$", deployment.metadata.name)
            )
        ):
            result.append(deployment)

    return result


def print_deployments_for_confirmation(deployments: list[Deployment]):
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


def poll_deployment(
    client: Client,
    name: str,
    retry_count: int = 50,
    sleep_interval: int = 6,
    ready_phases: list[str] = None,
):
    if ready_phases is None:
        ready_phases = []

    deployment = client.get_deployment(name=name)
    status = deployment.status

    for _ in range(retry_count):
        if status.phase in ready_phases:
            return deployment

        if status.phase == DeploymentPhaseConstants.DeploymentPhaseProvisioning.value:
            errors = status.error_codes or []
            if "DEP_E153" in errors:
                raise ImagePullError(
                    f"Deployment not running. Phase: Provisioning Status: {status.phase}"
                )
        elif status.phase == DeploymentPhaseConstants.DeploymentPhaseSucceeded.value:
            return deployment
        elif status.phase == DeploymentPhaseConstants.DeploymentPhaseStopped.value:
            raise DeploymentNotRunning(
                f"Deployment not running. Phase: Stopped  Status: {status.phase}"
            )

        time.sleep(sleep_interval)
        deployment = client.get_deployment(name=name)
        status = deployment.status

    msg = (
        f"Retries exhausted: Tried {retry_count} times with {sleep_interval}s interval. "
        f"Deployment: phase={status.phase} status={status.status} \n"
        f"{process_errors(status.error_codes or [])}"
    )
    raise RetriesExhausted(msg)
