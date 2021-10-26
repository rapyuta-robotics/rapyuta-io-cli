# Copyright 2021 Rapyuta Robotics
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
import typing

import click

from rapyuta_io import Client, DeploymentPhaseConstants
from riocli.config import new_client
from riocli.utils.selector import show_selection


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any) -> None:
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg='red')
            exit(1)

        name = kwargs.pop('deployment_name')
        guid = None

        if name.startswith('dep-'):
            guid = name
            name = None

        if name is None:
            name = get_deployment_name(client, guid)

        if guid is None:
            guid = find_deployment_guid(client, name)

        kwargs['deployment_name'] = name
        kwargs['deployment_guid'] = guid
        f(**kwargs)

    return decorated


def get_deployment_name(client: Client, guid: str) -> str:
    deployment = client.get_deployment(guid)
    return deployment.name


def find_deployment_guid(client: Client, name: str) -> str:
    deployments = client.get_all_deployments()
    for deployment in deployments:
        if deployment.name == name:
            return deployment.deploymentId

    click.secho("Deployment not found", fg='red')
    exit(1)


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

    if len(exec_status.metadata) == 1: # If there is a single pod
        pod_name = exec_status.metadata[0].podName
    else:
        pods = [p.podName for p in exec_status.metadata[0]]
        pod_name = show_selection(pods, 'Choose the pod')

    return selected_component.componentID, exec_meta.id, pod_name
