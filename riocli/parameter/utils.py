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
import filecmp
import json
import os
import re
import typing
from filecmp import dircmp
from typing import List

import click
from directory_tree import display_tree
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.config import Configuration
from riocli.constants import Colors


def filter_trees(root_dir: str, tree_names: typing.Tuple[str]) -> typing.List[str]:
    trees = []
    for each in os.listdir(root_dir):
        full_path = os.path.join(root_dir, each)

        if not os.path.isdir(full_path):
            continue

        if tree_names and each not in tree_names:
            continue

        if not is_valid_tree_name(each):
            raise Exception(
                "Invalid tree name '{}'. Tree name must be 3-50 characters "
                "and can contain letters, digits, _ and -".format(each)
            )
        trees.append(each)

    if tree_names and not trees:
        raise Exception("one or more specified tree names are invalid")

    return trees


def display_trees(root_dir: str, trees: typing.List[str]) -> None:
    trees = trees or []
    for each in trees:
        tree_out = display_tree(os.path.join(root_dir, each), string_rep=True)
        click.secho(tree_out, fg=Colors.YELLOW)


def _api_call(
    method: str,
    name: typing.Union[str, None] = None,
    payload: typing.Union[typing.Dict, None] = None,
    load_response: bool = True,
) -> typing.Any:
    config = Configuration()
    catalog_host = config.data.get(
        "core_api_host", "https://gaapiserver.apps.okd4v2.prod.rapyuta.io"
    )
    url = "{}/api/paramserver/tree".format(catalog_host)
    if name:
        url = "{}/{}".format(url, name)
    headers = config.get_auth_header()
    response = RestClient(url).method(method).headers(headers).execute(payload=payload)
    data = None
    err_msg = "error in the api call"
    if load_response:
        data = json.loads(response.text)

    if not response.ok:
        err_msg = data.get("error")
        raise Exception(err_msg)
    return data


def list_trees() -> List[str]:
    resp = _api_call(HttpMethod.GET)
    if "data" not in resp:
        raise Exception("Failed to list configurations")

    return resp.get("data")


class DeepDirCmp(dircmp):
    def phase3(self) -> None:
        # shallow=False enables the behaviour of matching the File content. The
        # original dircmp Class only compares os.Stat between the files, and
        # gives no way to modify the behaviour.
        f_comp = filecmp.cmpfiles(self.left, self.right, self.common_files, shallow=False)
        self.same_files, self.diff_files, self.funny_files = f_comp


def is_valid_tree_name(name: str) -> bool:
    """Validates a config tree name"""
    return bool(re.match(r"^[0-9A-Za-z][0-9A-Za-z._-]{0,49}$", name))
