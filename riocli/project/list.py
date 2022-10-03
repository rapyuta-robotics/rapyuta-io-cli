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
from rapyuta_io import Project

from riocli.config import new_client


@click.command('list')
@click.pass_context
def list_project(ctx: click.Context) -> None:
    """
    List all the projects you are part of
    """
    try:
        client = new_client(with_project=False)
        projects = client.list_projects()
        current = ctx.obj.data.get('project_id', None)
        _display_project_list(projects, current, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


def _display_project_list(projects: typing.List[Project], current: str = None, show_header: bool = True) -> None:
    if show_header:
        click.secho('{:40} {:<25} {:<27} {:40}'.
                    format('Project ID', 'Project Name', 'Created At', 'Creator'),
                    fg='yellow')

    for project in projects:
        fg = None
        if project.guid == current:
            fg = 'green'
        click.secho('{:40} {:<25} {:<24} {:40}'.format(project.guid, project.name,
                                                      project.created_at, project.creator), fg=fg)
