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

from riocli.rosbag.blob import rosbag_blob
from riocli.rosbag.job import rosbag_job


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def rosbag() -> None:
    """
    Record ROS Topics for ROS components
    """
    pass


rosbag.add_command(rosbag_job)
rosbag.add_command(rosbag_blob)
