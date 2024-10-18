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
from base64 import b64encode
from hashlib import md5
from typing import Optional, Type, Any

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup
from yaspin.core import Yaspin

from riocli.config import get_config_from_context, new_v2_client
from riocli.config.config import Configuration
from riocli.configtree.util import (
    MILESTONE_LABEL_KEY,
    display_config_tree_keys,
    get_revision_from_state,
    save_revision,
)
from riocli.constants.colors import Colors
from riocli.constants.symbols import Symbols
from riocli.utils.spinner import with_spinner
from riocli.utils.state import StateFile
from riocli.v2client import Client


class Revision(object):
    _DEFAULT_COMMIT_MSG = "imported through rio-cli"

    def __init__(
        self,
        tree_name: str,
        client: Client,
        rev_id: Optional[str] = None,
        milestone: Optional[str] = None,
        commit: bool = False,
        force_new: bool = False,
        spinner: Optional[Yaspin] = None,
        with_org: bool = True,
    ):
        self._tree_name = tree_name
        self._client = client
        self._commit = commit
        self._milestone = milestone
        self._config = Configuration()
        self._state_file = StateFile()
        self._spinner = spinner
        self._explicit = False
        self._data = {}
        self._org_guid = self._config.organization_guid
        self._project_guid = None
        if not with_org:
            self._project_guid = self._config.project_guid

        rev = get_revision_from_state(self._org_guid, self._project_guid, self._tree_name)

        if rev_id is not None:
            self._rev_id = rev_id
            self._explicit = True
            msg = "{} Using revision {}.".format(Symbols.INFO, self._rev_id)
        elif not force_new and rev and not rev.committed:
            self._rev_id = rev.rev_id
            msg = "{}  Re-using revision {}.".format(Symbols.INFO, self._rev_id)
        else:
            self._rev = self._client.initialize_config_tree_revision(
                tree_name=self._tree_name
            )
            self._rev_id = self._rev.metadata.guid
            msg = "{} Revision {} created successfully.".format(
                Symbols.SUCCESS, self._rev_id
            )
            save_revision(
                org_guid=self._org_guid,
                project_guid=self._project_guid,
                tree_name=self._tree_name,
                rev_id=self._rev_id,
            )

        if self._spinner:
            self._spinner.write(click.style(msg, fg=Colors.CYAN))

    @property
    def revision_id(self: Revision) -> str:
        return self._rev_id

    def store(
        self: Revision,
        key: str,
        value: str,
        perms: int = 644,
        metadata: Optional[dict] = None,
    ) -> None:
        str_val = str(value)
        enc_val = str_val.encode("utf-8")

        data = {
            "permissions": str(perms),
            "checksum": md5(enc_val).hexdigest(),
            "contentType": "kv",
            "contentLength": len(str_val),
            "data": b64encode(enc_val).decode(),
        }

        if metadata is not None:
            data["metadata"] = metadata

        self._data[key] = data

    def store_file(self: Revision, key: str, file_path: str) -> None:
        self._client.store_file_in_revision(
            tree_name=self._tree_name, rev_id=self._rev_id, key=key, file_path=file_path
        )

    def delete(self: Revision, key: str) -> None:
        self._client.delete_key_in_revision(
            tree_name=self._tree_name, rev_id=self._rev_id, key=key
        )

    def commit(
        self: Revision, msg: Optional[str] = None, author: Optional[str] = None
    ) -> None:
        if msg is None:
            msg = self._DEFAULT_COMMIT_MSG

        if author is None:
            author = self._get_author()

        payload: dict[str, Any] = {
            "kind": "ConfigTreeRevision",
            "apiVersion": "api.rapyuta.io/v2",
            "message": msg,
            "author": author,
        }

        if self._milestone is not None:
            payload["metadata"] = {
                "labels": {
                    MILESTONE_LABEL_KEY: self._milestone,
                }
            }

        self._client.commit_config_tree_revision(
            tree_name=self._tree_name, rev_id=self._rev_id, payload=payload
        )
        if not self._explicit:
            save_revision(
                org_guid=self._org_guid,
                project_guid=self._project_guid,
                tree_name=self._tree_name,
                rev_id=self._rev_id,
                committed=True,
            )

        if self._spinner:
            self._spinner.write(
                click.style(
                    "{} Revision {} committed.".format(Symbols.SUCCESS, self._rev_id),
                    fg=Colors.CYAN,
                )
            )

    def __enter__(self: Revision) -> Revision:
        return self

    def __exit__(self: Revision, typ: Type, val: Any, _: Any) -> None:
        if typ:
            raise val

        if self._data:
            self._client.store_keys_in_revision(
                tree_name=self._tree_name, rev_id=self._rev_id, payload=self._data
            )

        if self._commit and self._rev_id:
            self.commit()

    def _get_author(self: Revision) -> str:
        author = self._config.data.get("email_id", None)
        if author is not None:
            return author

        return os.getlogin()


@click.group(
    name="revision",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def revision() -> None:
    """
    Revision Operations on Config trees.
    """
    pass


@click.command(
    "init",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.option("--force", is_flag=True, type=bool)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
@with_spinner(text="Initializing Config tree revision...")
def init_revision(
    ctx: click.Context,
    tree_name: str,
    force: bool,
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Initialize a new revision for the Config tree
    """
    config = get_config_from_context(ctx)
    project_guid = None
    if not with_org:
        project_guid = config.project_guid

    rev = get_revision_from_state(
        org_guid=config.organization_guid,
        project_guid=project_guid,
        tree_name=tree_name,
    )

    if not force and rev is not None and not rev.committed:
        spinner.text = click.style(
            "Revision {} is already present. Subsequent commands will re-use it. \n"
            "If you want to force create a new revision use the --force flag.".format(
                rev.rev_id
            ),
            fg=Colors.CYAN,
        )
        spinner.green.ok(Symbols.INFO)
        return

    try:
        client = new_v2_client(with_project=(not with_org))
        Revision(
            tree_name=tree_name,
            force_new=force,
            spinner=spinner,
            client=client,
            with_org=with_org,
        )
    except Exception as e:
        spinner.text = click.style(
            "Failed to initialize Config tree revision: {}".format(e), Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "commit",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.argument("rev_id", type=str, required=False)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.option("-m", "--message", "message", type=str, help="Message for the Revision.")
@click.option(
    "--milestone",
    "milestone",
    type=str,
    help="Minestone name for the imported revision.",
)
@click.pass_context
@with_spinner(text="Committing Config tree revision...")
def commit_revision(
    ctx: click.Context,
    tree_name: str,
    rev_id: str,
    message: str,
    milestone: Optional[str],
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Commit the existing Revision
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

        if not rev or rev.committed:
            spinner.text = click.style(
                "RevisionID not provided as argument and not found in the State file.",
                fg=Colors.RED,
            )
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

    try:
        client = new_v2_client(with_project=(not with_org))
        rev = Revision(
            tree_name=tree_name,
            rev_id=rev_id,
            spinner=spinner,
            client=client,
            with_org=with_org,
            milestone=milestone,
        )
        rev.commit(msg=message)
    except Exception as e:
        spinner.text = click.style(
            "Failed to commit Config tree revision: {}".format(e), Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "put",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.argument("key", type=str)
@click.argument("value", type=str)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
@with_spinner(text="Adding key to Config tree revision...")
def put_key_in_revision(
    ctx: click.Context,
    tree_name: str,
    key: str,
    value: str,
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Put a key in the uncommitted revision.
    """

    config = get_config_from_context(ctx)
    project_guid = None
    if not with_org:
        project_guid = config.project_guid

    rev = get_revision_from_state(
        org_guid=config.organization_guid,
        project_guid=project_guid,
        tree_name=tree_name,
    )

    if not rev or rev.committed:
        spinner.text = click.style(
            "RevisionID not provided as argument and not found in the State file. \n"
            "Start a new commit using the `init` command.",
            fg=Colors.RED,
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    try:
        client = new_v2_client(with_project=(not with_org))
        with Revision(
            tree_name=tree_name, spinner=spinner, client=client, with_org=with_org
        ) as rev:
            rev.store(key=key, value=value)
            spinner.write(click.style("\t{} Key {} added.".format(Symbols.SUCCESS, key)))
    except Exception as e:
        spinner.text = click.style(
            "Failed to put key in Config tree revision: {}".format(e), Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "put-file",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.argument("key", type=str)
@click.argument("file-path", type=str)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
@with_spinner(text="Adding key to Config tree revision...")
def put_file_in_revision(
    ctx: click.Context,
    tree_name: str,
    key: str,
    file_path: str,
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Upload a file in the uncommitted revision.
    """

    config = get_config_from_context(ctx)
    project_guid = None
    if not with_org:
        project_guid = config.project_guid

    rev = get_revision_from_state(
        org_guid=config.organization_guid,
        project_guid=project_guid,
        tree_name=tree_name,
    )

    if not rev or rev.committed:
        spinner.text = click.style(
            "RevisionID not provided as argument and not found in the State file. \n"
            "Start a new commit using the `init` command.",
            fg=Colors.RED,
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    try:
        client = new_v2_client(with_project=(not with_org))
        with Revision(
            tree_name=tree_name, spinner=spinner, client=client, with_org=with_org
        ) as rev:
            rev.store_file(key=key, file_path=file_path)
            spinner.write(click.style("\t{} File {} added.".format(Symbols.SUCCESS, key)))
    except Exception as e:
        spinner.text = click.style(
            "Failed to put-file in Config tree revision: {}".format(e), Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("tree-name", type=str)
@click.argument("key", type=str)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.pass_context
@with_spinner(text="Deleting key to Config tree revision...")
def delete_key_in_revision(
    ctx: click.Context,
    tree_name: str,
    key: str,
    with_org: bool,
    spinner: Yaspin,
) -> None:
    """
    Delete the key in the uncommitted revision
    """
    config = get_config_from_context(ctx)
    project_guid = None
    if not with_org:
        project_guid = config.project_guid

    rev = get_revision_from_state(
        org_guid=config.organization_guid,
        project_guid=project_guid,
        tree_name=tree_name,
    )

    if not rev or rev.committed:
        spinner.text = click.style(
            "RevisionID not provided as argument and not found in the State file. \n"
            "Start a new commit using the `init` command.",
            fg=Colors.RED,
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    try:
        client = new_v2_client(with_project=(not with_org))
        with Revision(
            tree_name=tree_name, spinner=spinner, client=client, with_org=with_org
        ) as rev:
            rev.delete(key=key)
            spinner.write(
                click.style("\t{} Key {} removed.".format(Symbols.SUCCESS, key))
            )
    except Exception as e:
        spinner.text = click.style(
            "Failed to delete key in Config tree revision: {}".format(e), Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
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
def list_revision_keys(
    ctx: click.Context,
    tree_name: str,
    rev_id: Optional[str],
    with_org: bool,
) -> None:
    """
    Lists all the keys in the revision
    """
    if not rev_id:
        config = get_config_from_context(ctx)
        project_guid = None
        if not with_org:
            project_guid = config.project_guid

        rev = get_revision_from_state(
            org_guid=config.organization_guid,
            project_guid=project_guid,
            tree_name=tree_name,
        )

        if not rev or rev.committed:
            click.echo(
                click.style(
                    "RevisionID not provided as argument and not found in the State file.",
                    fg=Colors.RED,
                )
            )
            raise SystemExit(1)

        rev_id = rev.rev_id

    try:
        client = new_v2_client(with_project=(not with_org))
        tree = client.get_config_tree(tree_name=tree_name, rev_id=rev_id)

        keys = tree.get("keys")
        if not isinstance(keys, dict):
            raise Exception("Keys are not dictionary")

        display_config_tree_keys(keys=keys)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


revision.add_command(init_revision)
revision.add_command(commit_revision)
revision.add_command(put_key_in_revision)
revision.add_command(put_file_in_revision)
revision.add_command(delete_key_in_revision)
revision.add_command(list_revision_keys)
