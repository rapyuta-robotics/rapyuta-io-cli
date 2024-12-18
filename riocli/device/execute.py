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
import typing

import click
from click_help_colors import HelpColorsCommand

from riocli.constants import Colors
from riocli.device.util import name_to_guid
from riocli.utils.execute import run_on_device


@click.command(
    "execute",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option("--user", default="root")
@click.option("--timeout", default=300)
@click.option("--shell", default="/bin/bash")
@click.option(
    "--async",
    "run_async",
    is_flag=True,
    default=False,
    help="Run the command asynchronously.",
)
@click.argument("device-name", type=str)
@click.argument("command", nargs=-1)
@name_to_guid
def execute_command(
    device_name: str,
    device_guid: str,
    user: str,
    timeout: int,
    shell: str,
    run_async: bool,
    command: typing.List[str],
) -> None:
    """Execute commands on a device.

    You can specify the user, shell, run-async, and timeout options to customize
    the command execution. To specify the user, use the --user flag.
    The default is 'root'. To specify the shell, use the --shell flag.
    The default shell is '/bin/bash'. To run the command asynchronously,
    set the --async flag to true. The default value is false. To
    specify the timeout, use the --timeout flag, providing the duration
    in seconds. The default value is 300.

    Make sure you put your command in quotes to avoid any issues.

    Usage Examples:

        $ rio device execute DEVICE_NAME "ls -l"
    """
    try:
        response = run_on_device(
            device_guid=device_guid,
            user=user,
            shell=shell,
            command=command,
            background=run_async,
            timeout=timeout,
        )

        click.secho(response)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e
