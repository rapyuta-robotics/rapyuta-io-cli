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
import typing

import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.deployment.model import Deployment
from riocli.utils import tabulate_data
from riocli.v2client.util import process_errors

ALL_PHASES = [
    "InProgress",
    "Provisioning",
    "Succeeded",
    "FailedToStart",
    "Stopped",
]

DEFAULT_PHASES = [
    "InProgress",
    "Provisioning",
    "Succeeded",
    "FailedToStart",
]


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--device",
    prompt_required=False,
    default="",
    type=str,
    help="Filter the Deployment list by Device name",
)
@click.option(
    "--phase",
    prompt_required=False,
    multiple=True,
    type=click.Choice(ALL_PHASES),
    default=DEFAULT_PHASES,
    help="Filter the Deployment list by Phases",
)
@click.option(
    "--label",
    "-l",
    "labels",
    multiple=True,
    type=click.STRING,
    default=(),
    help="Filter the deployment list by labels",
)
@click.option(
    "--wide", "-w", is_flag=True, default=False, help="Print more details", type=bool
)
def list_deployments(
    device: str,
    phase: typing.List[str],
    labels: typing.List[str],
    wide: bool = False,
) -> None:
    """List the deployments in the current project

    You can filter the deployments by phase and labels.

    The -w or --wide flag prints more details about the deployments.

    Usage Examples:

      Filter by phase

      $ rio deployment list --phase InProgress --phase Stopped

      Filter by labels

      $ rio deployment list --label key1=value1 --label key2=value2
    """
    query = {
        "phases": phase,
        "labelSelector": labels,
    }

    try:
        client = new_v2_client(with_project=True)
        deployments = client.list_deployments(query=query)
        deployments = sorted(deployments, key=lambda d: d.metadata.name.lower())
        display_deployment_list(deployments, show_header=True, wide=wide)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def display_deployment_list(
    deployments: typing.List[Deployment],
    show_header: bool = True,
    wide: bool = False,
):
    headers = []
    if show_header:
        headers = ["Name", "Package", "Creation Time (UTC)", "Phase", "Status"]

    if show_header and wide:
        headers.extend(["Deployment ID", "Stopped Time (UTC)"])

    data = []
    for d in deployments:
        package_name_version = (
            f"{d.metadata.depends.nameOrGUID} ({d.metadata.depends.version})"
        )
        phase = d.get("status", {}).get("phase", "")

        status = ""

        if d.status:
            if d.status.get("error_codes"):
                status = click.style(
                    process_errors(d.status.error_codes, no_action=True), fg=Colors.RED
                )
            else:
                status = d.status.status

        row = [
            d.metadata.name,
            package_name_version,
            d.metadata.createdAt,
            phase,
            status,
        ]

        if wide:
            row.extend([d.metadata.guid, d.metadata.get("deletedAt")])

        data.append(row)

    tabulate_data(data, headers=headers)
