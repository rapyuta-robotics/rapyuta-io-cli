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
import typing

from munch import unmunchify

from riocli.config import new_v2_client
from riocli.constants import ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.model import Model
from riocli.package.enum import RestartPolicy
from riocli.v2client.error import HttpAlreadyExistsError, HttpNotFoundError


class Package(Model):
    RESTART_POLICY = {
        "always": RestartPolicy.Always,
        "never": RestartPolicy.Never,
        "onfailure": RestartPolicy.OnFailure,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> ApplyResult:
        client = new_v2_client()

        package = self._sanitize_package()

        try:
            client.create_package(package)
            return ApplyResult.CREATED
        except HttpAlreadyExistsError:
            return ApplyResult.EXISTS

    def delete(self, *args, **kwargs) -> None:
        client = new_v2_client()

        try:
            client.delete_package(
                self.metadata.name, query={"version": self.metadata.version}
            )
        except HttpNotFoundError:
            raise ResourceNotFound

    def _sanitize_package(self) -> typing.Dict:
        # Unset createdAt and updatedAt to avoid timestamp parsing issue.
        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        self._sanitize_command()

        return unmunchify(self)

    def _sanitize_command(self):
        for e in self.spec.executables:
            # Skip if command is not set.
            if e.get("command") is None:
                continue

            c = []

            if e.get("runAsBash"):
                c = ["/bin/bash", "-c"]

            if isinstance(e.command, list):
                c.extend(e.command)
            else:
                c.append(e.command)

            e.command = c
