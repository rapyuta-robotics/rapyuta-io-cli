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
from rapyuta_io.clients.package import Package

from riocli.config import new_client
from riocli.package.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--version', 'package_version', type=str,
              help='Semantic version of the Package, only used when name is used instead of GUID')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('package-name')
@name_to_guid
def inspect_package(format_type: str, package_name: str, package_guid: str) -> None:
    """
    Inspect the package resource
    """
    try:
        client = new_client()
        package = client.get_package(package_guid)
        data = make_package_inspectable(package)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def make_package_inspectable(package: Package) -> dict:
    return {
        'created_at': package.CreatedAt,
        'updated_at': package.UpdatedAt,
        'deleted_at': package.DeletedAt,
        'guid': package.guid,
        'package_version': package.packageVersion,
        'description': package.description,
        'package_name': package.packageName,
        'creator': package.creator,
        'owner_project': package.ownerProject,
        'tags': package.tags,
        'plans': package.plans,
        'build_generation': package.buildGeneration,
        'status': package.status,
        'is_public': package.isPublic,
        'category': package.category,
        'bindable': package.bindable,
        'api_version': package.apiVersion,
        'package_id': package.packageId,
    }
