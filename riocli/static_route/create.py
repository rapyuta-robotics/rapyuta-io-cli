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
from click_spinner import spinner

from riocli.config import new_client


@click.command('create')
@click.argument('prefix', type=str)
def create_static_route(prefix: str) -> None:
    """
    Creates a new instance of static route
    """
    try:
        client = new_client()
        with spinner():
            route = client.create_static_route(prefix)
        click.secho("Static Route created successfully for URL {}".format(route.urlString), fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)
