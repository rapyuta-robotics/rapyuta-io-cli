# Copyright 2025 Rapyuta Robotics
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
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from munch import Munch
from rapyuta_io import Client
from rapyuta_io_sdk_v2 import Client as v2Client
from rapyuta_io_sdk_v2.exceptions import (
    HttpAlreadyExistsError,
    HttpNotFoundError,
    UnauthorizedAccessError,
)

from riocli.config.config import Configuration
from riocli.constants import ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.jsonschema.validate import load_schema

DELETE_POLICY_LABEL = "rapyuta.io/deletionPolicy"


class Model(ABC, Munch):
    """Base class for all models.

    This class provides the basic structure for all models. It
    also provides the basic methods that should be implemented by
    all models. The methods are:

    @override
    def create_object(self, *args, **kwargs) -> Munch | None:
        pass

    @override
    def update_object(self, *args, **kwargs) -> Munch | None:
        pass

    @override
    def delete_object(self, *args, **kwargs) -> None:
        pass

    @override
    def list_dependencies(self, *args, **kwargs) -> list[str] | None:
        pass

    The validate method is a class method that need not be implemented
    by the subclasses. It validates the model against the corresponding
    schema that are defined in the schema files.
    """

    @abstractmethod
    def create_object(
        self,
        client: Client,
        v2_client: v2Client,
        config: Configuration,
        retry_count: int,
        retry_interval: int,
    ) -> Munch | None:
        """
        Create the object using passed clients and configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def update_object(
        self,
        client: Client,
        v2_client: v2Client,
        config: Configuration,
        retry_count: int,
        retry_interval: int,
    ) -> Munch | None:
        """Update the object using passed clients and configuration. If the
        Resource does not support Update operation, raise NotImplementedError.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_object(
        self,
        client: Client,
        v2_client: v2Client,
        config: Configuration,
        retry_count: int,
        retry_interval: int,
    ) -> None:
        """
        Delete the object using passed clients and configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def list_dependencies(self) -> list[str] | None:
        """List the object's direct dependencies.

        This method should be implemented by the subclasses. It should
        list the dependencies the object in the KIND:NAME format.
        """
        raise NotImplementedError

    @staticmethod
    def object_key(obj: Mapping[str, Any]) -> str:
        """
        Generate a unique object key for the Object.
        """

        # Note that this function will run on pre-parsed Objects.
        # Using defensive strategy to get the fields.

        kind = obj.get("kind", "")
        name = obj.get("metadata", {}).get("name", "")

        if not kind:
            raise ValueError("kind is a required field")
        if not name:
            raise ValueError(f"[kind:{kind}] {name} is required")

        return f"{kind.lower()}:{name}"

    def apply(
        self,
        client: Client,
        v2_client: v2Client,
        config: Configuration,
        retry_count: int,
        retry_interval: int,
    ) -> ApplyResult:
        """
        Create or update the object.
        """
        metadata = self.get("metadata")
        if metadata is not None:
            if "createdAt" in metadata:
                del metadata["createdAt"]
            if "updatedAt" in metadata:
                del metadata["updatedAt"]

        try:
            _ = self.create_object(
                client=client,
                v2_client=v2_client,
                config=config,
                retry_count=retry_count,
                retry_interval=retry_interval,
            )
            return ApplyResult.CREATED
        except (HttpAlreadyExistsError, UnauthorizedAccessError) as e:
            # In case of Unauthorized, still try to update. The user might only
            # have Update permission, and will get Unauthorized error on
            # creation.
            try:
                _ = self.update_object(
                    client=client,
                    v2_client=v2_client,
                    config=config,
                    retry_count=retry_count,
                    retry_interval=retry_interval,
                )
                return ApplyResult.UPDATED
            except NotImplementedError:
                # Handle the case where the resource does not implement Update.
                # If we received Unauthorized in creation, raise it again.
                if isinstance(e, UnauthorizedAccessError):
                    raise e

                return ApplyResult.EXISTS

    def delete(
        self,
        client: Client,
        v2_client: v2Client,
        config: Configuration,
        retry_count: int,
        retry_interval: int,
    ) -> None:
        """Delete the object."""
        try:
            _ = self.delete_object(
                client=client,
                v2_client=v2_client,
                config=config,
                retry_count=retry_count,
                retry_interval=retry_interval,
            )
        except HttpNotFoundError:
            raise ResourceNotFound

    @classmethod
    def validate(cls, d: Mapping[str, Any]) -> None:
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
