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
from click_help_colors import HelpColorsGroup
from click_spinner import spinner

from rapyuta_io import DeviceConfig
from riocli.config import new_client
from riocli.device.util import name_to_guid


@click.group(
    'config',
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def device_config() -> None:
    """
    Device Configuration Variables
    """
    pass


@device_config.command('list')
@click.argument('device-name', type=str)
@name_to_guid
def list_config(device_name: str, device_guid: str) -> None:
    """
    List all the config variables on the Device
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        config_variables = device.get_config_variables()
        _display_config_list(config_variables, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_config.command('create')
@click.argument('device-name', type=str)
@click.argument('key', type=str)
@click.argument('value', type=str)
@name_to_guid
def create_config(device_name: str, device_guid: str, key: str, value: str) -> None:
    """
    Create a new config variable on the Device
    """
    try:
        with spinner():
            client = new_client()
            device = client.get_device(device_id=device_guid)
            device.add_config_variable(key, value)
        click.secho('Config Variable added successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_config.command('update')
@click.argument('device-name', type=str)
@click.argument('key', type=str)
@click.argument('value', type=str)
@name_to_guid
def update_config(device_name: str, device_guid: str, key: str, value: str) -> None:
    """
    Update the config variable on the Device
    """
    try:
        with spinner():
            _update_config_variable(device_guid, key, value)
        click.secho('Config variable updated successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_config.command('delete')
@click.argument('device-name', type=str)
@click.argument('key', type=str)
@name_to_guid
def delete_config(device_name: str, device_guid: str, key: str) -> None:
    """
    Delete the config variable on the Device
    """
    try:
        with spinner():
            _delete_config_variable(device_guid, key)
        click.secho('Config variable deleted successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_config_list(config_variables: typing.List[DeviceConfig], show_header: bool = True) -> None:
    if show_header:
        click.echo(click.style("{:40} {:40}".format('Key', 'Value'), fg='yellow'))

    for cfg in config_variables:
        click.echo("{:40} {:40}".format(cfg.key, cfg.value))


def _update_config_variable(device_guid: str, key: str, value: str) -> None:
    client = new_client()
    device = client.get_device(device_id=device_guid)
    config_variable = _find_config_variable(device.get_config_variables(), key)
    config_variable.value = value
    device.update_config_variable(config_variable)


def _delete_config_variable(device_guid: str, key: str) -> None:
    client = new_client()
    device = client.get_device(device_id=device_guid)
    config_variable = _find_config_variable(device.get_config_variables(), key)
    device.delete_config_variable(config_variable.id)


def _find_config_variable(config_variables: typing.List[DeviceConfig], key: str) -> DeviceConfig:
    for cfg in config_variables:
        if cfg.key == key:
            return cfg

    raise Exception('Config variable not found')
