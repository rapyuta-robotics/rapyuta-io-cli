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
import os
import time

import click
from rapyuta_io.clients import LogsUploadRequest

from riocli.config import Configuration, new_client
from riocli.utils import run_bash, random_string
from riocli.utils.execute import run_on_device


def run_tunnel_on_device(device_guid: str, remote_port: int, path: str) -> None:
    config = Configuration()
    run_on_device(
        device_guid=device_guid,
        command=[
            "piping-tunnel",
            "server",
            "--server",
            config.piping_server,
            "--port",
            str(remote_port),
            path,
        ],
        background=True,
    )


def run_tunnel_on_local(local_port: int, path: str, background: bool = False) -> None:
    config = Configuration()
    tunnel = os.path.join(os.path.dirname(config.filepath), "tools", "piping-tunnel")
    command = "{} client --server {} --port {} {}".format(
        tunnel, config.piping_server, local_port, path
    )
    if background:
        command = "{} --progress=false".format(command)
    click.secho(command)
    run_bash(command, bg=background)


def copy_from_device(device_guid: str, src: str, dest: str) -> None:
    file = "{}-{}".format(src, random_string(7, 5)).lstrip("/").replace("/", "-")
    client = new_client()
    device = client.get_device(device_id=device_guid)
    request_uuid = device.upload_log_file(LogsUploadRequest(src, file_name=file))
    while True:
        status = device.get_log_upload_status(request_uuid)
        if status.status not in ["IN PROGRESS", "PENDING"]:
            break

        time.sleep(10)
        continue

    if status.status != "COMPLETED":
        raise Exception(
            "Upload status: {} Error: {}".format(status.status, status.error_message)
        )

    url = device.download_log_file(request_uuid)
    run_bash('curl -o "{}" "{}"'.format(dest, url))


def copy_to_device(device_guid: str, src: str, dest: str) -> None:
    config = Configuration()
    path = random_string(8, 5)
    run_bash("curl -sT {} {}/{}".format(src, config.piping_server, path), bg=True)
    run_on_device(
        device_guid=device_guid,
        command=["curl", "-s", "-o", dest, "{}/{}".format(config.piping_server, path)],
    )
