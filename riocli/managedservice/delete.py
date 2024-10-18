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

from riocli.config import new_v2_client


@click.command("delete")
@click.argument("instance-name", required=True)
def delete_instance(instance_name: str):
    """
    Delete a managedservice instance
    """
    try:
        client = new_v2_client()
        r = client.delete_instance(instance_name)
        if r.get("success", None):
            click.secho("✅ Deleted instance '{}'".format(instance_name), fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)
