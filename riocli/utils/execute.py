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
import json
import typing

import click

from rapyuta_io import Command
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod
from riocli.config import Configuration, new_client

_CLOUD_RUN_REMOTE_COMMAND = '{}/serviceinstance/{}/cmd'


def run_on_cloud(deployment_guid: str, comp_id: str, exec_id: str, pod_name: str, command: typing.List[str]) -> (str, str):
    """
    run_on_cloud uses the RunCommand API of the IOBroker to execute arbitrary commands on the cloud deployment
    containers.
    """
    config = Configuration()
    rest = RestClient(_run_cloud_url(config, deployment_guid)).headers(config.get_auth_header()).method(HttpMethod.PUT)
    resp = rest.execute(payload=_run_cloud_data(comp_id, exec_id, pod_name, command))
    data = json.loads(resp.text)
    click.secho(data)
    if 'err' in data and data['err']:
        raise Exception(data['err'])

    return data['stdout'], data['stderr']


def _run_cloud_data(comp_id: str, exec_id: str, pod_name: str, command: typing.List[str]) -> dict:
    return {
        'componentId': comp_id,
        'executableId': exec_id,
        'podName': pod_name,
        'command': command,
    }


def _run_cloud_url(config: Configuration, deployment_guid: str) -> str:
    host = config.data.get('catalog_host', 'https://gacatalog.apps.rapyuta.io')
    return _CLOUD_RUN_REMOTE_COMMAND.format(host, deployment_guid)


def run_on_device(
        device_guid: str,
        command: typing.List[str],
        user: str = 'root',
        shell: str = '/bin/bash',
        background: bool = False,
) -> str:
    client = new_client()
    device = client.get_device(device_id=device_guid)
    cmd = ' '.join(command)
    return device.execute_command(Command(cmd, shell=shell, bg=background, runas=user))
