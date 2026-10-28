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
from datetime import datetime

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

    subject_kind = splits[0].lower()

    if subject_kind not in ("user", "usergroup", "serviceaccount"):
        raise Exception(f"subject kind {subject_kind} is invalid")

    # The server stores user emails in lower case.
    if subject_kind == "user":
        return splits[0], splits[1].lower()

    return splits[0], splits[1]


def binding_body(
    organization_guid: str,
    role: str,
    domain: tuple[str, str],
    subject: tuple[str, str],
    not_before: datetime | None = None,
    not_after: datetime | None = None,
    labels: dict | None = None,
) -> dict:
    """The role binding request item for one binding, with its window if any."""
    spec = {
        "roleRef": {"name": role},
        "domain": {"kind": domain[0], "name": domain[1]},
        "subject": {"kind": subject[0], "name": subject[1]},
    }
    if not_before is not None:
        spec["notBefore"] = not_before.isoformat()
    if not_after is not None:
        spec["notAfter"] = not_after.isoformat()

    metadata: dict = {"organizationGUID": organization_guid}
    if labels:
        metadata["labels"] = labels

    return {"metadata": metadata, "spec": spec}
