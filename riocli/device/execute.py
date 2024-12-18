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
import functools
import click
from click_help_colors import HelpColorsCommand
from concurrent.futures import ThreadPoolExecutor
from riocli.config import new_client
from riocli.constants import Colors
from riocli.device.util import fetch_devices
from riocli.utils.execute import run_on_device
from queue import Queue


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
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers for executing command. Defaults to 10.",
    type=int,
    default=10,
)
@click.argument("device-name-or-regex", type=str)
@click.argument("command", nargs=-1)
def execute_command(
    device_name_or_regex: str,
    user: str,
    timeout: int,
    shell: str,
    run_async: bool,
    command: typing.List[str],
    workers: int = 10,
) -> None:
    """Execute commands on one or more devices.

    You can specify the user, shell, run-async, and timeout options to customize
    the command execution. To specify the user, use the --user flag.
    The default is 'root'. To specify the shell, use the --shell flag.
    The default shell is '/bin/bash'. To run the command asynchronously,
    set the --async flag to true. The default value is false. To
    specify the timeout, use the --timeout flag, providing the duration
    in seconds. The default value is 300.

    Make sure you put your command in quotes to avoid any issues.

    Usage Examples:

        $ rio device execute DEVICE_NAME_OR_REGEX "ls -l"

        To execute the command asynchronously:

            $ rio device execute DEVICE_NAME_OR_REGEX "ls -l" --async

        To run the command on all devices:

            $ rio device execute ".*" "ls -l"
    """

    client = new_client()

    try:
        devices = fetch_devices(
            client, device_name_or_regex, include_all=False, online_devices=True
        )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

    if not devices:
        click.secho("No device(s) found", fg=Colors.RED)
        raise SystemExit(1)

    device_guids = [d.uuid for d in devices]

    try:
        result = Queue()
        func = functools.partial(
            _run_on_device,
            user=user,
            shell=shell,
            command=command,
            background=run_async,
            timeout=timeout,
            result=result,
        )
        with ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(func, device_guids)

        for device_guid, success, response in result.queue:
            click.echo(
                ">>> {}: {}\n{}".format(
                    device_guid, "Success" if success else "Failed", response
                )
            )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def _run_on_device(device_guid, user, shell, command, background, timeout, result):
    """Wrapper on top of run_on_device to capture the output in a queue"""
    try:
        response = run_on_device(
            device_guid=device_guid,
            command=command,
            user=user,
            shell=shell,
            background=background,
            timeout=timeout,
        )
        result.put((device_guid, True, response))
    except Exception as e:
        result.put((device_guid, False, str(e)))
