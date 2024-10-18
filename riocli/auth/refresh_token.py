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

from riocli.auth.util import get_token, api_refresh_token
from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.exceptions import LoggedOut


@click.command(
    "refresh-token",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
@click.option("--password", type=str, help="Password for the rapyuta.io account")
@click.option(
    "--interactive/--no-interactive",
    "--interactive/--silent",
    is_flag=True,
    type=bool,
    default=True,
    help="Make login interactive",
)
def refresh_token(ctx: click.Context, password: str, interactive: bool):
    """Refreshes the authentication token.

    If the stores auth token has expired, this command will prompt the
    user to enter the password to refresh the token.
    """
    config = get_config_from_context(ctx)
    email = config.data.get("email_id", None)

    try:
        if not config.exists or email is None:
            raise LoggedOut
    except LoggedOut as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

    click.secho(f"Refreshing token for {email}...", fg=Colors.YELLOW)

    existing_token = config.data.get("auth_token")
    refreshed = api_refresh_token(existing_token)
    if not refreshed:
        if not interactive and password is None:
            click.secho(
                "The existing token has expired, re-run rio auth refresh-token "
                "in interactive mode or pass the password using the flag."
            )
            raise SystemExit(1)

        password = password or click.prompt("Password", hide_input=True)
        refreshed = get_token(email, password)

    ctx.obj.data["auth_token"] = refreshed
    ctx.obj.save()

    click.secho(
        "{} Token refreshed successfully!".format(Symbols.SUCCESS), fg=Colors.GREEN
    )
