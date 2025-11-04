# copyright 2025 rapyuta robotics
#
# licensed under the apache license, version 2.0 (the "license");
# you may not use this file except in compliance with the license.
# you may obtain a copy of the license at
#
#     http://www.apache.org/licenses/license-2.0
#
# unless required by applicable law or agreed to in writing, software
# distributed under the license is distributed on an "as is" basis,
# without warranties or conditions of any kind, either express or implied.
# see the license for the specific language governing permissions and
# limitations under the license.

from munch import Munch, unmunchify
from rapyuta_io_sdk_v2 import Client
from typing_extensions import override

from riocli.model import Model


class Package(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        self._sanitize_command()

        return v2_client.create_package(unmunchify(self))  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, *args, **kwargs) -> Munch | None:
        raise NotImplementedError

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_package(self.metadata.name, version=self.metadata.version)

    @override
    def list_dependencies(self) -> list[str] | None:
        dependencies: list[str] = []

        for exec in self.spec.executables:
            secret = (
                exec.get("docker", {})
                .get("pullSecret", {})
                .get("depends", {})
                .get("nameOrGUID", None)
            )
            if secret is not None:
                dependencies.append(f"secret:{secret}")

        return dependencies

    def _sanitize_command(self):
        for e in self.spec.executables:
            # Skip if command is not set.
            if e.get("command", None) is None:
                continue

            c = []

            if e.get("runAsBash"):
                c = ["/bin/bash", "-c"]

            if isinstance(e.command, list):
                c.extend(e.command)
            else:
                c.append(e.command)

            e.command = c
