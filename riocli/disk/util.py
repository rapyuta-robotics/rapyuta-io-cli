# Copyright 2022 Rapyuta Robotics
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
import typing
import functools
import click

from rapyuta_io import Client
from rapyuta_io.utils.rest_client import RestClient, HttpMethod

from riocli.config import Configuration, new_client


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        client = new_client()
        name = kwargs.pop('disk_name')
        guid = None

        if name.startswith('disk-'):
            guid = name
            name = None

        if name is None:
            name = get_disk_name(client, guid)

        if guid is None:
            try:
                guid = find_disk_guid(client, name)
            except Exception as e:
                click.secho(str(e), fg='red')
                raise SystemExit(1)

        kwargs['disk_name'] = name
        kwargs['disk_guid'] = guid
        f(**kwargs)

    return decorated


def get_disk_name(client: Client, guid: str) -> str:
    disk = _api_call(HttpMethod.GET, guid=guid)
    return disk['name']


def find_disk_guid(client: Client, name: str) -> str:
    try: 
        disks = _api_call(HttpMethod.GET)
        for disk in disks:
            if disk['name'] == name:
                return disk['guid']
        raise DiskNotFound()
    except Exception:
        raise DiskNotFound()


def _api_call(method: str, guid: typing.Union[str, None] = None,
              payload: typing.Union[typing.Dict, None] = None, load_response: bool = True,
) -> typing.Any:
    config = Configuration()
    catalog_host = config.data.get('catalog_host', 'https://gacatalog.apps.rapyuta.io')
    url = '{}/disk'.format(catalog_host)
    if guid:
        url = '{}/{}'.format(url, guid)
    headers = config.get_auth_header()
    response = RestClient(url).method(method).headers(headers).execute(payload=payload)
    data = None
    err_msg = 'error in the api call'
    if load_response:
        data = json.loads(response.text)

    if not response.ok:
        err_msg = data.get('error')
        raise Exception(err_msg)
    return data


class DiskNotFound(Exception):
    def __init__(self, message='disk not found!'):
        self.message = message
        super().__init__(self.message)
