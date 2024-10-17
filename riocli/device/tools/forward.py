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
import click
from click_help_colors import HelpColorsCommand

from riocli.constants import Colors
from riocli.device.tools.util import run_tunnel_on_device, run_tunnel_on_local
from riocli.device.util import name_to_guid
from riocli.utils import random_string
from riocli.utils.ssh_tunnel import get_free_tcp_port


@click.command(
    "port-forward",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("remote-port", type=int)
@click.argument("local-port", type=int, default=0, required=False)
@name_to_guid
def port_forward(
    device_name: str, device_guid: str, remote_port: int, local_port: int
) -> None:
    """Forwards a port on the device to local machine."""
    try:
        path = random_string(8, 5)
        if local_port == 0:
            local_port = get_free_tcp_port()
            click.secho("Listening on local port {}".format(local_port))

        run_tunnel_on_device(device_guid=device_guid, remote_port=remote_port, path=path)
        run_tunnel_on_local(local_port=local_port, path=path, background=False)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)
