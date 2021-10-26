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

from rapyuta_io import BuildOperation, BuildOperationInfo
from riocli.build.logs import stream_build_logs
from riocli.build.util import name_to_guid
from riocli.config import new_client


@click.command('trigger')
@click.option('--name', 'trigger_name', type=str, help='Name for the Trigger [optional]', default=None)
@click.option('--tail', 'tail', is_flag=True, type=bool, default=False,
              help='Tail the logs after triggering the build')
@click.argument('build-name', type=str)
@name_to_guid
def trigger_build(build_name: str, build_guid: str, trigger_name: str, tail: bool) -> None:
    """
    Trigger a build request for the build
    """
    try:
        client = new_client()
        with spinner():
            client.trigger_build(BuildOperation([BuildOperationInfo(build_guid, triggerName=trigger_name)]))
        click.secho('Triggered build successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

    if tail:
        stream_build_logs(build_guid)
