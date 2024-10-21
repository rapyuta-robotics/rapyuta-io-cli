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
import click

from riocli.config import new_client
from riocli.device.util import name_to_guid


@click.command("onboard")
@click.argument("device-name", type=str)
@name_to_guid
def device_onboard(device_name: str, device_guid: str) -> None:
    """Generates the on-boarding script for a device.

    You need to run the script on the device to onboard it.
    Copy the script to the device and run it. The device will be
    onboarded to the rapyuta.io in the selected project.
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        script = device.onboard_script()
        click.secho(script.full_command())
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)
