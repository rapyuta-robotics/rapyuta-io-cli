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
import functools
import re
import typing

import click
from rapyuta_io import DeploymentPhaseConstants
from rapyuta_io.clients.deployment import Deployment

from riocli.config import new_client, new_v2_client
from riocli.constants import Colors
from riocli.deployment.list import DEFAULT_PHASES
from riocli.utils import tabulate_data
from riocli.utils.selector import show_selection
from riocli.v2client import Client
from riocli.v2client.enums import DeploymentPhaseConstants

ALL_PHASES = [
    DeploymentPhaseConstants.DeploymentPhaseInProgress,
    DeploymentPhaseConstants.DeploymentPhaseProvisioning,
    DeploymentPhaseConstants.DeploymentPhaseSucceeded,
    DeploymentPhaseConstants.DeploymentPhaseStopped,
]


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any) -> None:
        try:
            client = new_v2_client()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1) from e

        name = kwargs.pop('deployment_name')
        guid = None

        if name.startswith('dep-'):
            guid = name
            name = None

        try:
            if name is None:
                name = get_deployment_name(client, guid)

            if guid is None:
                guid = get_deployment_guid(client, name)

        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1) from e

        kwargs['deployment_name'] = name
        kwargs['deployment_guid'] = guid
        f(**kwargs)

    return decorated


def get_deployment_guid(client: Client, name: str) -> str:
    deployment = client.get_deployment(name)
    return deployment.metadata.guid


def get_deployment_name(client: Client, guid: str) -> str:
    deployments = client.list_deployments(query={'guids': [guid]})
    if len(deployments) == 0:
        raise DeploymentNotFound

    return deployments[0].metadata.name

def fetch_deployments(
        client: Client,
        deployment_name_or_regex: str,
        include_all: bool,
) -> typing.List[Deployment]:
    deployments = client.list_deployments(query={'phases': DEFAULT_PHASES})
    result = []
    for deployment in deployments:
        if (include_all or deployment_name_or_regex == deployment.metadata.name or
                deployment_name_or_regex == deployment.metadata.guid or
                (deployment_name_or_regex not in deployment.metadata.name and
                 re.search(r'^{}$'.format(deployment_name_or_regex), deployment.metadata.name))):
            result.append(deployment)

    return result


def print_deployments_for_confirmation(deployments: typing.List[Deployment]):
    headers = ['Name', 'GUID', 'Phase', 'Status']

    data = []
    for deployment in deployments:
        data.append(
            [deployment.metadata.name, deployment.metadata.guid, deployment.status.phase,
             deployment.status.status])

    tabulate_data(data, headers)
