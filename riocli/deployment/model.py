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

import click
from rapyuta_io import Client
from rapyuta_io.clients.catalog_client import Package
from rapyuta_io.clients.package import ProvisionConfiguration

from riocli.deployment.validation import validate
from riocli.deployment.util import find_deployment_guid, DeploymentNotFound
from riocli.model import Model
from riocli.package.util import find_package_guid
from riocli.static_route.util import find_static_route_guid


class Deployment(Model):
    def find_object(self, client: Client) -> typing.Any:
        try:
            deployment = find_deployment_guid(client, self.metadata.name)
            click.echo('>> {}/{} {} exists'.format(self.apiVersion, self.kind, self.metadata.name))
            return deployment
        except DeploymentNotFound:
            return False

    def create_object(self, client: Client) -> typing.Any:
        click.secho("Creating {}:{}".format(self.kind.lower(), self.metadata.name), fg='green')
        # print(self)
        return

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        click.secho("Updating {}:{}".format(self.kind.lower(), self.metadata.name), fg='yellow')
        # print(self)
        pass

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:

        pass

    @staticmethod
    def validate(data):
        validate(data)

    def _get_package(self, client: Client) -> Package:
        name = self.metadata.depends.nameOrGUID
        if name.startswith('pkg-') or name.startswith('io-'):
            guid = name
        else:
            guid = find_package_guid(client, name, self.metadata.depends.version)

        return client.get_package(package_id=guid)

    def _get_provision_config(self, client: Client, pkg: Package):
        comp_name = pkg['plans']['components'][0]['name']
        prov_config = pkg.get_provision_configuration()
        self._configure_static_routes(client, prov_config, comp_name)

        return prov_config

    def _configure_networks(self, client: Client, prov_config: ProvisionConfiguration):
        if not self.spec.get('rosNetworks'):
            return

        native_networks = client.list_native_networks()
        routed_networks = client.get_all_routed_networks()


    def _configure_disks(self, client: Client, prov_config: ProvisionConfiguration, component: str):
        if not self.spec.get('volumes'):
            return

        # for volume in self.spec.volumes:
        #     # TODO: no support for the disk resource.
        #     # TODO: subpath is not there in the SDK.
        #     prov_config.mount_volume(component_name=component, volume='', mount_path=volume.mountPath)

    def _configure_static_routes(self, client: Client, prov_config: ProvisionConfiguration, component: str):
        if not self.spec.get('staticRoutes'):
            return

        # TODO: List instead of get calls again and again

        for route in self.spec.staticRoutes:
            name = route.depends.nameOrGUID
            if name.startswith('staticroute-'):
                guid = name
            else:
                guid = find_static_route_guid(client, name)
            static_route = client.get_static_route(route_guid=guid)
            prov_config.add_static_route(component_name=component, endpoint_name=route.name, static_route=static_route)
