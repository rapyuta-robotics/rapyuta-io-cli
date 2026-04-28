import re

from rapyuta_io_sdk_v2 import Client

from riocli.utils import tabulate_data


def fetch_databases(
    client: Client,
    database_name_or_regex: str,
    include_all: bool,
) -> list:
    databases = client.list_databases()

    if include_all:
        return list(databases.items)

    result = []
    for db in databases.items:
        if re.search(rf"^{database_name_or_regex}$", db.metadata.name):
            result.append(db)

    return result


def print_databases_for_confirmation(databases: list) -> None:
    headers = ["Name", "Type", "Phase"]
    data = [
        [
            db.metadata.name,
            db.spec.type,
            (
                db.status.postgres.primary.phase
                if db.status and db.status.postgres and db.status.postgres.primary
                else ""
            ),
        ]
        for db in databases
    ]
    tabulate_data(data, headers)
