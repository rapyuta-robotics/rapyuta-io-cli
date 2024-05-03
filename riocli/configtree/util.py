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
from typing import Optional, Iterable

from munch import Munch, munchify, unmunchify

from riocli.utils import tabulate_data
from riocli.utils.graph import Graphviz
from riocli.utils.state import StateFile


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

def get_revision_from_state(org_guid: str, project_guid: Optional[str], tree_name: str) -> Optional[Munch]:
    s = StateFile()

    if not s.state.get('configtrees'):
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

def save_revision(org_guid: str, project_guid: Optional[str], tree_name: str, rev_id: str, committed: bool = False) -> None:
    s = StateFile()

    # Either OrgGUID or ProjectGUID will be the Top-Level Key.
    top_level = org_guid
    if project_guid is not None:
        top_level = project_guid

    configtrees = s.state.get('configtrees')
    if configtrees is None:
        configtrees = dict()

    top_level_trees = configtrees.get(top_level, {})
    if top_level_trees is None:
        top_level_trees = dict()

    tree = {'rev_id': rev_id, 'committed': committed}
    top_level_trees[tree_name] = tree
    configtrees[top_level] = top_level_trees

    s.state.configtrees = munchify(configtrees)
    s.save()

def display_config_trees(trees: Iterable, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ['Tree Name', 'Head']

    data = []
    for tree in trees:
        head = None
        if tree.get('head'):
            head = tree.head.metadata.guid

        data.append([tree.metadata.name, head])

    tabulate_data(data, headers=headers)


def display_config_tree_keys(keys: dict, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ['Key', 'Metadata', 'Checksum']

    data = []
    for key, val in keys.items():
        metadata = val.get('metadata', None)
        if isinstance(metadata, Munch):
            metadata = unmunchify(metadata)

        data.append([key, metadata, val.get('checksum')])

    tabulate_data(data, headers=headers)

def display_config_tree_revisions(revisions: Iterable, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ['Updated At', 'RevisionID', 'Message', 'Parent', 'Committed']

    data = []
    for rev in revisions:
        message = rev.get('message')
        parent = rev.get('parent')
        committed = rev.get('committed', False)
        data.append([rev.metadata.updatedAt, rev.metadata.guid, message, parent, committed])

    tabulate_data(data, headers=headers)

def display_config_tree_revision_graph(tree_name: str, revisions: Iterable) -> None:
    g = Graphviz(name=tree_name)

    for rev in revisions:
        rev_id = rev.metadata.guid
        parent = rev.get('parent')
        message = rev.get('message')
        if not rev.get('committed', False):
            message = 'Uncommitted'

        g.node(key=rev_id, label='{} {}'.format(rev_id, message))

        if parent is not None:
            g.edge(from_node=parent, to_node=rev_id)

    g.visualize()

class Metadata(object):
    def __init__(self: Metadata, d: dict):
        self.data = d

    def get_dict(self: Metadata) -> dict:
        return self.data
