# Copyright 2025 Rapyuta Robotics
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

from riocli.v2client import Client
from riocli.config import new_v2_client
from riocli.constants import Colors

import click


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(*args: typing.Any, **kwargs: typing.Any):
        client = new_v2_client(with_project=False)
        name = kwargs.get("organization_name")
        guid = None
        short_id = None

        if name:
            try:
                if name.startswith("org-"):
                    guid = name
                    name, short_id = get_organization_name(client, guid)
                else:
                    guid, short_id = find_organization_guid(client, name)
            except Exception as e:
                click.secho(str(e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs["organization_name"] = name
        kwargs["organization_guid"] = guid
        kwargs["organization_short_id"] = short_id

        f(*args, **kwargs)

    return decorated


def find_organization_guid(client: Client, name: str) -> typing.Tuple[str, str]:
    user = client.get_user()

    for organization in user.spec.organizations:
        if organization.name == name:
            return organization.guid, organization.shortGUID

    raise OrganizationNotFound("User is not part of organization: {}".format(name))


def get_organization_name(client: Client, guid: str) -> typing.Tuple[str, str]:
    user = client.get_user()

    for organization in user.spec.organizations:
        if organization.guid == guid:
            return organization.name, organization.shortGUID

    raise OrganizationNotFound("User is not part of organization: {}".format(guid))


class OrganizationNotFound(Exception):
    def __init__(self, message="organization not found"):
        self.message = message
        super().__init__(self.message)
