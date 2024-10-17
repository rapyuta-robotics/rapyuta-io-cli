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

from riocli.config import new_v2_client
from riocli.package.model import Package
from riocli.utils import tabulate_data


@click.command("list")
@click.option(
    "--filter",
    "filter_word",
    type=str,
    default=None,
    help="A sub-string can be provided to filter down the package list",
)
def list_packages(filter_word: str) -> None:
    """
    List the packages in the selected project
    """
    try:
        client = new_v2_client(with_project=True)
        packages = client.list_packages()
        _display_package_list(packages, filter_word, show_header=True)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


def _display_package_list(
    packages: typing.List[Package],
    filter_word: str,
    show_header: bool = True,
    truncate_limit: int = 48,
) -> None:
    headers = []
    if show_header:
        headers = ("Name", "Version", "Package ID", "Description")

    # Show IO Packages first
    iter_pkg = list(map(lambda x: x.metadata.name, packages))
    iter_pkg.sort()

    package_dict = {}
    for pkgName in iter_pkg:
        filtered_pkg = list(filter(lambda x: x.metadata.name == pkgName, packages))
        filtered_pkg.sort(key=lambda x: x.metadata.version)
        package_dict[pkgName] = filtered_pkg

    data = []
    for _, pkgVersionList in package_dict.items():
        for package in pkgVersionList:
            description = package.metadata.get("description", "")
            name = package.metadata.name

            # check if filter word was passed.
            # if filter word was passed and it is not present in package name then continue
            if filter_word and not package.metadata.name.find(filter_word):
                continue

            if truncate_limit:
                if len(description) > truncate_limit:
                    description = description[:truncate_limit] + ".."
                if len(name) > truncate_limit:
                    name = name[:truncate_limit] + ".."

            data.append(
                [name, package.metadata.version, package.metadata.guid, description]
            )
    tabulate_data(data, headers=headers)
