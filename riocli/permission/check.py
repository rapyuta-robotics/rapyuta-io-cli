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
from yaspin.api import Yaspin

from riocli.auth.util import find_project_guid
from riocli.config import get_config_from_context, new_v2_client
from riocli.constants import Colors, Symbols
from riocli.role.util import get_domain
from riocli.utils.spinner import with_spinner


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
        client = new_v2_client(with_project=False)
        org_guid = config.organization_guid
        org_name = config.data.get("organization_name")

        user = client.get_myself()
        user_guid = user.metadata.guid

        # Get user permissions
        permissions = client.get_user_permissions(
            user_guid=user_guid, organization_guid=org_guid
        )
        permissions_dict = permissions.model_dump(
            by_alias=True, exclude_none=True, mode="json"
        )

        # Determine domain and resolve project name to GUID if needed
        domain_keys_to_check = []  # List of domain keys to check in order

        if domain:
            # Domain is explicitly provided
            domain_kind, domain_name = get_domain(domain)

            if domain_kind.lower() == "organization":
                # Validate org name matches config context
                if domain_name != org_name:
                    spinner.text = click.style(
                        f"Organization name '{domain_name}' does not match the current organization '{org_name}' in context.",
                        fg=Colors.RED,
                    )
                    spinner.red.fail(Symbols.ERROR)
                    raise SystemExit(1)

                # Check only organization level
                domain_keys_to_check = ["organization"]
                display_domain = f"Organization:{org_name}"

            elif domain_kind.lower() == "project":
                # Resolve project name to GUID
                try:
                    project_guid = find_project_guid(client, domain_name, org_guid)
                except Exception as e:
                    spinner.text = click.style(
                        f"Failed to find project '{domain_name}': {e}", fg=Colors.RED
                    )
                    spinner.red.fail(Symbols.ERROR)
                    raise SystemExit(1)

                # Check if project exists in permissions
                if project_guid not in permissions_dict.get("projects", {}):
                    spinner.text = click.style(
                        f"No permissions found for project '{domain_name}' ({project_guid})",
                        fg=Colors.RED,
                    )
                    spinner.red.fail(Symbols.ERROR)
                    raise SystemExit(1)

                # Check both project and org level (org level is higher)
                domain_keys_to_check = [f"projects.{project_guid}", "organization"]
                display_domain = f"Project:{domain_name}"
            else:
                spinner.text = click.style(
                    f"Permission check not supported for domain kind: {domain_kind}. Only Organization and Project are supported.",
                    fg=Colors.RED,
                )
                spinner.red.fail(Symbols.ERROR)
                raise SystemExit(1)
        else:
            # Domain not provided, use current project from config
            project_guid = config.project_guid
            project_name = config.data.get("project_name")

            if not project_guid:
                # No project in context, check only organization level
                domain_keys_to_check = ["organization"]
                display_domain = f"Organization:{org_name}"
            else:
                # Check if project exists in permissions
                if project_guid not in permissions_dict.get("projects", {}):
                    spinner.text = click.style(
                        f"No permissions found for project '{project_name}'",
                        fg=Colors.RED,
                    )
                    spinner.red.fail(Symbols.ERROR)
                    raise SystemExit(1)

                # Check both project and org level (org level is higher)
                domain_keys_to_check = [f"projects.{project_guid}", "organization"]
                display_domain = f"Project:{project_name}"

        # Check permissions in the domain keys
        authorized = False
        matched_domain = None

        for domain_key in domain_keys_to_check:
            # Navigate to the domain in permissions
            domain_permissions = permissions_dict
            for key in domain_key.split("."):
                domain_permissions = domain_permissions.get(key, {})

            if not domain_permissions:
                continue

            # Check if the resource exists in the domain permissions
            resource_permissions = domain_permissions.get(resource, {})

            if not resource_permissions:
                continue

            # Check if the action exists for the resource
            action_patterns = resource_permissions.get(action, [])

            if not action_patterns:
                continue

            # Check if the instance matches any of the patterns
            for pattern in action_patterns:
                try:
                    if re.match(pattern, instance):
                        authorized = True
                        matched_domain = domain_key
                        break
                except re.error as regex_err:
                    spinner.text = click.style(
                        f"Invalid regex pattern '{pattern}' in permissions for {resource}.{action}: {regex_err}",
                        fg=Colors.RED,
                    )
                    spinner.red.fail(Symbols.ERROR)
                    raise SystemExit(1)

            if authorized:
                break

        if authorized:
            # Determine the level where permission was found
            if matched_domain == "organization":
                permission_level = "organization level"
            else:
                permission_level = "project level"

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

    except SystemExit:
        raise
    except Exception as e:
        spinner.text = click.style(f"Error checking permissions: {e}", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
