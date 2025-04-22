# Copyright 2025 Rapyuta Robotics
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
from yaspin.core import Yaspin

from riocli.config import get_config_from_context
from riocli.constants.colors import Colors
from riocli.constants.symbols import Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument(
    "client-id",
    type=str,
)
@click.option(
    "--force", "-f", "--silent", "force", is_flag=True, help="Skip confirmation"
)
@click.pass_context
@with_spinner(text="Deleting OAuth2 Client...")
def delete_oauth2_client(
    ctx: click.Context, client_id: str, force: bool, spinner: Yaspin
):
    if not force:
        with spinner.hidden():
            click.confirm(
                "Deleting OAuth2 Client {}".format(client_id),
                abort=True,
            )

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        client.delete_oauth2_client(client_id=client_id)
        spinner.text = click.style("OAuth2 Client deleted successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to delete OAuth2 Client: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
