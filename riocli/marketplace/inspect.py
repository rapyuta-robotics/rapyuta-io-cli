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
from riocli.utils import inspect_with_format

_SKU_URL_FMT = '{}/marketplace/sku/{}@{}/detail'
_PRODUCT_FMT = '{}/marketplace/product/{}/detail'


@click.command('inspect')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('rrn')
@click.argument('version', required=False)
def inspect_marketplace(format_type: str, rrn: str, version: str = None) -> None:
    """
    Inspect the marketplace package
    """
    try:
        product = get_product(rrn=rrn, version=version)
        inspect_with_format(product, format_type=format_type)
    except Exception as e:
        click.secho(str(e), fg='red')


def get_product(rrn: str, version: str = None) -> dict:
    config = Configuration()
    catalog_host = config.data['catalog_host']
    if version is not None:
        url = _SKU_URL_FMT.format(catalog_host, rrn, version)
    else:
        url = _PRODUCT_FMT.format(catalog_host, rrn)
    headers = config.get_auth_header()
    response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
    if response.status_code != 200:
        raise Exception('Something went wrong!')
    return json.loads(response.text)
