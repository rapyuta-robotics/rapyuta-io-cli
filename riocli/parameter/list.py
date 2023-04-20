# Copyright 2023 Rapyuta Robotics
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
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.parameter.utils import _api_call
from riocli.utils import tabulate_data


@click.command('list')
def list_configuration_trees() -> None:
    """
    List the Configuration Parameter Trees.
    """
    try:
        data = _api_call(HttpMethod.GET)
        if 'data' not in data:
            raise Exception('Something went wrong!')

        trees = [[tree] for tree in data['data']]

        tabulate_data(trees, headers=['Tree Name'])

    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)
