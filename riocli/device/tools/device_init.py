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
from click_spinner import spinner

from riocli.config import Configuration
from riocli.device.util import name_to_guid
from riocli.utils import run_bash
from riocli.utils.execute import run_on_device


@click.command('init')
@click.argument('device-name', type=str)
@name_to_guid
def device_init(device_name: str, device_guid: str) -> None:
    """
    Initialize device for use with device tools. This is required to be executed first before all tools sub-commands.
    """
    try:
        with spinner():
            _setup_device(device_guid=device_guid)
            _setup_local()
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _setup_device(device_guid: str) -> None:
    run_on_device(device_guid=device_guid, command=[
        'apt', 'install', '-y', 'socat',
        # TODO: Install piping-tunnel during onboarding itself
        '&&', 'curl', '-sLO',
        'https://github.com/nwtgck/go-piping-tunnel/releases/download/v0.10.1/piping-tunnel-0.10.1-linux-amd64.deb',
        '&&', 'dpkg', '-i', 'piping-tunnel-0.10.1-linux-amd64.deb',
        '&&', 'rm', 'piping-tunnel-0.10.1-linux-amd64.deb',
        '&&', 'mkdir', '-p', '/root/.ssh',
        '&&', '/root/.ssh/authorized_keys'
    ])


def _setup_local() -> None:
    config = Configuration()
    path = os.path.join(os.path.dirname(config.filepath), 'tools')
    tunnel = os.path.join(path, 'piping-tunnel')
    if os.path.isfile(tunnel):
        return

    # TODO: Add support for non-linux and non-amd64 machines
    run_bash("""/bin/bash -c 'mkdir -p {}'""".format(path))
    run_bash("""/bin/bash -c 'pushd {} && curl -SLO https://github.com/nwtgck/go-piping-tunnel/releases/download/v0.10.1/piping-tunnel-0.10.1-linux-amd64.tar.gz && tar xf piping-tunnel-0.10.1-linux-amd64.tar.gz && rm CHANGELOG.md LICENSE piping-tunnel-0.10.1-linux-amd64.tar.gz README.md && popd'
    """.format(path))
