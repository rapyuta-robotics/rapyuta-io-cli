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

from rapyuta_io.clients.device import Device as v1Device, DevicePythonVersion

from riocli.config import new_client
from riocli.constants import ApplyResult
from riocli.device.util import (
    DeviceNotFound,
    create_hwil_device,
    delete_hwil_device,
    execute_onboard_command,
    find_device_by_name,
    make_device_labels_from_hwil_device,
    wait_until_online,
)
from riocli.exceptions import ResourceNotFound
from riocli.model import Model


class Device(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> ApplyResult:
        client = new_client()

        device = None

        try:
            device = find_device_by_name(client, self.metadata.name)
        except DeviceNotFound:
            pass

        virtual = self.spec.get("virtual", {})

        # If the device is not virtual, create it and return.
        if not virtual.get("enabled", False):
            if device is None:
                client.create_device(self.to_v1())
                return ApplyResult.CREATED

            return ApplyResult.EXISTS

        # Return if the device is already online or initializing.
        if device and device["status"] in ("ONLINE", "INITIALIZING"):
            return ApplyResult.EXISTS

        result = ApplyResult.CREATED if device is None else ApplyResult.UPDATED

        # Create the HWIL (virtual) device and then generate the labels
        # to store HWIL metadata in rapyuta.io device.
        hwil_response = create_hwil_device(virtual, self.metadata)
        labels = make_device_labels_from_hwil_device(hwil_response)

        # Create the rapyuta.io device with labels if the
        # device does not exist. Else, update the labels.
        if device is None:
            labels.update(self.metadata.get("labels", {}))
            self.metadata.labels = labels
            device = client.create_device(self.to_v1())
        else:
            device_labels = device.get("labels", {})
            # Convert list to dict for easy access.
            device_labels = {l["key"]: l for l in device_labels}
            # Add or update labels in the device.
            for k, v in labels.items():
                if k in device_labels:
                    device_labels[k]["value"] = v
                    device.update_label(device_labels[k])
                    continue

                device.add_label(k, v)

        # On-board the HWIL device using the onboard script.
        onboard_script = device.onboard_script()
        onboard_command = onboard_script.full_command()
        execute_onboard_command(hwil_response.id, onboard_command)

        if virtual.get("wait", False):
            wait_until_online(device)

        return result

    def delete(self, *args, **kwargs) -> None:
        client = new_client()

        try:
            device = find_device_by_name(client, self.metadata.name)
        except DeviceNotFound:
            # If it was a virtual device, try deleting the HWIL
            # resource if it is present and raise ResourceNotFound.
            if self.spec.get("virtual", {}).get("enabled", False):
                delete_hwil_device(self.spec.virtual, self.metadata)

            raise ResourceNotFound

        if self.spec.get("virtual", {}).get("enabled", False):
            delete_hwil_device(self.spec.virtual, self.metadata)

        device.delete()

    def to_v1(self) -> v1Device:
        python_version = DevicePythonVersion(self.spec.python)
        rosbag_mount_path = None
        ros_workspace = None

        docker_enabled = self.spec.get("docker", False) and self.spec.docker.enabled
        if docker_enabled:
            rosbag_mount_path = self.spec.docker.rosbagMountPath

        preinstalled_enabled = (
            self.spec.get("preinstalled", False) and self.spec.preinstalled.enabled
        )
        if preinstalled_enabled and self.spec.preinstalled.get("catkinWorkspace"):
            ros_workspace = self.spec.preinstalled.catkinWorkspace

        config_variables = self.spec.get("configVariables", {})
        labels = self.metadata.get("labels", {})

        return v1Device(
            name=self.metadata.name,
            description=self.spec.get("description"),
            runtime_docker=docker_enabled,
            runtime_preinstalled=preinstalled_enabled,
            ros_distro=self.spec.rosDistro,
            python_version=python_version,
            rosbag_mount_path=rosbag_mount_path,
            ros_workspace=ros_workspace,
            config_variables=config_variables,
            labels=labels,
        )
