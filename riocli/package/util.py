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
import re

import click
from rapyuta_io_sdk_v2 import Client, walk_pages
from rapyuta_io_sdk_v2 import Package as PackageModel

from riocli.utils import tabulate_data
from riocli.utils.selector import show_selection


def find_package(
    client: Client,
    package_name: str,
    package_version: str,
) -> None | PackageModel:
    package_obj = None

    if package_name.startswith("pkg-"):
        packages = []
        for page in walk_pages(client.list_packages):
            packages.extend(page)
        if not packages:
            raise Exception("Package not found")

        obj = packages[0]
        package_obj = client.get_package(
            name=obj.metadata.name, version=obj.metadata.version
        )
    elif package_name and package_version:
        package_obj = client.get_package(name=package_name, version=package_version)
    elif package_name:
        packages = []
        for page in walk_pages(client.list_packages, name=package_name):
            packages.extend(page)

        if len(packages) == 0:
            click.secho("package not found", fg="red")
            raise SystemExit(1)

        if len(packages) == 1:
            obj = packages[0]
            package_obj = client.get_package(
                name=obj.metadata.name, version=obj.metadata.version
            )
        else:
            options = {}
            package_objs = {}
            for pkg in packages:
                options[pkg.metadata.guid] = (
                    f"{pkg.metadata.name} ({pkg.metadata.version})"
                )
                package_objs[pkg.metadata.guid] = pkg
            choice = show_selection(
                options, header="Following packages were found with the same name"
            )
            obj = package_objs[choice]
            package_obj = client.get_package(
                name=obj.metadata.name, version=obj.metadata.version
            )

    return package_obj


def fetch_packages(
    client: Client,
    package_name_or_regex: str,
    package_version: str,
    include_all: bool,
) -> list[PackageModel]:
    packages = []
    for page in walk_pages(client.list_packages):
        packages.extend(page)

    result = []
    for pkg in packages:
        # We cannot delete public packages. Skip them instead.
        if "io-public" in pkg.metadata.guid:
            continue

        if include_all:
            result.append(pkg)
            continue

        if re.search(package_name_or_regex, pkg.metadata.name):
            if package_version and package_version == pkg.metadata.version:
                result.append(pkg)
            elif not package_version:
                result.append(pkg)

    return result


def print_packages_for_confirmation(packages: list[PackageModel]) -> None:
    headers = ["Name", "Version"]
    data = [[p.metadata.name, p.metadata.version] for p in packages]
    tabulate_data(data, headers)
