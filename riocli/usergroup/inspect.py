# Copyright 2023 Rapyuta Robotics
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
from click_help_colors import HelpColorsCommand
from rapyuta_io.clients.project import User, Project

from riocli.config import new_client
from riocli.constants import Colors
from riocli.usergroup.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command(
    'inspect',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('group-name')
@click.pass_context
@name_to_guid
def inspect_usergroup(ctx: click.Context, format_type: str, group_name: str, group_guid: str, spinner=None) -> None:
    """
    Inspect the usergroup resource
    """
    try:
        client = new_client()
        org_guid = ctx.obj.data.get('organization_id')
        usergroup = client.get_usergroup(org_guid, group_guid)
        data = make_usergroup_inspectable(usergroup)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def make_usergroup_inspectable(usergroup: typing.Any):
    return {
        'name': usergroup.name,
        'description': usergroup.description,
        'guid': usergroup.guid,
        'creator': usergroup.creator,
        'members': [make_user_inspectable(member) for member in usergroup.members],
        'admins': [make_user_inspectable(admin) for admin in usergroup.admins],
        'projects': [make_project_inspectable(project) for project in getattr(usergroup, 'projects') or []]
    }


def make_user_inspectable(u: User):
    return {
        'guid': u.guid,
        'firstName': u.first_name,
        'lastName': u.last_name,
        'emailID': u.email_id,
        'state': u.state,
        'organizations': u.organizations
    }


def make_project_inspectable(p: Project):
    return {
        'ID': p.id,
        'CreatedAt': p.created_at,
        'UpdatedAt': p.updated_at,
        'DeletedAt': p.deleted_at,
        'name': p.name,
        'guid': p.guid,
        'creator': p.creator
    }
