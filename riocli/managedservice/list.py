# Copyright 2024 Rapyuta Robotics
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
from munch import unmunchify

from riocli.config import new_v2_client
from riocli.utils import tabulate_data


@click.command("list")
def list_instances():
    """
    List all the managedservice instances
    """
    try:
        client = new_v2_client()
        instances = client.list_instances()
        _display_instances(instances)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


def _display_instances(instances: typing.Any):
    headers = ["Provider", "Name", "Created At", "Labels"]

    data = []
    for i in instances:
        m = i.metadata
        data.append([i.spec.provider, m.name, m.createdAt, unmunchify(m.labels)])

    tabulate_data(data, headers)
