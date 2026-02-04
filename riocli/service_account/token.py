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
from click_help_colors import HelpColorsCommand
from rapyuta_io_sdk_v2 import ServiceAccountToken

from riocli.config import new_v2_client
from riocli.constants.colors import Colors
from riocli.constants.symbols import Symbols
from riocli.service_account.utils import (
    calculate_time_remaining,
    convert_utc_to_offset,
    parse_human_readable_time_to_iso,
)
from riocli.utils import tabulate_data
from riocli.utils.alias import AliasedGroup


@click.group(
    name="token",
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def token() -> None:
    """
    Token operations in service accounts.
    """
    pass


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("account-name", type=str)
@click.option(
    "--offset",
    "offset",
    type=str,
    default="+00:00",
    help="Offset to display time in, e.g. +05:30, -09:00",
)
def list_tokens(
    account_name: str,
    offset: str,
) -> None:
    """
    List of tokens for a service account.
    """
    try:
        client = new_v2_client()
        tokens = client.list_service_account_tokens(name=account_name)
        # for items in walk_pages(client.list_service_account_tokens,name=account_name):
        #     tokens.extend(items)
        headers = ["Token ID", "Expiry At", "Time Remaining"]

        data = []
        for token in tokens.items:
            # Handle None expiry_at (infinite duration tokens)
            if token.expiry_at is None:
                expiry_display = "No expiry (infinite)"
                time_remaining = "Never expires"
            else:
                expiry_display = convert_utc_to_offset(token.expiry_at, offset_str=offset)
                time_remaining = calculate_time_remaining(token.expiry_at)

            data.append(
                [
                    token.id,
                    expiry_display,
                    time_remaining,
                ]
            )
        tabulate_data(data, headers)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


@click.command(
    "create",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("account-name", type=str)
@click.argument("expiry-at", type=str, required=False, default=None)
@click.option(
    "--owner", "owner", type=str, default=None, help="Define owner for the token."
)
@click.option(
    "--offset",
    "offset",
    type=str,
    default="+00:00",
    help="Offset to display time in, e.g. +05:30, -09:00",
)
def create_token(
    account_name: str,
    expiry_at: str | None,
    owner: str,
    offset: str,
) -> None:
    """
    Create a token for a service account.

    The EXPIRY-AT argument supports three formats:

    1. Default expiry (90 days): Leave empty.

    1. Custom expiry: Specify a relative time (e.g., '3 days', '2 hours')
       or an ISO 8601 timestamp (e.g., '2025-12-31T23:59:59+00:00')

    2. No expiry: Specify "0" to create a token with infinite duration.
    """
    try:
        client = new_v2_client()
        iso_expiry_at = parse_human_readable_time_to_iso(expiry_at)

        # Handle the three scenarios
        if iso_expiry_at is None:
            # Default expiry - let backend handle
            token_config = ServiceAccountToken(owner=owner)
        else:
            # Custom expiry or no expiry
            token_config = ServiceAccountToken(
                expiry_at=iso_expiry_at,
                owner=owner,
            )

        token_obj = client.create_service_account_token(
            name=account_name, expiry_at=token_config
        )

        # Handle display of expiry information
        if token_obj.expiry_at is None:
            expiry_msg = "no expiry (infinite duration)"
        else:
            expiry_msg = convert_utc_to_offset(token_obj.expiry_at, offset_str=offset)

        click.secho(
            f"{Symbols.SUCCESS}Token created with expiry at: {expiry_msg}",
            fg=Colors.GREEN,
        )
        click.echo(token_obj.token)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


@click.command(
    "refresh",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("account-name", type=str)
@click.argument("id", type=str)
@click.argument("expiry-at", type=str, required=False, default=None)
@click.option(
    "--offset",
    "offset",
    type=str,
    default="+00:00",
    help="Offset to display time in, e.g. +05:30, -09:00",
)
def refresh_token(
    account_name: str,
    id: str,
    expiry_at: str | None,
    offset: str,
) -> None:
    """
    Refresh an existing token for a service account.

    The EXPIRY-AT argument supports two formats:

    1. Custom expiry: Specify a relative time (e.g., '3 days', '2 hours')
       or an ISO 8601 timestamp (e.g., '2025-12-31T23:59:59+00:00')

    2. No expiry: Leave empty or omit the argument to refresh the token
       with infinite duration
    """
    try:
        client = new_v2_client()
        iso_expiry_at = parse_human_readable_time_to_iso(expiry_at)

        # Handle the three scenarios
        if iso_expiry_at is None:
            # Default expiry - let backend handle
            token_config = ServiceAccountToken()
        else:
            # Custom expiry or no expiry
            token_config = ServiceAccountToken(
                expiry_at=iso_expiry_at,
            )

        token_obj = client.refresh_service_account_token(
            name=account_name, token_id=id, expiry_at=token_config
        )

        # Handle display of expiry information
        if token_obj.expiry_at is None:
            if expiry_at.strip() == "0":
                expiry_msg = "no expiry (infinite duration)"
            else:
                expiry_msg = "default expiry (90 days)"
        else:
            expiry_msg = convert_utc_to_offset(token_obj.expiry_at, offset_str=offset)

        click.secho(
            f"{Symbols.SUCCESS}Token refreshed with expiry at: {expiry_msg}",
            fg=Colors.GREEN,
        )
        click.echo(token_obj.token)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("account-name", type=str)
@click.argument("id", type=str)
def delete_token(
    account_name: str,
    id: str,
) -> None:
    """
    Delete a token for a service account.
    """
    try:
        client = new_v2_client()
        client.delete_service_account_token(name=account_name, token_id=id)
        click.secho(
            f"{Symbols.SUCCESS} Token '{id}' deleted successfully.", fg=Colors.GREEN
        )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


token.add_command(list_tokens)
token.add_command(create_token)
token.add_command(refresh_token)
token.add_command(delete_token)
