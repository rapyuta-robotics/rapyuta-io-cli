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

_STAGING_ENVIRONMENT_HOSTS = {
    "v11": ("https://v11catalog.apps.okd4v2.okd4beta.rapyuta.io", "https://v11apiserver.apps.okd4v2.okd4beta.rapyuta.io", "https://v11rip.apps.okd4v2.okd4beta.rapyuta.io"),
    "v12": ("https://v12catalog.apps.okd4v2.okd4beta.rapyuta.io", "https://v12apiserver.apps.okd4v2.okd4beta.rapyuta.io", "https://v12rip.apps.okd4v2.okd4beta.rapyuta.io"),
    "v13": ("https://v13catalog.apps.okd4v2.okd4beta.rapyuta.io", "https://v13apiserver.apps.okd4v2.okd4beta.rapyuta.io", "https://v13rip.apps.okd4v2.okd4beta.rapyuta.io"),
    "v14": ("https://v14catalog.apps.okd4v2.okd4beta.rapyuta.io", "https://v14apiserver.apps.okd4v2.okd4beta.rapyuta.io", "https://v14rip.apps.okd4v2.okd4beta.rapyuta.io"),
    "v15": ("https://v15catalog.apps.okd4v2.okd4beta.rapyuta.io", "https://v15apiserver.apps.okd4v2.okd4beta.rapyuta.io", "https://v15rip.apps.okd4v2.okd4beta.rapyuta.io"),
    "qa":  ("https://qacatalog.apps.okd4v2.okd4beta.rapyuta.io",  "https://qaapiserver.apps.okd4v2.okd4beta.rapyuta.io",  "https://qarip.apps.okd4v2.okd4beta.rapyuta.io")
}


@click.command('environment', hidden=True)
@click.argument('name', type=click.Choice(['ga', 'qa', 'v11', 'v12', 'v13', 'v14', 'v15']))
def environment(name: str):
    """
    Sets the Rapyuta.io environment to use (Internal use)
    """

    config = Configuration()

    if name == 'ga':
        config.data.pop('environment', None)
        config.data.pop('catalog_host', None)
        config.data.pop('core_api_host', None)
        config.data.pop('rip_host', None)
    else:
        catalog, core, rip = _STAGING_ENVIRONMENT_HOSTS.get(name)
        config.data['environment'] = name
        config.data['catalog_host'] = catalog
        config.data['core_api_host'] = core
        config.data['rip_host'] = rip

    config.data.pop('project_id', None)
    email = config.data.get('email_id', None)
    password = config.data.get('password', None)
    config.save()

    config.data['auth_token'] = get_token(email, password)

    select_project(config)
    config.save()
