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
import functools
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import click
import requests
from click_help_colors import HelpColorsCommand
from rapyuta_io import Client
from rapyuta_io.clients.device import Device
from yaspin.api import Yaspin

from riocli.config import new_client
from riocli.device.util import fetch_devices
from riocli.constants import Symbols, Colors
from riocli.utils import tabulate_data
from riocli.utils.spinner import with_spinner


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--force', '-f', '--silent', is_flag=True, default=False,
              help='Skip confirmation')
@click.option('--delete-all', '-a', is_flag=True, default=False,
              help='Delete all devices')
@click.option('--workers', '-w',
              help="Number of parallel workers for deleting devices. Defaults to 10.", type=int, default=10)
@click.argument('device-name-or-regex', type=str, default="")
@with_spinner(text='Deleting device...')
def delete_device(
        force: bool,
        delete_all: bool,
        workers: int,
        device_name_or_regex: str,
        spinner: Yaspin = None,
) -> None:
    """
    Deletes one more devices
    """
    client = new_client()
    if not (device_name_or_regex or delete_all):
        spinner.text = 'Nothing to delete'
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        devices = fetch_devices(
            client, device_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style(
            'Failed to delete device(s): {}'.format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not devices:
        spinner.text = "No devices to delete"
        spinner.ok(Symbols.SUCCESS)
        return

    headers = ['Name', 'Device ID', 'Status']
    data = [[d.name, d.uuid, d.status] for d in devices]

    with spinner.hidden():
        tabulate_data(data, headers)

    spinner.write('')

    if not force:
        with spinner.hidden():
            click.confirm('Do you want to delete above device(s)?',
                          default=True, abort=True)
        spinner.write('')

    try:
        result = Queue()
        func = functools.partial(_delete_deivce, client, result)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(func, devices)

        result = sorted(list(result.queue), key=lambda x: x[0])

        data, fg, statuses = [], Colors.GREEN, []
        success_count, failed_count = 0, 0

        for name, response in result:
            if response.status_code and response.status_code < 400:
                fg = Colors.GREEN
                icon = Symbols.SUCCESS
                success_count += 1
                msg = ''
            else:
                fg = Colors.RED
                icon = Symbols.ERROR
                failed_count += 1
                msg = get_error_message(response, name)

            data.append([
                click.style(name, fg),
                click.style(icon, fg),
                click.style(msg, fg)
            ])

        with spinner.hidden():
            tabulate_data(data, headers=['Name', 'Status', 'Message'])

        spinner.write('')

        if failed_count == 0 and success_count == len(devices):
            spinner_text = click.style('All devices deleted successfully.', Colors.GREEN)
            spinner_char = click.style(Symbols.SUCCESS, Colors.GREEN)
        elif success_count == 0 and failed_count == len(devices):
            spinner_text = click.style('Failed to delete devices', Colors.YELLOW)
            spinner_char = click.style(Symbols.WARNING, Colors.YELLOW)
        else:
            spinner_text = click.style(
                '{}/{} devices deleted successfully'.format(success_count, len(devices)), Colors.YELLOW)
            spinner_char = click.style(Symbols.WARNING, Colors.YELLOW)

        spinner.text = spinner_text
        spinner.ok(spinner_char)
    except Exception as e:
        spinner.text = click.style(
            'Failed to delete devices: {}'.format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

def _delete_deivce(
        client: Client,
        result: Queue,
        device: Device = None,
) -> None:
    response = requests.models.Response()
    try:
        response = client.delete_device(device_id=device.uuid)
        result.put((device["name"], response))
    except Exception:
        result.put((device["name"], response))


def get_error_message(response: requests.models.Response, name: str) -> str:
    if response.status_code:
        r = response.json()
        error = r.get('response', {}).get('error')

        if 'deployments' in error:
            return 'Device {0} has running deployments.'.format(name)

    return ""
