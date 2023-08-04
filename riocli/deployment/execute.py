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
import sys
import typing

import click
from click_help_colors import HelpColorsCommand

if sys.stdout.isatty():
    from yaspin import kbi_safe_yaspin as Spinner
else:
    from riocli.utils.spinner import DummySpinner as Spinner

from riocli.constants import Colors
from riocli.deployment.util import name_to_guid, select_details
from riocli.utils.execute import run_on_cloud


@click.command(
    'execute',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--component', 'component_name', default=None,
              help='Name of the component in the deployment')
@click.option('--exec', 'exec_name', default=None,
              help='Name of a executable in the component')
@click.argument('deployment-name', type=str)
@click.argument('command', nargs=-1)
@name_to_guid
def execute_command(
        component_name: str,
        exec_name: str,
        deployment_name: str,
        deployment_guid: str,
        command: typing.List[str]
) -> None:
    """
    Execute commands on cloud deployment
    """
    try:
        comp_id, exec_id, pod_name = select_details(deployment_guid, component_name, exec_name)

        with Spinner(text='Executing command `{}`...'.format(command)):
            stdout, stderr = run_on_cloud(deployment_guid, comp_id, exec_id, pod_name, command)

        if stderr:
            click.secho(stderr, fg=Colors.RED)
        if stdout:
            click.secho(stdout, fg=Colors.YELLOW)
    except Exception as e:
        click.secho(e, fg=Colors.RED)
        raise SystemExit(1)
