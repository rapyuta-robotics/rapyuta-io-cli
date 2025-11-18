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

DEPLOYMENT_ERRORS = {
    # Device related Error codes
    "DEP_E151": {
        "description": "Device is either offline or not reachable",
        "action": "Ensure that the device is connected to the internet",
    },
    "DEP_E302": {
        "description": "Supervisord related error on device",
        "action": (
            "Ensure supervisord is installed on rapyuta virtual environment and working\n"
            "Re-onboard the device, if issue persists report to rapyuta.io support."
        ),
    },
    "DEP_E161": {
        "description": "Docker image not found for executables of components deployed on device",
        "action": "Ensure that the docker image path is valid and secrets have privileges",
    },
    "DEP_E316": {
        "description": "Docker image pull failed in device",
        "action": "Ensure that the docker image path is valid and secrets have privileges",
    },
    "DEP_E317": {
        "description": "Missing subpath or empty mount path",
        "action": (
            "Ensure the current device has a subpath\n"
            "Ensure that the mount path isn’t empty"
        ),
    },
    "DEP_E304": {
        "description": "DeviceManager internal error",
        "action": "Report to rapyuta.io support",
    },
    "DEP_E306": {
        "description": "DeviceEdge internal error",
        "action": "Ensure deviceedge is up and running",
    },
    "DEP_E307": {
        "description": "DeviceEdge bad request",
        "action": "Report to rapyuta.io support",
    },
    # Application related errors.
    "DEP_E152": {
        "description": "Executables of the component deployed on the device either exited too early or failed",
        "action": "Executables of the component deployed on the device either exited too early or failed",
    },
    "DEP_E153": {
        "description": "Unable to pull the docker image for the component deployed on cloud",
        "action": (
            "Ensure that the docker image provided while adding the package still "
            "exists at the specified registry endpoint "
        ),
    },
    "DEP_E154": {
        "description": "Executables of the component deployed on cloud exited too early",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
    "DEP_E155": {
        "description": "Executables of the component deployed on cloud failed",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
    "DEP_E156": {
        "description": "Dependent deployment is in error state",
        "action": "Troubleshoot the dependent deployment that is in error state",
    },
    "DEP_E162": {
        "description": (
            "Validation error. Cases include:\nInconsistent values of ROS distro "
            "and CPU architecture variables for the device and package being provisioned. "
            "\nrapyuta.io docker images not present on docker device."
        ),
        "action": (
            "Create package with appropriate values for ROS distro and CPU architecture "
            "variables.\nOnboard the device again."
        ),
    },
    "DEP_E163": {
        "description": "Application has stopped and exited unexpectedly, and crashes continuously on device",
        "action": "Debug the application using the corresponding deployment logs",
    },
    # CloudBridge related error codes.
    "DEP_E171": {
        "description": "Cloud bridge encountered duplicate alias on the device",
        "action": (
            "Change the alias name during deployment and ensure that there"
            " is no duplication of alias name under the same routed network"
        ),
    },
    "DEP_E172": {
        "description": "Compression library required for the cloud bridge is missing on the device",
        "action": "Re-onboard the device",
    },
    "DEP_E173": {
        "description": "Transport libraries required for the cloud bridge are missing on the device",
        "action": "Re-onboard the device",
    },
    "DEP_E174": {
        "description": "Cloud bridge on the device encountered multiple ROS service origins",
        "action": (
            "Ensure that there aren’t multiple deployments with the same ROS service "
            "endpoint under the same routed network"
        ),
    },
    "DEP_E175": {
        "description": "Python actionlib/msgs required for the cloud bridge is missing on the device",
        "action": "Re-onboard the device",
    },
    "DEP_E176": {
        "description": "Cloud bridge encountered duplicate alias on the cloud component",
        "action": (
            "Change the alias name during deployment and ensure that there is no"
            " duplication of alias name under the same routed network"
        ),
    },
    "DEP_E177": {
        "description": "Cloud bridge on the cloud component encountered multiple ROS service origins",
        "action": "Re-onboard the device",
    },
    # Docker image related Error codes
    "DEP_E350": {
        "description": "Get http error when pulling image from registry on device",
        "action": "Ensure registry is accesible.",
    },
    "DEP_E351": {
        "description": "Unable to parse the image name on device",
        "action": "Ensure image name is correct and available in registry.",
    },
    "DEP_E352": {
        "description": "Unable to inspect image on device",
        "action": "Ensure valid image is present",
    },
    "DEP_E353": {
        "description": "Required Image is absent on device and PullPolicy is NeverPullImage",
        "action": "Ensure pull policy is not set to never or image is present on device",
    },
    # Container related error codes
    "DEP_E360": {
        "description": "Failed to create container config on device",
        "action": (
            "Ensure executable config is mounted correctly\n"
            "If issue persists report to rapyuta.io support"
        ),
    },
    "DEP_E361": {
        "description": "Runtime failed to start any of pod's container on device",
        "action": (
            "Ensure executable command is valid\n"
            "If issue persists report to rapyuta.io support"
        ),
    },
    "DEP_E362": {
        "description": "Runtime failed to create container on device",
        "action": ("Report to rapyuta.io support"),
    },
    "DEP_E363": {
        "description": "Runtime failed to kill any of pod's containers on device",
        "action": ("Report to rapyuta.io support"),
    },
    "DEP_E364": {
        "description": "Runtime failed to create a sandbox for pod on device",
        "action": ("Report to rapyuta.io support"),
    },
    "DEP_E365": {
        "description": "Runtime failed to get pod sandbox config from pod on device",
        "action": ("Report to rapyuta.io support"),
    },
    "DEP_E366": {
        "description": "Runtime failed to stop pod's sandbox on device",
        "action": ("Report to rapyuta.io support"),
    },
    "DEP_E399": {
        "description": "Deployment failed for some unknown reason on device",
        "action": ("Report to rapyuta.io support"),
    },
    # ROS Comm Related Device Errors
    "DEP_E303": {
        "description": "Cloud Bridge executable not running on device",
        "action": ("Troubleshoot Cloud Bridge container on device by analyzing logs"),
    },
    "DEP_E305": {
        "description": "Native Network executable not running on device",
        "action": ("Troubleshoot native network container on device by analyzing logs"),
    },
    "DEP_E313": {
        "description": "ROS Master executable not running on device",
        "action": ("Troubleshoot ROS Master container on device by analyzing logs"),
    },
    "DEP_E330": {
        "description": "ROS2 Native Network executable not running on device",
        "action": (
            "Troubleshoot ROS2 Routed Network container on device by analyzing logs"
        ),
    },
    "DEP_E331": {
        "description": "ROS2 Routed Network executable not running on device",
        "action": (
            "Troubleshoot ROS2 Routed Network container on device by analyzing logs"
        ),
    },
    # Cloud error codes
    "DEP_E201": {
        "description": "Cloud component deployment pending",
        "action": ("Report to rapyuta.io support"),
    },
    "DEP_E202": {
        "description": "Cloud component status unknown",
        "action": ("Report to rapyuta.io support"),
    },
    "DEP_E203": {
        "description": "Cloud Bridge not running on cloud",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
    "DEP_E204": {
        "description": "ROS Master not running on cloud",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
    "DEP_E205": {
        "description": "Cloud Broker not running on cloud",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
    "DEP_E208": {
        "description": "Desired set of replicas not running on cloud",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
    "DEP_E209": {
        "description": "Native Network not running on cloud",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
    "DEP_E210": {
        "description": "Disk Not Running",
        "action": ("Ensure disk is running"),
    },
    "DEP_E213": {
        "description": "Broker running low on memory",
        "action": ("Report to rapyuta.io support"),
    },
    "DEP_E214": {
        "description": "ROS2 Native Network not running on cloud",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
    "DEP_E215": {
        "description": "ROS2 Routed Network not running on cloud",
        "action": "Troubleshoot the failed component by analyzing the deployment logs",
    },
}
