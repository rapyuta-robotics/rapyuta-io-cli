# Copyright 2023 Rapyuta Robotics
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
from dateutil import parser

from riocli.config import new_client, new_v2_client
from riocli.disk.list import get_all_disks
from riocli.organization.utils import get_organization_details
from riocli.utils import tabulate_data
from riocli.utils.context import get_root_context
from riocli.utils.spinner import with_spinner

DEPLOYMENTS = 'deployments'
PACKAGES = 'packages'
SECRETS = 'secrets'
DEVICES = 'devices'
DISKS = 'disks'
STATIC_ROUTES = 'staticroutes'
ROUTED_NETWORKS = 'routednetworks'
NATIVE_NETWORKS = 'nativenetworks'

SKIP_LIST = [
    DEPLOYMENTS,
    PACKAGES,
    SECRETS,
    DEVICES,
    DISKS,
    STATIC_ROUTES,
    ROUTED_NETWORKS,
    NATIVE_NETWORKS
]


@click.command('summary')
@click.option(
    '--skip',
    prompt_required=False,
    multiple=True,
    type=click.Choice(SKIP_LIST),
    help='Skip the resources you do not want to display',
)
@click.pass_context
@with_spinner(text="This may take a while...", timer=True)
def summary(ctx: click.Context, skip: list = None, spinner=None) -> None:
    """
    Prints a summary of the currently selected organization.

    This commands prints the summary of the organization in
    the context of the currently logged-in user. You will only
    see the summary of everything you have access to.
    """
    ctx = get_root_context(ctx)

    organization_id = ctx.obj.data.get('organization_id')

    # Convert skip list to a map for a quick lookup
    skip = {s: None for s in (skip or [])}

    try:
        prepare_summary(organization_id, skip, spinner)
    except Exception as e:
        spinner.red.text = 'Failed to generate summary'
        spinner.red.fail('❌')
        raise SystemExit(1) from e


def prepare_summary(organization_id, skip: dict = None, spinner=None):
    """
    Prepares and prints the summary
    """
    data = gather_details(organization_id, skip, spinner)

    organization = data.get('organization')
    project_resources = data.get('project_resources')

    rows = []
    for name, resources in project_resources.items():
        row = [click.style(name, fg='blue', bold=True)]

        if PACKAGES not in skip:
            row.append(len(resources.get(PACKAGES)))
        if DEPLOYMENTS not in skip:
            row.append(len(resources.get(DEPLOYMENTS)))
        if DEVICES not in skip:
            row.append(len(resources.get(DEVICES)))
        if SECRETS not in skip:
            row.append(len(resources.get(SECRETS)))
        if DISKS not in skip:
            row.append(len(resources.get(DISKS)))
        if NATIVE_NETWORKS not in skip:
            row.append(len(resources.get(NATIVE_NETWORKS)))
        if ROUTED_NETWORKS not in skip:
            row.append(len(resources.get(ROUTED_NETWORKS)))
        if STATIC_ROUTES not in skip:
            row.append(len(resources.get(STATIC_ROUTES)))

        rows.append(row)

    spinner.green.text = 'Your organization summary is ready'
    spinner.green.ok('✅')

    # Display organization details
    print_organization_details(organization)
    # Display project resources table
    tabulate_data(rows, headers=generate_headers(skip))
    click.echo()  # Line break
    click.secho('^ Only succeeded deployments and online devices')
    click.echo()  # Line break


def print_organization_details(organization: dict):
    organization_name = organization.get('name')
    users = organization.get('users')
    organization_admin = ''
    for u in users:
        if u.get('guid') == organization.get('creator'):
            organization_admin = '{} {} ({})'.format(
                u.get('firstName'),
                u.get('lastName'),
                u.get('emailID'),
            )
            break

    created_at = parser.parse(organization.get('CreatedAt'))

    click.echo()
    title = click.style('Organization Details', bold=True, underline=True)
    click.secho(title, fg='yellow')
    click.secho('  Name: {}'.format(organization_name))
    click.secho('  Admin: {}'.format(organization_admin))
    click.secho('  Users: {}'.format(len(users)))
    click.secho('  Projects: {}'.format(len(organization.get('projects'))))
    click.secho(
        '  Created: {}'.format(created_at.strftime('%Y-%m-%d %H:%M:%S')))
    click.secho('  Status: {}'.format(organization.get('state')))
    click.echo()


def generate_headers(skip: dict) -> list:
    """
    Generates table header based on the skip list
    """
    headers = ['Project']

    if PACKAGES not in skip:
        headers.append('Packages')
    if DEPLOYMENTS not in skip:
        headers.append('Deployments^')
    if DEVICES not in skip:
        headers.append('Devices^')
    if SECRETS not in skip:
        headers.append('Secrets')
    if DISKS not in skip:
        headers.append('Disks')
    if NATIVE_NETWORKS not in skip:
        headers.append('Native N/W')
    if ROUTED_NETWORKS not in skip:
        headers.append('Routed N/W')
    if STATIC_ROUTES not in skip:
        headers.append('Static Routes')

    return headers


def gather_details(organization_id, skip, spinner=None):
    """
    Gathers details of every project in the organization
    """
    spinner.text = 'Fetching organization details...'
    organization = get_organization_details(organization_id)

    spinner.text = 'Fetching list of all projects in the organization...'
    projects = get_projects(organization_id, spinner)

    project_resources = {}

    total_projects = len(projects)
    for i, p in enumerate(projects):
        project_guid = p.metadata.guid
        project_name = p.metadata.name
        styled_project_name = click.style(project_name, fg='blue')
        spinner.text = 'Fetching resources in project {}...'.format(
            styled_project_name)
        progress = '{}/{}'.format(i + 1, total_projects)
        resources = gather_project_resources(
            project_guid, styled_project_name, progress, skip, spinner)

        project_resources[project_name] = resources

    organization['projects'] = projects

    return {
        "organization": organization,
        "project_resources": project_resources,
    }


def get_projects(organization_id, spinner=None):
    v2 = new_v2_client()
    return v2.list_projects(organization_guid=organization_id)


def gather_project_resources(
        project_guid: str,
        project_name: str,
        progress: str,
        skip: dict,
        spinner=None
):
    """
    Gathers all resources in project based on the skip list
    """
    v1 = new_client(with_project=False)
    v1.set_project(project_guid)

    result = {}

    fetching = '[{}]({}) Fetching '.format(progress, project_name) + '{} ...'

    if DEPLOYMENTS not in skip:
        spinner.text = fetching.format(DEPLOYMENTS)
        result[DEPLOYMENTS] = v1.get_all_deployments(phases=['Succeeded'])

    if PACKAGES not in skip:
        spinner.text = fetching.format(PACKAGES)
        result[PACKAGES] = v1.get_all_packages()

    if SECRETS not in skip:
        spinner.text = fetching.format(SECRETS)
        result[SECRETS] = v1.list_secrets()

    if DEVICES not in skip:
        spinner.text = fetching.format(DEVICES)
        result[DEVICES] = v1.get_all_devices()

    if STATIC_ROUTES not in skip:
        spinner.text = fetching.format(STATIC_ROUTES)
        result[STATIC_ROUTES] = v1.get_all_static_routes()

    if DISKS not in skip:
        spinner.text = fetching.format(DISKS)
        result[DISKS] = get_all_disks(project_guid)

    if NATIVE_NETWORKS not in skip:
        spinner.text = fetching.format(NATIVE_NETWORKS)
        result[NATIVE_NETWORKS] = v1.list_native_networks()

    if ROUTED_NETWORKS not in skip:
        spinner.text = fetching.format(ROUTED_NETWORKS)
        result[ROUTED_NETWORKS] = v1.get_all_routed_networks()

    return result
