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
import sys
from typing import Any

import click
from click import types

from riocli.constants import Colors
from riocli.utils import tabulate_data


def show_selection(
    ranger: list | dict,
    header: str = "",
    prompt: str = "Select the option",
    show_keys: bool = True,
    highlight_item: str = None,
) -> Any:
    """
    Show a selection prompt to the user.

    When running in an interactive terminal, shows an fzf-style interactive
    selector with fuzzy search and arrow-key navigation. Falls back to a
    numbered list with integer prompt when not in a TTY.

    :param ranger: List or dictionary of options
    :param header: Header to show before the options
    :param prompt: Prompt to show after the options
    :param show_keys: Show keys in the dictionary (not applicable for lists)
    :param highlight_item: Highlight the selected item in the list (key in case of dict)

    :return: Selected option
    """
    # Use interactive fuzzy selector when stdout is a real TTY
    if sys.stdout.isatty() and sys.stdin.isatty():
        if isinstance(ranger, dict):
            return _fuzzy_selection_dict(ranger, header)
        if isinstance(ranger, list):
            return _fuzzy_selection_list(ranger, header)

    # Fallback: numbered list + integer prompt (for pipes / non-interactive use)
    if isinstance(ranger, dict):
        return _show_selection_dict(ranger, header, prompt, show_keys, highlight_item)
    if isinstance(ranger, list):
        return _show_selection_list(ranger, header, prompt, highlight_item)


# ---------------------------------------------------------------------------
# Interactive fuzzy selectors (prompt_toolkit)
# ---------------------------------------------------------------------------


def _fuzzy_selection_list(items: list, header: str) -> Any:
    """Interactive fuzzy-search selector for a plain list."""
    chosen = _run_fuzzy_picker(items, items, header)
    return chosen


def _fuzzy_selection_dict(ranger: dict, header: str) -> Any:
    """Interactive fuzzy-search selector for a dict (returns the key/GUID).

    Passes keys as ``return_items`` so the picker returns the selected key
    directly, avoiding any label-to-key lookup that would break on duplicate
    labels.
    """
    keys = list(ranger.keys())
    labels = list(ranger.values())
    return _run_fuzzy_picker(labels, keys, header)


def _run_fuzzy_picker(display_items: list, return_items: list, header: str) -> Any:
    """
    Renders an fzf-style interactive picker using prompt_toolkit.

    - Type to filter (fuzzy/substring match)
    - Up/Down arrows or Ctrl-P/Ctrl-N to move cursor
    - Enter to confirm selection
    - Ctrl-C / Escape to abort
    """
    from prompt_toolkit import Application
    from prompt_toolkit.formatted_text import HTML, to_formatted_text
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.layout.containers import HSplit, Window
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.styles import Style

    style = Style.from_dict(
        {
            "header": "bold ansiyellow",
            "selected": "bold ansiblue reverse",
            "item": "",
            "info": "ansigreen",
            "prompt": "ansicyan bold",
            "count": "ansibrightblack",
            "separator": "ansibrightblack",
        }
    )

    state = {
        "query": "",
        "cursor": 0,
        "filtered": list(range(len(display_items))),
        "result": None,
        "aborted": False,
    }

    def _matches(query: str, text: str) -> bool:
        """Case-insensitive fuzzy match: every character of query must appear
        in order somewhere in text (same algorithm as fzf's default mode)."""
        query = query.lower()
        text = text.lower()
        it = iter(text)
        return all(c in it for c in query)

    def _refilter():
        q = state["query"]
        if not q:
            state["filtered"] = list(range(len(display_items)))
        else:
            state["filtered"] = [
                i for i, item in enumerate(display_items) if _matches(q, str(item))
            ]
        # Clamp cursor
        if state["filtered"]:
            state["cursor"] = min(state["cursor"], len(state["filtered"]) - 1)
        else:
            state["cursor"] = 0

    def _get_content():
        # FormattedTextControl requires a flat list of (style, text) tuples.
        # Convert each HTML fragment and concatenate them.
        result = []

        def _add(html_str: str):
            result.extend(to_formatted_text(HTML(html_str)))

        if header:
            _add(f"<header>  {_escape(header)}</header>\n")

        filtered = state["filtered"]
        total = len(display_items)
        matched = len(filtered)
        _add(
            f"<count>  {matched}/{total} items</count>  "
            f"<info>↑↓ navigate · type to filter · Enter select · Esc abort</info>\n"
        )
        _add(f"<separator>  &gt; </separator>{_escape(state['query'])}\n")
        _add(f"<separator>  {'─' * 60}</separator>\n")

        for rank, orig_idx in enumerate(filtered):
            label = str(display_items[orig_idx])
            if rank == state["cursor"]:
                _add(f"<selected>  » {_escape(label)}</selected>\n")
            else:
                _add(f"<item>    {_escape(label)}</item>\n")

        return result

    def _escape(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    content_control = FormattedTextControl(text=_get_content, focusable=False)
    content_window = Window(content=content_control, wrap_lines=False)

    kb = KeyBindings()

    @kb.add("up")
    @kb.add("c-p")
    def _up(event):
        if state["filtered"] and state["cursor"] > 0:
            state["cursor"] -= 1

    @kb.add("down")
    @kb.add("c-n")
    def _down(event):
        if state["filtered"] and state["cursor"] < len(state["filtered"]) - 1:
            state["cursor"] += 1

    @kb.add("enter")
    def _enter(event):
        if state["filtered"]:
            orig_idx = state["filtered"][state["cursor"]]
            state["result"] = return_items[orig_idx]
        event.app.exit()

    @kb.add("escape")
    @kb.add("c-c")
    def _abort(event):
        state["aborted"] = True
        event.app.exit()

    @kb.add("backspace")
    @kb.add("c-h")
    def _backspace(event):
        if state["query"]:
            state["query"] = state["query"][:-1]
            state["cursor"] = 0
            _refilter()

    @kb.add("c-u")
    def _clear_line(event):
        state["query"] = ""
        state["cursor"] = 0
        _refilter()

    # Catch all printable characters for the search query
    @kb.add("<any>")
    def _char(event):
        data = event.data
        if data and data.isprintable() and len(data) == 1:
            state["query"] += data
            state["cursor"] = 0
            _refilter()

    layout = Layout(
        HSplit([content_window]),
        focused_element=content_window,
    )

    app = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=False,
        mouse_support=False,
    )

    app.run()

    if state["aborted"] or state["result"] is None:
        raise click.Abort()

    return state["result"]


# ---------------------------------------------------------------------------
# Legacy fallback selectors (numbered list + integer prompt)
# ---------------------------------------------------------------------------


def _show_selection_list(
    ranger: list,
    header: str,
    prompt: str,
    highlight_item: Any = None,
) -> Any:
    click.secho(header, fg=Colors.YELLOW)
    data = []
    for idx, opt in enumerate(ranger):
        idx_column = f"{idx + 1})"
        opt_column = opt
        if highlight_item is not None and opt == highlight_item:
            idx_column = click.style(idx_column, bold=True, italic=True)
            opt_column = click.style(opt_column, bold=True, italic=True)

        data.append([idx_column, opt_column])

    tabulate_data(data, headers=(), table_format="plain")

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
