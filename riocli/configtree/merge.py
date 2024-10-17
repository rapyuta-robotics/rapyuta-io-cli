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
import os
from tempfile import NamedTemporaryFile
from typing import Optional

import click
from benedict import benedict
from click_help_colors import HelpColorsCommand
from yaspin.core import Yaspin

from riocli.config import get_config_from_context, new_v2_client
from riocli.configtree.import_keys import split_metadata
from riocli.configtree.revision import Revision
from riocli.configtree.util import (
    Metadata,
    combine_metadata,
    fetch_last_milestone_keys,
    fetch_ref_keys,
    fetch_tree_keys,
    unflatten_keys,
)
from riocli.constants.colors import Colors
from riocli.constants.symbols import Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "merge",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("base-tree-name", type=str)
@click.argument("ref", type=str)
@click.option(
    "--silent",
    "silent",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Skip interactively, if fast merge is not possible, then fail.",
)
@click.option(
    "--ignore-conflict",
    "ignore_conflict",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Skip the conflicting keys and only perform a partial fast merge.",
)
@click.option(
    "--milestone",
    "milestone",
    type=str,
    help="Minestone name for the imported revision.",
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
@with_spinner(text="Merging...")
def merge_revisions(
    ctx: click.Context,
    base_tree_name: str,
    ref: str,
    silent: bool,
    with_org: bool,
    milestone: Optional[str],
    ignore_conflict: bool,
    spinner: Yaspin,
):
    """
    Merge the revision specified by the ref on the base-tree. The Base tree must
    be the name of the tree. Merge always works on the HEAD of the tree.

    The ref is a slash ('/') separated string.

    * The first part can be 'org' or 'proj' defining the scope of the reference.

    * The second part defines the name of the Tree.

    * The third optional part defines the revision-id or milestone of the Tree.

    Examples:

    * org/tree-name

    * org/tree-name/rev-id

    * org/tree-name/milestone

    * proj/tree-name

    * proj/tree-name/rev-id

    * proj/tree-name/milestone

    """
    try:
        base_keys = fetch_tree_keys(is_org=with_org, tree_name=base_tree_name)
        source_keys = fetch_ref_keys(ref=ref)
        old_base_keys = fetch_last_milestone_keys(
            is_org=with_org, tree_name=base_tree_name
        )
        fast_merge_possible = is_fast_merge_possible(base_keys, source_keys)

        if not fast_merge_possible and not ignore_conflict and silent:
            raise Exception("Fast merge is not possible")

        fast_merge(base_keys, source_keys)

        if not ignore_conflict and not fast_merge_possible:
            with spinner.hidden():
                merged = interactive_merge(ctx, base_keys, source_keys, old_base_keys)
            data, metadata = split_metadata(merged)
        else:
            spinner.write(
                click.style("{}  Fast-forwarding".format(Symbols.INFO), fg=Colors.CYAN)
            )
            # Combining and Splitting is required to remove the extra API fields
            # in the Value.
            base_keys = combine_metadata(base_keys)
            data, metadata = split_metadata(base_keys)

        data = benedict(data).flatten(separator="/")
        metadata = benedict(metadata).flatten(separator="/")

        client = new_v2_client(with_project=(not with_org))
        with Revision(
            tree_name=base_tree_name,
            client=client,
            force_new=True,
            with_org=with_org,
            commit=True,
            milestone=milestone,
        ) as rev:
            rev_id = rev.revision_id

            for key, value in data.items():
                key_metadata = metadata.get(key, None)
                if key_metadata is not None and isinstance(key_metadata, Metadata):
                    key_metadata = key_metadata.get_dict()

                rev.store(key=key, value=str(value), perms=644, metadata=key_metadata)

        payload = {
            "kind": "ConfigTree",
            "apiVersion": "api.rapyuta.io/v2",
            "metadata": {
                "name": base_tree_name,
            },
            "head": {
                "metadata": {
                    "guid": rev_id,
                }
            },
        }

        client.set_revision_config_tree(base_tree_name, payload)
        spinner.text = click.style("Config tree merged successfully.", fg=Colors.CYAN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.red.text = str(e)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def interactive_merge(
    ctx: click.Context, keys_1: dict, keys_2: dict, keys_3: Optional[dict]
) -> dict:
    cfg = get_config_from_context(ctx)
    keys_1 = unflatten_keys(keys_1)
    keys_2 = unflatten_keys(keys_2)
    keys_3 = unflatten_keys(keys_3)

    with NamedTemporaryFile(mode="w+b", prefix="HEAD_") as file_1, NamedTemporaryFile(
        mode="w+b", prefix="MERGE_HEAD_"
    ) as file_2, NamedTemporaryFile(mode="w+b", prefix="PREV_BASE_") as file_3:
        keys_1.to_json(filepath=file_1.name, indent=4)
        keys_2.to_json(filepath=file_2.name, indent=4)
        keys_3.to_json(filepath=file_3.name, indent=4)
        os.system(
            "{} {} {} {}".format(cfg.merge_tool, file_3.name, file_1.name, file_2.name)
        )

        return benedict(file_1.name, format="json")


def is_fast_merge_possible(base: dict, source: dict) -> bool:
    for key, value in base.items():
        source_value = source.get(key)
        if not source_value:
            continue

        source_data, base_data = source_value.get("data"), value.get("data")
        if source_data != base_data:
            return False

        source_meta, base_meta = source_value.get("metadata"), value.get("metadata")
        if source_meta != base_meta:
            return False

    return True


def fast_merge(base: dict, source: dict) -> None:
    for key, value in source.items():
        if not base.get(key):
            base[key] = value
