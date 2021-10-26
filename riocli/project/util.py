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
        client = new_client(with_project=False)
        name = kwargs.pop('project_name')
        guid = None

        if name.startswith('project-'):
            guid = name
            name = None

        if name is None:
            name = get_project_name(client, guid)

        if guid is None:
            guid = find_project_guid(client, name)

        kwargs['project_name'] = name
        kwargs['project_guid'] = guid
        f(**kwargs)

    return decorated


def find_project_guid(client: Client, name: str) -> str:
    projects = client.list_projects()
    for project in projects:
        if project.name == name:
            return project.guid

    click.secho("project not found", fg='red')
    exit(1)


def get_project_name(client: Client, guid: str) -> str:
    project = client.get_project(guid)
    return project.name
