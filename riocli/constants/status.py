from enum import Enum


class Status(str, Enum):

    def __str__(self):
        return str(self.value).lower()

    RUNNING = 'Running'
    AVAILABLE = 'Available'
