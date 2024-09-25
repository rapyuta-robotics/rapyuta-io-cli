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
import sys
import typing

import click
from click_help_colors import HelpColorsCommand

if sys.stdout.isatty():
    from yaspin import kbi_safe_yaspin as Spinner
else:
    from riocli.utils.spinner import DummySpinner as Spinner

from riocli.config import new_v2_client
from riocli.constants import Colors, Status, Symbols
from riocli.utils.execute import run_on_device
from riocli.utils.selector import show_selection


@click.command(
    'execute',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--user', default='root')
@click.option('--shell', default='/bin/bash')
@click.option('--exec', 'exec_name', default=None,
              help='Name of a executable in the component')
@click.argument('deployment-name', type=str)
@click.argument('command', nargs=-1)
def execute_command(
        user: str,
        shell: str,
        exec_name: str,
        deployment_name: str,
        command: typing.List[str]
) -> None:
    """
    Execute commands on a device deployment
    """
    try:
        client = new_v2_client()

        deployment = client.get_deployment(deployment_name)
        if not deployment:
            click.secho(f'{Symbols.ERROR} Deployment `{deployment_name}` not found', fg=Colors.RED)
            raise SystemExit(1)

        if deployment.status.status != Status.RUNNING:
            click.secho(f'{Symbols.ERROR} Deployment `{deployment_name}` is not running', fg=Colors.RED)
            raise SystemExit(1)

        if deployment.spec.runtime != 'device':
            click.secho(f'Only device runtime is supported.', fg=Colors.RED)
            raise SystemExit(1)

        if exec_name is None:
            package = client.get_package(deployment.metadata.depends.nameOrGUID,
                                         query={"version": deployment.metadata.depends.version})
            executables = [e.name for e in package.spec.executables]
            if len(executables) == 1:
                exec_name = executables[0]
            else:
                exec_name = show_selection(executables, '\nSelect executable')

        with Spinner(text='Executing command `{}`...'.format(command)):
            response = run_on_device(
                user=user,
                shell=shell,
                command=command,
                background=False,
                deployment=deployment,
                exec_name=exec_name,
                device_name=deployment.spec.device.depends.nameOrGUID
            )
        click.echo(response)
    except Exception as e:
        click.secho(e, fg=Colors.RED)
        raise SystemExit(1)
