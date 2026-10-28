# Copyright 2026 Rapyuta Robotics
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
from riocli.role import window
from riocli.role.select import (
    AmbiguousBindingError,
    display_candidates,
    find_bindings,
    select_binding,
)
from riocli.role.util import binding_body, get_domain, get_subject
from riocli.utils.spinner import with_spinner


@click.command(
    "extend",
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
    help="New end of the access window (ISO 8601).",
)
@click.option(
    "--for",
    "duration",
    type=str,
    default=None,
    help="New end as a duration from now, not from the window's start, for example 8h or 30m.",
)
@click.option(
    "--current-not-after",
    type=str,
    default=None,
    help="Select the binding that ends at this time when several match.",
)
@click.pass_context
@with_spinner(text="Extending...")
def extend(
    ctx: click.Context,
    role: str,
    domain: str,
    subject: str,
    not_after: str | None = None,
    duration: str | None = None,
    current_not_after: str | None = None,
    spinner: Yaspin | None = None,
) -> None:
    """Change the end of a time-bound role binding.

    The binding is replaced in one request by a binding with the same Role,
    Subject, domain and start, and the new end. The end can be earlier or
    later than the current one. Use 'rio role unbind' to end access now.

    --for counts from now, not from the window's start, so for a window that
    hasn't started it can end before the start; use --not-after there.

    Subject and Domain take the same form as in 'rio role bind'. When the
    Subject holds more than one time-bound binding of the Role in the domain,
    select one with --current-not-after (its end, as shown by
    'rio role list-bindings').

    Usage Examples:

        Extend access by 30 minutes from now:

        \b
        $ rio role extend project_admin Project:site-01 User:user@rapyuta.io \\
        --for 30m

        \b
        $ rio role extend project_admin Project:site-01 User:user@rapyuta.io \\
        --not-after 2026-10-27T20:00:00+09:00

    """
    assert spinner is not None

    if bool(not_after) == bool(duration):
        raise click.UsageError("use exactly one of --not-after or --for")

    now = window.utcnow()
    end = (
        window.parse_time(not_after)
        if not_after
        else now + window.parse_duration(duration)
    )
    current_end = window.parse_time(current_not_after) if current_not_after else None

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)

        candidates = [
            b
            for b in find_bindings(client, role, get_subject(subject), get_domain(domain))
            if b.spec.not_after is not None
        ]
        current = select_binding(candidates, not_after=current_end)
        if current is None:
            spinner.text = click.style("No time-bound binding matches.", fg=Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

        spec = current.spec
        new = binding_body(
            config.organization_guid,
            spec.role_ref.name,
            (spec.domain.kind, spec.domain.name),
            (spec.subject.kind, spec.subject.name),
            not_before=spec.not_before,
            not_after=end,
            labels=current.metadata.labels,
        )
        result = client.update_role_binding(
            {"oldBindings": [current], "newBindings": [new]}
        )
    except AmbiguousBindingError as e:
        with spinner.hidden():
            display_candidates(e.candidates)
        spinner.text = click.style(
            "More than one time-bound binding matches; "
            "select one with --current-not-after.",
            fg=Colors.RED,
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
    except Exception as e:
        spinner.text = click.style(f"Failed to extend binding: {e}.", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    # Show the window as the server stored it.
    start = spec.not_before
    if result.new_bindings:
        created = result.new_bindings[0].spec
        start, end = created.not_before, created.not_after or end

    spinner.text = click.style(
        f"Binding extended. Window: {window.format_window(start, end)}",
        fg=Colors.GREEN,
    )
    spinner.green.ok(Symbols.SUCCESS)
