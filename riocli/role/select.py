# Copyright 2026 Rapyuta Robotics
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
"""Selecting one role binding among those of the same role, subject and domain.

A subject can hold several time-bound bindings of a role in a domain. The
server rejects a permanent binding beside an active window, but one can sit
beside an ended window until cleanup removes it. Commands that act on one
binding pick it explicitly when several match.
"""

from datetime import datetime

from rapyuta_io_sdk_v2 import Client, RoleBinding
from rapyuta_io_sdk_v2.utils import walk_pages

from riocli.role.window import format_time, same_time
from riocli.utils import tabulate_data


class AmbiguousBindingError(Exception):
    def __init__(self, candidates: list[RoleBinding]):
        super().__init__("more than one binding matches")
        self.candidates = candidates


def find_bindings(
    client: Client,
    role: str,
    subject: tuple[str, str],
    domain: tuple[str, str],
) -> list[RoleBinding]:
    """List the bindings of a role for a subject in a domain."""
    subject_kind, subject_name = subject
    domain_kind, domain_name = domain

    found = []
    for page in walk_pages(
        client.list_role_bindings,
        role_names=[role],
        subject_kinds=[subject_kind],
        subject_names=[subject_name],
        domain_kinds=[domain_kind],
        domain_names=[domain_name],
    ):
        for b in page:
            if (
                b.spec.role_ref.name == role
                and (b.spec.subject.kind or "").lower() == subject_kind.lower()
                and b.spec.subject.name == subject_name
                and (b.spec.domain.kind or "").lower() == domain_kind.lower()
                and b.spec.domain.name == domain_name
            ):
                found.append(b)

    return found


def select_binding(
    candidates: list[RoleBinding],
    not_after: datetime | None = None,
    permanent: bool = False,
) -> RoleBinding | None:
    """Pick one binding.

    With permanent, the binding without a window; with not_after, the binding
    ending at that time (to the second). Returns None when nothing matches and
    raises AmbiguousBindingError when more than one does.
    """
    if permanent:
        candidates = [b for b in candidates if b.spec.not_after is None]
    elif not_after is not None:
        candidates = [
            b
            for b in candidates
            if b.spec.not_after is not None and same_time(b.spec.not_after, not_after)
        ]

    if not candidates:
        return None

    if len(candidates) > 1:
        raise AmbiguousBindingError(candidates)

    return candidates[0]


def display_candidates(candidates: list[RoleBinding]) -> None:
    data = [
        [
            b.spec.role_ref.name,
            f"{b.spec.domain.kind}:{b.spec.domain.name}",
            f"{b.spec.subject.kind}:{b.spec.subject.name}",
            format_time(b.spec.not_before) if b.spec.not_before else "",
            format_time(b.spec.not_after) if b.spec.not_after else "",
        ]
        for b in candidates
    ]
    tabulate_data(data, ["Role", "Domain", "Subject", "Not Before", "Not After"])
