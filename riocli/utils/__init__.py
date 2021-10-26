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
from socket import socket
from uuid import UUID

import click
import yaml
from click_help_colors import HelpColorsGroup


def inspect_with_format(obj: typing.Any, format_type: str):
    if format_type == 'json':
        click.echo(json.dumps(obj, indent=4))
    elif format_type == 'yaml':
        click.echo(yaml.dump(obj, allow_unicode=True))
    else:
        raise Exception('Invalid format')


def run_bash(cmd, bg=False):
    cmd_parts = shlex.split(cmd)

    if bg is True:
        bg_output = subprocess.Popen(cmd_parts)
        output = str(bg_output.stdout).strip()
    else:
        output = subprocess.run(cmd_parts, stdout=subprocess.PIPE).stdout.decode('utf-8')
    return output.strip()


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
