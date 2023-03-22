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
import click

from riocli.config import new_v2_client
from riocli.project.util import name_to_guid


@click.command('vpn')
@click.argument('project-name', type=str)
@click.argument('enable', type=bool)
@name_to_guid
def vpn(project_name: str, project_guid: str, enable: bool) -> None:
    """
    Enable or disable VPN on a project

    Example: rio project features vpn "my-project" true
    """
    client = new_v2_client(with_project=False)

    body = {
        "metadata": {
            "projectGUID": project_guid
        },
        "spec": {
            "features": {
                "vpn": enable
            }
        }
    }

    try:
        r = client.update_project(project_guid, body)
    except Exception as e:
        click.secho("❌ Failed: {}".format(e), fg='red')
        raise SystemExit(1) from e

    click.secho("✅ VPN has been {}".format("enabled" if enable else "disabled"), fg='green')
