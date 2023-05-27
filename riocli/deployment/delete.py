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

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.deployment.util import name_to_guid
from riocli.utils.spinner import with_spinner


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--force', '-f', '--silent', is_flag=True, default=False,
              help='Skip confirmation')
@click.argument('deployment-name', type=str)
@name_to_guid
@with_spinner(text="Deleting deployment...")
def delete_deployment(
        force: bool,
        deployment_name: str,
        deployment_guid: str,
        spinner=None,
) -> None:
    """
    Deletes a deployment
    """
    with spinner.hidden():
        if not force:
            click.confirm(
                'Deleting {} ({}) deployment'.format(
                    deployment_name, deployment_guid), abort=True)

    try:
        client = new_client()
        deployment = client.get_deployment(deployment_guid)
        deployment.deprovision()
        spinner.text = click.style(
            'Deployment deleted successfully.', fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            'Failed to delete deployment: {}'.format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
