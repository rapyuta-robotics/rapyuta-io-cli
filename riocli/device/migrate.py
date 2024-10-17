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
from yaspin.core import Yaspin

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.device.util import migrate_device_to_project, name_to_guid
from riocli.project.util import name_to_guid as project_name_to_guid
from riocli.utils.spinner import with_spinner


@click.command(
    "migrate",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("project-name", type=str)
@click.option(
    "--enable-vpn",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Enable VPN after migrating to the destination project.",
)
@click.option(
    "--advertise-routes",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Advertise subnets configured in project to VPN peers",
)
@name_to_guid
@project_name_to_guid
@click.pass_context
@with_spinner(text="Migrating device...")
def migrate_project(
    ctx: click.Context,
    device_name: str,
    device_guid: str,
    project_name: str,
    project_guid: str,
    enable_vpn: bool,
    advertise_routes: bool,
    spinner: Yaspin,
) -> None:
    """Migrate a device from current project to the target project.

    This process may take some time since it involves multiple steps.

    Optionally, you can enable VPN on the device after migration. Use
    the --enable-vpn flag to enable VPN on the device.

    If you want to advertise the subnets configured in the project to VPN peers,
    use the --advertise-routes flag. This is usually applicable for edge devices
    that are configured as subnet routers.
    """
    try:
        migrate_device_to_project(ctx, device_guid, project_guid)
        spinner.write(
            click.style(
                "{} Device {} migrated successfully.".format(
                    Symbols.SUCCESS, device_name
                ),
                fg=Colors.GREEN,
            )
        )

        if enable_vpn:
            spinner.text = "Enabling VPN on device..."
            client = new_client()
            client.set_project(project_guid)
            client.toggle_features(
                device_id=device_guid,
                features=[("vpn", True)],
                config={"vpn": {"advertise_routes": advertise_routes}},
            )
            spinner.write(
                click.style(
                    "{} Enabled VPN on the device.".format(Symbols.SUCCESS),
                    fg=Colors.GREEN,
                )
            )
    except Exception as e:
        spinner.text = click.style("Failed to migrate device: {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e
