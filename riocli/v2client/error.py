
class RetriesExhausted(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class DeploymentNotRunning(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)

class ImagePullError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)