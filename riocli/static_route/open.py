# Copyright 2023 Rapyuta Robotics
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
from riocli.constants import Colors


@click.command(
    'open',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('static-route', type=str)
def open_static_route(static_route) -> None:
    """
    Opens the static route in the default browser
    """
    try:
        client = new_v2_client()
        route = client.get_static_route(static_route)
        click.launch(url='https://{}'.format(route.spec.url), wait=False)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)
