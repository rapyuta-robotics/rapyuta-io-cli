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
from riocli.utils.selector import show_selection


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
            try:
                guid = find_project_guid(client, name)
            except Exception as e:
                click.secho(str(e), fg='red')
                raise SystemExit(1)

        kwargs['project_name'] = name
        kwargs['project_guid'] = guid
        f(**kwargs)

    return decorated


def find_project_guid(client: Client, name: str) -> str:
    projects = client.list_projects()
    for project in projects:
        if project.name == name:
            return project.guid

    raise ProjectNotFound()


def get_project_name(client: Client, guid: str) -> str:
    project = client.get_project(guid)
    return project.name


def find_organization_guid(client: Client, name: str) -> str:
    organizations = client.get_user_organizations()
    options = {}

    for organization in organizations:
        if organization.name == name:
            options[organization.guid] = '{} ({})'.format(organization.name, organization.url)

    if len(options) == 1:
        return list(options.keys())[0]

    if len(options) == 0:
        raise Exception("User is not part of organization: {}".format(name))

    choice = show_selection(options, header='Following packages were found with the same name')
    return choice


def get_organization_name(client: Client, guid: str) -> str:
    organizations = client.get_user_organizations()
    for organization in organizations:
        if organization.guid == guid:
            return organization.name

    raise OrganizationNotFound("User is not part of organization with guid: {}".format(guid))


def name_to_organization_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        client = new_client(with_project=False)
        name = kwargs.get('organization_name')
        guid = None

        if name:
            try:
                if name.startswith('org-'):
                    guid = name
                    name = get_organization_name(client, guid)
                else:
                    guid = find_organization_guid(client, name)
            except Exception as e:
                click.secho(str(e), fg='red')
                raise SystemExit(1)
        kwargs['organization_name'] = name
        kwargs['organization_guid'] = guid
        f(**kwargs)

    return decorated


class ProjectNotFound(Exception):
    def __init__(self, message='project not found'):
        self.message = message
        super().__init__(self.message)


class OrganizationNotFound(Exception):
    def __init__(self, message='organization not found'):
        self.message = message
        super().__init__(self.message)
