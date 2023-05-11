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
import os

import click
import typing

from riocli.deployment.util import name_to_guid, select_details
from riocli.utils.execute import run_on_cloud


@click.command('execute')
@click.option('--component', 'component_name', default=None)
@click.option('--exec', 'exec_name', default=None)
@click.argument('deployment-name', type=str)
@click.argument('command', nargs=-1)
@name_to_guid
def execute_command(component_name: str, exec_name: str, deployment_name: str, deployment_guid: str, command: typing.List[str]) -> None:
    """
    Execute commands on cloud deployment
    """
    try:
        comp_id, exec_id, pod_name = select_details(deployment_guid, component_name, exec_name)
        stdout, stderr = run_on_cloud(deployment_guid, comp_id, exec_id, pod_name, command)
        if stderr:
            click.secho(stderr, fg='red')
        if stdout:
            click.secho(stdout, fg='yellow')
    except Exception as e:
        click.secho(e, fg='red')
        raise SystemExit(1)