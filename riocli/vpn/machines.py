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
from collections.abc import Iterable

import click
from click_help_colors import HelpColorsCommand
from yaspin.core import Yaspin

from riocli.config import new_v2_client
from riocli.constants.colors import Colors
from riocli.constants.symbols import Symbols
from riocli.utils import tabulate_data
from riocli.utils.spinner import with_spinner
from riocli.vpn.util import create_binding, get_binding_labels
from riocli.utils import AliasedGroup


@click.group(
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def machines() -> None:
    """
    Manage Android or iOS devices connected to the VPN.
    """
    pass


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def list_machines() -> None:
    """List all the registered machines on the VPN.

    This command lists all the machines that are registered
    on the VPN using the CLI.
    """
    labels = "machine-key=true"

    try:
        client = new_v2_client()
        machines = client.list_instance_bindings("rio-internal-headscale", labels=labels)
        display_machines(machines=machines)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


@click.command(
    "register",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("name", type=str)
@click.argument("node_key", type=str)
@click.pass_context
@with_spinner(text="Registering machine...")
def register_machine(
    ctx: click.Context, name: str, node_key: str, spinner: Yaspin
) -> None:
    """Register an Android or iOS Tailscale Client in the project's VPN.

    Provide a name and the node key of the machine to register it
    in the project's VPN. The node key can be obtained from the
    Tailscale client running on the machine. The name can be any
    name that you want to give to the machine.
    """
    labels = get_binding_labels()
    labels["machine-key"] = "true"

    node_key = sanitize_node_key(node_key)

    try:
        create_binding(
            ctx,
            name=name,
            machine=node_key,
            ephemeral=False,
            throwaway=False,
            labels=labels,
        )
        spinner.text = click.style(
            f"Machine {name} registered successfully.", fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to register: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "deregister",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("name", type=str)
@with_spinner(text="De-registering machine...")
def deregister_machine(name: str, spinner: Yaspin) -> None:
    """Deregister an Android or iOS Tailscale Client in the Project VPN."""
    try:
        client = new_v2_client()
        client.delete_instance_binding("rio-internal-headscale", name)
        spinner.text = click.style(
            f"Machine {name} de-registered successfully.", fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to de-register: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def display_machines(machines: Iterable, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ["Machine Name"]

    data = []
    for machine in machines:
        data.append([machine.metadata.name])

    tabulate_data(data, headers=headers)


def sanitize_node_key(node_key: str) -> str:
    if node_key.startswith("nodekey:"):
        return node_key

    return f"nodekey:{node_key}"


machines.add_command(register_machine)
machines.add_command(deregister_machine)
machines.add_command(list_machines)
