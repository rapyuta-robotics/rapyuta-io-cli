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
    "execute",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option("--user", default="root")
@click.option("--shell", default="/bin/bash")
@click.option("--timeout", default=300)
@click.option(
    "--async",
    "run_async",
    is_flag=True,
    default=False,
    help="Run the command asynchronously.",
)
@click.option(
    "--exec", "exec_name", default=None, help="Name of a executable in the component"
)
@click.argument("deployment-name", type=str)
@click.argument("command", nargs=-1)
def execute_command(
    user: str,
    shell: str,
    timeout: int,
    exec_name: str,
    run_async: bool,
    deployment_name: str,
    command: typing.List[str],
) -> None:
    """Execute a command on a device deployment

    You can execute a command on a deployment running on a device.
    In case there are more than one executable in the deployment,
    you can specify the executable name using the ``--exec`` option.
    If you do not specify the executable name, you will be prompted
    to select one from the list of executables. If the deployment
    only has one executable, it will be selected automatically.

    You can specify the shell using the ``--shell`` option. The default
    shell is ``/bin/bash``. You can also specify the user using the ``--user``
    option. The default user is ``root``.

    To run the command asynchronously, set the --async flag to true.
    The default value is false.

    To specify the timeout, use the --timeout
    flag, providing the duration in seconds. The default value is 300.

    Please ensure that you enclose the command in quotes to avoid
    any issues with the command parsing.

    Usage Examples:

        Execute a command on a device deployment with one executable

            $ rio deployment execute DEPLOYMENT_NAME 'ls -l'

        Execute a command on a device deployment with multiple executables

            $ rio deployment execute DEPLOYMENT_NAME --exec EXECUTABLE_NAME 'ls -l'
    """
    try:
        client = new_v2_client()

        deployment = client.get_deployment(deployment_name)
        if not deployment:
            click.secho(
                f"{Symbols.ERROR} Deployment `{deployment_name}` not found",
                fg=Colors.RED,
            )
            raise SystemExit(1)

        if deployment.status.status != Status.RUNNING:
            click.secho(
                f"{Symbols.ERROR} Deployment `{deployment_name}` is not running",
                fg=Colors.RED,
            )
            raise SystemExit(1)

        if deployment.spec.runtime != "device":
            click.secho("Only device runtime is supported.", fg=Colors.RED)
            raise SystemExit(1)

        if exec_name is None:
            package = client.get_package(
                deployment.metadata.depends.nameOrGUID,
                query={"version": deployment.metadata.depends.version},
            )
            executables = [e.name for e in package.spec.executables]
            if len(executables) == 1:
                exec_name = executables[0]
            else:
                exec_name = show_selection(executables, "\nSelect executable")

        with Spinner(text="Executing command `{}`...".format(command)):
            response = run_on_device(
                user=user,
                shell=shell,
                command=command,
                background=run_async,
                deployment=deployment,
                exec_name=exec_name,
                device_name=deployment.spec.device.depends.nameOrGUID,
                timeout=timeout,
            )
        click.echo(response)
    except Exception as e:
        click.secho(e, fg=Colors.RED)
        raise SystemExit(1)
