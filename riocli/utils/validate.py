# Copyright 2023 Rapyuta Robotics
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

from functools import lru_cache
from pathlib import Path

import yaml

import jsonschema


@lru_cache(maxsize=None)
def load_schema(resource: str) -> dict:
    """
    Reads JSON schema yaml and returns a dict.
    """
    schema_dir = Path('jsonschema')
    with open(schema_dir.joinpath(resource + "-schema.yaml")) as f:
        return yaml.safe_load(f)


def validate_manifest(instance, schema) -> None:
    """
    Validates a manifest against a JSON schema.
    """
    jsonschema.validate(instance, schema)
