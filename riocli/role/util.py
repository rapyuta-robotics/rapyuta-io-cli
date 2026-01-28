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
import re

from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2.utils import walk_pages

from riocli.role.model import Role


def fetch_roles(
    client: Client,
    role_name_or_regex: str,
    include_all: bool,
) -> list[Role]:
    roles = walk_pages(client.list_roles)

    result = []
    for page in roles:
        if include_all:
            result.extend(page)
            continue

        for r in page:
            if re.search(role_name_or_regex, r.metadata.name):
                result.append(r)

    return result


def get_domain(input: str) -> tuple[str, str]:
    splits = input.split(":", maxsplit=2)
    if len(splits) < 2:
        raise Exception(f"domain {input} is invalid")

    domain_kind = splits[0].lower()

    if domain_kind not in ("organization", "project", "usergroup"):
        raise Exception(f"domain kind {domain_kind} is invalid")

    return splits[0], splits[1]


def get_subject(input: str) -> tuple[str, str]:
    splits = input.split(":", maxsplit=2)
    if len(splits) < 2:
        raise Exception(f"subject {input} is invalid")

    domain_kind = splits[0].lower()

    if domain_kind not in ("user", "usergroup", "serviceaccount"):
        raise Exception(f"subject kind {domain_kind} is invalid")

    return splits[0], splits[1]
