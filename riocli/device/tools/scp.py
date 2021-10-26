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

from riocli.config import new_client
from riocli.device.tools.util import copy_from_device, copy_to_device
from riocli.device.util import is_remote_path


@click.command()
@click.argument('source', nargs=1)
@click.argument('destination', nargs=1)
def scp(source, destination) -> None:
    """
    scp like interface to copy files to and from the device
    """
    try:
        client = new_client()
        devices = client.get_all_devices()
        src_device_guid, src = is_remote_path(source, devices=devices)
        dest_device_guid, dest = is_remote_path(destination, devices=devices)

        if src_device_guid is None and dest_device_guid is None:
            click.secho('One of source or destination paths should be a remote path of format '
                        '<device-id|device-name>:path', fg='red')
            exit(1)

        if src_device_guid is not None:
            copy_from_device(src_device_guid, src, dest)

        if dest_device_guid is not None:
            copy_to_device(dest_device_guid, src, dest)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)
