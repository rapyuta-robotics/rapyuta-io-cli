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
from click_spinner import spinner

from riocli.config import new_client
from riocli.constants import Colors
from riocli.usergroup.util import name_to_guid


@click.command('delete')
@click.option('--force', '-f', '--silent', 'force', is_flag=True,
              default=False, help='Skip confirmation')
@click.argument('group-name')
@click.pass_context
@name_to_guid
def delete_usergroup(ctx: click.Context, group_name: str, group_guid: str, force: bool) -> None:
    """
    Delete usergroup from organization
    """
    if not force:
        click.confirm('Deleting usergroup {} ({})'.format(group_name, group_guid), abort=True)

    try:
        client = new_client()
        org_guid = ctx.obj.data.get('organization_id')
        with spinner():
            client.delete_usergroup(org_guid, group_guid)
        click.echo(click.style('Usergroup deleted syccessfully!', fg=Colors.GREEN))
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


