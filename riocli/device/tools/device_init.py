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
import os

import click

from riocli.config import Configuration
from riocli.constants import Colors, Symbols
from riocli.device.util import name_to_guid
from riocli.utils import run_bash
from riocli.utils.execute import run_on_device
from riocli.utils.spinner import with_spinner


@click.command("init")
@click.argument("device-name", type=str)
@with_spinner(text="Initializing device...", timer=True)
@name_to_guid
def device_init(device_name: str, device_guid: str, spinner=None) -> None:
    """Initialize a device for use with device tools.

    This is required to be executed first before all tools sub-commands.
    The command will install the necessary tools on the device and locally
    on the machine you are running this command on.
    """
    try:
        _setup_device(device_guid=device_guid, spinner=spinner)
        _setup_local(spinner=spinner)

        spinner.text = click.style(
            "Initialized device {}".format(device_name), fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to initialize device. Error: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)


def _setup_device(device_guid: str, spinner=None) -> None:
    spinner.write("> Installing pre-requisites on device")
    run_on_device(
        device_guid=device_guid,
        command=[
            "apt",
            "install",
            "-y",
            "socat",
            # TODO: Install piping-tunnel during onboarding itself
            "&&",
            "curl",
            "-sLO",
            "https://github.com/nwtgck/go-piping-tunnel/releases/download/v0.10.1/piping-tunnel-0.10.1-linux-amd64.deb",
            "&&",
            "dpkg",
            "-i",
            "piping-tunnel-0.10.1-linux-amd64.deb",
            "&&",
            "rm",
            "piping-tunnel-0.10.1-linux-amd64.deb",
            "&&",
            "mkdir",
            "-p",
            "/root/.ssh",
            "&&",
            "/root/.ssh/authorized_keys",
        ],
    )


def _setup_local(spinner=None) -> None:
    config = Configuration()
    path = os.path.join(os.path.dirname(config.filepath), "tools")
    tunnel = os.path.join(path, "piping-tunnel")
    if os.path.isfile(tunnel):
        spinner.write("> Tools already installed on local machine")
        return

    # TODO: Add support for non-linux and non-amd64 machines
    spinner.write("> Installing pre-requisites locally...")
    run_bash("""/bin/bash -c 'mkdir -p {}'""".format(path))
    run_bash(
        """/bin/bash -c 'pushd {} && curl -sSLO https://github.com/nwtgck/go-piping-tunnel/releases/download/v0.10.1/piping-tunnel-0.10.1-linux-amd64.tar.gz && tar xf piping-tunnel-0.10.1-linux-amd64.tar.gz && rm CHANGELOG.md LICENSE piping-tunnel-0.10.1-linux-amd64.tar.gz README.md && popd'
    """.format(path)
    )
