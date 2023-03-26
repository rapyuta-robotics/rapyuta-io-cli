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

from rapyuta_io import Client
from rapyuta_io.clients.device import Device as v1Device, DevicePythonVersion

from riocli.jsonschema.validate import load_schema
from riocli.model import Model


class Device(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        guid, obj = self.rc.find_depends({
            "kind": "device",
            "nameOrGUID": self.metadata.name,
        })

        if not guid:
            return False

        return obj

    def create_object(self, client: Client, **kwargs) -> v1Device:
        device = client.create_device(self.to_v1())
        return device

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        obj.delete()

    def to_v1(self) -> v1Device:
        python_version = DevicePythonVersion(self.spec.python)
        rosbag_mount_path = None
        ros_workspace = None

        docker_enabled = self.spec.get('docker', False) and self.spec.docker.enabled
        if docker_enabled:
            rosbag_mount_path = self.spec.docker.rosbagMountPath

        preinstalled_enabled = self.spec.get('preinstalled', False) and self.spec.preinstalled.enabled
        if preinstalled_enabled and self.spec.preinstalled.get('catkinWorkspace'):
            ros_workspace = self.spec.preinstalled.catkinWorkspace

        return v1Device(
            name=self.metadata.name, description=self.spec.get('description'),
            runtime_docker=docker_enabled, runtime_preinstalled=preinstalled_enabled,
            ros_distro=self.spec.rosDistro, python_version=python_version,
            rosbag_mount_path=rosbag_mount_path, ros_workspace=ros_workspace
        )

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        """
        Validates if device data is matching with its corresponding schema
        """
        schema = load_schema('device')
        schema.validate(data)
