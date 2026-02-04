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

import click
from rapyuta_io_sdk_v2 import Client

from riocli.config import new_v2_client
from riocli.constants import Colors


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(*args: typing.Any, **kwargs: typing.Any) -> None:
        try:
            client = new_v2_client(with_project=False)
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1)

        group_name = kwargs.pop("group_name")
        group_guid = None

        if group_name.startswith("group-"):
            group_guid = group_name
            group_name = None

        if group_name is None:
            group_name = get_usergroup_name(
                client,
                group_guid=group_guid,
            )

        if group_guid is None:
            try:
                group_guid = find_usergroup_guid(client, group_name)
            except Exception as e:
                click.secho(str(e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs["group_name"] = group_name
        kwargs["group_guid"] = group_guid
        f(*args, **kwargs)

    return decorated


def get_usergroup_name(client: Client, group_guid: str) -> str:
    try:
        usergroup = client.list_user_groups(guid=group_guid)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)
    # v2 shape: metadata.name fallback
    return getattr(getattr(usergroup.items[0], "metadata", None), "name", None)


def find_usergroup_guid(client: Client, group_name: str) -> str:
    result = client.list_user_groups(name=group_name)
    user_group_guid = None
    if result and getattr(result, "items", None):
        user_group = result.items[0] if len(result.items) > 0 else None
        if user_group:
            user_group_guid = getattr(getattr(user_group, "metadata", None), "guid", None)
    if user_group_guid:
        return user_group_guid
    raise UserGroupNotFound()


class UserGroupNotFound(Exception):
    def __init__(self, message="usergroup not found!"):
        self.message = message
        super().__init__(self.message)
