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

from riocli.config import new_v2_client
from riocli.utils import tabulate_data
from riocli.v2client.client import Client


class StaticRouteNotFound(Exception):
    def __init__(self):
        super().__init__("static route not found")


def find_static_route_guid(client: Client, name: str) -> str:
    client = new_v2_client(with_project=True)
    static_route = client.get_static_route(name)
    if not static_route:
        raise StaticRouteNotFound()
    return static_route.metadata.guid


def fetch_static_routes(
    client: Client,
    route_name_or_regex: str,
    include_all: bool,
) -> List[Munch]:
    routes = client.list_static_routes()
    result = []
    for route in routes:
        if (
            include_all
            or route_name_or_regex == route.metadata.name
            or route_name_or_regex == route.metadata.guid
            or (
                route_name_or_regex not in route.metadata.name
                and re.search(r"^{}$".format(route_name_or_regex), route.metadata.name)
            )
        ):
            result.append(route)

    return result


def print_routes_for_confirmation(routes: List[Munch]):
    data = []
    for route in routes:
        data.append(
            [
                route.metadata.name,
                route.metadata.creatorGUID,
                route.metadata.createdAt,
            ]
        )

    tabulate_data(data, ["Name", "Creator", "CreatedAt"])
