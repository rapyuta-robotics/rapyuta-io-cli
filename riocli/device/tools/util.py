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
from shlex import join

import click
from rapyuta_io.clients import LogsUploadRequest, Command

from riocli.config import Configuration, new_client
from riocli.constants import Colors
from riocli.utils import run_bash, random_string
from riocli.utils.execute import run_on_device
from riocli.device.execute import execute_async


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


def copy_to_device(
    device_guid: str,
    device_name: str,
    src: str,
    dest: str,
    run_async: bool = False,
    timeout: int = 600,
) -> None:
    """Copy a local file to the device.

    Reuses async command execution logic from execute.py to avoid duplication.

    Steps:
      1. Start background upload (local -> piping server) via curl -T.
      2. Execute curl on device to download file to destination path.
      3. If run_async=True, delegate streaming to execute_async from execute.py.
         (We allow empty output as success; execute_async may raise if device returns nothing.)
      4. If run_async=False, perform synchronous execution and print output if any.

    Note: File transfer command (curl -s -o) typically produces no stdout on success.
          We treat empty output as success for sync mode.
    """
    config = Configuration()
    path = random_string(8, 5)
    remote_cmd = f"curl -s -o {dest} {config.piping_server}/{path} && echo '__RIO_COPY_SUCCESS__'"

    # Start background upload from local machine to piping server.
    run_bash(f"curl -sT {src} {config.piping_server}/{path}", bg=True)

    client = new_client()
    # Build command similarly to execute.py (bash -c wrapping) for consistency.
    cmd_obj = Command(
        cmd=join(("bash", "-c", remote_cmd)),
        shell="/bin/bash",
        bg=False,
        run_async=run_async,
        runas="root",
        timeout=timeout,
    )

    try:
        if run_async:
            # Delegates execution + streaming to existing async helper
            execute_async(
                client=client,
                device_guids=[device_guid],
                device_dict={device_guid: device_name},
                command=cmd_obj,
                timeout=timeout,
            )
        else:
            # Synchronous execution: directly invoke execute_command and print output
            result = client.execute_command(
                device_ids=[device_guid],
                command=cmd_obj,
                timeout=timeout,
            )
            output = result.get(device_guid, "")
            click.secho(f">>> {device_name}({device_guid})", fg=Colors.YELLOW)
            if output:
                click.echo(f"{output}\n")
            # Empty output is normal for quiet curl success
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e
