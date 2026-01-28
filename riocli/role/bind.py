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
from yaspin.api import Yaspin

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.role.util import get_domain, get_subject
from riocli.utils.spinner import with_spinner


@click.command(
    "bind",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("role", type=str)
@click.argument("domain", type=str)
@click.argument("subject", type=str)
@click.pass_context
@with_spinner(text="Binding...")
def bind(
    ctx: click.Context,
    role: str,
    domain: str,
    subject: str,
    spinner: Yaspin | None = None,
) -> None:
    """Bind a role to a Subject.

    The bind command binds a Subject to a Role in the given domain.

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

        $ rio role bind project_admin Project:site-01 User:user@rapyuta.io

    """
    assert spinner is not None

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)

        domain_kind, domain_name = get_domain(domain)
        subject_kind, subject_name = get_subject(subject)

        binding = {
            "newBindings": [
                {
                    "metadata": {
                        "organizationGUID": config.organization_guid,
                    },
                    "spec": {
                        "roleRef": {
                            "name": role,
                        },
                        "domain": {
                            "kind": domain_kind,
                            "name": domain_name,
                        },
                        "subject": {
                            "kind": subject_kind,
                            "name": subject_name,
                        },
                    },
                }
            ],
            "oldBindings": [],
        }

        _ = client.update_role_binding(binding=binding)
        spinner.text = click.style("Binding created successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to create binding: {e}.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.ERROR)
        raise SystemExit(1)
