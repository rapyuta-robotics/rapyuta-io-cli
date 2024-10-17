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
from riocli.constants import Colors
from riocli.utils import inspect_with_format


@click.command("inspect")
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("network-name")
def inspect_network(format_type: str, network_name: str) -> None:
    """Print the details of a network.

    You can specify the format of the output using the ``--format`` flag.
    The supported formats are ``json`` and ``yaml``. Default is ``yaml``.
    """
    try:
        client = new_v2_client()
        network_obj = client.get_network(network_name)

        if not network_obj:
            click.secho("network not found", fg="red")
            raise SystemExit(1)

        inspect_with_format(unmunchify(network_obj), format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e
