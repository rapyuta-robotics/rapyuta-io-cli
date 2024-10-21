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
from base64 import b64encode

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io.utils import UnauthorizedError

from riocli.constants import Colors, Symbols
from riocli.hwilclient import Client as HwilClient
from riocli.utils.context import get_root_context
from riocli.utils.spinner import with_spinner

HWIL_LOGIN_SUCCESS = click.style(
    "{} Successfully logged into HWIL!".format(Symbols.SUCCESS), fg=Colors.GREEN
)


@click.command(
    "login",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option("--username", help="Username for HWIL API")
@click.option("--password", help="Password for HWIL API")
@click.option(
    "--interactive/--no-interactive",
    "--interactive/--silent",
    is_flag=True,
    type=bool,
    default=True,
    help="Make login interactive",
)
@click.pass_context
def login(
    ctx: click.Context,
    username: str,
    password: str,
    interactive: bool = True,
) -> None:
    """Authenticate with HWIL API.

    This is mandatory to use the HWIL commands and also
    to create virtual devices with the device manifest.

    You can choose to login non-interactively by providing
    --username and --password flags or interactively by
    not providing any flags.
    """
    ctx = get_root_context(ctx)

    if interactive:
        username = username or click.prompt("Username")
        password = password or click.prompt("Password", hide_input=True)

    if not username:
        click.secho(f"{Symbols.ERROR} Username not specified", fg=Colors.RED)
        raise SystemExit(1)

    if not password:
        click.secho(f"{Symbols.ERROR} Password not specified", fg=Colors.RED)
        raise SystemExit(1)

    try:
        validate_and_set_hwil_token(ctx, username, password)
    except Exception as e:
        raise SystemExit(1) from e


@with_spinner(text="Validating credentials...")
def validate_and_set_hwil_token(
    ctx: click.Context, username: str, password: str, spinner=None
) -> None:
    """Validates an auth token."""
    if "environment" in ctx.obj.data:
        os.environ["RIO_CONFIG"] = ctx.obj.filepath

    token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    client = HwilClient(auth_token=token)

    try:
        client.list_devices()
        ctx.obj.data["hwil_auth_token"] = token
        ctx.obj.save()
        spinner.text = click.style("Successfully logged in.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except UnauthorizedError as e:
        spinner.red.text = click.style("Incorrect credentials.", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise e
    except Exception as e:
        spinner.text = click.style(f"Failed to login: {str(e)}", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise e
