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


from datetime import timedelta
import click
from click_help_colors import HelpColorsCommand
from yaspin.api import Yaspin

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.utils import run_bash_with_return_code
from riocli.utils.spinner import with_spinner
from riocli.vpn.util import (
    create_binding,
    get_binding_labels,
    is_tailscale_up,
    priviledged_command,
    stop_tailscale,
    install_vpn_tools,
    is_vpn_enabled_in_project
)

_TAILSCALE_CMD_FORMAT = 'tailscale up --auth-key={} --login-server={} --reset --force-reauth ' \
'--accept-routes --accept-dns --advertise-tags={} --timeout=30s'


@click.command(
    'connect',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
@with_spinner(text="Connecting...")
def connect(ctx: click.Context, spinner: Yaspin):
    """
    Connect to the current project's VPN network
    """
    config = get_config_from_context(ctx)

    try:
        with spinner.hidden():
            install_vpn_tools()

        client = config.new_v2_client()

        if not is_vpn_enabled_in_project(client, config.project_guid):
            spinner.write(
                click.style('{} VPN is not enabled in the project. '
                            'Please ask the organization or project '
                            'creator to enable VPN'.format(Symbols.WAITING),
                            fg=Colors.YELLOW))
            raise SystemExit(1)

        with spinner.hidden():
            if is_tailscale_up():
                click.confirm(
                    '{} The VPN client is already running. '
                    'Do you want to stop it and connect to the VPN of '
                    'the current project?'.format(Symbols.WARNING),
                    default=False, abort=True)
                success = stop_tailscale()
                if not success:
                    msg = (
                        '{} Failed to stop tailscale. Please run the '
                        'following commands manually\n sudo tailscale down\n '
                        'sudo tailscale logout'.format(Symbols.ERROR))
                    click.secho(msg, fg=Colors.YELLOW)
                    raise SystemExit(1)

        spinner.write(
            click.style(
                '{} VPN is enabled in the project ({})'.format(
                    Symbols.INFO, ctx.obj.data.get('project_name')),
                fg=Colors.CYAN))

        if not start_tailscale(ctx, spinner):
            click.secho('{} Failed to connect to the project VPN'.format(
                Symbols.ERROR), fg=Colors.RED)
            raise SystemExit(1)

        spinner.green.text = 'You are now connected to the project\'s VPN'
        spinner.green.ok(Symbols.SUCCESS)
    except click.exceptions.Abort as e:
        spinner.red.text = 'Aborted!'
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e
    except Exception as e:
        spinner.red.text = str(e)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def start_tailscale(ctx: click.Context, spinner: Yaspin) -> bool:
    spinner.text = 'Generating a token to join the network...'

    binding = create_binding(ctx, delta=timedelta(minutes=10), labels=get_binding_labels())
    cmd = _TAILSCALE_CMD_FORMAT.format(binding.HEADSCALE_PRE_AUTH_KEY, binding.HEADSCALE_URL, binding.HEADSCALE_ACL_TAG)
    cmd = priviledged_command(cmd)

    with spinner.hidden():
        _, code = run_bash_with_return_code(cmd)

    if code != 0:
        spinner.write(
            click.style('{} Failed to start vpn client'.format(Symbols.ERROR),
                        fg=Colors.RED))
        return False

    return True


