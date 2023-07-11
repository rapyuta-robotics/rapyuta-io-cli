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
import copy
import functools
import typing

import click
from rapyuta_io import Client, DeploymentPhaseConstants
from rapyuta_io.clients import Device
from rapyuta_io.clients.package import ExecutableMount
from rapyuta_io.utils import InvalidParameterException, OperationNotAllowedError
from rapyuta_io.utils.constants import DEVICE_ID

from riocli.config import new_client
from riocli.constants import Colors
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


def add_mount_volume_provision_config(provision_config, component_name, device, executable_mounts):
    if not isinstance(device, Device):
        raise InvalidParameterException('device must be of type Device')

    component_id = provision_config.plan.get_component_id(component_name)
    if not isinstance(executable_mounts, list) or not all(
            isinstance(mount, ExecutableMount) for mount in executable_mounts):
        raise InvalidParameterException(
            'executable_mounts must be a list of rapyuta_io.clients.package.ExecutableMount')
    if device.get_runtime() != Device.DOCKER_COMPOSE and not device.is_docker_enabled():
        raise OperationNotAllowedError('Device must be a {} device'.format(Device.DOCKER_COMPOSE))
    component_params = provision_config.parameters.get(component_id)
    if component_params.get(DEVICE_ID) != device.deviceId:
        raise OperationNotAllowedError('Device must be added to the component')
    # self._add_disk_mount_info(device.deviceId, component_id, executable_mounts)

    dep_info = dict()
    dep_info['diskResourceId'] = device.deviceId
    dep_info['applicableComponentId'] = component_id
    dep_info['config'] = dict()

    for mount in executable_mounts:
        exec_mount = {
            'mountPath': mount.mount_path
        }
        if mount.sub_path:
            exec_mount['subPath'] = mount.sub_path
        else:
            exec_mount['subPath'] = '/'

        tmp_info = copy.deepcopy(dep_info)
        tmp_info['config']['mountPaths'] = {
            mount.exec_name: exec_mount,
        }
        provision_config.context['diskMountInfo'].append(tmp_info)

    return provision_config
