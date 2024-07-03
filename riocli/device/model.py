# Copyright 2024 Rapyuta Robotics
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

from riocli.device.util import (
    create_hwil_device,
    delete_hwil_device,
    execute_onboard_command,
    find_device_guid,
    make_device_labels_from_hwil_device
)
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
        if not self.spec.get('virtual', {}).get('enabled', False):
            device = client.create_device(self.to_v1())
            return device

        # Create the HWIL device.
        hwil_response = create_hwil_device(self.spec, self.metadata)

        # Generate labels to store HWIL metadata in rapyuta.io device.
        labels = make_device_labels_from_hwil_device(hwil_response)
        labels.update(self.metadata.get('labels', {}))
        self.metadata.labels = labels

        # Create the rapyuta.io device.
        device = client.create_device(self.to_v1())

        # On-board the HWIL device using the onboard script.
        onboard_script = device.onboard_script()
        onboard_command = onboard_script.full_command()
        execute_onboard_command(hwil_response.id, onboard_command)

        return device

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        if not self.spec.get('virtual', {}).get('enabled', False):
            return obj

        device_uuid = find_device_guid(client, self.metadata.name)
        device = client.get_device(device_uuid)

        # Nothing to do if the device is already online or initializing.
        if device['status'] in ('ONLINE', 'INITIALIZING'):
            return device

        device_labels = device.get('labels', {})
        # Convert list to dict for easy access.
        device_labels = {l['key']: l for l in device_labels}

        # Otherwise, re-onboard the device.
        hwil_response = create_hwil_device(self.spec, self.metadata)
        labels = make_device_labels_from_hwil_device(hwil_response)

        # Add or update labels in the device.
        for k, v in labels.items():
            if k in device_labels:
                device_labels[k]['value'] = v
                device.update_label(device_labels[k])
                continue

            device.add_label(k, v)

        onboard_script = device.onboard_script()
        onboard_command = onboard_script.full_command()
        execute_onboard_command(hwil_response.id, onboard_command)

        return device

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        if self.spec.get('virtual', {}).get('enabled', False):
            device_uuid = find_device_guid(client, self.metadata.name)
            device = client.get_device(device_uuid)
            delete_hwil_device(device)

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

        config_variables = self.spec.get('configVariables', {})
        labels = self.metadata.get('labels', {})

        return v1Device(
            name=self.metadata.name, description=self.spec.get('description'),
            runtime_docker=docker_enabled, runtime_preinstalled=preinstalled_enabled,
            ros_distro=self.spec.rosDistro, python_version=python_version,
            rosbag_mount_path=rosbag_mount_path, ros_workspace=ros_workspace,
            config_variables=config_variables, labels=labels,
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
