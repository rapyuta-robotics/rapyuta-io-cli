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
from click_help_colors import HelpColorsGroup

from riocli.package.create import create_package
from riocli.package.delete import delete_package
from riocli.package.deployment import list_package_deployments
from riocli.package.inspect import inspect_package
from riocli.package.list import list_packages


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def package() -> None:
    """
    Define groups of executables to deploy together
    """
    pass


package.add_command(create_package)
package.add_command(delete_package)
package.add_command(list_packages)
package.add_command(inspect_package)
package.add_command(list_package_deployments)
