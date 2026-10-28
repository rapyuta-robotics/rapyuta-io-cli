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
from riocli.role.select import (
    AmbiguousBindingError,
    display_candidates,
    find_bindings,
    select_binding,
)
from riocli.role.util import get_domain, get_subject
from riocli.role.window import parse_time
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
@click.option(
    "--not-after",
    type=str,
    default=None,
    help="Remove the time-bound binding that ends at this time (ISO 8601).",
)
@click.option(
    "--permanent",
    is_flag=True,
    default=False,
    help="Remove the permanent binding, when ended windows awaiting cleanup also match.",
)
@click.pass_context
@with_spinner(text="Unbinding...")
def unbind(
    ctx: click.Context,
    role: str,
    domain: str,
    subject: str,
    not_after: str | None = None,
    permanent: bool = False,
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

    A Subject can hold several time-bound bindings of the same Role in the
    same domain, and a permanent one beside windows that have ended but not
    been cleaned up yet. When more than one matches, the command lists them
    and removes nothing; select one with --not-after (its end, as shown by
    'rio role list-bindings') or --permanent.

    Usage Examples:

        $ rio role unbind project_admin Project:site-01 User:user@rapyuta.io

        \b
        $ rio role unbind project_admin Project:site-01 User:user@rapyuta.io \\
        --not-after 2026-10-27T17:00:00+09:00

    """
    assert spinner is not None

    if not_after and permanent:
        raise click.UsageError("use either --not-after or --permanent, not both")

    end = parse_time(not_after) if not_after else None

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)

        candidates = find_bindings(client, role, get_subject(subject), get_domain(domain))
        binding = select_binding(candidates, not_after=end, permanent=permanent)
        if binding is None:
            spinner.text = click.style("Binding does not exist.", fg=Colors.YELLOW)
            spinner.green.ok(Symbols.INFO)
            return

        payload = {"oldBindings": [binding], "newBindings": []}

        _ = client.update_role_binding(payload)
        spinner.text = click.style("Binding deleted successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except AmbiguousBindingError as e:
        with spinner.hidden():
            display_candidates(e.candidates)
        spinner.text = click.style(
            "More than one binding matches; select one with --not-after or --permanent.",
            fg=Colors.RED,
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
    except Exception as e:
        spinner.text = click.style(f"Failed to delete binding: {e}.", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
