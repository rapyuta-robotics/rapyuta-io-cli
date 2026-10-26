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

from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest
from click.testing import CliRunner
from rapyuta_io_sdk_v2 import RoleBinding

NOW = datetime(2026, 10, 26, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def tokyo(monkeypatch):
    """Run every test in a fixed local zone (UTC+9, no DST)."""
    monkeypatch.setenv("TZ", "Asia/Tokyo")
    time.tzset()
    yield
    monkeypatch.undo()
    time.tzset()


@pytest.fixture
def runner():
    return CliRunner()


def make_binding(
    guid: str = "rb-1",
    role: str = "rio-project_admin",
    subject: str = "User:engineer@example.com",
    domain: str = "Project:warehouse-prod",
    not_before: str | None = None,
    not_after: str | None = None,
) -> RoleBinding:
    subject_kind, subject_name = subject.split(":", 1)
    domain_kind, domain_name = domain.split(":", 1)
    spec = {
        "roleRef": {"kind": "Role", "name": role},
        "subject": {"kind": subject_kind, "name": subject_name},
        "domain": {"kind": domain_kind, "name": domain_name},
    }
    if not_before:
        spec["notBefore"] = not_before
    if not_after:
        spec["notAfter"] = not_after

    return RoleBinding.model_validate(
        {
            "metadata": {"guid": guid, "organizationGUID": "org-1"},
            "spec": spec,
        }
    )
