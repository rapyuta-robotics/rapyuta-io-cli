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
import os

import click

from riocli.build.util import name_to_guid
from riocli.config import Configuration

_LOG_URL_FORMAT = '{}/logs/build?buildRequestId={}'


@click.command('logs')
@click.argument('build-name', type=str)
@name_to_guid
def build_logs(build_name: str, build_guid: str) -> None:
    """
    Stream the live logs for the Build
    """
    try:
        stream_build_logs(build_guid)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def stream_build_logs(build_guid: str) -> None:
    config = Configuration()
    client = config.new_client()
    build = client.get_build(build_guid, include_build_requests=True)
    build_request_id = build.buildRequests[-1]['requestId']
    url = get_log_stream_url(config, build_request_id)
    auth = config.get_auth_header()
    curl = 'curl -H "project: {}" -H "Authorization: {}" "{}"'.format(auth['project'], auth['Authorization'], url)
    click.secho(curl, fg='blue')
    os.system(curl)


def get_log_stream_url(config: Configuration, build_request_id: str) -> str:
    catalog_host = config.data.get('catalog_host', 'https://gacatalog.apps.rapyuta.io')
    return _LOG_URL_FORMAT.format(catalog_host, build_request_id)
