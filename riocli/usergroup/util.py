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

from riocli.config import new_client
from riocli.constants import Colors


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(*args: typing.Any, **kwargs: typing.Any) -> None:
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1)

        group_name = kwargs.pop("group_name")
        group_guid = None

        ctx = args[0]
        org_guid = ctx.obj.data.get("organization_id")

        if group_name.startswith("group-"):
            group_guid = group_name
            group_name = None

        if group_name is None:
            group_name = get_usergroup_name(client, org_guid, group_guid)

        if group_guid is None:
            try:
                group_guid = find_usergroup_guid(client, org_guid, group_name)
            except Exception as e:
                click.secho(str(e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs["group_name"] = group_name
        kwargs["group_guid"] = group_guid
        f(*args, **kwargs)

    return decorated


def get_usergroup_name(client: Client, org_guid: str, group_guid: str) -> str:
    try:
        usergroup = client.get_usergroup(org_guid, group_guid)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

    return usergroup.name


def find_usergroup_guid(client: Client, org_guid, group_name: str) -> str:
    user_groups = client.list_usergroups(org_guid=org_guid)

    for g in user_groups:
        if g.name == group_name:
            return g.guid

    raise UserGroupNotFound()


class UserGroupNotFound(Exception):
    def __init__(self, message="usergroup not found!"):
        self.message = message
        super().__init__(self.message)
