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
from riocli.hwilclient import Client as HwilClient
from click_help_colors import HelpColorsCommand
from riocli.constants import Colors, Symbols
from riocli.utils.context import get_root_context
from base64 import b64encode
from rapyuta_io.utils import UnauthorizedError
from riocli.utils.spinner import with_spinner

HWIL_LOGIN_SUCCESS = click.style('{} Successfully logged into HWIL!'.format(Symbols.SUCCESS), fg=Colors.GREEN)

@click.command(
    'login',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--hwil-user', required=True, help='Username for HWIL login')
@click.option('--hwil-password', required=True, help='Password for HWIL login')

def login(
        ctx: click.Context,
        hwil_user: str,
        hwil_password: str,
) -> None:
    """Log in to HWIL."""

    ctx = get_root_context(ctx)
    try:
        if hwil_user and not hwil_password:
            click.secho('hwil password not specified')

        if hwil_password and not hwil_user:
            click.secho('hwil user not specified')

        if hwil_user and hwil_password:
            if not validate_and_set_hwil_token(ctx, hwil_user, hwil_password):
                raise SystemExit(1)
    except Exception as e:
        click.echo(f"Login failed: {e}")

    ctx.obj.save()

    click.echo(HWIL_LOGIN_SUCCESS)


@with_spinner(text='Validating hwil credentials...')
def validate_and_set_hwil_token(
        ctx: click.Context,
        username: str,
        password: str,
        spinner=None
) -> bool:
    """Validates an auth token."""
    if 'environment' in ctx.obj.data:
        os.environ['RIO_CONFIG'] = ctx.obj.filepath

    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    client = HwilClient(auth_token=token)

    try:
        client.list_devices()
        ctx.obj.data['hwil_auth_token'] = token
        spinner.ok(Symbols.INFO)
        return True
    except UnauthorizedError:
        spinner.text = click.style("incorrect credentials for hwil", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        return False
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        return False