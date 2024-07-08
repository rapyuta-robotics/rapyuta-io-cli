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
from munch import munchify, unmunchify
import click
import time

from rapyuta_io import Client
from rapyuta_io.clients.common_models import Limits
from rapyuta_io.clients.native_network import NativeNetwork, \
    Parameters as NativeNetworkParameters
from rapyuta_io.clients.routed_network import RoutedNetwork, \
    Parameters as RoutedNetworkParameters

from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.v2client.client import NetworkNotFound
from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols, Status

class Network(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        try:
            network, obj = self.rc.find_depends({"kind": self.kind.lower(),
                            "nameOrGUID": self.metadata.name}, self.spec.type)
            if not network:
                return False

            return obj
        except NetworkNotFound:
            return False

    def poll_deployment_till_ready(self, client: Client, network: typing.Any, retry_count = 50, sleep_interval = 6):
        for _ in range(retry_count):
            if network.status and network.status.status == Status.RUNNING:
                return network

            time.sleep(sleep_interval)
            network = client.get_network(network.metadata.name)
        return network

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        network = unmunchify(self)
        network.pop("rc", None)
        r = client.create_network(network)

        retry_count = int(kwargs.get('retry_count'))
        retry_interval = int(kwargs.get('retry_interval'))

        try:
            r = self.poll_deployment_till_ready(
                client = client,
                network = r,
                retry_count=retry_count,
                sleep_interval=retry_interval,
            )
        except Exception as e:
            click.secho(">> {}: Error polling for network ({}:{})".format(
                Symbols.WARNING,
                self.kind.lower(),
                self.metadata.name), fg=Colors.YELLOW)


        return unmunchify(r)

    def update_object(self, client: Client,
                      obj: Union[RoutedNetwork, NativeNetwork]) -> Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()
        client.delete_network(obj.metadata.name)

    @classmethod
    def pre_process(cls, client: Client, d: Dict) -> None:
        pass

    def _get_limits(self):
        return Limits(self.spec.resourceLimits['cpu'],
                      self.spec.resourceLimits['memory'])

    @staticmethod
    def validate(data):
        """
        Validates if network data is matching with its corresponding schema
        """
        schema = load_schema('network')
        schema.validate(data)
