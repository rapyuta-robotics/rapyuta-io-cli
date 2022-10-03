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

from riocli.auth.login import select_project
from riocli.auth.util import get_token
from riocli.config import Configuration
from riocli.utils.context import get_root_context

_STAGING_ENVIRONMENT_SUBDOMAIN = "apps.okd4v2.okd4beta.rapyuta.io"
_NAMED_ENVIRONMENTS = ["v11", "v12", "v13", "v14", "v15", "qa"]


@click.command('environment', hidden=True)
@click.argument('name', type=str)
@click.pass_context
def environment(ctx: click.Context, name: str):
    """
    Sets the Rapyuta.io environment to use (Internal use)
    """

    ctx = get_root_context(ctx)

    if name == 'ga':
        ctx.obj.data.pop('environment', None)
        ctx.obj.data.pop('catalog_host', None)
        ctx.obj.data.pop('core_api_host', None)
        ctx.obj.data.pop('rip_host', None)
    else:
        _configure_environment(ctx.obj, name)

    ctx.obj.data.pop('project_id', None)
    email = ctx.obj.data.get('email_id', None)
    password = ctx.obj.data.get('password', None)
    ctx.obj.save()

    ctx.obj.data['auth_token'] = get_token(email, password)

    select_project(ctx.obj)
    ctx.obj.save()


def _validate_environment(name: str) -> bool:
    valid = name in _NAMED_ENVIRONMENTS or name.startswith('pr')
    if not valid:
        click.secho('Invalid staging environment!', fg='red')
        raise SystemExit(1)


def _configure_environment(config: Configuration, name: str) -> None:
    _validate_environment(name)

    # Named Staging environments don't have hyphen in the name. Ephemeral environments do.
    name = name+'-' if name.startswith('pr') else name

    catalog = 'https://{}catalog.{}'.format(name, _STAGING_ENVIRONMENT_SUBDOMAIN)
    core = 'https://{}apiserver.{}'.format(name, _STAGING_ENVIRONMENT_SUBDOMAIN)
    rip = 'https://{}rip.{}'.format(name, _STAGING_ENVIRONMENT_SUBDOMAIN)

    config.data['environment'] = name
    config.data['catalog_host'] = catalog
    config.data['core_api_host'] = core
    config.data['rip_host'] = rip
