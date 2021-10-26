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
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.config import Configuration

_LIST_URL_FMT = '{}/marketplace/products'


@click.command('list')
@click.option('--format', '-f', 'format_type', default='table',
              type=click.Choice(['json', 'yaml', 'table'], case_sensitive=False))
def list_marketplace(format_type: str) -> None:
    """
    List the marketplace packages
    """
    try:
        config = Configuration()
        catalog_host = config.data['catalog_host']
        url = _LIST_URL_FMT.format(catalog_host)
        headers = config.get_auth_header()
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        if response.status_code != 200:
            raise Exception('Something went wrong!')
        packages = json.loads(response.text)
        display_marketplace_list(packages=packages, format_type=format_type, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')


def display_marketplace_list(packages: list, format_type: str, show_header: bool = True):
    if show_header:
        click.secho('{:35} {:<35} {:<24} {:40}'.format('RRN', 'Name', 'Publisher', 'Categories'), fg='yellow')

    for package in packages:
        categories = ', '.join([category['category_name'] for category in package['categories']])
        click.secho('{:35} {:<35} {:<24} {:40}'.format(package['rrn'], package['name'], package['publisher']['name'],
                                                       categories))
