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

import enum


class DeploymentPhaseConstants(str, enum.Enum):
    """
    Enumeration variables for the deployment phase
    """

    def __str__(self):
        return str(self.value)

    DeploymentPhaseInProgress = "InProgress"
    DeploymentPhaseProvisioning = "Provisioning"
    DeploymentPhaseSucceeded = "Succeeded"
    DeploymentPhaseStopped = "Stopped"


class DeploymentStatusConstants(str, enum.Enum):
    """
    Enumeration variables for the deployment status

    """

    def __str__(self):
        return str(self.value)

    DeploymentStatusRunning = "Running"
    DeploymentStatusPending = "Pending"
    DeploymentStatusError = "Error"
    DeploymentStatusUnknown = "Unknown"
    DeploymentStatusStopped = "Stopped"


class DiskStatusConstants(str, enum.Enum):
    """
    Enumeration variables for the deployment status

    """

    def __str__(self):
        return str(self.value)

    DiskStatusAvailable = "Available"
    DiskStatusBound = "Bound"
    DiskStatusReleased = "Released"
    DiskStatusFailed = "Failed"
    DiskStatusPending = "Pending"
