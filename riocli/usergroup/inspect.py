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

import click

from riocli.config import new_client
from riocli.constants import Colors
from riocli.usergroup.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('group-name')
@click.pass_context
@name_to_guid
def inspect_usergroup(ctx: click.Context, format_type: str, group_name: str, group_guid: str) -> None:
    """
    Inspect the usergroup resource
    """
    try:
        client = new_client()
        org_guid = ctx.obj.data.get('organization_id')
        usergroup = client.get_usergroup(org_guid, group_guid)
        inspect_with_format(usergroup, format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)
