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
import typing

import click

from riocli.config import new_v2_client
from riocli.utils import tabulate_data


@click.command("providers")
def list_providers():
    """
    List available managedservice providers
    """
    try:
        client = new_v2_client()
        providers = client.list_providers()
        _display_providers(providers)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


def _display_providers(providers: typing.Any):
    headers = ["Provider Name"]

    data = []
    for provider in providers:
        if provider.name == "dummy":
            continue
        data.append([provider.name])

    tabulate_data(data, headers)
