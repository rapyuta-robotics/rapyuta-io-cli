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
from munch import unmunchify

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.utils import inspect_with_format


@click.command(
    'inspect',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('deployment-name')
def inspect_deployment(
        format_type: str,
        deployment_name: str,
) -> None:
    """
    Inspect the deployment resource
    """
    try:
        client = new_v2_client()
        deployment_obj = client.get_deployment(deployment_name)

        if not deployment_obj:
            click.secho("deployment not found", fg='red')
            raise SystemExit(1)

        inspect_with_format(unmunchify(deployment_obj), format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)
