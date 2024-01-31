# Copyright 2023 Rapyuta Robotics
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

from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.config import Configuration


def _api_call(
        method: str,
        path: typing.Union[str, None] = None,
        payload: typing.Union[typing.Dict, None] = None,
        load_response: bool = True,
) -> typing.Dict:
    config = Configuration()
    coreapi_host = config.data.get(
        'core_api_host',
        'https://gaapiserver.apps.okd4v2.prod.rapyuta.io'
    )

    url = '{}/api/organization'.format(coreapi_host)
    if path:
        url = '{}/{}'.format(url, path)

    headers = config.get_auth_header()
    response = RestClient(url).method(method).headers(headers).execute(
        payload=payload)

    data = None

    if load_response:
        data = response.json()

    if not response.ok:
        err_msg = data.get('error')
        raise Exception(err_msg)

    return data


def get_organization_details(organization_guid: str) -> typing.Dict:
    return _api_call(HttpMethod.GET, '{}/get'.format(organization_guid))


def invite_user_to_org(organization_guid: str, user_email: str) -> typing.Dict:
    payload = {'userEmail': user_email}
    return _api_call(HttpMethod.PUT, '{}/adduser'.format(organization_guid), payload=payload)


def remove_user_from_org(organization_guid: str, user_email: str) -> typing.Dict:
    payload = {'userEmail': user_email}
    return _api_call(HttpMethod.DELETE, '{}/removeuser'.format(organization_guid), payload=payload)
