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
from riocli.parameter.apply import apply_configurations
from riocli.parameter.delete import delete_configurations
from riocli.parameter.diff import diff_configurations
from riocli.parameter.download import download_configurations
from riocli.parameter.list import list_configuration_trees
from riocli.parameter.upload import upload_configurations


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def parameter() -> None:
    """Configuration parameters for your devices and deployments.

    The configuration parameters are file based configs that are
    stored in a directory-like structure. You can upload, download,
    and apply these configurations to your devices and deployments.

    The platform ensures the availability of the configurations at
    predefined paths on the devices and deployments as well as the
    deployments in the cloud.
    """
    pass


parameter.add_command(diff_configurations)
parameter.add_command(apply_configurations)
parameter.add_command(delete_configurations)
parameter.add_command(upload_configurations)
parameter.add_command(download_configurations)
parameter.add_command(list_configuration_trees)
