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

from riocli.auth.util import get_token
from riocli.config import Configuration
from riocli.exceptions import LoggedOut


@click.command()
def refresh_token():
    """
    Refreshes the authentication Token after it expires
    """

    config = Configuration()
    email = config.data.get('email_id', None)
    password = config.data.get('password', None)
    if not config.exists or not email or not password:
        raise LoggedOut

    config.data['auth_token'] = get_token(email, password)

    config.save()
    click.echo('Token refreshed successfully!')
