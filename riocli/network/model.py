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
from rapyuta_io_sdk_v2 import Network as NetworkModel
from typing_extensions import override

from riocli.model import Model
from riocli.network.util import poll_network


class Network(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = NetworkModel.model_validate(self)

    @override
    def create_object(
        self, v2_client: Client, retry_count: int, retry_interval: int, *args, **kwargs
    ) -> NetworkModel:
        network = v2_client.create_network(self._obj)  # pyright:ignore[reportArgumentType]
        return poll_network(
            client=v2_client,
            name=network.metadata.name,  # pyright: ignore[reportOptionalMemberAccess]
            retry_count=retry_count,
            sleep_interval=retry_interval,
        )

    @override
    def update_object(self, *args, **kwargs) -> Munch | None:
        raise NotImplementedError

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_network(self._obj.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        self._obj.list_dependencies()
