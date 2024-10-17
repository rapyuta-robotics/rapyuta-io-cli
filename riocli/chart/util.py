import typing

import requests
from yaml import safe_load

from riocli.utils import tabulate_data

DEFAULT_REPOSITORY = (
    "https://rapyuta-robotics.github.io/rapyuta-charts/incubator/index.yaml"  # noqa
)


def find_chart(chart: str) -> typing.List:
    """Finds a chart in the upstream index."""
    chart, ver = parse_chart(chart)

    index = fetch_index()
    if "entries" not in index:
        raise Exception("No entries found!")

    if chart not in index["entries"]:
        raise Exception("No such chart found!")

    versions = index["entries"][chart]
    if ver:
        versions = _find_version(entries=versions, version=ver)

    return versions


def fetch_index(repository=DEFAULT_REPOSITORY) -> typing.Dict:
    """Fetches the upstream chart index."""
    response = requests.get(repository)
    if not response.ok:
        raise Exception(f"Fetching index failed: {repository}")

    index = safe_load(response.text)
    return index


def parse_chart(val: str) -> (str, str):
    # TODO: Add support for repository
    chart, ver = None, None

    # Separate repository and chart
    # splits = val.split('/')
    # if len(splits) > 2:
    #     raise Exception('Multiple / are not allowed in the chart!')
    # elif len(splits) == 2:
    #     repo, chart = splits[0], splits[1]
    # else:
    #     chart = splits[0]

    # Separate version
    splits = val.split(":")
    if len(splits) > 2:
        raise Exception("Multiple : are not allowed in the chart!")
    elif len(splits) == 2:
        chart, ver = splits[0], splits[1]
    else:
        chart = splits[0]

    return chart, ver


def _find_version(entries: typing.List, version: str):
    for entry in entries:
        if entry.get("version") == version:
            return [entry]


def print_chart_entries(entries: typing.List, wide: bool = False) -> None:
    """Prints charts in a tabular format."""
    entries = sorted(entries, key=lambda x: x.get("name").lower())

    headers = ["Name", "Version", "Created At"]
    if wide:
        headers.append("Description")

    data = []
    for entry in entries:
        row = [entry.get("name"), entry.get("version"), entry.get("created")]
        if wide:
            row.append(entry.get("description"))

        data.append(row)

    tabulate_data(data, headers)
