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
import typing

import click
import munch
from click_help_colors import HelpColorsCommand
from munch import unmunchify

from riocli.config import get_config_from_context
from riocli.constants.colors import Colors
from riocli.utils import tabulate_data


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--wide", "-w", is_flag=True, default=False, help="Print more details", type=bool
)
@click.pass_context
def list_oauth2_clients(
    ctx: click.Context,
    wide: bool = False,
) -> None:
    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        oauth2_clients = client.list_oauth2_clients()
        _display_oauth2_client_list(oauth2_clients, wide=wide)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_oauth2_client_list(
    oauth2_clients: typing.List[munch.Munch],
    show_header: bool = True,
    wide: bool = False,
) -> None:
    headers = []
    if show_header:
        headers = ["Client ID", "Client", "Grant Types", "Response Types", "Scope"]
        if wide:
            headers.extend(["Redirect URIs", "Logout Redirect URIs"])

    data = []
    for client in oauth2_clients:
        row = [
            client.client_id,
            client.client_name,
            unmunchify(client.grant_types),
            unmunchify(client.response_types),
            client.scope,
        ]
        if wide:
            row.extend(
                [
                    unmunchify(client.get("redirect_uris", None)),
                    unmunchify(client.get("post_logout_redirect_uris", None)),
                ]
            )

        data.append(row)

    tabulate_data(data, headers)
