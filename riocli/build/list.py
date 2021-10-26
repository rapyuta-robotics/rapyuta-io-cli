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
import typing

import click
from rapyuta_io import Build

from riocli.config import new_client


@click.command('list')
@click.option('--phase', 'status', multiple=True, help='Filter the Builds list by Phases',
              type=click.Choice(['BuildInProgress', 'Complete', 'BuildFailed']),
              default=['BuildInProgress', 'Complete', 'BuildFailed'])
def list_builds(status: typing.List[str]) -> None:
    """
    List the builds in the selected project
    """
    try:
        client = new_client()
        builds = client.list_builds(statuses=list(status))
        _display_build_list(builds, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_build_list(builds: typing.List[Build], show_header: bool = True):
    if show_header:
        click.secho('{:32} {:25} {:15} {:9} {:<64}'.format('Build ID', 'Name', 'Status', 'Strategy', 'Repository'),
                    fg='yellow')

    for build in builds:
        click.secho('{:32} {:25} {:15} {:9} {:<64}'.format(build.guid, build.buildName, build.status,
                                                           build.buildInfo.strategyType.value,
                                                           build.buildInfo.repository))
