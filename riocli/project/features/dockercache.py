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
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.project.util import name_to_guid
from riocli.utils.spinner import with_spinner


@click.command(
    "dockercache",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("project-name", type=str)
@click.argument("enable", type=bool)
@click.option(
    "--proxy-device",
    type=click.STRING,
    default=(),
    help="Name of the device for docker-cache proxy.",
)
@click.option(
    "--proxy-interface",
    type=click.STRING,
    default=(),
    help="Name of the network interface for docker-cache proxy.",
)
@click.option(
    "--registry-url",
    type=click.STRING,
    default=(),
    help="URL for the upstream docker registry.",
)
@click.option(
    "--registry-secret",
    type=click.STRING,
    default=(),
    help="Name of the secret for upstream docker registry",
)
@name_to_guid
@with_spinner(text="Updating DockerCache state...")
def dockercache(
    project_name: str,
    project_guid: str,
    enable: bool,
    proxy_device: str,
    proxy_interface: str,
    registry_url: str,
    registry_secret: str,
    spinner=None,
) -> None:
    """
    Enable or disable DockerCache on a project

    Example:

    \b
        rio project features dockercache "my-project" true \\
            --proxy-device edge01 \\
            --proxy-interface eth0 \\
            --registry-url https://quay.io \\
            --registry-secret quay
    """
    client = new_v2_client(with_project=False)

    try:
        project = client.get_project(project_guid)
    except Exception as e:
        spinner.text = click.style("Failed: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    project["spec"]["features"]["dockerCache"] = {
        "enabled": enable,
        "proxyDevice": proxy_device,
        "proxyInterface": proxy_interface,
        "registryURL": registry_url,
        "registrySecret": registry_secret,
    }

    is_enabled = project["spec"]["features"]["dockerCache"].get("enabled", False)

    status = "Enabling DockerCache..." if enable else "Disabling DockerCache..."
    if is_enabled and enable:
        status = "Updating DockerCache..."
    spinner.text = status

    try:
        client.update_project(project_guid, project)
        spinner.text = click.style("Done", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e
