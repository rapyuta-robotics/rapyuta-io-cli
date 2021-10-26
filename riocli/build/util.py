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
import functools
import typing

import click
from rapyuta_io import Client

from riocli.config import new_client


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        client = new_client()
        name = kwargs.pop('build_name')
        guid = None

        if name.startswith('build-'):
            guid = name
            name = None

        if name is None:
            name = get_build_name(client, guid)

        if guid is None:
            guid = find_build_guid(client, name)

        kwargs['build_name'] = name
        kwargs['build_guid'] = guid
        f(**kwargs)

    return decorated


def get_build_name(client: Client, guid: str) -> str:
    build = client.get_build(guid=guid)
    return build.buildName


def find_build_guid(client: Client, name: str) -> str:
    builds = client.list_builds()
    for build in builds:
        if build.buildName == name:
            return build.guid

    click.secho("Build not found", fg='red')
    exit(1)
