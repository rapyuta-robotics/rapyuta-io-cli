# Copyright 2025 Rapyuta Robotics
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

import glob
import os
import typing
from datetime import datetime
from shutil import get_terminal_size
from typing import Iterable

import click
import jinja2
from yaspin.api import Yaspin
from ansible.plugins.filter.core import FilterModule as CoreFilterModule
from ansible.plugins.filter.urls import FilterModule as URLFilterModule
from ansible.plugins.filter.urlsplit import FilterModule as URLSplitFilterModule
from ansible.plugins.filter.mathstuff import FilterModule as MathFilterModule
from ansible.plugins.filter.encryption import FilterModule as EncryptionFilterModule

from riocli.apply.filters import get_interface_ip, getenv
from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.constants.symbols import Symbols
from riocli.deployment.model import Deployment
from riocli.device.model import Device
from riocli.disk.model import Disk
from riocli.managedservice.model import ManagedService
from riocli.model import Model
from riocli.network.model import Network
from riocli.organization.model import Organization
from riocli.package.model import Package
from riocli.project.model import Project
from riocli.secret.model import Secret
from riocli.static_route.model import StaticRoute
from riocli.usergroup.model import UserGroup
from riocli.utils import tabulate_data

KIND_TO_CLASS = {
    "deployment": Deployment,
    "device": Device,
    "disk": Disk,
    "managedservice": ManagedService,
    "network": Network,
    "organization": Organization,
    "package": Package,
    "project": Project,
    "secret": Secret,
    "staticroute": StaticRoute,
    "usergroup": UserGroup,
}

FILTERS = {
    "getenv": getenv,
    "get_intf_ip": get_interface_ip,
}


def get_model(data: dict) -> Model:
    """Get the model class based on the kind"""
    kind = data.get("kind", None)
    if kind is None:
        raise Exception("kind is missing")

    klass = KIND_TO_CLASS.get(str(kind).lower(), None)
    if klass is None:
        raise Exception("invalid kind {}".format(kind))

    return klass


def parse_variadic_path_args(path_item):
    glob_files = []
    abs_path = os.path.abspath(path_item)
    # make it absolute
    # does the path exist.
    #     is it a dir?  scan recursively
    #     not a dir but has  special characters in it?  [*?^!]
    #        assume it's a valid glob, use it to glob recursively
    #      if all else fails
    #        consider it a file path directly.
    if not os.path.exists(abs_path):
        return glob_files

    if os.path.isdir(abs_path):
        # TODO: Should we keep this recursive?
        return glob.glob(abs_path + "/**/*", recursive=True)

    return glob.glob(abs_path, recursive=True)


def process_files_values_secrets(
    files: Iterable[str],
    values: Iterable[str],
    secrets: Iterable[str],
):
    glob_files = []

    for path_item in files:
        path_glob = parse_variadic_path_args(path_item)
        glob_files.extend([f for f in path_glob if os.path.isfile(f)])

    # Remove value files from template files list.
    abs_values = values
    if values:
        for v in values:
            abs_v = os.path.abspath(v)
            if abs_v in glob_files:
                glob_files.remove(abs_v)

    # Remove secret files from template files list.
    abs_secret = secrets
    if secrets:
        for s in secrets:
            abs_s = os.path.abspath(s)
            if abs_s in glob_files:
                glob_files.remove(abs_s)

    glob_files = sorted(list(set(glob_files)))
    return glob_files, abs_values, abs_secret


def message_with_prompt(
    left_msg: str,
    right_msg: str = "",
    fg: str = Colors.WHITE,
    spinner: Yaspin = None,
) -> None:
    """Prints a message with a prompt and a timestamp.

    >> left_msg spacer right_msg time
    """
    columns, _ = get_terminal_size()
    t = datetime.now().isoformat("T")
    spacer = " " * (int(columns) - len(left_msg + right_msg + t) - 12)
    text = click.style(f">> {left_msg}{spacer}{right_msg} [{t}]", fg=fg)
    printer = spinner.write if spinner else click.echo
    printer(text)


def print_resolved_objects(objects: typing.Dict) -> None:
    data = []
    for o in objects:
        kind, name = o.split(":")
        data.append([kind.title(), name])

    tabulate_data(data, headers=["Kind", "Name"])


def init_jinja_environment():
    """Initialize Jinja2 environment with custom filters"""
    environment = jinja2.Environment()
    for name, func in FILTERS.items():
        environment.filters[name] = func

    for name, func in CoreFilterModule().filters().items():
        environment.filters[name] = func

    for name, func in URLFilterModule().filters().items():
        environment.filters[name] = func

    for name, func in URLSplitFilterModule().filters().items():
        environment.filters[name] = func

    for name, func in MathFilterModule().filters().items():
        environment.filters[name] = func

    for name, func in EncryptionFilterModule().filters().items():
        environment.filters[name] = func

    return environment


def print_context(ctx: click.Context):
    config = get_config_from_context(ctx)

    org_guid = config.organization_guid
    org_name = config.data.get("organization_name")
    project_guid = config.project_guid
    project_name = config.data.get("project_name")

    click.secho(
        "{} Organization: {} ({})".format(Symbols.INFO, org_name, org_guid),
        fg=Colors.YELLOW,
    )
    click.secho(
        "{} Project: {} ({})".format(Symbols.INFO, project_name, project_guid),
        fg=Colors.YELLOW,
    )
