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

"""Tests for configtree value serialization."""

from __future__ import annotations

import json
from datetime import datetime

from riocli.configtree.util import serialize_value


class TestSerializeValue:
    """Tests for serialize_value()."""

    def test_string_passes_through(self):
        assert serialize_value("hello") == "hello"

    def test_logging_format_string_is_untouched(self):
        fmt = "[%(levelname)s] [%(asctime)s] [%(name)s] <%(process)d>: %(message)s"
        assert serialize_value(fmt) == fmt

    def test_dict_serializes_to_json_with_double_quotes(self):
        value = {"csv_column_name": "Order box type", "name": "box_type"}

        result = serialize_value(value)

        assert "'" not in result
        assert json.loads(result) == value

    def test_list_of_dicts_serializes_to_json(self):
        # Regression: str() on a list of dicts produces Python repr with
        # single quotes, which is not valid JSON.
        value = [
            {
                "csv_column_name": "Order box type",
                "display_name": "Box Type",
                "name": "box_type",
                "type": "string",
            }
        ]

        result = serialize_value(value)

        assert "'" not in result
        assert json.loads(result) == value

    def test_scalars_serialize_to_json(self):
        assert serialize_value(300) == "300"
        assert serialize_value(True) == "true"
        assert serialize_value(None) == "null"

    def test_datetime_serializes_to_isoformat(self):
        value = {"ts": datetime(2026, 6, 6, 15, 31, 8)}

        result = serialize_value(value)

        assert json.loads(result) == {"ts": "2026-06-06T15:31:08"}

    def test_unicode_is_not_escaped(self):
        result = serialize_value({"site": "台場"})

        assert "台場" in result
