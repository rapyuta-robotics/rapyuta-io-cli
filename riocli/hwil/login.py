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
import os

import click
from click_help_colors import HelpColorsCommand

from riocli.constants import Colors, Symbols
from riocli.hwilclient import Client as HwilClient
from riocli.hwilclient import entra
from riocli.utils.context import get_root_context


@click.command(
    "login",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--az",
    "use_az",
    is_flag=True,
    default=False,
    help="Use the token of your logged-in Azure CLI (az login). For boxes without a browser",
)
@click.option(
    "--device-code",
    "use_device_code",
    is_flag=True,
    default=False,
    help="Device-code sign-in (blocked by Rapyuta's tenant policy; prefer --az without a browser)",
)
@click.pass_context
def login(
    ctx: click.Context, use_az: bool = False, use_device_code: bool = False
) -> None:
    """Authenticate with the HWIL API using your company (Microsoft Entra ID) account.

    By default this opens your browser to sign in (if you are already signed
    in, usually one click). The session is refreshed automatically. HWIL no
    longer accepts usernames or passwords.

    On a machine without a browser, run `az login` there and use `--az`.

    In CI, do not log in: export RIO_HWIL_TOKEN. For the HWIL CI service
    principal (GitHub OIDC + az), get it with
    `az account get-access-token --scope api://hwil-api/.default`
    (an app token can't request the HWIL.Access scope). It is read per
    invocation and never written to the rio config.
    """
    ctx = get_root_context(ctx)
    if "environment" in ctx.obj.data:
        os.environ["RIO_CONFIG"] = ctx.obj.filepath

    if use_az and use_device_code:
        click.secho(f"{Symbols.ERROR} Use either --az or --device-code", fg=Colors.RED)
        raise SystemExit(1)

    cache = entra.cache_path(ctx.obj.filepath)
    try:
        if use_az:
            auth = {"mode": "az"}
        elif not use_device_code:
            auth = {"mode": "browser", "account": entra.browser_login(cache)}
        else:
            account = entra.device_code_login(
                cache, lambda m: click.secho(m, fg=Colors.BRIGHT_CYAN)
            )
            auth = {"mode": "device_code", "account": account}

        client = HwilClient(
            token_provider=entra.token_provider(auth, ctx.obj.filepath),
            hwil_host=ctx.obj.data.get("hwil_host"),
        )
        client.list_devices()
    except Exception as e:
        click.secho(f"{Symbols.ERROR} Failed to login to HWIL: {e}", fg=Colors.RED)
        raise SystemExit(1) from e

    ctx.obj.data["hwil_auth"] = auth
    ctx.obj.data.pop("hwil_auth_token", None)  # legacy basic-auth credential
    ctx.obj.save()
    who = f" as {auth['account']}" if auth.get("account") else ""
    click.secho(f"{Symbols.SUCCESS} Successfully logged into HWIL{who}!", fg=Colors.GREEN)


@click.command(
    "logout",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Forget the HWIL session (token cache and login mode)."""
    ctx = get_root_context(ctx)
    entra.logout(entra.cache_path(ctx.obj.filepath))
    ctx.obj.data.pop("hwil_auth", None)
    ctx.obj.data.pop("hwil_auth_token", None)
    ctx.obj.save()
    click.secho(f"{Symbols.SUCCESS} Logged out of HWIL.", fg=Colors.GREEN)
