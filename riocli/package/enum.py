import enum


class RestartPolicy(str, enum.Enum):
    """
    Enumeration variables for the Restart Policy. Restart Policy may be 'Always', 'Never' or 'OnFailure' \n
    RestartPolicy.Always \n
    RestartPolicy.Never \n
    RestartPolicy.OnFailure \n
    """

    def __str__(self):
        return str(self.value)

    Always = "always"
    Never = "no"
    OnFailure = "on-failure"
