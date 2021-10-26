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

from riocli.config import new_client
from riocli.static_route.util import repr_static_routes


@click.command('list')
def list_static_routes() -> None:
    """
    List the static routes in the selected project
    """
    try:
        client = new_client()
        routes = client.get_all_static_routes()
        repr_static_routes(routes)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


