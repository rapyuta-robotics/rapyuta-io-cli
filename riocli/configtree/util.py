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
from __future__ import annotations

import os
from base64 import b64decode
from typing import TYPE_CHECKING

import yaml
from benedict import benedict
from munch import Munch, munchify, unmunchify

from riocli.config import new_v2_client
from riocli.utils import tabulate_data
from riocli.utils.graph import Graphviz
from riocli.utils.state import StateFile

if TYPE_CHECKING:
    from collections.abc import Iterable

MILESTONE_LABEL_KEY = "rapyuta.io/milestone"


# The following describes how configtrees are stored in the Statefile.
# "configtrees": {
#   # Org-level Trees
#   "org-guid": {
# 	"tree-name": {
# 	  "rev_id": "rev-asdasd",  # Identifier of the current Revision.
# 	  "committed": false,      # If the current Revision is committed.
# 	}
#   }
#   # Project-level Trees
#   "project-guid": {
# 	"tree-name": {
# 	  "rev_id": "rev-asdasd",  # Identifier of the current Revision.
# 	  "committed": false,      # If the current Revision is committed.
# 	}
#   }
# }


def get_revision_from_state(
    org_guid: str, project_guid: str | None, tree_name: str
) -> Munch | None:
    s = StateFile()

    if not s.state.get("configtrees"):
        return

    # Either OrgGUID or ProjectGUID will be the Top-Level Key.
    top_level = org_guid
    if project_guid is not None:
        top_level = project_guid

    top_level_trees = s.state.configtrees.get(top_level)
    if top_level_trees is None:
        return

    tree = top_level_trees.get(tree_name)
    if tree is None:
        return

    return tree


def save_revision(
    org_guid: str,
    project_guid: str | None,
    tree_name: str,
    rev_id: str,
    committed: bool = False,
) -> None:
    s = StateFile()

    # Either OrgGUID or ProjectGUID will be the Top-Level Key.
    top_level = org_guid
    if project_guid is not None:
        top_level = project_guid

    configtrees = s.state.get("configtrees")
    if configtrees is None:
        configtrees = dict()

    top_level_trees = configtrees.get(top_level, {})
    if top_level_trees is None:
        top_level_trees = dict()

    tree = {"rev_id": rev_id, "committed": committed}
    top_level_trees[tree_name] = tree
    configtrees[top_level] = top_level_trees

    s.state.configtrees = munchify(configtrees)
    s.save()


def display_config_trees(trees: Iterable, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ["Tree Name", "Head"]

    data = []
    for tree in trees:
        head = None
        if tree.get("head"):
            head = tree.head.metadata.guid

        data.append([tree.metadata.name, head])

    tabulate_data(data, headers=headers)


def display_config_tree_keys(keys: dict, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ["Key", "Metadata", "Checksum"]

    data = []
    for key, val in keys.items():
        metadata = val.get("metadata", None)
        if isinstance(metadata, Munch):
            metadata = unmunchify(metadata)

        data.append([key, metadata, val.get("checksum")])

    tabulate_data(data, headers=headers)


def display_config_tree_revisions(revisions: Iterable, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = [
            "Updated At",
            "RevisionID",
            "Message",
            "Milestone",
            "Parent",
            "Committed",
        ]

    data = []
    for rev in revisions:
        message = rev.get("message")
        parent = rev.get("parent")
        committed = rev.get("committed", False)
        milestone = get_revision_milestone(rev)

        data.append(
            [
                rev.metadata.updatedAt,
                rev.metadata.guid,
                message,
                milestone,
                parent,
                committed,
            ]
        )

    tabulate_data(data, headers=headers)


def display_config_tree_revision_graph(tree_name: str, revisions: Iterable) -> None:
    g = Graphviz(name=tree_name)

    for rev in revisions:
        rev_id = rev.metadata.guid
        parent = rev.get("parent")
        message = rev.get("message")
        if not rev.get("committed", False):
            message = "Uncommitted"

        g.node(key=rev_id, label=f"{rev_id} {message}")

        if parent is not None:
            g.edge(from_node=parent, to_node=rev_id)

    g.visualize()


class Metadata:
    def __init__(self: Metadata, d: dict):
        self.data = d

    def get_dict(self: Metadata) -> dict:
        return self.data


def export_to_files(base_dir: str, data: dict, file_format: str = "yaml") -> None:
    base_dir = os.path.abspath(base_dir)

    for file_name, file_data in data.items():
        file_path = os.path.join(base_dir, f"{file_name}.{file_format}")
        final_data = benedict(file_data)
        if file_format == "yaml":
            final_data.to_yaml(filepath=file_path)
        elif file_format == "json":
            final_data.to_json(filepath=file_path, indent=4)
        else:
            raise Exception("file_format is not supported")


def parse_ref(input: str) -> (bool, str, str | None):
    """
    The input can be a slash ('/') separated string.

    * The first part can be 'org' or 'proj' defining the scope of the reference.
    * The second part defines the name of the Tree.
    * The third optional part defines the revision-id or milestone of the Tree.

    This function returns a Tuple with 3 values:

    * bool: True if the scope is organization, else False.
    * str: Name of the Tree in the scope.
    * Optional[str]: RevisionID if specified.
    * Optional[str]: Milestone if specified

    Examples:
    * org/tree-name
    * org/tree-name/rev-id
    * org/tree-name/milestone
    * proj/tree-name
    * proj/tree-name/rev-id
    * proj/tree-name/milestone
    """

    splits = input.split("/", maxsplit=2)

    if len(splits) < 2:
        raise Exception(f"ref {input} is invalid")

    if splits[0] not in ("org", "proj"):
        raise Exception(f"ref scope {splits[0]} is invalid")

    is_org = splits[0] == "org"

    revision = None
    if len(splits) == 3:
        revision = splits[2]

    milestone = None
    if revision is not None and not revision.startswith("rev-"):
        milestone = revision
        revision = None

    return is_org, splits[1], revision, milestone


def unflatten_keys(keys: dict | None) -> benedict:
    if keys is None:
        return benedict()

    data = combine_metadata(keys)
    return benedict(data).unflatten(separator="/")


def combine_metadata(keys: dict) -> dict:
    result = {}

    for key, val in keys.items():
        data = val.get("data", None)
        if data is not None:
            data = b64decode(data).decode("utf-8")
            # The data received from the API is always in string format. To use
            # appropriate data-type in Python (as well in exports), we are
            # passing it through YAML parser.
            data = yaml.safe_load(data)
        metadata = val.get("metadata", None)

        if metadata:
            result[key] = {
                "value": data,
                "metadata": metadata,
            }
        else:
            result[key] = data

    return result


def fetch_last_milestone_keys(is_org: bool, tree_name: str) -> dict | None:
    client = new_v2_client(with_project=(not is_org))
    revisions = client.list_revisions(tree_name=tree_name)
    if len(revisions) == 0:
        return

    for rev in revisions:
        milestone = get_revision_milestone(rev)
        if milestone is not None:
            return fetch_tree_keys(
                is_org=is_org, tree_name=tree_name, rev_id=rev.metadata.guid
            )


def fetch_ref_keys(ref: str) -> dict:
    is_org, tree, rev_id, milestone = parse_ref(ref)
    return fetch_tree_keys(
        is_org=is_org, tree_name=tree, rev_id=rev_id, milestone=milestone
    )


def fetch_tree_keys(
    is_org: bool,
    tree_name: str,
    rev_id: str | None = None,
    milestone: str | None = None,
) -> dict:
    if milestone:
        rev_id = fetch_milestone_revision_id(
            is_org=is_org, tree_name=tree_name, milestone=milestone
        )

    client = new_v2_client(with_project=(not is_org))
    tree = munchify(
        client.get_configtree(
            name=tree_name,
            revision=rev_id,
            include_data=True,
            content_types=["kv"],
            with_project=(not is_org),
        )
    )

    if not tree.get("head"):
        raise Exception(
            f"Config tree {tree.metadata.name} does not have keys in the revision"
        )

    keys = tree.get("keys")
    if not isinstance(keys, dict):
        raise Exception("Keys are not dictionary")

    return keys


def fetch_milestone_revision_id(is_org: bool, tree_name: str, milestone: str) -> str:
    client = new_v2_client(with_project=(not is_org))
    labels = f"{MILESTONE_LABEL_KEY}={milestone}"

    revisions = client.list_revisions(tree_name=tree_name, label_selector=[labels])
    if len(revisions) == 0:
        raise Exception(f"Revision with milestone {milestone} not found")

    if len(revisions) > 1:
        raise Exception(f"More than one revision with milestone {milestone} exists")

    return revisions[0].metadata.guid


def get_revision_milestone(rev: dict) -> str | None:
    metadata = rev.get("metadata", None)
    if metadata is None:
        return

    labels = metadata.get("labels", None)
    if labels is None:
        return

    return labels.get(MILESTONE_LABEL_KEY)
