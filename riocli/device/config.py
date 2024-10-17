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
import typing

import click
from click_help_colors import HelpColorsCommand
from click_help_colors import HelpColorsGroup
from rapyuta_io import DeviceConfig

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.device.util import name_to_guid
from riocli.utils import tabulate_data
from riocli.utils.spinner import with_spinner


@click.group(
    "config",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def device_config() -> None:
    """
    Device Configuration Variables
    """
    pass


@device_config.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
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
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@device_config.command(
    "create",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("key", type=str)
@click.argument("value", type=str)
@name_to_guid
@with_spinner(text="Creating new config variable...")
def create_config(
    device_name: str,
    device_guid: str,
    key: str,
    value: str,
    spinner=None,
) -> None:
    """
    Create a new config variable on the device
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        device.add_config_variable(key, value)
        spinner.text = click.style("Config variable added successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to add config variable: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@device_config.command(
    "update",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("key", type=str)
@click.argument("value", type=str)
@name_to_guid
@with_spinner(text="Updating config variable...")
def update_config(
    device_name: str,
    device_guid: str,
    key: str,
    value: str,
    spinner=None,
) -> None:
    """
    Update the config variable on the device
    """
    try:
        _update_config_variable(device_guid, key, value)
        spinner.text = click.style(
            "Config variable updated successfully.", fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to update config variable: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@device_config.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("key", type=str)
@name_to_guid
@with_spinner(text="Deleting config variable...")
def delete_config(device_name: str, device_guid: str, key: str, spinner=None) -> None:
    """
    Delete the config variable on the device
    """
    try:
        _delete_config_variable(device_guid, key)
        spinner.text = click.style(
            "Config variable deleted successfully.", fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to delete config variable: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _display_config_list(
    config_variables: typing.List[DeviceConfig], show_header: bool = True
) -> None:
    headers = []
    if show_header:
        headers = ("Key", "Value")

    data = [[c.key, c.value] for c in config_variables]

    tabulate_data(data, headers)


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


def _find_config_variable(
    config_variables: typing.List[DeviceConfig], key: str
) -> DeviceConfig:
    for cfg in config_variables:
        if cfg.key == key:
            return cfg

    raise Exception("Config variable not found")
