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
import functools
import typing

import click
from rapyuta_io import Client

from riocli.config import new_client
from riocli.utils.selector import show_selection


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg='red')
            exit(1)

        name = kwargs.pop('package_name')
        guid = None
        version = kwargs.pop('package_version')

        if name.startswith('pkg-') or name.startswith('io-'):
            guid = name
            name = None

        if name is None:
            name = get_package_name(client, guid)

        if guid is None:
            guid = find_package_guid(client, name, version)

        kwargs['package_name'] = name
        kwargs['package_guid'] = guid
        f(**kwargs)

    return decorated


def get_package_name(client: Client, guid: str) -> str:
    pkg = client.get_package(guid)
    return pkg.packageName


def find_package_guid(client: Client, name: str, version: str = None) -> str:
    packages = client.get_all_packages(name=name, version=version)
    if len(packages) == 0:
        click.secho("package not found", fg='red')
        exit(1)

    if len(packages) == 1:
        return packages[0].packageId

    options = {}
    for pkg in packages:
        options[pkg.packageId] = '{} ({})'.format(pkg.packageName, pkg.packageVersion)

    choice = show_selection(options, header='Following packages were found with the same name')
    return choice
