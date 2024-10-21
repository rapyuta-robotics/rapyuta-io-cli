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

import click

from riocli.device.tools.util import run_tunnel_on_device, run_tunnel_on_local
from riocli.device.util import name_to_guid
from riocli.utils import random_string
from riocli.utils.ssh_tunnel import get_free_tcp_port


@click.command("agent-logs", hidden=True)
@click.argument("device-name", type=str)
@name_to_guid
def rapyuta_agent_logs(device_name: str, device_guid: str) -> None:
    """Stream rapyuta agent logs from the device.

    This is useful for debugging issues with the rapyuta
    agent running on the device.
    """
    try:
        path = random_string(8, 5)
        local_port = get_free_tcp_port()
        run_tunnel_on_device(device_guid=device_guid, remote_port=22, path=path)
        run_tunnel_on_local(local_port=local_port, path=path, background=True)
        os.system(
            "ssh -p {} -o StrictHostKeyChecking=no root@localhost tail -f /var/log/salt/minion".format(
                local_port
            )
        )
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)
