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
from click_spinner import spinner
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.config import Configuration

_INSTALL_URL_FMT = '{}/marketplace/product/{}/install/{}'


@click.command('install')
@click.argument('rrn')
@click.argument('version', required=False, default='*')
def install_product(rrn: str, version: str) -> None:
    """
    Install a package from the marketplace
    """
    try:
        with spinner():
            install_product_with_version(rrn, version)
        click.secho('Package installed successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')


def install_product_with_version(rrn: str, version: str) -> None:
    config = Configuration()
    catalog_host = config.data['catalog_host']
    url = _INSTALL_URL_FMT.format(catalog_host, rrn, version)
    headers = config.get_auth_header()
    response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
    if response.status_code != 200:
        raise Exception('Something went wrong!')
