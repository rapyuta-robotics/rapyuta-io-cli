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
import json
import os
import random
import shlex
import string
import subprocess
import sys
import typing
import uuid
from pathlib import Path
from shutil import get_terminal_size, move
from tempfile import TemporaryDirectory
from uuid import UUID

import click
import requests
import semver
import yaml
from click_help_colors import HelpColorsGroup
from munch import munchify
from tabulate import tabulate

from riocli.constants import Colors, Symbols


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def inspect_with_format(obj: typing.Any, format_type: str):
    if format_type == "json":
        click.echo_via_pager(json.dumps(obj, indent=4))
    elif format_type == "yaml":
        click.echo_via_pager(yaml.dump(obj, allow_unicode=True))
    else:
        raise Exception("Invalid format")


def dump_all_yaml(objs: typing.List):
    """
    Dump multiple documents as YAML separated by triple dash (---)
    """
    click.echo_via_pager(
        yaml.safe_dump_all(documents=objs, allow_unicode=True, explicit_start=True)
    )


def run_bash_with_return_code(cmd, bg=False) -> (str, int):
    cmd_parts = shlex.split(cmd)

    if bg is True:
        output = subprocess.Popen(cmd_parts)
        stdout = str(output.stdout).strip()
        ret_code = output.returncode
    else:
        output = subprocess.run(cmd_parts, stdout=subprocess.PIPE)
        stdout = output.stdout.decode("utf-8")
        ret_code = output.returncode

    return stdout.strip(), ret_code


def run_bash(cmd, bg=False):
    """
    Runs a bash command and returns the output only
    """
    cmd_parts = shlex.split(cmd)
    if bg is True:
        bg_output = subprocess.Popen(cmd_parts)
        output = str(bg_output.stdout).strip()
    else:
        output = subprocess.run(
            cmd_parts, stdout=subprocess.PIPE, check=True
        ).stdout.decode("utf-8")
    return output.strip()


riocli_group_opts = {
    "invoke_without_command": True,
    "cls": HelpColorsGroup,
    "help_headers_color": "yellow",
    "help_options_color": "green",
}


def random_string(letter_count, digit_count):
    str1 = "".join((random.choice(string.ascii_letters) for x in range(letter_count)))
    str1 += "".join((random.choice(string.digits) for x in range(digit_count)))

    sam_list = list(str1)  # it converts the string to list.
    random.shuffle(sam_list)  # It uses a random.shuffle() function to shuffle the string.
    final_string = "".join(sam_list)
    return final_string


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def tabulate_data(data: typing.List[typing.List], headers: typing.List[str] = None):
    """
    Prints data in tabular format
    """
    # https://github.com/astanin/python-tabulate#table-format
    table_format = "simple"
    header_foreground = "yellow"

    if headers:
        headers = [click.style(h, fg=header_foreground) for h in headers]

    click.echo(tabulate(data, headers=headers, tablefmt=table_format))


def print_separator(color: str = "blue"):
    """
    Prints a separator
    """
    col, _ = get_terminal_size()
    click.secho(" " * col, bg=color)


def is_pip_installation() -> bool:
    return "python" in sys.executable


def check_for_updates(current_version: typing.Text) -> typing.Tuple[bool, typing.Text]:
    try:
        package_info = requests.get("https://pypi.org/pypi/rapyuta-io-cli/json").json()
    except Exception as e:
        click.secho("Failed to fetch upstream package info: {}".format(e), fg=Colors.RED)
        raise SystemExit(1) from e

    upstream_version = package_info.get("info", {}).get("version")

    current_version = semver.Version.parse(current_version)
    available = semver.Version.parse(upstream_version).compare(current_version)

    return available > 0, upstream_version


def pip_install_cli(
    version: str,
    force_reinstall: bool = False,
) -> subprocess.CompletedProcess:
    """
    Installs the given rapyuta-io-cli version using pip
    """
    if not version:
        raise ValueError("version cannot by empty.")

    try:
        semver.Version.parse(version)
    except ValueError as err:
        raise err

    package_name = "rapyuta-io-cli=={}".format(version)

    # https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
    command = [sys.executable, "-m", "pip", "install", package_name]
    if force_reinstall:
        command.append("--force-reinstall")

    return subprocess.run(command, check=True)


def update_appimage(version: str):
    """
    Updates the AppImage locally
    """
    if not version:
        raise ValueError("version cannot be empty")

    # URL to get the latest release metadata
    url = "https://api.github.com/repos/rapyuta-robotics/rapyuta-io-cli/releases/latest"

    try:
        response = requests.get(url)
        data = munchify(response.json())
    except Exception as e:
        click.secho("Failed to fetch release info: {}".format(e), fg=Colors.RED)
        raise SystemExit(1) from e

    asset = None
    for a in data.get("assets", []):
        if "AppImage" in a.name and version in a.name:
            asset = a
            break

    if asset is None:
        raise Exception("Failed to retrieve the download URL for the latest AppImage")

    # Download the AppImage
    try:
        response = requests.get(asset.browser_download_url)
    except Exception as e:
        raise Exception("Failed to download the new version: {}".format(e))

    with TemporaryDirectory() as tmp:
        # Save the binary in a temp dir
        save_to = Path(tmp) / "rio"
        save_to.write_bytes(response.content)
        os.chmod(save_to, 0o755)
        # Now replace the current executable with the new file
        try:
            os.remove(sys.executable)
            move(save_to, sys.executable)
        except OSError as e:
            click.secho(
                "{} Please consider running as a root user.".format(Symbols.WARNING),
                fg=Colors.YELLOW,
            )
            raise e
        except Exception as e:
            raise e


def generate_short_guid() -> str:
    return uuid.uuid4().hex[:8]


def trim_suffix(name):
    if len(name) == 0 or name[0].isalnum():
        return name

    return trim_suffix(name[1:])


def trim_prefix(name):
    if len(name) == 0 or name[len(name) - 1].isalnum():
        return name

    return trim_prefix(name[: len(name) - 1])


def sanitize_label(name):
    if len(name) == 0:
        return name

    name = name[0:63]
    name = trim_suffix(name)
    name = trim_prefix(name)

    r = ""
    for c in name:
        if c.isalnum() or c in ["-", "_", "."]:
            r = r + c

    return r


def print_centered_text(text: str, color: str = Colors.YELLOW):
    col, _ = get_terminal_size()
    text = click.style(f" {text} ".center(col, "-"), fg=color, bold=True)
    click.echo(text)
