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
from __future__ import annotations

import errno
import json
import os
import subprocess
import uuid
from functools import lru_cache
from pathlib import Path

from click import get_app_dir
from rapyuta_io import Client
from rapyuta_io_sdk_v2 import Client as v2Client
from rapyuta_io_sdk_v2 import Configuration as v2Config

from riocli.exceptions import (
    HwilLoggedOut,
    LoggedOut,
    NoOrganizationSelected,
    NoProjectSelected,
)
from riocli.hwilclient import Client as HwilClient


class Configuration:
    """
    Configuration defines a class to define operations on the CLI's configuration file centrally.
    The class can be initialized irrespective of if the actual file exists or not. The object will
    automatically read the file if one exists and exposes the data through the `data` field.

    Example config:
        {
            "email_id": "<user-email>",
            "password": "<user-password>",
            "auth_token": "<rapyuta-auth-token>",
            "project_id": "<project-guid>"
        }
    """

    APP_NAME = "rio-cli"
    PIPING_SERVER = (
        "https://piping-server-v0-rapyuta-infra.apps.okd4v2.okd4beta.rapyuta.io"
    )
    DIFF_TOOL = "diff"
    MERGE_TOOL = "vimdiff"

    def __init__(self, filepath: str | None = None):
        self._filepath = os.environ.get("RIO_CONFIG", filepath)
        self.exists = True

        # If config file does not exist, then initialize an empty dictionary instead.
        if not os.path.exists(self.filepath):
            self.exists = False
            self.data = dict()
            return

        with open(self.filepath) as config_file:
            self.data = json.load(config_file)

    def save(self: Configuration):
        if not os.path.exists(self.filepath):
            try:
                os.makedirs(os.path.dirname(self.filepath))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(self.filepath, "w") as config_file:
            json.dump(self.data, config_file)

    # We are using lru_cache to cache the calls to new_v2_client
    # with project and without project. This is to avoid creating a
    # new client object every time we call new_v2_client.
    # https://docs.python.org/3.8/library/functools.html#functools.lru_cache
    @lru_cache(maxsize=2)  # noqa: B019
    def new_client(self: Configuration, with_project: bool = True) -> Client:
        if "auth_token" not in self.data:
            raise LoggedOut

        if "environment" in self.data:
            os.environ["RIO_CONFIG"] = self.filepath

        token = self.data.get("auth_token", None)
        project = self.data.get("project_id", None)
        if with_project and project is None:
            raise NoProjectSelected

        if not with_project:
            project = None

        return Client(auth_token=token, project=project)

    @lru_cache(maxsize=2)  # noqa: B019
    def new_v2_client(
        self: Configuration,
        with_project: bool = True,
        from_file: bool = True,  # from_file parameter is deprecated
    ) -> v2Client:
        if "auth_token" not in self.data:
            raise LoggedOut

        environment = self.data.get("environment", "ga")
        if environment:
            os.environ["RIO_CONFIG"] = self.filepath

        config_kwargs = dict(
            auth_token=self.data["auth_token"],
            environment=environment,
            organization_guid=self.data.get("organization_id"),
            v2_api_host=self.data.get("v2api_host"),
            rip_host=self.data.get("rip_host"),
        )

        if with_project:
            config_kwargs["project_guid"] = self.data.get("project_id")
            config_kwargs["email"] = self.data.get("email_id")

        return v2Client(config=v2Config(**config_kwargs))

    def new_hwil_client(self: Configuration) -> HwilClient:
        if "hwil_auth_token" not in self.data:
            raise HwilLoggedOut

        if "environment" in self.data:
            os.environ["RIO_CONFIG"] = self.filepath

        token = self.data.get("hwil_auth_token", None)

        return HwilClient(auth_token=token, email_id=self.data.get("email_id"))

    def get_auth_header(self: Configuration) -> dict:
        if not ("auth_token" in self.data and "project_id" in self.data):
            raise LoggedOut

        token, project = self.data["auth_token"], self.data["project_id"]
        if not token.startswith("Bearer"):
            token = f"Bearer {token}"

        return dict(Authorization=token, project=project)

    @property
    def filepath(self: Configuration) -> str:
        path = self._filepath
        if path is None:
            path = os.path.join(get_app_dir(self.APP_NAME), "config.json")
        return os.path.abspath(path)

    @property
    def project_guid(self: Configuration) -> str:
        if "auth_token" not in self.data:
            raise LoggedOut

        if "organization_id" not in self.data:
            raise NoOrganizationSelected

        guid = self.data.get("project_id")
        if guid is None:
            raise NoProjectSelected

        return guid

    @property
    def organization_guid(self: Configuration) -> str:
        if "auth_token" not in self.data:
            raise LoggedOut

        guid = self.data.get("organization_id")
        if guid is None:
            raise NoOrganizationSelected

        return guid

    @property
    def organization_short_id(self: Configuration) -> str:
        if "auth_token" not in self.data:
            raise LoggedOut

        short_id = self.data.get("organization_short_id")
        if short_id is None:
            raise NoOrganizationSelected

        return short_id

    @property
    def piping_server(self: Configuration):
        return self.data.get("piping_server", self.PIPING_SERVER)

    @property
    def diff_tool(self: Configuration):
        return self.data.get("diff_tool", self.DIFF_TOOL)

    @property
    def merge_tool(self: Configuration):
        return self.data.get("merge_tool", self.MERGE_TOOL)

    @property
    def machine_id(self: Configuration):
        if "machine_id" not in self.data:
            self.data["machine_id"] = str(uuid.uuid4())
            self.save()

        return self.data.get("machine_id")

    # ------------------------------------------------------------------
    # SSH key pair management
    # ------------------------------------------------------------------

    #: Base name for the dedicated SSH key pair.
    _SSH_KEY_NAME = "rio_ed25519"

    @property
    def ssh_private_key(self: Configuration) -> Path:
        """Path to the dedicated SSH private key (``rio_ed25519``).

        Located in the CLI's configuration directory alongside
        ``config.json``.
        """
        return Path(get_app_dir(self.APP_NAME)) / self._SSH_KEY_NAME

    @property
    def ssh_public_key(self: Configuration) -> Path:
        """Path to the dedicated SSH public key (``rio_ed25519.pub``)."""
        return Path(get_app_dir(self.APP_NAME)) / f"{self._SSH_KEY_NAME}.pub"

    @property
    def ssh_certificate(self: Configuration) -> Path:
        """Path to the SSH certificate (``rio_ed25519-cert.pub``)."""
        return Path(get_app_dir(self.APP_NAME)) / f"{self._SSH_KEY_NAME}-cert.pub"

    def ensure_ssh_keys(self: Configuration) -> bool:
        """Ensure the dedicated ed25519 key pair exists, creating if needed.

        If both the private and public key files exist, they are reused.
        Otherwise, any orphaned files (including a stale certificate) are
        cleaned up and a fresh key pair is generated via ``ssh-keygen``.

        Returns:
            ``True`` when a new key pair was generated, ``False`` when
            the existing pair was reused.
        """
        private_path = self.ssh_private_key
        public_path = self.ssh_public_key
        cert_path = self.ssh_certificate

        # Ensure the config directory exists with correct permissions.
        private_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

        if private_path.is_file() and public_path.is_file():
            return False

        # Orphaned files from a previous key pair must be removed to
        # avoid cert/key mismatch and because ssh-keygen refuses to
        # overwrite an existing private key.
        private_path.unlink(missing_ok=True)
        public_path.unlink(missing_ok=True)
        cert_path.unlink(missing_ok=True)

        # Generate a fresh ed25519 key pair.
        result = subprocess.run(
            [
                "ssh-keygen",
                "-t",
                "ed25519",
                "-f",
                str(private_path),
                "-N",
                "",
                "-C",
                "rio-ssh",
                "-q",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ssh-keygen failed: {result.stderr.strip()}")

        # Ensure correct permissions (ssh-keygen normally sets these).
        private_path.chmod(0o600)
        public_path.chmod(0o644)

        return True
