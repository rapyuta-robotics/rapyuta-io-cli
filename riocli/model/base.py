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
import typing
from abc import ABC, abstractmethod

from munch import Munch

from riocli.constants import ApplyResult
from riocli.jsonschema.validate import load_schema

DELETE_POLICY_LABEL = "rapyuta.io/deletionPolicy"


class Model(ABC, Munch):
    """Base class for all models.

    This class provides the basic structure for all models. It
    also provides the basic methods that should be implemented by
    all models. The methods are:

    # Create or update the object
    def apply(self, *args, **kwargs):
        pass

    # Delete the object
    def delete(self, *args, **kwargs):
        pass

    The validate method is a class method that need not be implemented
    by the subclasses. It validates the model against the corresponding
    schema that are defined in the schema files.
    """

    @abstractmethod
    def apply(self, *args, **kwargs) -> ApplyResult:
        """Create or update the object.

        This method should be implemented by the subclasses. It should
        create or update the object based on the values in the model.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs) -> None:
        """Delete the object.

        This method should be implemented by the subclasses. It should
        delete the object based on the values in the model.
        """
        raise NotImplementedError

    @classmethod
    def validate(cls, d: typing.Dict) -> None:
        """Validate the model against the corresponding schema."""
        kind = d.get("kind")
        if not kind:
            raise ValueError("kind is required")

        # StaticRoute's schema file is named
        # static_route-schema.yaml.
        if kind == "StaticRoute":
            kind = "static_route"

        schema = load_schema(kind.lower())
        schema.validate(d)
