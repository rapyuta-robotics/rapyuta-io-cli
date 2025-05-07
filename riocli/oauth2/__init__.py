# Copyright 2025 Rapyuta Robotics
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
from riocli.oauth2.create import create_oauth2_client
from riocli.oauth2.delete import delete_oauth2_client
from riocli.oauth2.inspect import inspect_oauth2_client
from riocli.oauth2.list import list_oauth2_clients
from riocli.oauth2.update import update_oauth2_client, update_oauth2_client_uri


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def oauth2() -> None:
    """
    OAuth2 Admin operations.
    """
    pass


@click.group(
    "client",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def oauth2_clients() -> None:
    """
    OAuth2 Admin operations.
    """
    pass


oauth2.add_command(oauth2_clients)

oauth2_clients.add_command(list_oauth2_clients)
oauth2_clients.add_command(create_oauth2_client)
oauth2_clients.add_command(update_oauth2_client)
oauth2_clients.add_command(update_oauth2_client_uri)
oauth2_clients.add_command(delete_oauth2_client)
oauth2_clients.add_command(inspect_oauth2_client)
