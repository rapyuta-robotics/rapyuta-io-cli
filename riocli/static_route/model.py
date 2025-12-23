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
from munch import Munch
from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2 import StaticRoute as StaticRouteModel
from typing_extensions import override

from riocli.config.config import Configuration
from riocli.model import Model


class StaticRoute(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = StaticRouteModel.model_validate(self)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.create_staticroute(self._obj)

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.update_staticroute(name=self._obj.metadata.name, body=self._obj)

    @override
    def delete_object(
        self, v2_client: Client, config: Configuration, *args, **kwargs
    ) -> None:
        _ = v2_client.delete_staticroute(
            name=f"{self._obj.metadata.name}-{config.organization_short_id}"
        )

    @override
    def list_dependencies(self) -> list[str] | None:
        return None
