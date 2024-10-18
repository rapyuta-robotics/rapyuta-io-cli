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

from riocli.config import Configuration
from riocli.constants import Colors, Symbols
from riocli.utils.context import get_root_context

_STAGING_ENVIRONMENT_SUBDOMAIN = "apps.okd4v2.okd4beta.rapyuta.io"
_NAMED_ENVIRONMENTS = ["v11", "v12", "v13", "v14", "v15", "qa", "dev"]


@click.command("environment", hidden=True)
@click.option(
    "--interactive/--no-interactive",
    "--interactive/--silent",
    is_flag=True,
    type=bool,
    default=True,
    help="Make login interactive",
)
@click.argument("name", type=str)
@click.pass_context
def environment(ctx: click.Context, interactive: bool, name: str):
    """
    Sets the Rapyuta.io environment to use (Internal use only)
    """
    ctx = get_root_context(ctx)

    if name == "ga":
        ctx.obj.data.pop("environment", None)
        ctx.obj.data.pop("catalog_host", None)
        ctx.obj.data.pop("core_api_host", None)
        ctx.obj.data.pop("rip_host", None)
        ctx.obj.data.pop("v2api_host", None)
    else:
        _configure_environment(ctx.obj, name)

    # Remove all relevant data
    ctx.obj.data.pop("project_id", None)
    ctx.obj.data.pop("organization_id", None)
    ctx.obj.data.pop("auth_token", None)
    ctx.obj.save()

    success_msg = click.style(
        "{} Your Rapyuta.io environment is set to {}".format(Symbols.SUCCESS, name),
        fg=Colors.GREEN,
    )

    if not interactive:
        click.echo(success_msg)
        click.secho(
            "{} Please set your organization and project with"
            " `rio organization select ORGANIZATION_NAME`".format(Symbols.WARNING),
            fg=Colors.YELLOW,
        )
        return

    ctx.obj.data["email_id"] = None
    ctx.obj.data["auth_token"] = None

    ctx.obj.save()

    click.secho(
        f"Your environment is set to {name}. Please login again using `rio auth login`",
        fg=Colors.GREEN,
    )


def _configure_environment(config: Configuration, name: str) -> None:
    is_valid_env = name in _NAMED_ENVIRONMENTS or name.startswith("pr")

    if not is_valid_env:
        click.secho(
            "{} Invalid environment: {}".format(Symbols.ERROR, name), fg=Colors.RED
        )
        raise SystemExit(1)

    subdomain = _STAGING_ENVIRONMENT_SUBDOMAIN

    catalog = "https://{}catalog.{}".format(name, subdomain)
    core = "https://{}apiserver.{}".format(name, subdomain)
    rip = "https://{}rip.{}".format(name, subdomain)
    v2api = "https://{}api.{}".format(name, subdomain)

    config.data["environment"] = name
    config.data["catalog_host"] = catalog
    config.data["core_api_host"] = core
    config.data["rip_host"] = rip
    config.data["v2api_host"] = v2api
