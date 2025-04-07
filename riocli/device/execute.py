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
from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.device.util import fetch_devices
from rapyuta_io import Command
from shlex import join


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
@click.argument("device-name-or-regex", type=str)
@click.argument("command", nargs=-1)
def execute_command(
    device_name_or_regex: str,
    user: str,
    timeout: int,
    shell: str,
    run_async: bool,
    command: typing.List[str],
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

    if len(command) == 0:
        click.secho("{} No command specified".format(Symbols.ERROR), fg=Colors.RED)
        raise SystemExit(1)

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

    device_guids = [d.uuid for d in devices if d.status == "ONLINE"]
    device_dict = {d.uuid: d.name for d in devices}
    cmd = join(tuple(["bash", "-c"]) + command)
    try:
        result = client.execute_command(
            device_ids=device_guids,
            command=Command(cmd, shell=shell, bg=run_async, runas=user, timeout=timeout),
            timeout=timeout,
        )
        for device_guid in result:
            click.secho(">>> {}({})".format(device_dict[device_guid], device_guid), fg=Colors.YELLOW)
            click.echo("{}\n".format(result[device_guid]))
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

