# Copyright 2021 Rapyuta Robotics
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
from click_spinner import spinner
from click_help_colors import HelpColorsCommand
from riocli.config import new_client, new_hwil_client
from riocli.hwil.util import find_device_id, DeviceNotFound
from riocli.device.util import find_device_guid


@click.command(
    'delete',
    cls=HelpColorsCommand,
)
@click.argument('device-name', type=str, default="")
@click.option('--deboard', 'deboard', is_flag=True, type=bool, default=False)
def delete_device(
        device_name: str,
        deboard: bool,
) -> None:
    """
        delete a  virtual device on the cloud
    """
    try:
        client = new_client()
        hwil_client = new_hwil_client()
        with spinner():
            try:
                hwil_client.delete_device(find_device_id(hwil_client, device_name))
                click.secho('HWIL Device deleted successfully!', fg='green')
            except DeviceNotFound as d:
                click.secho('HWIL Device already deleted!', fg='green')

            if deboard:
                try:
                    client.delete_device(device_id=find_device_guid(client, device_name))
                    click.secho('Rapyuta.io Device deleted successfully in rapyuta.io!', fg='green')
                except DeviceNotFound as d:
                    click.secho('Rapyuta.io Device already deleted!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)
