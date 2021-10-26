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
from typing import Union

import click
from click import types


def show_selection(ranger: Union[list, dict], header: str = '', prompt: str = 'Select the option'):
    if isinstance(ranger, dict):
        return _show_selection_dict(ranger, header, prompt)
    elif isinstance(ranger, list):
        return _show_selection_list(ranger, header, prompt)


def _show_selection_list(ranger: list, header: str, prompt: str):
    fmt = header
    for idx, opt in enumerate(ranger):
        fmt = '{}\n{}) {}'.format(fmt, idx+1, opt)

    fmt = '{}\n{}'.format(fmt, prompt)
    choice = click.prompt(fmt, type=types.IntParamType())
    return ranger[choice-1]


def _show_selection_dict(ranger: dict, header: str, prompt: str):
    options = []
    fmt = header
    for idx, key in enumerate(ranger):
        options.append(key)
        fmt = '{}\n{}) {} - {}'.format(fmt, idx+1, key, ranger[key])

    fmt = '{}\n{}'.format(fmt, prompt)
    choice = click.prompt(fmt, type=types.IntParamType())
    return options[choice-1]
