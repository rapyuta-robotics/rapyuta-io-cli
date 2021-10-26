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
import os

import click

from riocli.device.tools.util import run_tunnel_on_device, run_tunnel_on_local, copy_to_device
from riocli.device.util import name_to_guid
from riocli.utils import random_string
from riocli.utils.execute import run_on_device
from riocli.utils.ssh_tunnel import get_free_tcp_port


@click.command('ssh')
@click.option('--user', '-u', default='root', help='Username for the SSH')
@click.option('--local-port', '-L', default=None, help='Port number on the local machine for forwarding SSH')
@click.option('--remote-port', '-R', default=22, help='Port number on the Device on which SSH Server is listening')
@click.option('--x-forward/--no-x-forward', '-X', default=False, is_flag=True,
              help='Flag to enable X Forwarding over SSH')
@click.argument('device-name', type=str)
@name_to_guid
def device_ssh(device_name: str, device_guid: str, user: str, local_port: int, remote_port: int, x_forward: bool) -> None:
    """
    SSH to the Device
    """
    extra_args = ""
    if not x_forward:
        extra_args = extra_args + " -X "
    try:
        path = random_string(8, 5)
        if not local_port:
            local_port = get_free_tcp_port()
        run_tunnel_on_device(device_guid=device_guid, remote_port=remote_port, path=path)
        run_tunnel_on_local(local_port=local_port, path=path, background=True)
        os.system('ssh -p {} {} -o StrictHostKeyChecking=no {}@localhost'.format(local_port, extra_args, user))
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@click.command('ssh-authorize')
@click.argument('device-name', type=str)
@click.argument('public-key-file', default="~/.ssh/id_rsa.pub", type=click.Path(exists=True))
@name_to_guid
def ssh_authorize_key(device_name: str, device_guid: str, public_key_file: click.Path) -> None:
    """
    Authorize Public SSH Key
    """
    try:
        temp_path = "/tmp/{}".format(random_string(8, 5))
        copy_to_device(device_guid, public_key_file, temp_path)
        run_on_device(device_guid=device_guid, command=['cat', temp_path, '>>', '/root/.ssh/authorized_keys'])
        click.secho('Keys added successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)
