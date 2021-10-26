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

from riocli.build.create import create_build
from riocli.build.delete import delete_build
from riocli.build.import_build import import_build
from riocli.build.inspect import inspect_build
from riocli.build.list import list_builds
from riocli.build.logs import build_logs
from riocli.build.trigger import trigger_build


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def build() -> None:
    """
    Build the source code as a Docker image
    """
    pass


build.add_command(create_build)
build.add_command(delete_build)
build.add_command(import_build)
build.add_command(list_builds)
build.add_command(inspect_build)
build.add_command(build_logs)
build.add_command(trigger_build)
