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
import click
from munch import unmunchify

from riocli.config import new_v2_client
from riocli.utils import inspect_with_format
from riocli.utils.selector import show_selection

@click.command('inspect')
@click.option('--version', 'package_version', type=str,
              help='Semantic version of the Package, only used when name is used instead of GUID')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('package-name')
def inspect_package(format_type: str, package_name: str, package_version: str) -> None:
    """
    Inspect the package resource
    """
    try:
        client = new_v2_client()
        package_obj = None
        if package_name.startswith("pkg-"):
            packages = client.list_packages(query = {"guid": package_name})
            if packages:
                package_obj = packages[0]

        elif package_name and package_version:
            package_obj = client.get_package(package_name, query = {"version": package_version})
        elif package_name:
            packages = client.list_packages(query={"name": package_name})

            if len(packages) == 0:
                click.secho("package not found", fg='red')
                raise SystemExit(1)

            options = {}
            package_objs = {}
            for pkg in packages:
                options[pkg.metadata.guid] = '{} ({})'.format(pkg.metadata.name, pkg.metadata.version)
                package_objs[pkg.metadata.guid] = pkg
            choice = show_selection(options, header='Following packages were found with the same name')
            package_obj = package_objs[choice]

        if not package_obj:
            click.secho("package not found", fg='red')
            raise SystemExit(1)

        inspect_with_format(unmunchify(package_obj), format_type)

    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)
