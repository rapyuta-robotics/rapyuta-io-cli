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
from typing import Any
from typing import Union

import click
from click import types

from riocli.constants import Colors
from riocli.utils import tabulate_data


def show_selection(
    ranger: Union[list, dict],
    header: str = "",
    prompt: str = "Select the option",
    show_keys: bool = True,
    highlight_item: str = None,
) -> Any:
    """
    Show a selection prompt to the user.

    :param ranger: List or dictionary of options
    :param header: Header to show before the options
    :param prompt: Prompt to show after the options
    :param show_keys: Show keys in the dictionary (not applicable for lists)
    :param highlight_item: Highlight the selected item in the list (key in case of dict)

    :return: Selected option
    """
    if isinstance(ranger, dict):
        return _show_selection_dict(ranger, header, prompt, show_keys, highlight_item)

    if isinstance(ranger, list):
        return _show_selection_list(ranger, header, prompt, highlight_item)


def _show_selection_list(
    ranger: list,
    header: str,
    prompt: str,
    highlight_item: Any = None,
) -> Any:
    click.secho(header, fg=Colors.YELLOW)
    data = []
    for idx, opt in enumerate(ranger):
        idx_column = f"{idx+1})"
        opt_column = opt
        if highlight_item is not None and opt == highlight_item:
            idx_column = click.style(idx_column, bold=True, italic=True)
            opt_column = click.style(opt_column, bold=True, italic=True)

        data.append([idx_column, opt_column])

    tabulate_data(data, header=(), table_format="plain")

    prompt = click.style(prompt, fg=Colors.BLUE)
    choice = click.prompt(prompt, type=types.IntParamType())

    return ranger[choice - 1]


def _show_selection_dict(
    ranger: dict,
    header: str,
    prompt: str,
    show_keys: bool = True,
    highlight_item: Any = None,
) -> Any:
    click.secho(header, fg=Colors.YELLOW)
    data = []

    for idx, key in enumerate(ranger):
        row = []

        idx_column = f"{idx + 1})"
        key_column = key
        value_column = f"{ranger[key]}"
        if highlight_item is not None and key == highlight_item:
            idx_column = click.style(idx_column, bold=True, italic=True)
            key_column = click.style(key_column, bold=True, italic=True)
            value_column = click.style(value_column, bold=True, italic=True)

        row.append(idx_column)
        row.append(value_column)
        if show_keys:
            row.append(key_column)

        data.append(row)

    tabulate_data(data, headers=(), table_format="plain")

    prompt = click.style(prompt, fg=Colors.BLUE)
    choice = click.prompt(prompt, type=types.IntParamType())

    options = list(ranger.keys())

    return options[choice - 1]
