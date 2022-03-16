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
from rapyuta_io import Client

from riocli.auth.login import login
from riocli.auth.logout import logout
from riocli.auth.refresh_token import refresh_token
from riocli.auth.staging import environment
from riocli.auth.status import status
from riocli.auth.token import token
from riocli.auth.util import read_config
from riocli.config import new_client


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def auth():
    """
    Account and Login on Rapyuta.io
    """
    pass


def get_rio_client() -> Client:
    return new_client()


auth.add_command(login)
auth.add_command(logout)
auth.add_command(status)
auth.add_command(refresh_token)
auth.add_command(token)
auth.add_command(environment)
