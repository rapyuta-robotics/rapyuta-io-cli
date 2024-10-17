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

import click
from munch import unmunchify

from riocli.config import new_v2_client
from riocli.utils import inspect_with_format


@click.command("inspect")
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("instance-name", required=True)
def inspect_instance(format_type: str, instance_name: str):
    """
    Inspect a managedservice instance
    """
    try:
        client = new_v2_client()
        instance = client.get_instance(instance_name)
        inspect_with_format(unmunchify(instance), format_type)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)
