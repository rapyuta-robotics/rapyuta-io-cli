# Copyright 2025 Rapyuta Robotics
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
from munch import Munch

from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.utils import tabulate_data

@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--label",
    "-l",
    "labels",
    multiple=True,
    type=click.STRING,
    default=(),
    help="Filter the roles list by labels",
)
@click.pass_context
def list_roles(ctx: click.Context, labels: typing.Union[typing.List[str], None] = None):
    """List all the roles in current organization.

    You can also filter the list by specifying labels using the ``--label``
    or the ``-l`` flag.

    Usage Examples:

        List all roles in the organization.

            $ rio role list

        List all roles with label "release=3.0"

            $ rio role list --label release=3.0
    """
    query = {}
    if labels:
        query = {"labelSelector": labels}

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        roles = client.list_roles(query=query)
        roles = sorted(roles, key=lambda r: r.metadata.name.lower())
        _display_role_list(roles)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--label",
    "-l",
    "labels",
    multiple=True,
    type=click.STRING,
    default=(),
    help="Filter the rolebindings list by labels",
)
@click.pass_context
def list_role_bindings(ctx: click.Context, labels: typing.Union[typing.List[str], None] = None):
    """List all the rolebindings in current organization.
    Usage:
        rio rolebinding list
    """
    query = {}
    if labels:
        query = {"labelSelector": labels}
    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        role_bindings = client.list_role_bindings(query=query)
        role_bindings = sorted(role_bindings, key=lambda r: r.metadata.name.lower())
        _display_rolebindings_list(role_bindings)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_role_list(
        roles: typing.List[Munch],
        show_header: bool = True,
) -> None:
    headers = []
    if show_header:
        headers = ["Role Name", "Description"]

    data = [
            [r.metadata.name, getattr(r.spec, "description", "")] for r in roles
    ]

    tabulate_data(data, headers)


def _display_rolebindings_list(rolebindings: typing.List[Munch], show_header: bool=True):
    headers = ["RoleBinding Name", "RoleRef", "Subject"] if show_header else []
    data = [
        [
            r.metadata.name,
            r.spec.roleRef.name,
            _format_subject(r.spec.subject),
            _format_domain(r.spec.subject.domain),
        ]
        for r in rolebindings
    ]
    tabulate_data(data, headers)

def _format_subject(subject: dict[str, str]) -> str:
    if subject.kind == "User":
        return f"User/{subject.emailID}"

    return f"{subject.kind}/{subject.name}"

def _format_domain(domain: dict[str, str]) -> str:
    return f"{domain.kind}/{domain.name}"
