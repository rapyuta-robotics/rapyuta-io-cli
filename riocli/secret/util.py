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

import re
from typing import List

from munch import Munch

from riocli.utils import tabulate_data
from riocli.v2client.client import Client


def fetch_secrets(
    client: Client,
    secret_name_or_regex: str,
    include_all: bool,
) -> List[Munch]:
    secrets = client.list_secrets()
    result = []
    for secret in secrets:
        if (
            include_all
            or secret_name_or_regex == secret.metadata.name
            or secret_name_or_regex == secret.metadata.guid
            or (
                secret_name_or_regex not in secret.metadata.name
                and re.search(r"^{}$".format(secret_name_or_regex), secret.metadata.name)
            )
        ):
            result.append(secret)

    return result


def print_secrets_for_confirmation(secrets: List[Munch]):
    data = []
    for secret in secrets:
        data.append(
            [
                secret.metadata.name,
                secret.metadata.creatorGUID,
                secret.metadata.createdAt,
            ]
        )

    tabulate_data(data, ["Name", "Creator", "CreatedAt"])
