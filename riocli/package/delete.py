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
from queue import Queue

import click
from rapyuta_io.clients.package import Package
from yaspin.api import Yaspin

from riocli.config import new_client
from riocli.constants import Symbols, Colors
from riocli.package.util import fetch_packages, print_packages_for_confirmation
from riocli.utils import tabulate_data
from riocli.utils.execute import apply_func_with_result
from riocli.utils.spinner import with_spinner


@click.command('delete')
@click.option('--force', '-f', is_flag=True, default=False, help='Skip confirmation')
@click.option('-a', '--all', 'delete_all', is_flag=True, default=False, help='Deletes all packages in the project')
@click.option('--version', 'package_version', type=str,
              help='Semantic version of the Package, only used when name is used instead of GUID')
@click.option('--workers', '-w',
              help="Number of parallel workers while running deleting packages. Defaults to 10",
              type=int, default=10)
@click.argument('package-name-or-regex', type=str, default="")
@with_spinner(text="Deleting package(s)...")
def delete_package(
        package_name_or_regex: str,
        package_version: str,
        force: bool = False,
        delete_all: bool = False,
        workers: int = 10,
        spinner: Yaspin = None,
) -> None:
    """
    Delete the package from the Platform
    """
    client = new_client()

    if not (package_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        packages = fetch_packages(client, package_name_or_regex, delete_all, package_version)
    except Exception as e:
        spinner.text = click.style(
            'Failed to find package(s): {}'.format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not packages:
        spinner.text = click.style("Package(s) not found", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    with spinner.hidden():
        print_packages_for_confirmation(packages)

    spinner.write('')

    if not force:
        with spinner.hidden():
            click.confirm('Do you want to delete the above package(s)?', default=True, abort=True)

    try:
        result = apply_func_with_result(
            f=_apply_delete, items=packages,
            workers=workers, key=lambda x: x[0]
        )

        data, statuses = [], []
        for name, status in result:
            fg = Colors.GREEN if status else Colors.RED
            icon = Symbols.SUCCESS if status else Symbols.ERROR
            statuses.append(status)
            data.append([
                click.style(name, fg),
                click.style(icon, fg)
            ])

        with spinner.hidden():
            tabulate_data(data, headers=['Name', 'Status'])

        icon = Symbols.SUCCESS if all(statuses) else Symbols.WARNING
        fg = Colors.GREEN if all(statuses) else Colors.YELLOW
        text = "successfully" if all(statuses) else "partially"

        spinner.text = click.style(
            'Package(s) deleted {}.'.format(text), fg)
        spinner.ok(click.style(icon, fg))
    except Exception as e:
        spinner.text = click.style(
            'Failed to delete package(s): {}'.format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _apply_delete(result: Queue, package: Package) -> None:
    name_version = "{}@{}".format(package.packageName, package.packageVersion)
    try:
        package.delete()
        result.put((name_version, True))
    except Exception:
        result.put((name_version, False))
