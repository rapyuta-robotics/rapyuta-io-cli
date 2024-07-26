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
import functools
import json
import re
import typing
from pathlib import Path

import click
from munch import Munch
from rapyuta_io import Client
from rapyuta_io.clients import LogUploads
from rapyuta_io.clients.device import Device
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.config import get_config_from_context, new_client, new_hwil_client
from riocli.config.config import Configuration
from riocli.constants import Colors
from riocli.exceptions import DeviceNotFound
from riocli.hwil.util import execute_command, find_device_id
from riocli.utils import is_valid_uuid, trim_prefix, trim_suffix


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1)

        name = kwargs.pop('device_name')

        # device_name is not specified
        if name is None:
            f(**kwargs)
            return

        guid = None

        if is_valid_uuid(name):
            guid = name
            name = None

        if name is None:
            name = get_device_name(client, guid)

        if guid is None:
            try:
                guid = find_device_guid(client, name)
            except Exception as e:
                click.secho(str(e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs['device_name'] = name
        kwargs['device_guid'] = guid
        f(**kwargs)

    return decorated


def get_device_name(client: Client, guid: str) -> str:
    device = client.get_device(device_id=guid)
    return device.name


def find_device_guid(client: Client, name: str) -> str:
    devices = client.get_all_devices()
    for device in devices:
        if device.name == name:
            return device.uuid

    raise DeviceNotFound()


def name_to_request_id(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1)

        file_name = kwargs.pop('file_name')

        device_guid = kwargs.get('device_guid')
        device = client.get_device(device_id=device_guid)
        requests = device.list_uploaded_files_for_device(filter_by_filename=file_name)

        file_name, request_id = find_request_id(requests, file_name)

        kwargs['file_name'] = file_name
        kwargs['request_id'] = request_id
        f(**kwargs)

    return decorated


def fetch_devices(
        client: Client,
        device_name_or_regex: str,
        include_all: bool,
        online_devices: bool = False
) -> typing.List[Device]:
    devices = client.get_all_devices(online_device=online_devices)
    result = []
    for device in devices:
        if (include_all or device.name == device_name_or_regex or
                device_name_or_regex == device.uuid or
                (device_name_or_regex not in device.name and
                 re.search(r'^{}$'.format(device_name_or_regex), device.name))):
            result.append(device)

    return result


def migrate_device_to_project(ctx: click.Context, device_id: str, dest_project_id: str) -> None:
    config = get_config_from_context(ctx)
    host = config.data.get('core_api_host', 'https://gaapiserver.apps.okd4v2.prod.rapyuta.io')
    url = '{}/api/device-manager/v0/devices/{}/migrate'.format(host, device_id)
    headers = config.get_auth_header()
    payload = {'project': dest_project_id}

    response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload)
    err_msg = 'error in the api call'
    data = json.loads(response.text)

    if not response.ok:
        err_msg = data.get('response', {}).get('error', '')
        raise Exception(err_msg)


def find_request_id(requests: typing.List[LogUploads], file_name: str) -> (str, str):
    for request in requests:
        if request.filename == file_name or request.request_uuid == file_name:
            return request.filename, request.request_uuid

    click.secho("file not found", fg=Colors.RED)
    raise SystemExit(1)


def device_identity(src, devices=[]):
    if is_valid_uuid(src):
        return src
    else:
        for device in devices:
            if device.name == src:
                return device.uuid
    return None


def is_remote_path(src, devices=[]):
    if ":" in src:
        parts = src.split(":")
        if len(parts) == 2:
            if is_valid_uuid(parts[0]):
                return parts[0], Path(parts[1]).absolute().as_posix()
            else:
                for device in devices:
                    if device.name == parts[0]:
                        return device.uuid, Path(parts[1]).absolute().as_posix()
    return None, src


def create_hwil_device(spec: dict, metadata: dict) -> Munch:
    """Create a new hardware-in-the-loop device."""
    virtual = spec['virtual']
    os = virtual['os']
    codename = virtual['codename']
    arch = virtual['arch']
    product = virtual['product']
    name = metadata['name']

    labels = make_hwil_labels(virtual, name)
    device_name = sanitize_hwil_device_name(f"{name}-{product}-{labels['user']}")

    client = new_hwil_client()

    try:
        device_id = find_device_id(client, device_name)
        return client.get_device(device_id)
    except DeviceNotFound:
        pass  # Do nothing and proceed.

    response = client.create_device(device_name, arch, os, codename, labels)
    client.poll_till_device_ready(response.id, sleep_interval=5, retry_limit=12)

    if response.status == 'FAILED':
        raise Exception('device has failed')

    return response


def delete_hwil_device(device: Device) -> None:
    """Delete a hardware-in-the-loop device.

    This is a helper method that deletes a HWIL device
    associated with the rapyuta.io device.
    """
    labels = device.get('labels', {})
    if not labels:
        raise DeviceNotFound(message='hwil device not found')

    device_id = None

    for l in labels:
        if l['key'] == 'hwil_device_id':
            device_id = l['value']
            break

    if device_id is None:
        raise DeviceNotFound(message='hwil device not found')

    client = new_hwil_client()
    client.delete_device(device_id)


def execute_onboard_command(device_id: int, onboard_command: str) -> None:
    """Execute the onboard command on a hardware-in-the-loop device."""
    client = new_hwil_client()
    try:
        code, _, stderr = execute_command(client, device_id, onboard_command)
        if code != 0:
            raise Exception(f"Failed with exit code {code}: {stderr}")
    except Exception as e:
        raise e


def make_hwil_labels(spec: dict, device_name: str) -> typing.Dict:
    data = Configuration().data
    user_email = data['email_id']
    user_email = user_email.split('@')[0]

    labels = {
        "user": user_email,
        "organization": data['organization_id'],
        "project": data['project_id'],
        "product": spec['product'],
        "rapyuta_device_name": device_name,
    }

    if spec.get("highperf", False):
        labels["highperf"] = ""

    return labels


def make_device_labels_from_hwil_device(d: Munch) -> dict:
    return {
        "hwil_device_id": str(d.id),
        "hwil_device_name": d.name,
        "arch": d.architecture,
        "flavor": d.flavor,
        "hwil_device_username": d.username,
    }


def sanitize_hwil_device_name(name):
    if len(name) == 0:
        return name

    name = name[0:50]
    name = trim_suffix(name)
    name = trim_prefix(name)

    r = ''
    for c in name:
        if c.isalnum() or c in ['-', '_']:
            r = r + c

    return r
