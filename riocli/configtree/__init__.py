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
import click
from click_help_colors import HelpColorsGroup

from riocli.configtree.diff import diff_revisions
from riocli.configtree.export_keys import export_keys
from riocli.configtree.import_keys import import_keys
from riocli.configtree.merge import merge_revisions
from riocli.configtree.revision import revision
from riocli.configtree.tree import (
    clone_tree,
    create_config_tree,
    delete_config_tree,
    list_config_tree_keys,
    list_config_trees,
    list_tree_revisions,
    set_tree_revision,
)
from riocli.constants.colors import Colors


@click.group(
    name="configtree",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def config_trees() -> None:
    """
    Config Trees are version controlled config.
    """
    pass


config_trees.add_command(list_config_trees)
config_trees.add_command(create_config_tree)
config_trees.add_command(delete_config_tree)
config_trees.add_command(list_config_tree_keys)
config_trees.add_command(clone_tree)
config_trees.add_command(import_keys)
config_trees.add_command(export_keys)
config_trees.add_command(set_tree_revision)
config_trees.add_command(list_tree_revisions)
config_trees.add_command(revision)
config_trees.add_command(diff_revisions)
config_trees.add_command(merge_revisions)
