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
import copy
import functools
import re
import typing
from typing import List

import click
from rapyuta_io import Client, DeploymentPhaseConstants
from rapyuta_io.clients import Device
from rapyuta_io.clients.deployment import Deployment
from rapyuta_io.clients.package import ExecutableMount
from rapyuta_io.utils import InvalidParameterException, OperationNotAllowedError
from rapyuta_io.utils.constants import DEVICE_ID

from riocli.config import new_client
from riocli.constants import Colors
from riocli.deployment.errors import ERRORS
from riocli.utils import tabulate_data
from riocli.utils.selector import show_selection


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any) -> None:
        try:
            client = new_client()
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
                guid = find_deployment_guid(client, name)
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1) from e

        kwargs['deployment_name'] = name
        kwargs['deployment_guid'] = guid
        f(**kwargs)

    return decorated


def get_deployment_name(client: Client, guid: str) -> str:
    deployment = client.get_deployment(guid)
    return deployment.name


def find_deployment_guid(client: Client, name: str) -> str:
    find_func = functools.partial(client.get_all_deployments,
                                  phases=[DeploymentPhaseConstants.SUCCEEDED,
                                          DeploymentPhaseConstants.PROVISIONING])
    deployments = find_func()
    for deployment in deployments:
        if deployment.name == name:
            return deployment.deploymentId

    raise DeploymentNotFound()


def select_details(deployment_guid, component_name=None, exec_name=None) -> (str, str, str):
    client = new_client()
    deployment = client.get_deployment(deployment_guid)
    if deployment.phase != DeploymentPhaseConstants.SUCCEEDED.value:
        raise Exception('Deployment is not in succeeded phase')

    if component_name is None:
        components = [c.name for c in deployment.componentInfo]
        component_name = show_selection(components, 'Choose the component')

    for component in deployment.componentInfo:
        if component.name == component_name:
            selected_component = component

    if exec_name is None:
        executables = [e.name for e in selected_component.executableMetaData]
        exec_name = show_selection(executables, 'Choose the executable')

    for executable in selected_component.executableMetaData:
        if executable.name == exec_name:
            exec_meta = executable

    for executable in selected_component.executablesStatusInfo:
        if executable.id == exec_meta.id:
            exec_status = executable

    if len(exec_status.metadata) == 1:  # If there is a single pod
        pod_name = exec_status.metadata[0].podName
    else:
        pods = [p.podName for p in exec_status.metadata[0]]
        pod_name = show_selection(pods, 'Choose the pod')

    return selected_component.componentID, exec_meta.id, pod_name


class DeploymentNotFound(Exception):
    def __init__(self, message='deployment not found!'):
        self.message = message
        super().__init__(self.message)

def fetch_deployments(
        client: Client,
        deployment_name_or_regex: str,
        include_all: bool,
) -> List[Deployment]:
    deployments = client.list_deployments()
    result = []
    for deployment in deployments:
        if (include_all or deployment_name_or_regex == deployment.metadata.name or
                deployment_name_or_regex == deployment.metadata.guid or
                (deployment_name_or_regex not in deployment.metadata.name and
                 re.search(r'^{}$'.format(deployment_name_or_regex), deployment.metadata.name))):
            result.append(deployment)

    return result


def print_deployments_for_confirmation(deployments: List[Deployment]):
    headers = ['Name', 'GUID', 'Phase', 'Status']

    data = []
    for deployment in deployments:
        data.append([deployment.metadata.name, deployment.metadata.guid, deployment.status.phase, deployment.status.status])

    tabulate_data(data, headers)


def process_deployment_errors(errors: List, no_action: bool = False) -> str:
    err_fmt = '[{}] {}\nAction: {}'
    support_action = ('Report the issue together with the relevant'
                      ' details to the support team')

    action, description = '', ''
    msgs = []
    for code in errors:
        if code in ERRORS:
            description = ERRORS[code]['description']
            action = ERRORS[code]['action']
        elif code.startswith('DEP_E2'):
            description = 'Internal rapyuta.io error in the components deployed on cloud'
            action = support_action
        elif code.startswith('DEP_E3'):
            description = 'Internal rapyuta.io error in the components deployed on a device'
            action = support_action
        elif code.startswith('DEP_E4'):
            description = 'Internal rapyuta.io error'
            action = support_action

        code = click.style(code, fg=Colors.YELLOW)
        description = click.style(description, fg=Colors.RED)
        action = click.style(action, fg=Colors.GREEN)

        if no_action:
            msgs.append('{}: {}'.format(code, description, ''))
        else:
            msgs.append(err_fmt.format(code, description, action))

    return '\n'.join(msgs)
