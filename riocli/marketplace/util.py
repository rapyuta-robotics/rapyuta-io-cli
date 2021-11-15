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
import yaml
import json
from riocli.utils import inspect_with_format
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod
from riocli.config import Configuration


def parse_dependency_file(dependency_file: click.File) -> typing.Dict:
    input_dependency_dict = yaml.load(dependency_file, Loader=yaml.FullLoader)
    output_dependency_list = []
    for dependency in input_dependency_dict['dependencies']:
        output_dependency_list.append({'rrn': dependency['name'], 'version_spec': dependency['version']})
    output_dependency_dict = {'requires': output_dependency_list}
    return output_dependency_dict


def api_call(route: str, method: str, payload: typing.Dict = None) -> typing.Any:
    config = Configuration()
    catalog_host = config.data.get('catalog_host', 'https://gacatalog.apps.rapyuta.io')
    url = '{}/{}'.format(catalog_host, route)
    headers = config.get_auth_header()
    response = RestClient(url).method(method).headers(headers).execute(payload=payload)
    data = json.loads(response.text)
    if not response.ok:
        raise Exception(data['error'])
    return data


def match_dependencies(url: str, dependencies: typing.Dict, ignore_missing: bool) -> typing.Dict:
    data = api_call(url, HttpMethod.POST, dependencies)
    unresolved_dependencies = data.get('no_match')
    if unresolved_dependencies:
        if ignore_missing:
            return get_resolved_dependencies(dependencies, unresolved_dependencies)
        data = display_products(unresolved=unresolved_dependencies, show_header=False)
        raise Exception('Found following unresolved dependencies:\n' + data)
    else:
        return dependencies


def get_resolved_dependencies(dependencies: typing.Dict, unresolved: typing.List) -> typing.Dict:
    resolved_dependencies = {'requires': []}
    unresolved_rrn_list = []
    for product in unresolved:
        unresolved_rrn_list.append(product['rrn'])
    for product in dependencies['requires']:
        if product['rrn'] not in unresolved_rrn_list:
            resolved_dependencies['requires'].append(product)
    return resolved_dependencies


def display_products(resolved: typing.List = None, unresolved: typing.List = None, single_product: typing.Dict = None,
                     show_header: bool = True) -> str:
    product_str = ''
    if show_header:
        product_str += '{:45} {:15} {:10}\n'.format('RRN', 'Version', 'Match')
    if resolved:
        for dependency in resolved:
            product_str += '{:45} {:15} {:10}\n'.format(dependency['product']['rrn'], dependency['semver'], '✔️')
    if unresolved:
        for dependency in unresolved:
            product_str += '{:45} {:15} {:10}\n'.format(dependency['rrn'], dependency['version_spec'], '❌')
    return product_str
