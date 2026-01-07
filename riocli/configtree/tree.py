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

from collections.abc import Iterable

import click
from click_help_colors import HelpColorsCommand
from munch import munchify
from yaspin.core import Yaspin

from riocli.config import get_config_from_context, new_v2_client
from riocli.configtree.util import (
    display_config_tree_keys,
    display_config_tree_revision_graph,
    display_config_tree_revisions,
    display_config_trees,
    fetch_tree_keys,
    get_revision_from_state,
)
from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "create",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
@with_spinner(text="Creating Config tree...")
def create_config_tree(
    ctx: click.Context,
    tree_name: str,
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Creates a new Config tree.
    """

    config = get_config_from_context(ctx)

    try:
        client = config.new_v2_client(with_project=(not with_org))
        payload = {
            "kind": "ConfigTree",
            "apiVersion": "api.rapyuta.io/v2",
            "metadata": {
                "name": tree_name,
            },
        }
        config_tree = munchify(client.create_configtree(body=payload, with_project=(not with_org)))
        spinner.text = click.style(
            f"Config tree {config_tree.metadata.name} created successfully.",
            fg=Colors.GREEN,
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to create Config tree: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
@with_spinner(text="Deleting Config tree...")
def delete_config_tree(
    _: click.Context,
    tree_name: str,
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Deletes the Config tree.
    """

    try:
        client = new_v2_client(with_project=(not with_org))
        client.delete_configtree(tree_name)
        spinner.text = click.style("Config tree deleted successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to delete Config tree: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "clone",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.argument("new-tree", type=str)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
@with_spinner(text="Cloning Config tree...")
def clone_tree(
    _: click.Context,
    tree_name: str,
    new_tree: str,
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Clones an existing Config tree.
    """

    payload = {
        "kind": "ConfigTree",
        "apiVersion": "api.rapyuta.io/v2",
        "metadata": {
            "name": new_tree,
        },
    }

    try:
        client = new_v2_client(with_project=(not with_org))
        tree = munchify(
            client.get_configtree(name=tree_name, with_project=(not with_org))
        )
        head = tree.get("head")

        if head is not None:
            payload["head"] = head
        else:
            spinner.write(
                click.style(
                    "The head of the given Config tree is empty. Creating a new Config tree instead",
                    fg=Colors.YELLOW,
                )
            )

        # We always clone into the current project.
        # Thus, we recreate the client with_project=True.
        client = new_v2_client(with_project=True)
        config_tree = munchify(client.create_configtree(body=payload))
        spinner.text = click.style(
            f"Config tree {config_tree.metadata.name} cloned successfully.",
            fg=Colors.GREEN,
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to clone Config tree: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "set-revision",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.argument("rev-id", type=str, required=False)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
@with_spinner(text="Setting Config tree head...")
def set_tree_revision(
    ctx: click.Context,
    tree_name: str,
    rev_id: str | None,
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Sets the revision as head of the Config tree.
    """

    config = get_config_from_context(ctx)
    project_guid = None
    if not with_org:
        project_guid = config.project_guid

    if not rev_id:
        rev = get_revision_from_state(
            org_guid=config.organization_guid,
            project_guid=project_guid,
            tree_name=tree_name,
        )

        if not rev or not rev.committed:
            spinner.text = click.style(
                "RevisionID not provided as argument and not found in the State file.",
                fg=Colors.RED,
            )
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

        rev_id = rev.rev_id

    payload = {
        "kind": "ConfigTree",
        "apiVersion": "api.rapyuta.io/v2",
        "metadata": {
            "name": tree_name,
        },
        "head": {
            "metadata": {
                "guid": rev_id,
            }
        },
    }

    try:
        client = new_v2_client(with_project=(not with_org))
        client.set_configtree_revision(
            name=tree_name, configtree=payload, with_project=(not with_org)
        )
        spinner.text = click.style(
            "Config tree head updated successfully.", fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to update config-tree Head: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
def list_config_trees(
    _: click.Context,
    with_org: bool,
) -> None:
    """
    Lists the Config trees.
    """

    try:
        client = new_v2_client(with_project=(not with_org))
        result = client.list_configtrees(with_project=(not with_org))
        trees = munchify(result.get("items", []))
        if not isinstance(trees, Iterable):
            raise Exception("List items are not iterable")

        display_config_trees(trees=trees)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


@click.command(
    "keys",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.argument("rev-id", type=str, required=False)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
def list_config_tree_keys(
    _: click.Context,
    tree_name: str,
    rev_id: str | None,
    with_org: bool,
) -> None:
    """
    Lists all the keys in the Config tree.
    """
    try:
        keys = fetch_tree_keys(is_org=with_org, tree_name=tree_name, rev_id=rev_id)
        display_config_tree_keys(keys=keys)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


@click.command(
    "history",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.option("--graph", is_flag=True, type=bool, help="Display in the graph format.")
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
def list_tree_revisions(
    _: click.Context,
    graph: bool,
    tree_name: str,
    with_org: bool,
) -> None:
    """
    Shows the revisions of the Config Tree.
    """
    try:
        client = new_v2_client(with_project=(not with_org))
        result = client.list_revisions(tree_name=tree_name, with_project=(not with_org))
        revisions = munchify(result.get("items", []))
        if not isinstance(revisions, Iterable):
            raise Exception("List items are not iterable")

        if graph:
            display_config_tree_revision_graph(tree_name=tree_name, revisions=revisions)
        else:
            display_config_tree_revisions(revisions=revisions)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e
