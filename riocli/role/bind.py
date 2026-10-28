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
from rapyuta_io_sdk_v2 import BulkRoleBindingUpdate, Client
from yaspin.api import Yaspin

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.role import window
from riocli.role.util import binding_body, get_domain, get_subject
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
@click.option(
    "--not-before",
    type=str,
    default=None,
    help="Start of the access window (ISO 8601). Defaults to now.",
)
@click.option(
    "--not-after",
    type=str,
    default=None,
    help="End of the access window (ISO 8601).",
)
@click.option(
    "--for",
    "duration",
    type=str,
    default=None,
    help="Length of the access window, for example 8h, 90m, 1d or 2h30m.",
)
@click.pass_context
@with_spinner(text="Binding...")
def bind(
    ctx: click.Context,
    role: str,
    domain: str,
    subject: str,
    not_before: str | None = None,
    not_after: str | None = None,
    duration: str | None = None,
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

    Without window options the binding is permanent. With --not-after or
    --for the binding is time-bound: it grants access from --not-before (or
    now) until the end, and is removed automatically afterwards. Times are
    ISO 8601; a time without an offset is read in your local time zone.
    Time-bound bindings are not supported for UserGroup subjects or domains.

    Usage Examples:

        $ rio role bind project_admin Project:site-01 User:user@rapyuta.io

        Grant access for this shift only:

        \b
        $ rio role bind project_admin Project:site-01 User:user@rapyuta.io \\
        --for 8h

        Grant access for a planned window:

        \b
        $ rio role bind project_admin Project:site-01 User:user@rapyuta.io \\
        --not-before 2026-10-27T09:00:00+09:00 \\
        --not-after 2026-10-27T17:00:00+09:00

    """
    assert spinner is not None

    start, end = window.resolve_window(not_before, not_after, duration, window.utcnow())

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)

        new = binding_body(
            config.organization_guid,
            role,
            get_domain(domain),
            get_subject(subject),
            not_before=start,
            not_after=end,
        )
        result = client.update_role_binding({"newBindings": [new], "oldBindings": []})
    except Exception as e:
        spinner.text = click.style(f"Failed to create binding: {e}.", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    if end is None:
        spinner.text = click.style("Binding created successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
        return

    created = _created_binding(result)
    if created is None or created.spec.not_after is None:
        _remove_unbounded(client, created, f"{role} {domain} {subject}", spinner)
        raise SystemExit(1)

    spinner.text = click.style(
        "Binding created successfully. Window: "
        f"{window.format_window(created.spec.not_before, created.spec.not_after)}",
        fg=Colors.GREEN,
    )
    spinner.green.ok(Symbols.SUCCESS)


def _created_binding(result: BulkRoleBindingUpdate):
    return result.new_bindings[0] if result.new_bindings else None


def _remove_unbounded(client: Client, created, label: str, spinner: Yaspin) -> None:
    """Remove a binding created without the requested window.

    A server without time-bound support ignores notBefore and notAfter and
    creates a permanent binding, which must not be left behind.
    """
    try:
        if created is None:
            raise Exception("the created binding was not returned")

        client.update_role_binding({"oldBindings": [created], "newBindings": []})
    except Exception:
        guid = created.metadata.guid if created is not None else "unknown"
        spinner.text = click.style(
            f"A permanent binding may exist: {label} ({guid})", fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        return

    spinner.text = click.style(
        "This environment does not support time-bound role bindings; "
        "no binding was kept.",
        fg=Colors.RED,
    )
    spinner.red.fail(Symbols.ERROR)
