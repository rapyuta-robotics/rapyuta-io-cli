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
from rapyuta_io_sdk_v2 import Client


class Secret(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.create_secret(unmunchify(self))  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.update_secret(self.metadata.name, unmunchify(self))  # pyright:ignore[reportArgumentType]

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_secret(self.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        return None
