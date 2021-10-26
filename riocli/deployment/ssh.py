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
import functools

import click

from riocli.deployment.util import select_details, name_to_guid
from riocli.utils.execute import run_on_cloud
from riocli.utils.ssh_tunnel import establish_ssh_tunnel


@click.command('ssh', hidden=True)
@click.argument('deployment-name')
@name_to_guid
def ssh_deployment(deployment_name: str, deployment_guid: str) -> None:
    # FIXME(ankit): The remote command always exits in error
    comp_id, exec_id, pod_name = select_details(deployment_guid)
    exec_remote_command = functools.partial(run_on_cloud, deployment_guid, comp_id, exec_id, pod_name)
    establish_ssh_tunnel(exec_remote_command)


@click.command('ssh-init', hidden=True)
@click.argument('deployment-name')
@name_to_guid
def ssh_init(deployment_name: str, deployment_guid: str) -> None:
    try:
        _ssh_setup(deployment_guid)
        click.secho('Deployment ready for SSH', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _ssh_setup(deployment_guid: str) -> None:
    """
    Sets up Socat and SSH Authorized Keys File for SSH through Piping server
    """
    comp_id, exec_id, pod_name = select_details(deployment_guid)

    cmd_apt_update = ['apt', 'update']
    cmd_apt_install = ['apt', 'install', 'socat', 'openssh-server', '-y']
    cmd_mkdir_ssh = ['mkdir', '-p', '/root/.ssh']
    cmd_touch_file = ['touch', '/root/.ssh/authorized_keys']
    cmd_start_ssh = ['service', 'ssh', 'start']
    # FIXME(ankit): Setup SSH Keys
    commands = [cmd_apt_update, cmd_apt_install, cmd_mkdir_ssh, cmd_touch_file, cmd_start_ssh]
    click.clear()
    for cmd in commands:
        click.secho('$ {}'.format(' '.join(cmd)), fg='yellow')
        stdout, stderr = run_on_cloud(deployment_guid, comp_id, exec_id, pod_name, cmd)
        if stderr:
            click.secho(stderr, fg='red')
        if stdout:
            click.secho(stdout, fg='yellow')
