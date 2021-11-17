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
from click_spinner import spinner
from riocli.marketplace.util import parse_dependency_file, api_call, match_dependencies, display_products
from rapyuta_io.utils.rest_client import HttpMethod
from riocli.utils import inspect_with_format

_RESOLVE_SINGLE_PRODUCT_URL_FMT = 'marketplace/product/{}/resolve/{}'
_INSTALL_SINGLE_PRODUCT_URL_FMT = 'marketplace/product/{}/install/{}'
_RESOLVE_BULK_PRODUCT_URL_FMT = 'marketplace/resolve'
_INSTALL_BULK_PRODUCT_URL_FMT = 'marketplace/install'


@click.command('install')
@click.option('--dry-run/--no-dry-run', is_flag=True, help='Flag to enable Dry Run', default=False)
@click.option('--ignore-missing/--no-ignore-missing', is_flag=True, help='Flag to ignore missing dependencies',
              default=False)
@click.option('--format', 'format_type', default='yaml', type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.option('--dependency-file', type=click.File(mode='r', lazy=True), default=None)
@click.argument('rrn', required=False)
@click.argument('version', required=False, default='*')
def install_product(rrn: str, version: str, dry_run: bool, ignore_missing: bool, format_type: str,
                    dependency_file: click.File = None) -> None:
    """
    Install a package from the marketplace
    """
    if not dependency_file and not rrn:
        click.secho('Either one of RRN or Dependency Filename must be provided', fg='red')
        exit(1)
    try:
        if dependency_file is not None:
            dependencies = parse_dependency_file(dependency_file)
            bulk_product(dependencies, dry_run, ignore_missing)
        else:
            single_product(rrn, version, dry_run, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def bulk_product(products: dict, dry_run: bool, ignore_missing: bool) -> None:
    if dry_run:
        bulk_product_dry_run(products)
    else:
        bulk_product_install(products, ignore_missing)


def bulk_product_dry_run(products: dict) -> None:
    data = api_call(_RESOLVE_BULK_PRODUCT_URL_FMT, HttpMethod.POST, products)
    resolved_dependencies = data.get('resolved', None)
    unresolved_dependencies = data.get('no_match', None)
    products = display_products(resolved=resolved_dependencies, unresolved=unresolved_dependencies)
    click.secho(products)


def bulk_product_install(products: dict, ignore_missing: bool) -> None:
    with spinner():
        products = match_dependencies(_RESOLVE_BULK_PRODUCT_URL_FMT, products, ignore_missing)
        api_call(_INSTALL_BULK_PRODUCT_URL_FMT, HttpMethod.POST, products)
    click.secho('packages installed successfully', fg='green')


def single_product(rrn: str, version: str, dry_run: bool, format_type: str) -> None:
    if dry_run:
        single_product_dry_run(rrn, version, format_type)
    else:
        single_product_install(rrn, version)


def single_product_dry_run(rrn: str, version: str, format_type: str) -> None:
    url_format = _RESOLVE_SINGLE_PRODUCT_URL_FMT.format(rrn, version)
    data = api_call(url_format, HttpMethod.GET)
    resolved_dependencies = [data]
    products = display_products(resolved=resolved_dependencies)
    click.secho(products)


def single_product_install(rrn: str, version: str) -> None:
    with spinner():
        url_format = _INSTALL_SINGLE_PRODUCT_URL_FMT.format(rrn, version)
        api_call(url_format, HttpMethod.GET)
    click.secho('package installed successfully', fg='green')



