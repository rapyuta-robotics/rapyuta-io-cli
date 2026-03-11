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
import re

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2.models.user import ResourceMap
from yaspin.api import Yaspin

from riocli.auth.util import find_organization_guid, find_project_guid
from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.exceptions import NoProjectSelected
from riocli.role.util import get_domain
from riocli.utils.spinner import with_spinner


def resolve_domain(
    client: Client, config, domain: str | None
) -> tuple[str, str, ResourceMap | None]:
    """Resolve the domain string to a (domain_kind, domain_name, resource_map) tuple.

    If domain is explicitly provided, it is resolved independently of config.
    Otherwise, the current org/project from config is used.

    Returns:
        (domain_kind, domain_name, resource_map)
        domain_kind is one of "organization" or "project".
        resource_map is the ResourceMap for the resolved domain.
    """
    domain_kind: str | None = None
    domain_name: str | None = None

    if domain:
        domain_kind, domain_name = get_domain(domain)
    elif config.data.get("project_name"):
        domain_kind, domain_name = "project", config.data.get("project_name")
    elif config.data.get("organization_name"):
        domain_kind, domain_name = "organization", config.data.get("organization_name")
    else:
        raise NoProjectSelected

    if domain_kind is None or domain_kind.lower() not in ["project", "organization"]:
        raise Exception(f"invalid domain {domain}")

    if domain_kind.lower() == "organization":
        org_guid, _ = find_organization_guid(client, domain_name)
        permissions = client.get_user_permissions(
            user_guid="", organization_guid=org_guid
        )

        return domain_kind, domain_name, permissions.organization

    # Domain must be Project
    project_guid = find_project_guid(client, domain_name)
    user = client.get_myself()
    org_guid = next(
        (
            p.organization_guid
            for p in (user.spec.projects or [])
            if p.guid == project_guid
        ),
        None,
    )
    if not org_guid:
        raise Exception(f"Could not determine organization for project '{domain_name}'")

    permissions = client.get_user_permissions(user_guid="", organization_guid=org_guid)

    project_map = (permissions.projects or {}).get(project_guid)
    if project_map is None:
        raise Exception(
            f"No permissions found for project '{domain_name}' ({project_guid})"
        )

    return domain_kind, domain_name, project_map


def check_permission(
    resource_map: ResourceMap | None,
    resource: str,
    action: str,
    instance: str,
) -> bool:
    """Return True if the resource_map grants permission to perform action on instance.

    Checks whether any of the stored regex patterns for resource.action match instance.
    """
    patterns = []
    if resource_map:
        patterns = resource_map.get(resource, {}).get(action, [])

    return any(re.match(pattern, instance) for pattern in patterns)


@click.command(
    "check",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("resource", type=str)
@click.argument("action", type=str)
@click.option(
    "--domain",
    "-d",
    type=str,
    default=None,
    help="Domain in format 'Kind:Name' (e.g., 'Organization:my-org' or 'Project:my-project'). Defaults to current project from config.",
)
@click.option(
    "--instance",
    "-i",
    type=str,
    default=".*",
    help="Resource instance name or pattern (default: .*)",
)
@click.pass_context
@with_spinner(text="Checking...")
def check(
    ctx: click.Context,
    resource: str,
    action: str,
    domain: str | None,
    instance: str,
    spinner: Yaspin | None = None,
) -> None:
    """\b
    Check if user has permission to perform an action on a resource.

    The check command verifies if the current user has permission to perform
    a given action on a specific resource instance within a domain.

    If domain is not specified, the command uses the current project from
    config and checks permissions at both project and organization levels.

    The Domain (when specified) is a colon (':') separated string:

    \b
    * The first part defines the Domain's Kind: Organization or Project.
    * The second part defines the Domain's name.

    Examples: "Organization:my-org", "Project:my-project".

    \b
    Usage Examples:
        Check in current project

            $ rio permission check device get_device

        Check specific instance

            $ rio permission check device get_device -i device-123

        Check in organization

            $ rio permission check device get_device -d Organization:my-org

        Check in project

            $ rio permission check deployment get -d Project:my-project

        Check with pattern

            $ rio permission check deployment get -i "^prod-.*"
    """
    assert spinner is not None

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        domain_kind, domain_name, permissions = resolve_domain(client, config, domain)
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    authorized = check_permission(permissions, resource, action, instance)
    display_domain = f"{domain_kind.capitalize()}:{domain_name}"
    permission_level = (
        "organization level" if domain_kind.lower() == "organization" else "project level"
    )

    if authorized:
        spinner.text = click.style(
            f"Authorized: Can perform '{action}' on '{resource}:{instance}' in {display_domain} ({permission_level})",
            fg=Colors.GREEN,
        )
        spinner.green.ok(Symbols.SUCCESS)
    else:
        spinner.text = click.style(
            f"Unauthorized: No permission to perform '{action}' on '{resource}:{instance}' in {display_domain}",
            fg=Colors.RED,
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
