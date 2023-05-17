# Copyright 2021 Rapyuta Robotics
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
import random
import shlex
import string
import subprocess
import typing
from shutil import get_terminal_size
from uuid import UUID

import click
import yaml
from click_help_colors import HelpColorsGroup
from tabulate import tabulate


def inspect_with_format(obj: typing.Any, format_type: str):
    if format_type == 'json':
        click.echo_via_pager(json.dumps(obj, indent=4))
    elif format_type == 'yaml':
        click.echo_via_pager(yaml.dump(obj, allow_unicode=True))
    else:
        raise Exception('Invalid format')


def dump_all_yaml(objs: typing.List):
    """
    Dump multiple documents as YAML separated by triple dash (---)
    """
    click.echo_via_pager(
        yaml.safe_dump_all(
            documents=objs,
            allow_unicode=True,
            explicit_start=True
        )
    )


def run_bash_with_return_code(cmd, bg=False) -> (str, int):
    cmd_parts = shlex.split(cmd)

    if bg is True:
        output = subprocess.Popen(cmd_parts)
        stdout = str(output.stdout).strip()
        ret_code = output.returncode
    else:
        output = subprocess.run(cmd_parts, stdout=subprocess.PIPE)
        stdout = output.stdout.decode('utf-8')
        ret_code = output.returncode

    return stdout.strip(), ret_code


def run_bash(cmd, bg=False) -> str:
    """
    Runs a bash command and returns the output only
    """
    output, _ = run_bash_with_return_code(cmd, bg)

    return output


riocli_group_opts = {
    'invoke_without_command': True,
    'cls': HelpColorsGroup,
    'help_headers_color': 'yellow',
    'help_options_color': 'green'
}


def random_string(letter_count, digit_count):
    str1 = ''.join((random.choice(string.ascii_letters) for x in range(letter_count)))
    str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))

    sam_list = list(str1)  # it converts the string to list.
    random.shuffle(sam_list)  # It uses a random.shuffle() function to shuffle the string.
    final_string = ''.join(sam_list)
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
    table_format = 'simple'
    header_foreground = 'yellow'

    if headers:
        headers = [click.style(h, fg=header_foreground) for h in headers]

    click.echo(tabulate(data, headers=headers, tablefmt=table_format))


def print_separator(color: str = 'blue'):
    """
    Prints a separator
    """
    col, _ = get_terminal_size()
    click.secho(" " * col, bg=color)
