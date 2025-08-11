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
import click
from click_help_colors import HelpColorsCommand
from munch import unmunchify

from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.utils import inspect_with_format

@click.command(
    "inspect",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("role_name", type=str)
@click.pass_context
def inspect_role(ctx: click.Context, role_name: str, format_type: str):
    """Print the role details.

    You can specify the format of the output using the ``--format`` flag.
    The supported formats are ``json`` and ``yaml``. Default is ``yaml``.
    """
    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        role = client.get_role(role_name)
        inspect_with_format(unmunchify(role), format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


@click.command(
    "inspect",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("binding_name", type=str)
@click.pass_context
def inspect_role_binding(ctx: click.Context, binding_name: str, format_type: str):
    """Print the RoleBinding details.
    Usage:
        rio rolebinding inspect <binding_name>
    """
    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        rolebinding = client.get_role_binding(binding_name)
        inspect_with_format(unmunchify(rolebinding), format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)
