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

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "create",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("name", type=str)
@with_spinner(text="Creating static route...")
def create_static_route(name: str, spinner=None) -> None:
    """Create a new static route

    Please note that the name you provide while creating the
    static route will be suffixed with the organization's
    short guid in the backend. Please run the list command
    to view the name of the static route and inspect it later.
    """
    try:
        client = new_v2_client(with_project=True)
        payload = {"metadata": {"name": name}}
        route = client.create_static_route(payload)
        spinner.text = click.style(
            "Static Route created successfully for URL {}".format(route.spec.url),
            fg=Colors.GREEN,
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to create static route: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e
