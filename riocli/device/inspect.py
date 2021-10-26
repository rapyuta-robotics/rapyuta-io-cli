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
import click
import typing
from rapyuta_io.clients import Device

from riocli.config import new_client
from riocli.device.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type',
              type=click.Choice(['json', 'yaml'], case_sensitive=False), default='yaml')
@click.argument('device-name', type=str)
@name_to_guid
def inspect_device(format_type: str, device_name: str, device_guid: str) -> None:
    """
    Inspect the device resource
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        data = make_device_inspectable(device)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')


def make_device_inspectable(device: Device) -> dict:
    blacklist_attr = ['deviceId', 'config_variables']
    device_data = remove_non_inspecting_attributes(device, blacklist_attr)
    return device_data


def remove_non_inspecting_attributes(device: Device, blacklist: typing.List[str]) -> dict:
    device_response = dict(device)
    for key in device_response.keys():
        if key.startswith('_') or key in blacklist:
            if key == 'config_variables':
                for config_var in device_response['config_variables']:
                    config_var.pop('id')
            else:
                device_response.pop(key)
    return device_response
