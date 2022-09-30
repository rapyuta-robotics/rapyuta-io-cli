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

from rapyuta_io import Label
from riocli.config import new_client
from riocli.device.util import name_to_guid


@click.group(
    'labels',
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def device_labels() -> None:
    """
    Device Labels
    """
    pass


@device_labels.command('list')
@click.argument('device-name', type=str)
@name_to_guid
def list_labels(device_name: str, device_guid: str) -> None:
    """
    List all the labels for the Device
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        labels = device.get_labels()
        _display_label_list(labels, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


@device_labels.command('create')
@click.argument('device-name', type=str)
@click.argument('key', type=str)
@click.argument('value', type=str)
@name_to_guid
def create_label(device_name: str, device_guid: str, key: str, value: str) -> None:
    """
    Create a label for the Device
    """
    try:
        with spinner():
            client = new_client()
            device = client.get_device(device_id=device_guid)
            device.add_label(key, value)
        click.secho('Label added successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


@device_labels.command('update')
@click.argument('device-name', type=str)
@click.argument('key', type=str)
@click.argument('value', type=str)
@name_to_guid
def update_label(device_name: str, device_guid: str, key: str, value: str) -> None:
    """
    Update the label for the Device
    """
    try:
        with spinner():
            _update_label(device_guid, key, value)
        click.secho('Label updated successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


@device_labels.command('delete')
@click.argument('device-name', type=str)
@click.argument('key', type=str)
@name_to_guid
def delete_label(device_name: str, device_guid: str, key: str) -> None:
    """
    Delete the label for the Device
    """
    try:
        with spinner():
            _delete_label(device_guid, key)
        click.secho('Label deleted successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


def _display_label_list(labels: typing.List[Label], show_header: bool = True) -> None:
    if show_header:
        click.echo(click.style("{:40} {:40}".format('Key', 'Value'), fg='yellow'))

    for label in labels:
        click.echo("{:40} {:40}".format(label.key, label.value))


def _update_label(device_guid: str, key: str, value: str) -> None:
    client = new_client()
    device = client.get_device(device_id=device_guid)
    label = _find_label(device.get_labels(), key)
    label.value = value
    device.update_label(label)


def _delete_label(device_guid: str, key: str) -> None:
    client = new_client()
    device = client.get_device(device_id=device_guid)
    label = _find_label(device.get_labels(), key)
    device.delete_label(label.id)


def _find_label(labels: typing.List[Label], key: str) -> Label:
    for label in labels:
        if label.key == key:
            return label

    raise Exception('Label not found')
