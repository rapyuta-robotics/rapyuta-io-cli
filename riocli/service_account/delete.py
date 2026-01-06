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
from yaspin.api import Yaspin

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.constants.symbols import Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("account-name", type=str)
@click.option(
    "--force",
    "-f",
    "--silent",
    "force",
    is_flag=True,
    default=False,
    help="Skip confirmation",
)
@with_spinner(text="Deleting package(s)...")
def delete_service_acc(
    account_name: str,
    spinner: Yaspin = None,
    force: bool = False,
):
    """
    Delete a service account.
    """
    if not force:
        with spinner.hidden():
            click.confirm(
                "Do you want to delete the above service account(s)?", abort=True
            )
        spinner.write("")
    try:
        client = new_v2_client()
        client.delete_service_account(name=account_name)

        spinner.text = click.style(f"Service account {account_name} deleted.")
        spinner.ok(click.style(Symbols.SUCCESS, Colors.GREEN))
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e
