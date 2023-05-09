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
import typing

import click
from munch import unmunchify
from rapyuta_io import Project

from riocli.config import new_v2_client
from riocli.project.util import name_to_organization_guid
from riocli.utils import tabulate_data


@click.command('list')
@click.option('--organization', 'organization_name',
              help='Pass organization name for which project needs to be created. Default will be current organization')
@click.option('--wide', '-w', is_flag=True, default=False,
              help='Print more details', type=bool)
@click.pass_context
@name_to_organization_guid
def list_project(ctx: click.Context = None, organization_guid: str = None,
                 organization_name: str = None, wide: bool = False) -> None:
    """
    List all the projects you are part of
    """
    try:
        client = new_v2_client(with_project=False)
        projects = client.list_projects(organization_guid=organization_guid)
        projects = sorted(projects, key=lambda p: p.metadata.name.lower())
        current = ctx.obj.data.get('project_id', None)
        _display_project_list(projects, current, show_header=True, wide=wide)
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


def _display_project_list(projects: typing.List[Project], current: str = None,
                          show_header: bool = True,
                          wide: bool = False) -> None:
    headers = []
    if show_header:
        headers = ['Project ID', 'Project Name', 'Status']
        if wide:
            headers.extend(['Created At', 'Creator', "Features"])

    data = []
    for project in projects:
        metadata = project.metadata
        fg = None
        if metadata.guid == current:
            fg = 'green'

        row = [metadata.guid, metadata.name, project.status.status]
        if wide:
            row.extend([metadata.createdAt, metadata.creatorGUID,
                        unmunchify(project.spec.features)])
        data.append([click.style(v, fg=fg) for v in row])

    tabulate_data(data, headers)
