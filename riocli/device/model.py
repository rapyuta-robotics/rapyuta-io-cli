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
from rapyuta_io.clients.device import Device as v1Device, DevicePythonVersion, DeviceRuntime

from riocli.device.util import find_device_guid, DeviceNotFound
from riocli.device.validation import validate
from riocli.model import Model


class Device(Model):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        try:
            find_device_guid(client, self.metadata.name)
            click.echo('{}/{} {} exists'.format(self.apiVersion, self.kind, self.metadata.name))
            return True
        except DeviceNotFound:
            return False

    def create_object(self, client: Client) -> v1Device:
        project = client.create_device(self.to_v1())
        click.secho('{}/{} {} created'.format(self.apiVersion, self.kind, self.metadata.name), fg='green')
        return project

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def to_v1(self) -> v1Device:
        python_version = DevicePythonVersion(self.spec.python)
        runtime = self._get_runtime()
        rosbag_mount_path = None
        ros_workspace = None

        if runtime == DeviceRuntime.DOCKER:
            rosbag_mount_path = self.spec.docker.rosbagMountPath
        else:
            ros_workspace = self.spec.preinstalled.catkinWorkspace

        return v1Device(name=self.metadata.name, description=self.spec.get('description'),
                        runtime=runtime, ros_distro=self.spec.rosDistro,
                        python_version=python_version, rosbag_mount_path=rosbag_mount_path,
                        ros_workspace=ros_workspace)

    def _get_runtime(self) -> DeviceRuntime:
        # TODO: Get rid of it once we support both runtimes on same device.
        if self.spec.get('docker') and self.spec.docker.enabled:
            return DeviceRuntime.DOCKER

        if self.spec.get('preinstalled') and self.spec.preinstalled.enabled:
            return DeviceRuntime.PREINSTALLED

        raise Exception('select atleast one device runtime')

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data) -> None:
        validate(data)
