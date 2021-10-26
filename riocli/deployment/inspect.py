# Copyright 2021 Rapyuta Robotics
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
from rapyuta_io.clients.deployment import Deployment

from riocli.config import new_client
from riocli.deployment.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('deployment-name')
@name_to_guid
def inspect_deployment(format_type: str, deployment_name: str, deployment_guid: str) -> None:
    """
    Inspect the deployment resource
    """
    try:
        client = new_client()
        deployment = client.get_deployment(deployment_guid)
        data = make_deployment_inspectable(deployment)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def make_deployment_inspectable(deployment: Deployment) -> dict:
    return {
        'created_at': deployment.CreatedAt,
        'updated_at': deployment.UpdatedAt,
        'deleted_at': deployment.DeletedAt,
        'package_id': deployment.packageId,
        'package_name': deployment.packageName,
        'package_api_version': deployment.packageAPIVersion,
        'owner_project': deployment.ownerProject,
        'creator': deployment.creator,
        'plan_id': deployment.planId,
        'deployment_id': deployment.deploymentId,
        'current_generation': deployment.currentGeneration,
        'bindable': deployment.bindable,
        'name': deployment.name,
        'parameters': deployment.parameters,
        'provision_context': deployment.provisionContext,
        'component_instance_ids': deployment.componentInstanceIds,
        'dependent_deployments': deployment.dependentDeployments,
        'labels': deployment.labels,
        'in_use': deployment.inUse,
        'used_by': deployment.usedBy,
        'phase': deployment.phase,
        'status': deployment.status,
        'component_info': deployment.componentInfo,
        'dependent_deployment_status': deployment.dependentDeploymentStatus,
        'errors': deployment.errors,
        'package_dependency_status': deployment.packageDependencyStatus,
        'core_networks': deployment.coreNetworks,
    }
