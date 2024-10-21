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

from riocli.managedservice.delete import delete_instance
from riocli.managedservice.inspect import inspect_instance
from riocli.managedservice.list import list_instances
from riocli.managedservice.list_providers import list_providers


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
    hidden=True,
)
def managedservice() -> None:
    """
    Managed Services on rapyuta.io

    With managed services on rapyuta.io, you can provision services
    like elasticsearch, etc. on-demand and use them with your deployments.
    """
    pass


managedservice.add_command(delete_instance)
managedservice.add_command(list_providers)
managedservice.add_command(list_instances)
managedservice.add_command(inspect_instance)
