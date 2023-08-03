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
from time import sleep

import click
from munch import munchify
from rapyuta_io import Client
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.constants import Colors, Symbols
from riocli.disk.util import _api_call
from riocli.jsonschema.validate import load_schema
from riocli.model import Model


class Disk(Model):
    def find_object(self, client: Client) -> typing.Any:
        _, disk = self.rc.find_depends({
            'kind': 'disk',
            'nameOrGUID': self.metadata.name
        })

        if not disk:
            return False

        return disk

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        labels = self.metadata.get('labels', None)
        payload = {
            "labels": labels,
            "name": self.metadata.name,
            "diskType": "ssd",
            "runtime": self.spec.runtime,
            "capacity": self.spec.capacity,
        }

        result = _api_call(HttpMethod.POST, payload=payload)
        result = munchify(result)
        disk_dep_guid, disk = self.rc.find_depends({
            'kind': self.kind.lower(),
            'nameOrGUID': self.metadata.name
        })

        volume_instance = client.get_volume_instance(disk_dep_guid)

        retry_count = int(kwargs.get('retry_count'))
        retry_interval = int(kwargs.get('retry_interval'))
        try:
            volume_instance.poll_deployment_till_ready(
                retry_count=retry_count,
                sleep_interval=retry_interval
            )
        except Exception as e:
            click.secho(">> {}: Error polling for disk ({}:{})".format(
                Symbols.WARNING,
                self.kind.lower(),
                self.metadata.name), fg=Colors.YELLOW)

        return result

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        self._poll_till_available(client, obj)
        volume_instance = client.get_volume_instance(obj.internalDeploymentGUID)
        volume_instance.destroy_volume_instance()

    def _poll_till_available(self, client: Client, obj: typing.Any, sleep_interval=5, retries=10):
        dep_guid = obj.internalDeploymentGUID
        deployment = client.get_deployment(deployment_id=dep_guid)

        for _ in range(retries):
            status = deployment.get_status().status
            if status != 'Available':
                sleep(sleep_interval)
                continue

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        schema = load_schema('disk')
        schema.validate(data)
