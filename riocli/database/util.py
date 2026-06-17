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

from riocli.utils import tabulate_data
from riocli.utils.error import DeploymentNotRunning, RetriesExhausted

_TERMINAL_PHASES = {"Running", "Failed", "Degraded"}


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


def display_database_list(databases: typing.Any, show_header: bool = True):
    headers = []
    if show_header:
        headers = ("GUID", "Name", "Phase", "Device", "Version")

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
                version or "-",
            ]
        )

    tabulate_data(data, headers)


def poll_database(
    client: Client,
    name: str,
    retry_count: int = 50,
    sleep_interval: int = 6,
):
    database = client.get_database(name)

    for _ in range(retry_count):
        phase = getattr(database.status, "phase", None) if database.status else None
        if phase in _TERMINAL_PHASES:
            if phase == "Failed":
                raise DeploymentNotRunning(
                    f"Database reached Failed phase. Message: {getattr(database.status, 'message', '')}"
                )
            return database

        time.sleep(sleep_interval)
        database = client.get_database(name)

    raise RetriesExhausted(
        f"Retries exhausted: Tried {retry_count} times with {sleep_interval}s interval."
    )
