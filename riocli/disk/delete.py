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
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.constants import Symbols, Colors
from riocli.disk.util import name_to_guid, _api_call
from riocli.utils.spinner import with_spinner


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--force', '-f', 'force', is_flag=True, default=False,
              help='Skip confirmation')
@click.argument('disk-name', required=True, type=str)
@name_to_guid
@with_spinner(text="Deleting disk...")
def delete_disk(
        disk_name: str,
        disk_guid: str,
        force: bool,
        spinner=None
) -> None:
    """
    Delete a disk
    """
    with spinner.hidden():
        if not force:
            click.confirm(
                'Deleting disk {} ({})'.format(disk_name, disk_guid), abort=True)

    try:
        _api_call(HttpMethod.DELETE, guid=disk_guid, load_response=False)

        spinner.text = click.style('Disk deleted successfully.', fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style('Failed to delete disk: {}'.format(str(e)), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
