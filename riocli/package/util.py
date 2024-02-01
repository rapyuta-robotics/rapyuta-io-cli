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
import functools
import re
import typing
from typing import List

import click
from rapyuta_io import Client
from rapyuta_io.clients.package import Package

from riocli.config import new_client
from riocli.utils import tabulate_data
from riocli.utils.selector import show_selection


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg='red')
            raise SystemExit(1)

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
        raise SystemExit(1)

    if len(packages) == 1:
        return packages[0].packageId

    options = {}
    for pkg in packages:
        options[pkg.packageId] = '{} ({})'.format(pkg.packageName, pkg.packageVersion)

    choice = show_selection(options, header='Following packages were found with the same name')
    return choice


def fetch_packages(
        client: Client,
        package_name_or_regex: str,
        include_all: bool,
        version: str = None
) -> List[Package]:
    packages = client.get_all_packages(version=version)

    result = []
    for pkg in packages:
        # We cannot delete public packages. Skip them instead.
        if 'io-public' in pkg.packageId:
            continue

        if (include_all or package_name_or_regex == pkg.packageName or
                pkg.packageId == package_name_or_regex or
                (package_name_or_regex not in pkg.packageName and
                 re.search(package_name_or_regex, pkg.packageName))):
            result.append(pkg)

    return result


def print_packages_for_confirmation(packages: List[Package]) -> None:
    headers = ['Name', 'Version']
    data = [[p.packageName, p.packageVersion] for p in packages]

    tabulate_data(data, headers)
