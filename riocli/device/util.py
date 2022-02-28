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
from pathlib import Path

import click
from rapyuta_io import Client
from rapyuta_io.clients import LogUploads

from riocli.config import new_client
from riocli.utils import is_valid_uuid


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg='red')
            exit(1)

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
            guid = find_device_guid(client, name)

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

    click.secho("device not found", fg='red')
    exit(1)


def name_to_request_id(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg='red')
            exit(1)

        device_guid = kwargs.get('device_guid')
        device = client.get_device(device_id=device_guid)
        requests = device.list_uploaded_files_for_device()

        file_name = kwargs.pop('file_name')

        file_name, request_id = find_request_id(requests, file_name)

        kwargs['file_name'] = file_name
        kwargs['request_id'] = request_id
        f(**kwargs)

    return decorated


def find_request_id(requests: typing.List[LogUploads], file_name: str) -> (str, str):
    for request in requests:
        if request.filename == file_name or request.request_uuid == file_name:
            return request.filename, request.request_uuid

    click.secho("file not found", fg='red')
    exit(1)


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
