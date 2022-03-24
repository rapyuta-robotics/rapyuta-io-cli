# -*- coding: utf-8 -*-
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

__version__ = "0.3.0"

import click
import rapyuta_io.version
from click_help_colors import HelpColorsGroup
from click_plugins import with_plugins
from click_repl import register_repl
from pkg_resources import iter_entry_points

from riocli.auth import auth
from riocli.build import build
from riocli.completion import completion
from riocli.deployment import deployment
from riocli.device import device
from riocli.marketplace import marketplace
from riocli.network import network
from riocli.package import package
from riocli.project import project
from riocli.rosbag import rosbag
from riocli.secret import secret
from riocli.static_route import static_route


@with_plugins(iter_entry_points('riocli.plugins'))
@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def cli():
    pass


@cli.command('help')
@click.pass_context
def cli_help(ctx):
    """
    Prints the help message
    """
    click.echo(cli.get_help(ctx))


@cli.command()
def version():
    """
    Version of the CLI/SDK
    """
    click.echo("rio {} / SDK {}".format(__version__, rapyuta_io.VERSIONSTR))
    return


cli.add_command(auth)
cli.add_command(project)
cli.add_command(device)
cli.add_command(build)
cli.add_command(secret)
cli.add_command(package)
cli.add_command(deployment)
cli.add_command(static_route)
cli.add_command(rosbag)
cli.add_command(network)
cli.add_command(completion)
cli.add_command(marketplace)
register_repl(cli)
