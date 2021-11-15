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
import json

import click
from riocli.marketplace.util import api_call
from rapyuta_io.utils.rest_client import HttpMethod


_LIST_URL_FMT = 'marketplace/products'


@click.command('list')
def list_marketplace() -> None:
    """
    List the marketplace packages
    """
    try:
        packages = api_call(_LIST_URL_FMT, HttpMethod.GET)
        display_marketplace_list(packages=packages, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def display_marketplace_list(packages: list, show_header: bool = True) -> None:
    if show_header:
        click.secho('{:35} {:<35} {:<24} {:40}'.format('RRN', 'Name', 'Publisher', 'Categories'), fg='yellow')

    for package in packages:
        categories = ', '.join([category['category_name'] for category in package['categories']])
        click.secho('{:35} {:<35} {:<24} {:40}'.format(package['rrn'], package['name'], package['publisher']['name'],
                                                       categories))
