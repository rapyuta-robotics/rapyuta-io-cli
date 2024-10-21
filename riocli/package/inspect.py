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
import click
from munch import unmunchify

from riocli.config import new_v2_client
from riocli.package.util import find_package
from riocli.utils import inspect_with_format


@click.command("inspect")
@click.option(
    "--version",
    "package_version",
    type=str,
    help="Semantic version of the Package, only used when name is used instead of GUID",
)
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("package-name")
def inspect_package(format_type: str, package_name: str, package_version: str) -> None:
    """
    Inspect the package resource
    """
    try:
        client = new_v2_client()
        package_obj = find_package(client, package_name, package_version)
        if not package_obj:
            click.secho("package not found", fg="red")
            raise SystemExit(1)

        inspect_with_format(unmunchify(package_obj), format_type)

    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)
