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
from functools import wraps, lru_cache
import json
import re
import time
import typing
from datetime import datetime, timedelta
from pathlib import Path

import click
from munch import Munch
from rapyuta_io import Client
from rapyuta_io.clients import LogUploads, SharedURL
from rapyuta_io.clients.device import Device, DeviceStatus
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.config import get_config_from_context, new_client, new_hwil_client
from riocli.config.config import Configuration
from riocli.constants import Colors
from riocli.exceptions import DeviceNotFound
from riocli.hwil.util import execute_command, find_device_id
from riocli.utils import is_valid_uuid, trim_prefix, trim_suffix
from riocli.v2client.util import handle_server_errors


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @wraps(f)
    def decorated(**kwargs: typing.Any):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1)

        name = kwargs.pop("device_name")

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

        kwargs["device_name"] = name
        kwargs["device_guid"] = guid
        f(**kwargs)

    return decorated


def upload_debug_logs(device_guid: str) -> dict:
    config = Configuration()
    coreapi_host = config.data.get(
        "core_api_host", "https://gaapiserver.apps.okd4v2.prod.rapyuta.io"
    )

    url = "{}/api/device-manager/v0/error_handler/upload_debug_logs/{}".format(
        coreapi_host, device_guid
    )

    headers = config.get_auth_header()
    response = (
        RestClient(url).method(HttpMethod.POST).headers(headers).execute(payload={})
    )

    result = handle_server_errors(response)

    if result:
        return result

    return response.json()


def generate_shared_url(device_guid: str, request_id: str, expiry: int, spinner=None):
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        expiry_time = datetime.now() + timedelta(days=expiry)

        # Create the shared URL
        public_url = device.create_shared_url(
            SharedURL(request_id, expiry_time=expiry_time)
        )
        return public_url
    except Exception as e:
        raise Exception(f"Failed to create shared URL: {e}")


def get_device_name(client: Client, guid: str) -> str:
    device = client.get_device(device_id=guid)
    return device.name


@lru_cache
def find_device_guid(client: Client, name: str) -> str:
    devices = client.get_all_devices(device_name=name)
    for device in devices:
        if device.name == name:
            return device.uuid

    raise DeviceNotFound()


def find_device_by_name(client: Client, name: str) -> Device:
    devices = client.get_all_devices(device_name=name)
    if devices:
        return devices[0]

    raise DeviceNotFound()


def name_to_request_id(f: typing.Callable) -> typing.Callable:
    @wraps(f)
    def decorated(**kwargs):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1)

        file_name = kwargs.pop("file_name")

        device_guid = kwargs.get("device_guid")
        device = client.get_device(device_id=device_guid)
        requests = device.list_uploaded_files_for_device(filter_by_filename=file_name)

        file_name, request_id = find_request_id(requests, file_name)

        kwargs["file_name"] = file_name
        kwargs["request_id"] = request_id
        f(**kwargs)

    return decorated


def fetch_devices(
    client: Client,
    device_name_or_regex: str,
    include_all: bool,
    online_devices: bool = False,
) -> typing.List[Device]:
    devices = client.get_all_devices(online_device=online_devices)
    result = []
    for device in devices:
        if (
            include_all
            or device.name == device_name_or_regex
            or device_name_or_regex == device.uuid
            or (
                device_name_or_regex not in device.name
                and re.search(r"^{}$".format(device_name_or_regex), device.name)
            )
        ):
            result.append(device)

    return result


def migrate_device_to_project(
    ctx: click.Context, device_id: str, dest_project_id: str
) -> None:
    config = get_config_from_context(ctx)
    host = config.data.get(
        "core_api_host", "https://gaapiserver.apps.okd4v2.prod.rapyuta.io"
    )
    url = "{}/api/device-manager/v0/devices/{}/migrate".format(host, device_id)
    headers = config.get_auth_header()
    payload = {"project": dest_project_id}

    response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload)
    err_msg = "error in the api call"
    data = json.loads(response.text)

    if not response.ok:
        err_msg = data.get("response", {}).get("error", "")
        raise Exception(err_msg)


def find_request_id(requests: typing.List[LogUploads], file_name: str) -> (str, str):
    for request in requests:
        if request.filename == file_name or request.request_uuid == file_name:
            return request.filename, request.request_uuid

    click.secho("file not found", fg=Colors.RED)
    raise SystemExit(1)


def is_remote_path(src, devices=None):
    devices = devices or []

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


def sanitize_hwil_device_name(name: str) -> str:
    if len(name) == 0:
        return name

    name = name[0:50]
    name = trim_suffix(name)
    name = trim_prefix(name)

    r = ""
    for c in name:
        if c.isalnum() or c in ["-", "_"]:
            r = r + c

    return r


def generate_hwil_device_name(
    name: str,
    product: str,
    user: str,
    project_id: str,
) -> str:
    """Generates a valid hardware-in-the-loop device name."""
    project = project_id.split("project-")[1]
    device_name = f"{name}-{product}-{user}-{project}"
    if not product:
        device_name = f"{name}-{user}-{project}"

    return sanitize_hwil_device_name(device_name)


def create_hwil_device(spec: dict, metadata: dict) -> Munch:
    """Create a new hardware-in-the-loop device."""
    os = spec["os"]
    codename = spec["codename"]
    arch = spec["arch"]
    product = spec.get("product")
    name = metadata["name"]

    labels = make_hwil_labels(spec, name)
    device_name = generate_hwil_device_name(
        name, product, labels["user"], labels["project"]
    )

    client = new_hwil_client()
    device = None

    try:
        device_id = find_device_id(client, device_name)
        device = client.get_device(device_id)
        if device and device.status != "FAILED":
            return device
    except DeviceNotFound:
        pass  # Do nothing and proceed.

    if device and device.status == "FAILED":
        try:
            client.delete_device(device.id)
        except Exception:
            raise Exception("cannot delete previously failed device")

    response = client.create_device(device_name, arch, os, codename, labels)
    client.poll_till_device_ready(response.id, sleep_interval=5, retry_limit=12)

    if response.status == "FAILED":
        raise Exception("device has failed")

    return response


def delete_hwil_device(spec: dict, metadata: dict) -> None:
    """Delete a hardware-in-the-loop device by name."""
    product = spec.get("product")
    name = metadata["name"]
    labels = make_hwil_labels(spec, name)
    device_name = generate_hwil_device_name(
        name, product, labels["user"], labels["project"]
    )

    client = new_hwil_client()
    devices = client.list_devices(query={"name": device_name})
    if not devices:
        return

    client.delete_device(devices[0].id)


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
    user_email = data["email_id"]
    user_email = user_email.split("@")[0]

    labels = {
        "user": user_email,
        "organization": data["organization_id"],
        "project": data["project_id"],
        "rapyuta_device_name": device_name,
        "expiry_after": spec["expireAfter"],
    }

    if "product" in spec:
        labels["product"] = spec["product"]

    return labels


def make_device_labels_from_hwil_device(d: Munch) -> dict:
    return {
        "arch": d.architecture,
        "flavor": d.flavor,
        "hwil_device_id": str(d.id),
        "hwil_device_name": d.name,
        "hwil_device_username": d.username,
    }


def wait_until_online(device: Device, timeout: int = 600) -> None:
    """Wait until the device is online.

    This is a helper method that waits until the device is online.
    Or, until the timeout is reached. The default timeout is 600 seconds.
    """
    counter, interval = 0, 20
    failed_states = (DeviceStatus.FAILED, DeviceStatus.REJECTED)

    device.refresh()

    while (
        not device.is_online()
        and device.status not in failed_states
        and counter < timeout
    ):
        counter += interval
        time.sleep(interval)
        device.refresh()

    if not device.is_online() and counter >= timeout:
        raise Exception("timeout reached while waiting for the device to be online")
