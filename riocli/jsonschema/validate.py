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
import functools
from pathlib import Path

import yaml
from jsonschema import validators, Draft7Validator


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for p, sub_schema in properties.items():
            if "default" not in sub_schema:
                continue
            if isinstance(instance, dict):
                instance.setdefault(p, sub_schema["default"])
            if isinstance(instance, list):
                for i in instance:
                    i.setdefault(p, sub_schema["default"])

        for error in validate_properties(
            validator,
            properties,
            instance,
            schema,
        ):
            yield error

    return validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


DefaultValidator = extend_with_default(Draft7Validator)


@functools.lru_cache(maxsize=None)
def load_schema(resource: str) -> DefaultValidator:
    """
    Reads JSON schema yaml and returns a validator.
    """
    schema_dir = Path(__file__).parent.joinpath("schemas")
    with open(schema_dir.joinpath(resource + "-schema.yaml")) as f:
        return DefaultValidator(yaml.safe_load(f))
