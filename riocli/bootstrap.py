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

__version__ = "10.0.3"

import os

import click
import rapyuta_io
from click import Context

from riocli.apply import apply, delete, graph
from riocli.apply.explain import explain, list_examples
from riocli.apply.template import template
from riocli.auth import auth
from riocli.chart import chart
from riocli.completion import completion
from riocli.compose import compose
from riocli.config import Configuration
from riocli.config.context import cli_context
from riocli.configtree import config_trees
from riocli.constants import Colors, Symbols
from riocli.deployment import deployment
from riocli.device import device
from riocli.disk import disk
from riocli.hwil import hwildevice
from riocli.network import network
from riocli.oauth2 import oauth2
from riocli.organization import organization
from riocli.package import package
from riocli.parameter import parameter
from riocli.permission import permission
from riocli.project import project
from riocli.role import role
from riocli.secret import secret
from riocli.service_account import service_account
from riocli.shell import deprecated_repl, shell
from riocli.static_route import static_route
from riocli.usergroup import usergroup
from riocli.utils import (
    AliasedGroup,
    check_for_updates,
    is_pip_installation,
    pip_install_cli,
    update_appimage,
)
from riocli.vpn import vpn


@click.group(
    invoke_without_command=False,
    cls=AliasedGroup,
    aliases={
        "o2": "oauth2",
        "sr": "static-route",
        "ug": "usergroup",
        "sa": "service-account",
    },
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def cli(ctx: Context, config: str | None = None):
    """Manage rapyuta.io features on the command-line"""
    ctx.obj = Configuration(filepath=config)


def safe_cli():
    if os.environ.get("DEBUG", "false").lower() != "true":
        try:
            cli()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1) from e
    else:
        cli()


@cli.command("help")
@click.pass_context
def cli_help(ctx):
    """Print the help message."""
    click.echo(cli.get_help(ctx))


@cli.command()
def version():
    """View installed CLI and SDK versions."""
    click.echo(f"rio {__version__} / SDK {rapyuta_io.__version__}")


@cli.command("update")
@click.option(
    "-f",
    "--force",
    "--silent",
    "silent",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Skip confirmation",
)
def update(silent: bool) -> None:
    """Update the CLI to the latest version.

    You can update your existing installation of the CLI to
    its latest version. Based on the installation method, i.e.
    pip or AppImage, the command will update the right
    installation.

    You can skip the confirmation prompt by using the --silent or
    --force or -f flag.
    """
    available, latest = check_for_updates(__version__)
    if not available:
        click.secho("🎉 You are using the latest version", fg=Colors.GREEN)
        return

    click.secho(f"🎉 A newer version ({latest}) is available.", fg=Colors.GREEN)

    if not silent:
        _ = click.confirm("Do you want to update?", abort=True, default=False)

    try:
        if is_pip_installation():
            _ = pip_install_cli(version=latest)
        else:
            update_appimage(version=latest)
    except Exception as e:
        click.secho(f"{Symbols.ERROR} Failed to update: {e}", fg=Colors.RED)
        raise SystemExit(1) from e

    click.secho(f"{Symbols.SUCCESS} Update successful!", fg=Colors.GREEN)


cli.add_command(apply)
cli.add_command(chart)
cli.add_command(explain)
cli.add_command(list_examples)
cli.add_command(graph)
cli.add_command(delete)
cli.add_command(auth)
cli.add_command(project)
cli.add_command(device)
cli.add_command(secret)
cli.add_command(package)
cli.add_command(deployment)
cli.add_command(static_route)
cli.add_command(network)
cli.add_command(completion)
cli.add_command(parameter)
cli.add_command(disk)
cli.add_command(shell)
cli.add_command(deprecated_repl)
cli.add_command(template)
cli.add_command(organization)
cli.add_command(vpn)
cli.add_command(usergroup)
cli.add_command(config_trees)
cli.add_command(hwildevice)
cli.add_command(cli_context)
cli.add_command(oauth2)
cli.add_command(compose)
cli.add_command(role)
cli.add_command(service_account)
cli.add_command(permission)
