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
from pathlib import Path
from typing import Iterable, Optional

import click
from benedict import benedict
from click_help_colors import HelpColorsCommand
from yaspin.core import Yaspin

from riocli.config import new_v2_client
from riocli.configtree.etcd import import_in_etcd
from riocli.configtree.revision import Revision
from riocli.configtree.util import Metadata, export_to_files
from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "import",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--commit/--no-commit",
    "commit",
    is_flag=True,
    type=bool,
    help="Commit the imported keys to the Config Tree.",
)
@click.option(
    "--update-head/--no-update-head",
    "update_head",
    is_flag=True,
    type=bool,
    help="Update the HEAD of the Config Tree after importing the keys.",
)
@click.option(
    "--milestone",
    "milestone",
    type=str,
    help="Milestone name for the imported revision.",
)
@click.option(
    "--etcd-endpoint",
    "etcd_endpoint",
    type=str,
    help="Import keys to local etcd instead of rapyuta.io cloud",
)
@click.option(
    "--export-directory",
    "export_directory",
    type=str,
    help="Path to the directory for exporting files.",
)
@click.option(
    "--export-format",
    "export_format",
    type=click.Choice(["json", "yaml"]),
    default="json",
    help="Format of the exported files.",
)
@click.option(
    "--etcd-port",
    "etcd_port",
    type=int,
    default=2379,
    help="Port for the etcd endpoint",
)
@click.option(
    "--etcd-prefix", "etcd_prefix", type=str, help="Prefix to use for the key-space"
)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.option(
    "--override",
    "overrides",
    type=click.Path(exists=True),
    default=None,
    multiple=True,
    help="Override values for keys in the imported files.",
)
@click.argument("tree-name", type=str)
@click.argument(
    "files",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
    nargs=-1,
)
@click.pass_context
@with_spinner(text="Importing keys...")
def import_keys(
    _: click.Context,
    tree_name: str,
    files: Iterable[str],
    commit: bool,
    update_head: bool,
    milestone: Optional[str],
    export_directory: Optional[str],
    export_format: Optional[str],
    etcd_endpoint: Optional[str],
    etcd_port: Optional[int],
    etcd_prefix: Optional[str],
    overrides: Optional[Iterable[str]],
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """Imports keys from JSON or YAML files.

    The import command can import keys into an existing Config Tree or
    to an ETCD cluster. It can also output the keys to files in JSON or
    YAML format. The command can also apply overrides to the keys before
    importing them.

    The keys are imported from the one or more files provided as arguments.
    The supported file formats are JSON and YAML.

    Usage Examples:

      Import keys from master.json to the sootballs Config Tree along with overrides. Also, commit and update the head of the Config Tree.

      $ rio configtree import sootballs master.json --override overrides.json --commit --update-head

      Import keys from master.json to etcd along with overrides.

      $ rio configtree import sootballs master.json --override overrides.json --etcd-endpoint localhost


    You can specify more than one override file by providing the files with --override flag multiple times.

    When importing to ETCD, the name of the base JSON or YAML file will be prefixed to the keys.

    Note: If --etcd-endpoint is provided, the keys are imported to the local etcd cluster instead of the rapyuta.io cloud.
    """
    if not files:
        spinner.text = click.style("No files provided.", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    data, metadata = _process_files_with_overrides(files, overrides, spinner)

    if export_directory is not None:
        try:
            export_to_files(
                base_dir=export_directory, data=data, file_format=export_format
            )
            spinner.write(
                click.style(
                    f"{Symbols.SUCCESS} Keys exported to {export_format} files in {Path(export_directory).absolute()}.",
                    fg=Colors.GREEN,
                )
            )
        except Exception as e:
            spinner.text = click.style(
                f"Error exporting keys to files: {e}", fg=Colors.RED
            )
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    data = benedict(data).flatten(separator="/")
    metadata = benedict(metadata).flatten(separator="/")

    if etcd_endpoint:
        try:
            import_in_etcd(
                data=data, endpoint=etcd_endpoint, port=etcd_port, prefix=etcd_prefix
            )
            spinner.text = click.style(
                "Keys imported to etcd successfully.", fg=Colors.GREEN
            )
            spinner.green.ok(Symbols.SUCCESS)
            return
        except Exception as e:
            spinner.text = click.style(
                f"Error importing keys to etcd: {e}", fg=Colors.RED
            )
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    try:
        client = new_v2_client(with_project=(not with_org))
        with Revision(
            tree_name=tree_name,
            commit=commit,
            client=client,
            spinner=spinner,
            with_org=with_org,
            milestone=milestone,
        ) as rev:
            rev_id = rev.revision_id

            for key, value in data.items():
                key_metadata = metadata.get(key, None)
                if key_metadata is not None and isinstance(key_metadata, Metadata):
                    key_metadata = key_metadata.get_dict()

                rev.store(key=key, value=str(value), perms=644, metadata=key_metadata)
                spinner.write(
                    click.style(
                        "\t{} Key {} added.".format(Symbols.SUCCESS, key),
                        fg=Colors.CYAN,
                    )
                )

        if update_head:
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

            client.set_revision_config_tree(tree_name, payload)
            spinner.text = click.style(
                "Config tree HEAD updated successfully.", fg=Colors.CYAN
            )
            spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Error importing keys: {e}", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def split_metadata(data: Iterable) -> (Iterable, Iterable):
    """Helper function to split data and metadata from the input data."""
    if not isinstance(data, dict):
        return data, None

    content, metadata = {}, {}

    for key, value in data.items():
        if not isinstance(value, dict):
            content[key] = value
            continue

        potential_content = value.get("value")
        potential_meta = value.get("metadata")

        if (
            len(value) == 2
            and potential_content is not None
            and potential_meta is not None
            and isinstance(potential_meta, dict)
        ):
            content[key] = potential_content
            metadata[key] = Metadata(potential_meta)
            continue

        content[key], metadata[key] = split_metadata(value)

    return content, metadata


def _process_files_with_overrides(
    files: Iterable[str],
    overrides: Iterable[str],
    spinner: Yaspin,
) -> (benedict, benedict):
    """Helper function to process the files and overrides.

    Reads the base files and splits data and metadata. Then
    applies overrides to the data and metadata.
    """
    data = {}

    for f in files:
        file_prefix = Path(f).stem
        file_format = "yaml"
        if f.endswith("json"):
            file_format = "json"

        data[file_prefix] = benedict(f, format=file_format)
        spinner.write(
            click.style(
                "{} File {} processed.".format(Symbols.SUCCESS, f),
                fg=Colors.CYAN,
            )
        )

    data, metadata = split_metadata(data)

    # Process the override files.
    override = benedict({})

    for f in overrides:
        file_format = "yaml"
        if f.endswith("json"):
            file_format = "json"

        override.merge(benedict(f, format=file_format).unflatten(separator="/"))

        spinner.write(
            click.style(
                "{} Override file {} processed.".format(Symbols.SUCCESS, f),
                fg=Colors.CYAN,
            )
        )

    override_data, override_metadata = split_metadata(override)

    # Merge the override data and metadata with
    # the original data and metadata.
    benedict(data).merge(override_data)
    benedict(metadata).merge(override_metadata)

    return data, metadata
