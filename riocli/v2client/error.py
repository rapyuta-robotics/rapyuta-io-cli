class RetriesExhausted(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class DeploymentNotRunning(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class ImagePullError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class NetworkNotFound(Exception):
    def __init__(self, message='network not found!'):
        self.message = message
        super().__init__(self.message)


class DeploymentNotFound(Exception):
    def __init__(self, message='deployment not found!'):
        self.message = message
        super().__init__(self.message)
