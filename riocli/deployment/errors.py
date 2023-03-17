# Copyright 2021 Rapyuta Robotics
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

ERRORS = {
    "DEP_E151": {
        "description": "Device is either offline or not reachable",
        "action": "Ensure that the device is connected to the internet"
    },
    "DEP_E152": {
        "description": "Executables of the component deployed on the device either exited too early or failed",
        "action": "Executables of the component deployed on the device either exited too early or failed"
    },
    "DEP_E153": {
        "description": "Unable to pull the docker image for the component deployed on cloud",
        "action": ("Ensure that the docker image provided while adding the package still "
                   "exists at the specified registry endpoint ")
    },
    "DEP_E154": {
        "description": "Executables of the component deployed on cloud exited too early",
        "action": "Troubleshoot the failed component by analyzing the deployment logs"
    },
    "DEP_E155": {
        "description": "Executables of the component deployed on cloud failed",
        "action": "Troubleshoot the failed component by analyzing the deployment logs"
    },
    "DEP_E156": {
        "description": "Dependent deployment is in error state",
        "action": "Troubleshoot the dependent deployment that is in error state"
    },
    "DEP_E161": {
        "description": "Docker image not found for executables of components deployed on device",
        "action": "Ensure that the docker image path is valid"
    },
    "DEP_E162": {
        "description": ("Validation error. Cases include:\nInconsistent values of ROS distro "
                        "and CPU architecture variables for the device and package being provisioned. "
                        "\nrapyuta.io docker images not present on docker device."),
        "action": ("Create package with appropriate values for ROS distro and CPU architecture "
                   "variables.\nOnboard the device again.")
    },
    "DEP_E163": {
        "description": "Application has stopped and exited unexpectedly, and crashes continuously",
        "action": "Debug the application using the corresponding deployment logs"
    },
    "DEP_E171": {
        "description": "Cloud bridge encountered duplicate alias on the device",
        "action": ("Change the alias name during deployment and ensure that there"
                   " is no duplication of alias name under the same routed network")
    },
    "DEP_E172": {
        "description": "Compression library required for the cloud bridge is missing on the device",
        "action": "Re-onboard the device"
    },
    "DEP_E173": {
        "description": "Transport libraries required for the cloud bridge are missing on the device",
        "action": "Re-onboard the device"
    },
    "DEP_E174": {
        "description": "Cloud bridge on the device encountered multiple ROS service origins",
        "action": ("Ensure that there aren’t multiple deployments with the same ROS service "
                   "endpoint under the same routed network")
    },
    "DEP_E175": {
        "description": "Python actionlib/msgs required for the cloud bridge is missing on the device",
        "action": "Re-onboard the device"
    },
    "DEP_E176": {
        "description": "Cloud bridge encountered duplicate alias on the cloud component",
        "action": ("Change the alias name during deployment and ensure that there is no"
                   " duplication of alias name under the same routed network")
    },
    "DEP_E177": {
        "description": "Cloud bridge on the cloud component encountered multiple ROS service origins",
        "action": "Re-onboard the device"
    },
    "DEP_E317": {
        "description": "Missing subpath or empty mount path",
        "action": ("Ensure the current device has a subpath\n"
                   "Ensure that the mount path isn’t empty")
    }
}
