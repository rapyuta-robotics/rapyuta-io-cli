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

from riocli.config import Configuration


@click.command()
@click.pass_context
def logout(ctx: click.Context):
    """
    Log out from the Rapyuta.io account using the CLI.
    """

    if not ctx.obj.exists:
        return

    ctx.obj.data.pop('auth_token', None)
    ctx.obj.data.pop('password', None)
    ctx.obj.data.pop('email_id', None)
    ctx.obj.data.pop('project_id', None)
    ctx.obj.save()

    click.secho('Logged out successfully!', fg='green')
