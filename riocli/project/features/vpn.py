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
from riocli.constants import Colors, Symbols
from riocli.project.util import name_to_guid
from riocli.utils.spinner import with_spinner


@click.command(
    'vpn',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('project-name', type=str)
@click.argument('enable', type=bool)
@name_to_guid
@with_spinner()
def vpn(
        project_name: str,
        project_guid: str,
        enable: bool,
        spinner=None,
) -> None:
    """
    Enable or disable VPN on a project

    Example: rio project features vpn "my-project" true
    """
    client = new_v2_client(with_project=False)

    body = {
        "metadata": {
            "projectGUID": project_guid
        },
        "spec": {
            "features": {
                "vpn": enable
            }
        }
    }

    state = 'Enabling' if enable else 'Disabling'
    spinner.text = click.style('{} VPN...'.format(state), fg=Colors.YELLOW)

    try:
        client.update_project(project_guid, body)
        spinner.text = click.style('Done', fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e
