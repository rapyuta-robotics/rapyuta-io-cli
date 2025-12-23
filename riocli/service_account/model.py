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
from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2 import ServiceAccount as ServiceAccountModel
from typing_extensions import override

from riocli.model import Model


class ServiceAccount(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = ServiceAccountModel.model_validate(self)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs):
        return v2_client.create_service_account(service_account=self._obj)

    @override
    def update_object(self, v2_client: Client, *args, **kwargs):
        return v2_client.update_service_account(
            service_account=self._obj, name=self._obj.metadata.name
        )

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_service_account(name=self._obj.metadata.name)

    @override
    def list_dependencies(self):
        return self._obj.list_dependencies()
