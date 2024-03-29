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
import os

import click
from click_help_colors import HelpColorsCommand

from riocli.config import Configuration
from riocli.constants import Colors
from riocli.deployment.util import name_to_guid, select_details

_LOG_URL_FORMAT = '{}/deployment/logstream?tailLines={}&deploymentId={}&componentId={}&executableId={}&podName={}'


@click.command(
    'logs',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--component', 'component_name', default=None,
              help='Name of the component in the deployment')
@click.option('--exec', 'exec_name', default=None,
              help='Name of a executable in the component')
@click.argument('deployment-name', type=str)
@name_to_guid
def deployment_logs(
        component_name: str,
        exec_name: str,
        deployment_name: str,
        deployment_guid: str,
) -> None:
    """
    Stream live logs from cloud deployments (not supported for device deployments)
    """
    try:
        comp_id, exec_id, pod_name = select_details(deployment_guid, component_name, exec_name)
        stream_deployment_logs(deployment_guid, comp_id, exec_id, pod_name)
    except Exception as e:
        click.secho(e, fg=Colors.RED)
        raise SystemExit(1)


def stream_deployment_logs(deployment_id, component_id, exec_id, pod_name=None):
    # FIXME(ankit): The Upstream API ends up timing out when there is no log being written.
    #               IMO the correct behaviour should be to not timeout and keep the stream open.
    config = Configuration()

    url = get_log_stream_url(config, deployment_id, component_id, exec_id, pod_name)
    auth = config.get_auth_header()
    curl = 'curl -H "project: {}" -H "Authorization: {}" "{}"'.format(
        auth['project'], auth['Authorization'], url)
    click.echo(click.style(curl, fg=Colors.BLUE, italic=True))

    os.system(curl)


def get_log_stream_url(config, deployment_id, component_id, exec_id, pod_name=None, tail=50000):
    catalog_host = config.data.get('catalog_host', 'https://gacatalog.apps.okd4v2.prod.rapyuta.io')
    return _LOG_URL_FORMAT.format(catalog_host, tail, deployment_id, component_id, exec_id, pod_name)
