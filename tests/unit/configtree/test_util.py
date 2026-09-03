# Copyright 2026 Rapyuta Robotics
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

"""Tests for configtree utility functions."""

from __future__ import annotations

from base64 import b64encode

from riocli.configtree.util import (
    combine_metadata,
    parse_configtree_value,
    serialize_value,
)


def _encode(value: str) -> str:
    return b64encode(value.encode("utf-8")).decode("utf-8")


class TestCombineMetadata:
    """Tests for combine_metadata()."""

    def test_yaml_scalars_are_typed(self):
        keys = {
            "a/int": {"data": _encode("42")},
            "a/bool": {"data": _encode("true")},
            "a/str": {"data": _encode("hello")},
        }

        result = combine_metadata(keys)

        assert result["a/int"] == 42
        assert result["a/bool"] is True
        assert result["a/str"] == "hello"

    def test_yaml11_booleans_are_preserved_as_strings(self):
        # YAML 1.1 coerces yes/no/on/off to bool; YAML 1.2 (ruamel) keeps them
        # as strings — the core fix for the configtree import/export pipeline.
        keys = {
            "a/yes": {"data": _encode("yes")},
            "a/no": {"data": _encode("no")},
            "a/on": {"data": _encode("on")},
            "a/off": {"data": _encode("off")},
        }

        result = combine_metadata(keys)

        assert result["a/yes"] == "yes"
        assert result["a/no"] == "no"
        assert result["a/on"] == "on"
        assert result["a/off"] == "off"

    def test_octal_0777_is_decimal_777(self):
        # YAML 1.1 (PyYAML) parses 0777 as octal 511; YAML 1.2 treats it as decimal.
        keys = {"cfg/mode": {"data": _encode("0777")}}

        result = combine_metadata(keys)

        assert result["cfg/mode"] == 777

    def test_non_yaml_value_is_kept_as_raw_string(self):
        # Logging format strings are not valid YAML: the leading '[' starts a
        # flow sequence and '%' cannot start a token. They must survive as-is
        # instead of crashing the export.
        fmt = "[%(levelname)s] [%(asctime)s] [%(name)s] <%(process)d>: %(message)s"
        keys = {"wms/logging/format": {"data": _encode(fmt)}}

        result = combine_metadata(keys)

        assert result["wms/logging/format"] == fmt


class TestParseConfigtreeValue:
    """Tests for parse_configtree_value() — ensures put-key matches import types."""

    def test_integer_string_becomes_int(self):
        assert parse_configtree_value("300") == 300
        assert isinstance(parse_configtree_value("300"), int)

    def test_float_string_becomes_float(self):
        assert parse_configtree_value("3.14") == 3.14

    def test_bool_true_becomes_bool(self):
        assert parse_configtree_value("true") is True
        assert parse_configtree_value("false") is False

    def test_null_becomes_none(self):
        assert parse_configtree_value("null") is None

    def test_yaml11_booleans_stay_as_strings(self):
        # YAML 1.2: yes/no/on/off are NOT booleans — strings preserved.
        assert parse_configtree_value("yes") == "yes"
        assert parse_configtree_value("no") == "no"
        assert parse_configtree_value("on") == "on"
        assert parse_configtree_value("off") == "off"

    def test_plain_string_passes_through(self):
        assert parse_configtree_value("hello") == "hello"

    def test_dict_normalizes_to_json_form(self):
        # YAML shorthand {a: 1} → Python dict → json.dumps → '{"a": 1}'
        parsed = parse_configtree_value("{a: 1}")
        stored = serialize_value(parsed)
        assert stored == '{"a": 1}'

    def test_list_normalizes_spacing(self):
        # '[1,2]' (no space) → list [1,2] → json.dumps → '[1, 2]'
        parsed = parse_configtree_value("[1,2]")
        stored = serialize_value(parsed)
        assert stored == "[1, 2]"

    def test_invalid_yaml_falls_back_to_raw_string(self):
        fmt = "[%(levelname)s] [%(asctime)s]: %(message)s"
        assert parse_configtree_value(fmt) == fmt

    def test_metadata_is_combined_with_value(self):
        keys = {
            "a/key": {
                "data": _encode("value"),
                "metadata": {"contentType": "kv"},
            }
        }

        result = combine_metadata(keys)

        assert result["a/key"] == {
            "value": "value",
            "metadata": {"contentType": "kv"},
        }

    def test_key_without_data(self):
        keys = {"a/key": {}}

        result = combine_metadata(keys)

        assert result["a/key"] is None
