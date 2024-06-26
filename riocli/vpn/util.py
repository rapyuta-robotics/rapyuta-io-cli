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
from datetime import datetime, timedelta
import getpass
import json
import os
import socket
import tempfile
from os.path import exists, join
from shutil import move, which
from sys import platform
import time
from typing import Optional

import click
from munch import Munch

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.utils import run_bash, run_bash_with_return_code
from riocli.v2client import Client as v2Client


def get_host_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]


def get_host_name() -> str:
    return socket.gethostname()


def is_linux() -> bool:
    return platform.lower() == 'linux'

def is_windows() -> bool:
    return platform.lower() == 'win32'

def is_curl_installed() -> bool:
    return which('curl') is not None


def is_tailscale_installed() -> bool:
    return which('tailscale') is not None


def is_tailscale_up() -> bool:
    _, code = run_bash_with_return_code('tailscale status')
    return code == 0


def get_tailscale_ip() -> str:
    return run_bash('tailscale ip')


def stop_tailscale() -> bool:
    _, code = run_bash_with_return_code(priviledged_command('tailscale down'))
    if code != 0:
        return False

    output, code = run_bash_with_return_code(priviledged_command('tailscale logout'))
    if code != 0 and 'no nodekey to log out' not in output:
        return False

    return True


def get_tailscale_status() -> dict:
    output, _ = run_bash_with_return_code("tailscale status --json")
    return json.loads(output)


def install_vpn_tools() -> None:
    if is_tailscale_installed():
        return

    click.confirm(
        click.style(
            '{} VPN tools are not installed. Do you want '
            'to install them now?'.format(Symbols.INFO),
            fg=Colors.YELLOW),
        default=True, abort=True)

    if not is_linux():
        click.secho('Only linux is supported', fg=Colors.YELLOW)
        raise SystemExit(1)

    if is_tailscale_installed():
        click.secho('VPN tools already installed', fg=Colors.GREEN)
        return

    if not is_curl_installed():
        click.secho('Please install `curl`', fg=Colors.RED)
        raise SystemExit(1)

    # download the tailscale install script
    run_bash('curl -sLO https://tailscale.com/install.sh')

    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = join(tmp_dir, 'install.sh')

        # move it to the tmp directory
        move('install.sh', script_path)

        if not exists(script_path):
            raise FileNotFoundError

        run_bash('sh {}'.format(script_path))

    if not is_tailscale_installed():
        raise Exception('{} Failed to install VPN tools'.format(Symbols.ERROR))

    click.secho('{} VPN tools installed'.format(Symbols.SUCCESS),
                fg=Colors.GREEN)


def tailscale_ping(tailscale_peer_ip):
    cmd = 'tailscale ping --icmp --tsmp --peerapi {}'.format(tailscale_peer_ip)
    return run_bash_with_return_code(cmd)


def is_vpn_enabled_in_project(client: v2Client, project_guid: str) -> bool:
    project = client.get_project(project_guid)
    return (project.status.status.lower() == 'success' and
            project.status.vpn.lower() == 'success')


def priviledged_command(cmd: str) -> str:
    """Returns an effective command to execute."""
    if is_windows() or (is_linux() and os.geteuid() == 0):
        return cmd

    return 'sudo {}'.format(cmd)


def create_binding(
        ctx: click.Context,
        name: str = '',
        machine: str = '',
        labels: dict = {},
        delta: Optional[timedelta] = None,
        ephemeral: bool = True,
        throwaway: bool = True,
) -> Munch:
    vpn_instance = 'rio-internal-headscale'
    if name == '':
        name = '{}-{}'.format(ctx.obj.machine_id, int(time.time()))

    body = {
        'metadata': {
            'name': name,
            'labels': labels,
        },
        'spec': {
            'instance': vpn_instance,
            'provider': 'headscalevpn',
            'throwaway': throwaway,
            'config': {
                'ephemeral': ephemeral,
                'expirationTime': get_key_expiry_time(delta),
                'nodeKey': machine,
            }
        }
    }

    client = get_config_from_context(ctx).new_v2_client()

    # We may end up creating multiple throwaway tokens in the database.
    # But that's okay and something that we can live with
    binding = client.create_instance_binding(vpn_instance, binding=body)
    return binding.spec.get('environment', {})


def get_key_expiry_time(delta: Optional[timedelta]) -> Optional[str]:
    if delta is None:
        return None

    expiry = datetime.utcnow() + delta
    return expiry.isoformat('T') + 'Z'

def get_binding_labels() -> dict:
    return {
        'creator': 'riocli',
        'hostname': get_host_name(),
        'ip_address': str(get_host_ip()),
        'username': getpass.getuser(),
        'rapyuta.io/internal': 'true',
    }
