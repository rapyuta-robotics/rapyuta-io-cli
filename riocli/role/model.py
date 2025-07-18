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

from munch import Munch, unmunchify
from typing_extensions import override

from riocli.model import Model
from riocli.v2client.client import Client


class Role(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.create_role(unmunchify(self))  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.update_role(self.metadata.name, unmunchify(self))  # pyright:ignore[reportArgumentType]

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_role(self.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        return None


class RoleBinding(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.create_role_binding(unmunchify(self))  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.update_role_binding(self.metadata.name, unmunchify(self))  # pyright:ignore[reportArgumentType]

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_role_binding(self.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        dependencies: list[str] = []

        role_name = self.spec.get("roleRef", {}).get("name", None)
        if role_name is not None:
            dependencies.append(f"role:{role_name}")

        subject_kind = self.spec.get("subject", {}).get("kind", None)
        subject_name = self.spec.get("subject", {}).get("name", None)
        if subject_kind is not None and subject_name is not None:
            dependencies.append(f"{subject_kind}:{subject_name}")

        domain_kind = self.spec.get("domain", {}).get("kind", None)
        domain_name = self.spec.get("domain", {}).get("name", None)
        if domain_kind is not None and domain_name is not None:
            dependencies.append(f"{domain_kind}:{domain_name}")

        return dependencies
