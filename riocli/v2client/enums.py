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
    DeploymentPhaseFailedToUpdate = "FailedToUpdate"
    DeploymentPhaseFailedToStart = "FailedToStart"
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