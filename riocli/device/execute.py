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
import typing

import click

from riocli.device.util import name_to_guid
from riocli.utils.execute import run_on_device


@click.command('execute')
@click.option('--user', default='root')
@click.option('--shell', default='/bin/bash')
@click.argument('device-name', type=str)
@click.argument('command', nargs=-1)
@name_to_guid
def execute_command(device_name: str, device_guid: str, user: str, shell: str, command: typing.List[str]):
    """
    Execute commands on the Device
    """
    try:
        response = run_on_device(device_guid=device_guid, user=user, shell=shell, command=command, background=False)
        click.secho(response)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

