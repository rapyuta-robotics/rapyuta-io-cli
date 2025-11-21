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

from riocli.constants import Colors
from riocli.service_account.delete import delete_service_acc
from riocli.service_account.inspect import inspect_service_account
from riocli.service_account.list import list_service_acc
from riocli.service_account.token import token
from riocli.utils import AliasedGroup


@click.group(
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def service_account() -> None:
    """
    A non-human user created to run services and automated tasks.
    """
    pass


service_account.add_command(list_service_acc)
service_account.add_command(inspect_service_account)
service_account.add_command(token)
service_account.add_command(delete_service_acc)
