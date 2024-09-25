# Copyright 2024 Rapyuta Robotics
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

from riocli.config import new_client, new_v2_client
from riocli.constants import Colors, Symbols
from riocli.exceptions import LoggedOut
from riocli.v2client import Client as v2Client


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        ctx = click.get_current_context()
        name = kwargs.pop('project_name')
        guid = None

        if name is None:
            guid = ctx.obj.data.get('project_id')
            name = ctx.obj.data.get('project_name')

        if not name:
            raise LoggedOut

        if name.startswith('project-'):
            guid = name
            name = None

        client = new_v2_client(with_project=False)

        if name is None:
            name = get_project_name(client, guid)

        if guid is None:
            try:
                organization = ctx.obj.data.get('organization_id')
                guid = find_project_guid(client, name, organization)
            except Exception as e:
                click.secho('{} {}'.format(Symbols.ERROR, e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs['project_name'] = name
        kwargs['project_guid'] = guid
        f(**kwargs)

    return decorated


def find_project_guid(client: v2Client, name: str,
                      organization: str = None) -> str:
    projects = client.list_projects(query={"name": name}, organization_guid=organization)

    if projects and projects[0].metadata.name == name:
        return projects[0].metadata.guid

    raise ProjectNotFound()


def get_project_name(client: v2Client, guid: str) -> str:
    project = client.get_project(guid)
    return project.metadata.name


def find_organization_guid(client: Client, name: str) -> typing.Tuple[str, str]:
    organizations = client.get_user_organizations()

    for organization in organizations:
        if organization.name == name:
            return organization.guid, organization.short_guid

    raise OrganizationNotFound(
        "User is not part of organization: {}".format(name))


def get_organization_name(client: Client, guid: str) -> typing.Tuple[str, str]:
    organizations = client.get_user_organizations()
    for organization in organizations:
        if organization.guid == guid:
            return organization.name, organization.short_guid

    raise OrganizationNotFound(
        "User is not part of organization: {}".format(guid))


def name_to_organization_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(*args: typing.Any, **kwargs: typing.Any):
        client = new_client(with_project=False)
        name = kwargs.get('organization_name')
        guid = None
        short_id = None

        if name:
            try:
                if name.startswith('org-'):
                    guid = name
                    name, short_id = get_organization_name(client, guid)
                else:
                    guid, short_id = find_organization_guid(client, name)
            except Exception as e:
                click.secho(str(e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs['organization_name'] = name
        kwargs['organization_guid'] = guid
        kwargs['organization_short_id'] = short_id

        f(*args, **kwargs)

    return decorated


class ProjectNotFound(Exception):
    def __init__(self, message='project not found'):
        self.message = message
        super().__init__(self.message)


class OrganizationNotFound(Exception):
    def __init__(self, message='organization not found'):
        self.message = message
        super().__init__(self.message)
