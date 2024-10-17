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

from riocli.auth.util import get_token, TOKEN_LEVELS
from riocli.config import Configuration
from riocli.constants import Colors
from riocli.exceptions import LoggedOut


@click.command(
    "token",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option("--email", default=None, help="Email of the Rapyuta.io account")
@click.option(
    "--password",
    default=None,
    hide_input=True,
    help="Password for the Rapyuta.io account",
)
@click.option("--level", default=0, help="Level of the token. 0 = low, 1 = med, 2 = high")
def token(email: str, password: str, level: int = 0):
    """Generates a new rapyuta.io auth token.

    There may be times when you just need a new auth token.
    This command will generate a new token for you based on
    the level you specify. The default level is 0. You will
    have to specify a valid email and password.

    The token levels are as follows:
    0 = low, 24 hours
    1 = medium, 7 days
    2 = high, 30 days
    """
    config = Configuration()

    if level not in TOKEN_LEVELS:
        click.secho(
            "Invalid token level. Valid levels are {0}".format(list(TOKEN_LEVELS.keys())),
            fg=Colors.RED,
        )
        raise SystemExit(1)

    if not email:
        email = config.data.get("email_id", None)

    password = password or click.prompt("Password", hide_input=True)

    if not config.exists or not email or not password:
        raise LoggedOut

    new_token = get_token(email, password, level=level)

    click.echo(new_token)
