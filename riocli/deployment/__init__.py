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
from click_help_colors import HelpColorsGroup

from riocli.constants import Colors
from riocli.deployment.delete import delete_deployment
from riocli.deployment.execute import execute_command
from riocli.deployment.inspect import inspect_deployment
from riocli.deployment.list import list_deployments
from riocli.deployment.logs import deployment_logs
from riocli.deployment.status import status
from riocli.deployment.update import update_deployment, restart_deployment
from riocli.deployment.wait import wait_for_deployment


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def deployment():
    """
    Deployed instances of a Package.
    """
    pass


deployment.add_command(delete_deployment)
deployment.add_command(inspect_deployment)
deployment.add_command(list_deployments)
deployment.add_command(deployment_logs)
deployment.add_command(wait_for_deployment)
deployment.add_command(status)
deployment.add_command(execute_command)
deployment.add_command(update_deployment)
deployment.add_command(restart_deployment)
