# Copyright 2025 Rapyuta Robotics
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
from click_help_colors import HelpColorsCommand
from munch import Munch
from rapyuta_io_sdk_v2 import Client
from yaspin.api import Yaspin

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.role.util import get_domain, get_subject
from riocli.utils.spinner import with_spinner


@click.command(
    "unbind",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("role", type=str)
@click.argument("domain", type=str)
@click.argument("subject", type=str)
@click.pass_context
@with_spinner(text="Unbinding...")
def unbind(
    ctx: click.Context,
    role: str,
    domain: str,
    subject: str,
    spinner: Yaspin | None = None,
) -> None:
    """Unbind a role from the Subject.

    The unbind command removes the Role from the Subject in the given domain.

    The Subject is a colon (':') separated string:

    * The first part defines the Subject's Kind: User, UserGroup,
      ServiceAccount.

    * The second part defines the Subject's name:
      Email (User), Name (UserGroup, ServiceAccount).

    Examples: User:user@rapyuta.io, UserGroup:roboops, ServiceAccount:deployer.

    The Domain is a colon (':') separated string:

    * The first part defines the Domain's Kind: Organization, Project,
      UserGroup.

    * The second part defines the Domain's name.

    Examples: Project:site-01, "Organization:Product JP Staging",
    "UserGroup:roboops".

    Usage Examples:

        $ rio role unbind project_admin Project:site-01 User:user@rapyuta.io

    """
    assert spinner is not None

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)

        domain_kind, domain_name = get_domain(domain)
        subject_kind, subject_name = get_subject(subject)

        binding = _find_role_binding(
            client, role, subject_kind, subject_name, domain_kind, domain_name
        )
        if binding is None:
            spinner.text = click.style("Binding does not exist.", fg=Colors.YELLOW)
            spinner.green.ok(Symbols.INFO)
            return

        payload = {"oldBindings": [binding], "newBindings": []}

        _ = client.update_role_binding(payload)
        spinner.text = click.style("Binding deleted successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to delete binding: {e}.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.ERROR)
        raise SystemExit(1)


def _find_role_binding(
    client: Client,
    role: str,
    subject_kind: str,
    subject_name: str,
    domain_kind: str,
    domain_name: str,
) -> Munch | None:
    role_bindings = client.list_role_bindings(
        role_names=role,
        subject_names=subject_name,
        subject_kinds=subject_kind,
        domain_names=domain_name,
        domain_kinds=domain_kind,
    )

    if len(role_bindings.items) == 0:
        return

    return role_bindings.items[0]
