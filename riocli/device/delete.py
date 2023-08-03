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
from requests import Response

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.device.util import name_to_guid
from riocli.utils.spinner import with_spinner


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--force', '-f', 'force', is_flag=True, help='Skip confirmation')
@click.argument('device-name', type=str)
@name_to_guid
@with_spinner(text='Deleting device...')
def delete_device(device_name: str, device_guid: str, force: bool, spinner=None):
    """
    Deletes a device
    """
    with spinner.hidden():
        if not force:
            click.confirm(
                'Deleting device {} ({})'.format(
                    device_name, device_guid), abort=True)

    try:
        client = new_client(with_project=True)
        handle_device_delete_error(client.delete_device(device_id=device_guid))
        spinner.text = click.style('Device deleted successfully', fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style('Failed to delete device: {}'.format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def handle_device_delete_error(response: Response):
    if response.status_code < 400:
        return

    data = response.json()

    error = data.get('response', {}).get('error')

    if 'deployments' in error:
        msg = 'Device has running deployments. Please de-provision them before deleting the device.'
        raise Exception(msg)

    raise Exception(error)
