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

from riocli.config import new_v2_client
from riocli.utils import inspect_with_format


@click.command("inspect")
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("service-account-name")
def inspect_service_account(format_type: str, service_account_name: str) -> None:
    """
    Inspect a service account.
    """
    try:
        client = new_v2_client()
        acc_obj = client.get_service_account(name=service_account_name)
        if not acc_obj:
            click.secho("service account not found")
            raise SystemExit(1)
        inspect_with_format(
            obj=acc_obj.model_dump(by_alias=True, exclude_none=True),
            format_type=format_type,
        )
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)
