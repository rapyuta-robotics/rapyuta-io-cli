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
import functools
from queue import Queue

import click
import requests
from click_help_colors import HelpColorsCommand
from munch import Munch
from rapyuta_io_sdk_v2 import Client
from yaspin.api import Yaspin

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.role.util import fetch_roles
from riocli.utils import tabulate_data
from riocli.utils.execute import apply_func_with_result
from riocli.utils.spinner import with_spinner


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force", "-f", "--silent", is_flag=True, default=False, help="Skip confirmation"
)
@click.option(
    "-a", "--all", "delete_all", is_flag=True, default=False, help="Delete all devices"
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers for deleting devices. Defaults to 10.",
    type=int,
    default=10,
)
@click.argument("role-name-or-regex", type=str, default="")
@click.pass_context
@with_spinner(text="Deleting role...")
def delete_role(
    ctx: click.Context,
    force: bool,
    workers: int,
    role_name_or_regex: str,
    spinner: Yaspin,
    delete_all: bool = False,
) -> None:
    """Delete one or more roles with a name or a regex pattern.

    You can specify a name or a regex pattern to delete one
    or more roles.

    If you want to delete all the roles, then
    simply use the --all flag.

    If you want to delete roles without confirmation, then
    use the --force or --silent or -f

    Usage Examples:

      Delete a role by name

      $ rio role delete ROLE_NAME

      Delete a role without confirmation

      $ rio role delete ROLE_NAME --force

      Delete all role in the project

      $ rio role delete --all

      Delete roles using regex pattern

      $ rio role delete "ROLE.*"
    """
    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client()
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

    if not (role_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        roles = fetch_roles(client, role_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style(f"Failed to delete role(s): {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not roles:
        spinner.text = "Role(s) not found"
        spinner.green.ok(Symbols.SUCCESS)
        return

    headers = ["Name", "Role ID"]
    data = [[r.metadata.name, r.metadata.guid] for r in roles]

    with spinner.hidden():
        tabulate_data(data, headers)

    spinner.write("")

    if not force:
        with spinner.hidden():
            _ = click.confirm("Do you want to delete above role(s)?", abort=True)
        spinner.write("")

    try:
        f = functools.partial(_delete_role, client)
        result = apply_func_with_result(
            f=f, items=roles, workers=workers, key=lambda x: x
        )

        data, fg = [], Colors.GREEN
        success_count, failed_count = 0, 0

        for name, status, response in result:
            if status:
                fg = Colors.GREEN
                icon = Symbols.SUCCESS
                success_count += 1
                msg = ""
            else:
                fg = Colors.RED
                icon = Symbols.ERROR
                failed_count += 1
                msg = get_error_message(response)

            data.append(
                [click.style(name, fg), click.style(icon, fg), click.style(msg, fg)]
            )

        with spinner.hidden():
            tabulate_data(data, headers=["Name", "Status", "Message"])

        spinner.write("")

        if failed_count == 0 and success_count == len(roles):
            spinner_text = click.style(
                f"{len(roles)} role(s) deleted successfully.", Colors.GREEN
            )
            spinner_char = click.style(Symbols.SUCCESS, Colors.GREEN)
        elif success_count == 0 and failed_count == len(roles):
            spinner_text = click.style("Failed to delete role(s)", Colors.YELLOW)
            spinner_char = click.style(Symbols.WARNING, Colors.YELLOW)
        else:
            spinner_text = click.style(
                f"{success_count}/{len(roles)} roles deleted successfully",
                Colors.YELLOW,
            )
            spinner_char = click.style(Symbols.WARNING, Colors.YELLOW)

        spinner.text = spinner_text
        spinner.ok(spinner_char)
        raise SystemExit(failed_count)
    except Exception as e:
        spinner.text = click.style(f"Failed to delete roles: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _delete_role(
    client: Client,
    result: Queue[tuple[str, bool, Munch | requests.Response]],
    role: Munch,
) -> None:
    response = requests.models.Response()
    role_name = role.metadata.name
    try:
        response = client.delete_role(role_name)
        result.put((role_name, True, response))
    except Exception:
        result.put((role_name, False, response))


def get_error_message(response: requests.models.Response) -> str:
    if response.status_code:
        r = response.json()
        return r.get("response", {}).get("error")

    return ""
