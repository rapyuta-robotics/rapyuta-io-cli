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
from rapyuta_io.clients.package import Package

from riocli.config import new_client


@click.command('list')
@click.option('--filter', 'filter_word', type=str, default=None,
              help='A sub-string can be provided to filter down the package list')
def list_packages(filter_word: str) -> None:
    """
    List the packages in the selected project
    """
    try:
        client = new_client()
        packages = client.get_all_packages(name=filter_word)
        _display_package_list(packages, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_package_list(
        packages: typing.List[Package],
        show_header: bool = True,
        truncate_limit: int = 32,
) -> None:
    if show_header:
        click.secho('{:30} {:34} {:10} {:<32}'.
                    format('Package ID', 'Name', 'Version', 'Description'),
                    fg='yellow')

    # Show IO Packages first
    packages.sort(key=lambda p: p.packageId)

    for package in packages:
        description = package.description
        name = package.packageName
        if truncate_limit:
            if len(description) > truncate_limit:
                description = description[:truncate_limit] + '..'
            if len(name) > truncate_limit:
                name = name[:truncate_limit] + '..'
        click.echo('{:30} {:34} {:10} {:<32}'.
                   format(package.packageId, name, package.packageVersion, description))
