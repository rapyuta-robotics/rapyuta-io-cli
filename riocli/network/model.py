# Copyright 2022 Rapyuta Robotics
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
from rapyuta_io.clients.native_network import NativeNetwork, NativeNetworkLimits, Parameters as NativeNetworkParameters
from rapyuta_io.clients.routed_network import RoutedNetwork, RoutedNetworkLimits, Parameters as RoutedNetworkParameters

from riocli.model import Model
from riocli.network.util import find_network_name, NetworkNotFound
from riocli.network.validation import validate


class Network(Model):
    _RoutedNetworkLimits = {
        'small': RoutedNetworkLimits.SMALL,
        'medium': RoutedNetworkLimits.MEDIUM,
        'large': RoutedNetworkLimits.LARGE,
    }

    _NativeNetworkLimits = {
        'xSmall': NativeNetworkLimits.X_SMALL,
        'small': NativeNetworkLimits.SMALL,
        'medium': NativeNetworkLimits.MEDIUM,
        'large': NativeNetworkLimits.LARGE,

    }

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        try:
            network, _ = find_network_name(client, self.metadata.name, self.spec.type, is_resolve_conflict=False)
            return network
        except NetworkNotFound:
            return False

    def create_object(self, client: Client) -> Union[NativeNetwork, RoutedNetwork]:
        if self.spec.type == 'routed':
            return self._create_routed_network(client)

        network = client.create_native_network(self.to_v1(client))
        return network

    def update_object(self, client: Client, obj: Union[RoutedNetwork, NativeNetwork]) -> Any:
        # try:
        #     obj.delete()
        #     self.create_object(client)
        # except Exception as e:
        #     click.secho(str(e), fg='red')
        #     raise SystemExit(1)
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        obj.delete()

    @classmethod
    def pre_process(cls, client: Client, d: Dict) -> None:
        pass

    @staticmethod
    def validate(data) -> None:
        validate(data)

    def to_v1(self, client: Client) -> NativeNetwork:
        if self.spec.runtime == 'cloud':
            limits = self._get_limits()
            parameters = NativeNetworkParameters(limits=limits)
        else:
            device = client.get_device(self.spec.deviceGUID)
            parameters = NativeNetworkParameters(device=device,
                                                 network_interface=self.spec.networkInterface)

        return NativeNetwork(self.metadata.name, self.spec.runtime.lower(), self.spec.rosDistro, parameters=parameters)

    def _create_routed_network(self, client: Client) -> RoutedNetwork:
        if self.spec.runtime == 'cloud':
            network = self._create_cloud_routed_network(client)
        else:
            network = self._create_device_routed_network(client)

        return network

    def _create_cloud_routed_network(self, client: Client) -> RoutedNetwork:
        limits = self._get_limits()
        parameters = RoutedNetworkParameters(limits)
        return client.create_cloud_routed_network(self.metadata.name, self.spec.rosDistro, True, parameters=parameters)

    def _create_device_routed_network(self, client: Client) -> RoutedNetwork:
        device = client.get_device(self.spec.deviceGUID)
        return client.create_device_routed_network(name=self.metadata.name, ros_distro=self.spec.rosDistro, shared=True,
                                                   device=device,
                                                   network_interface=self.spec.networkInterface)

    def _get_limits(self) -> Union[RoutedNetworkLimits, NativeNetworkLimits]:
        if self.spec.type == 'routed':
            return self._RoutedNetworkLimits[self.spec.resourceLimits]
        else:
            return self._NativeNetworkLimits[self.spec.resourceLimits]
