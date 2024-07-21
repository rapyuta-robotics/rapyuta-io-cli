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
