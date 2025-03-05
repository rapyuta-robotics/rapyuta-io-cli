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
from typing import Optional, Callable, Any

import click

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.exceptions import LoggedOut
from riocli.v2client import Client as v2Client


def name_to_guid(f: Callable) -> Callable:
    @functools.wraps(f)
    def decorated(**kwargs: Any):
        ctx = click.get_current_context()
        name = kwargs.pop("project_name")
        guid = None

        if name is None:
            guid = ctx.obj.data.get("project_id")
            name = ctx.obj.data.get("project_name")

        if not name:
            raise LoggedOut

        if name.startswith("project-"):
            guid = name
            name = None

        client = new_v2_client(with_project=False)

        if name is None:
            name = get_project_name(client, guid)

        if guid is None:
            try:
                organization = ctx.obj.data.get("organization_id")
                guid = find_project_guid(client, name, organization)
            except Exception as e:
                click.secho("{} {}".format(Symbols.ERROR, e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs["project_name"] = name
        kwargs["project_guid"] = guid
        f(**kwargs)

    return decorated


def find_project_guid(
    client: v2Client, name: str, organization: Optional[str] = None
) -> str:
    projects = client.list_projects(
        query={"name": name},
        organization_guid=organization,
    )

    if projects and projects[0].metadata.name == name:
        return projects[0].metadata.guid

    raise ProjectNotFound()


def get_project_name(client: v2Client, guid: str) -> str:
    project = client.get_project(guid)
    return project.metadata.name


class ProjectNotFound(Exception):
    def __init__(self, message="project not found"):
        self.message = message
        super().__init__(self.message)
