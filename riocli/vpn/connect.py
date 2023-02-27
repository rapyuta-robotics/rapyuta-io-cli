# Copyright 2023 Rapyuta Robotics
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

import getpass
import time
from datetime import datetime, timedelta

import click
from munch import Munch

from riocli.config import new_v2_client
from riocli.utils import run_bash_with_return_code
from riocli.v2client import Client as v2Client
from riocli.vpn.util import (
    is_tailscale_installed,
    is_tailscale_up,
    stop_tailscale,
    install_vpn_tools,
    get_host_name,
    get_host_ip,
    is_vpn_enabled_in_project
)


@click.command('connect')
@click.pass_context
def connect(ctx: click.Context):
    """
    Connect to the current project's VPN network
    """
    try:
        if not is_tailscale_installed():
            click.confirm(
                click.style('VPN tools are not installed. Do you want '
                            'to install them now?', fg='yellow'),
                default=True, abort=True)
            install_vpn_tools()

        client = new_v2_client()

        if not is_vpn_enabled_in_project(
                client, ctx.obj.data.get('project_id')):
            click.secho('⚠ VPN is not enabled in the project. '
                        'Please ask the organization or project '
                        'creator to enable VPN', fg='yellow')
            raise SystemExit(1)

        if is_tailscale_up():
            click.confirm('The VPN client is already running. '
                          'Do you want to stop it and connect to the VPN of '
                          'the current project?', default=False, abort=True)
            success = stop_tailscale()
            if not success:
                msg = ('❌ Failed to stop tailscale. Please run the following '
                       'commands manually\n sudo tailscale down\n sudo '
                       'tailscale logout')
                click.secho(msg, fg='yellow')
                raise SystemExit(1)

        click.secho('🛈 VPN is enabled in the project ({})'.format(
            ctx.obj.data.get('project_name')), fg='cyan')

        if not start_tailscale(ctx, client):
            click.secho('❌ Failed to connect to the project VPN', fg='red')
            raise SystemExit(1)

        click.secho('✅ You are now connected to the project\'s VPN',
                    fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1) from e


def start_tailscale(ctx: click.Context, client: v2Client) -> bool:
    cmd = ('sudo tailscale up --auth-key={} --login-server={}'
           ' --reset --force-reauth --accept-routes --accept-dns'
           ' --advertise-tags={} --timeout=30s')
    args = generate_tailscale_args(ctx, client)
    command = cmd.format(args.HEADSCALE_PRE_AUTH_KEY,
                         args.HEADSCALE_URL,
                         args.HEADSCALE_ACL_TAG)
    output, code = run_bash_with_return_code(command)
    if code != 0:
        click.secho('❌ Failed to start vpn client', fg='red')
        return False

    return True


def generate_tailscale_args(ctx: click.Context, client: v2Client) -> Munch:
    vpn_instance = 'rio-internal-headscale'
    binding_name = '{}-{}'.format(ctx.obj.machine_id, int(time.time()))

    body = {
        'metadata': {
            'name': binding_name,
            'labels': {
                'creator': 'riocli',
                'hostname': get_host_name(),
                'ip_address': str(get_host_ip()),
                'username': getpass.getuser(),
                'rapyuta.io/internal': 'true',
            }
        },
        'spec': {
            'instance': vpn_instance,
            'provider': 'headscalevpn',
            'config': {
                'ephemeral': True,
                'throwaway': True,
                'expirationTime': get_key_expiry_time(),
            }
        }
    }

    click.secho('⌛ Generating a token to join the network...')
    try:
        # We may end up creating multiple throwaway tokens in the database.
        # But that's okay and something that we can live with
        binding = client.create_instance_binding(vpn_instance, binding=body)
        return binding.spec.environment
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1) from e


def get_key_expiry_time() -> str:
    expiry = datetime.utcnow()
    expiry = expiry + timedelta(minutes=10)
    return expiry.isoformat('T') + 'Z'
