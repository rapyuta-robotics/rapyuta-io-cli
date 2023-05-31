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
import typing
from typing import Union, Any, Dict

from rapyuta_io import Client
from rapyuta_io.clients.common_models import Limits
from rapyuta_io.clients.native_network import NativeNetwork, \
    Parameters as NativeNetworkParameters
from rapyuta_io.clients.routed_network import RoutedNetwork, \
    Parameters as RoutedNetworkParameters

from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.network.util import find_network_name, NetworkNotFound


class Network(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        try:
            network, _ = find_network_name(client, self.metadata.name,
                                           self.spec.type,
                                           is_resolve_conflict=False)
            return network
        except NetworkNotFound:
            return False

    def create_object(self, client: Client, **kwargs) -> Union[NativeNetwork, RoutedNetwork]:
        retry_count = int(kwargs.get('retry_count'))
        retry_interval = int(kwargs.get('retry_interval'))
        if self.spec.type == 'routed':
            network = self._create_routed_network(client)
            network.poll_routed_network_till_ready(retry_count=retry_count, sleep_interval=retry_interval)
            return network

        network = client.create_native_network(self.to_v1(client))
        network.poll_native_network_till_ready(retry_count=retry_count, sleep_interval=retry_interval)
        return network

    def update_object(self, client: Client,
                      obj: Union[RoutedNetwork, NativeNetwork]) -> Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        obj.delete()

    @classmethod
    def pre_process(cls, client: Client, d: Dict) -> None:
        pass

    def to_v1(self, client: Client) -> NativeNetwork:
        if self.spec.runtime == 'cloud':
            limits = self._get_limits()
            parameters = NativeNetworkParameters(limits=limits)
        else:
            device = client.get_device(self.spec.deviceGUID)
            parameters = NativeNetworkParameters(
                device=device,
                network_interface=self.spec.networkInterface)

        return NativeNetwork(
            self.metadata.name,
            self.spec.runtime.lower(),
            self.spec.rosDistro,
            parameters=parameters
        )

    def _get_limits(self):
        return Limits(self.spec.resourceLimits['cpu'],
                      self.spec.resourceLimits['memory'])

    def _create_routed_network(self, client: Client) -> RoutedNetwork:
        if self.spec.runtime == 'cloud':
            network = self._create_cloud_routed_network(client)
        else:
            network = self._create_device_routed_network(client)

        return network

    def _create_cloud_routed_network(self, client: Client) -> RoutedNetwork:
        limits = self._get_limits()
        parameters = RoutedNetworkParameters(limits)
        return client.create_cloud_routed_network(self.metadata.name,
                                                  self.spec.rosDistro, True,
                                                  parameters=parameters)

    def _create_device_routed_network(self, client: Client) -> RoutedNetwork:
        device = client.get_device(self.spec.deviceGUID)
        return client.create_device_routed_network(
            name=self.metadata.name,
            ros_distro=self.spec.rosDistro,
            shared=True,
            device=device,
            network_interface=self.spec.networkInterface,
        )

    @staticmethod
    def validate(data):
        """
        Validates if network data is matching with its corresponding schema
        """
        schema = load_schema('network')
        schema.validate(data)
