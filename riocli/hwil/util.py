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
import time
import typing

import click

from riocli.config import new_hwil_client
from riocli.constants import Colors
from riocli.exceptions import DeviceNotFound
from riocli.hwilclient import Client


def name_to_id(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        try:
            client = new_hwil_client()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1)

        name = kwargs.pop("device_name")

        # device_name is not specified
        if name is None:
            f(**kwargs)
            return

        guid = None
        if guid is None:
            try:
                guid = find_device_id(client, name)
            except Exception as e:
                click.secho(str(e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs["device_name"] = name
        kwargs["device_id"] = guid
        f(**kwargs)

    return decorated


def get_device(client: Client, name: str) -> str:
    devices = client.list_devices()
    for device in devices:
        if device.name == name:
            return device

    raise DeviceNotFound()


def find_device_id(client: Client, name: str) -> str:
    devices = client.list_devices()
    for device in devices:
        if device.name == name:
            return device.id

    raise DeviceNotFound(message="HWIL device not found")


def execute_command(
    client: Client, device_id: int, command: str
) -> typing.Tuple[int, str, str]:
    """Executes a command and waits for it to complete."""
    try:
        response = client.execute_command(device_id, command)
    except Exception as e:
        raise e

    try:
        while response.status == "PENDING":
            response = client.get_command(response.uuid)
            time.sleep(1)
    except Exception as e:
        raise e

    o = response.result.output.pop()

    return o.get("rc"), o.get("stdout"), o.get("stderr")
