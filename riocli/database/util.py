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
import time
import typing

from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2.exceptions import HttpNotFoundError

from riocli.utils import tabulate_data


def fetch_databases(
    client: Client,
    database_name_or_regex: str,
    include_all: bool,
) -> list:
    databases = client.list_databases()

    if include_all:
        return databases.items

    result = []
    for db in databases.items:
        if re.search(database_name_or_regex, db.metadata.name):
            result.append(db)

    return result


def _standby_summary(db: typing.Any) -> str:
    """running/desired standby count, or "-" when the database has no standbys."""
    standby = getattr(db.spec.postgres, "standby", None) if db.spec.postgres else None
    desired = len(standby.devices) if standby and standby.devices else 0
    if not desired:
        return "-"

    status = getattr(db.status, "postgres", None) if db.status else None
    reported = (status.standby or []) if status else []
    running = sum(1 for s in reported if s.phase == "running")

    return f"{running}/{desired}"


def display_database_list(databases: typing.Any, show_header: bool = True):
    headers = []
    if show_header:
        headers = ("GUID", "Name", "Phase", "Device", "Standby", "Version")

    data = []
    for db in databases:
        phase = getattr(db.status, "phase", None) if db.status else None
        primary = None
        version = None
        if db.spec.postgres:
            primary = db.spec.postgres.primary.device_name
            version = db.spec.postgres.version
        data.append(
            [
                db.metadata.guid,
                db.metadata.name,
                phase or "Unknown",
                primary or "-",
                _standby_summary(db),
                version or "-",
            ]
        )

    tabulate_data(data, headers)


def wait_until_listed(
    get: typing.Callable[[str], typing.Any],
    kind: str,
    name: str,
    timeout: int = 60,
    interval: int = 5,
) -> None:
    """Block until get(name) finds the resource; apply ordering cannot see a
    dependency that another apply is still creating."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            get(name)
            return
        except HttpNotFoundError as e:
            if time.monotonic() >= deadline:
                raise Exception(f"{kind} {name} not found after {timeout}s") from e
            time.sleep(interval)


def wait_until_deleted(
    get: typing.Callable[[str], typing.Any],
    kind: str,
    name: str,
    timeout: int = 60,
    interval: int = 5,
) -> None:
    """Block until get(name) returns 404; the server removes the row only after the
    device acks, and until then it blocks deleting the parent."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            get(name)
        except HttpNotFoundError:
            return
        if time.monotonic() >= deadline:
            raise Exception(f"{kind} {name} still present {timeout}s after delete")
        time.sleep(interval)
