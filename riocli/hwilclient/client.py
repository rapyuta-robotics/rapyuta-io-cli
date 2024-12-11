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

import http
import json
import time

import requests
from munch import Munch, munchify
from rapyuta_io.utils import ConflictError, RetriesExhausted, UnauthorizedError
from rapyuta_io.utils.rest_client import HttpMethod, RestClient

from riocli.utils import generate_short_guid, sanitize_label


def handle_server_errors(response: requests.Response):
    status_code = response.status_code

    # 409 Conflict
    if status_code == http.HTTPStatus.CONFLICT:
        raise ConflictError("already exists")
    # 401 Unauthorized
    if status_code == http.HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError("unauthorized access")
    # 500 Internal Server Error
    if status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR:
        raise Exception("internal server error")
    # 501 Not Implemented
    if status_code == http.HTTPStatus.NOT_IMPLEMENTED:
        raise Exception("not implemented")
    # 502 Bad Gateway
    if status_code == http.HTTPStatus.BAD_GATEWAY:
        raise Exception("bad gateway")
    # 503 Service Unavailable
    if status_code == http.HTTPStatus.SERVICE_UNAVAILABLE:
        raise Exception("service unavailable")
    # 504 Gateway Timeout
    if status_code == http.HTTPStatus.GATEWAY_TIMEOUT:
        raise Exception("gateway timeout")
    # Anything else that is not known
    if status_code > 504:
        raise Exception("unknown server error")


class Client(object):
    """
    HWILv3 API Client
    """

    HWIL_URL = "https://hwilv3.rapyuta.io"
    ARCH_OS_DICT = {
        "amd64": {
            "ubuntu": {
                "bionic": "bionic",
                "focal": "focal",
                "jammy": "jammy",
                "noble": "noble",
            }
        },
        "arm64": {
            "ubuntu": {"focal": "focal"},
            "debian": {"bullseye": "bullseye"},
        },
    }

    def __init__(self, auth_token: str):
        self._token = auth_token
        self._host = self.HWIL_URL

    def create_device(
        self: Client,
        name: str,
        arch: str,
        os: str,
        codename: str,
        labels: dict = None,
    ) -> Munch:
        """Create a HWIL device."""
        url = f"{self._host}/device/"
        headers = self._get_auth_header()

        flavor = self.ARCH_OS_DICT.get(arch, {}).get(os, {}).get(codename)
        if not flavor:
            raise Exception(f"image not found for {arch}:{os}:{codename}")

        labels = labels or {}
        labels.update({"agent": "rapyuta-io-cli"})

        sanitized_labels = {}
        for key, value in labels.items():
            sanitized_labels.update({sanitize_label(key): sanitize_label(value)})

        payload = {
            "kind": "VIRTUAL",
            "name": name,
            "architecture": arch,
            "labels": sanitized_labels,
            "flavor": self.ARCH_OS_DICT.get(arch).get(os).get(codename),
        }

        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=payload)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            raise Exception("hwil: {}".format(response.text))

        return munchify(data)

    def delete_device(self: Client, device_id: int) -> None:
        """Delete a HWIL device."""
        url = f"{self._host}/device/{device_id}"
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        handle_server_errors(response)

    def get_device(self: Client, device_id: int) -> Munch:
        """Fetch a HWIL device."""
        url = f"{self._host}/device/{device_id}"
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            raise Exception("hwil: {}".format(response.text))

        return munchify(data)

    def execute_command(self: Client, device_id: int, command: str) -> Munch:
        """Execute a command on the HWIL device."""
        url = f"{self._host}/command/"
        headers = self._get_auth_header()

        payload = {
            "kind": "VIRTUAL",
            "device_id": device_id,
            "command": command,
            "uuid": generate_short_guid(),
        }

        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=payload)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            raise Exception("hwil: {}".format(response.text))

        return munchify(data)

    def get_command(self: Client, command_uuid: str) -> Munch:
        """Fetch a command."""
        url = f"{self._host}/command/{command_uuid}"
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            raise Exception("hwil: {}".format(response.text))

        return munchify(data)

    def poll_till_device_ready(
        self: Client, device_id: int, sleep_interval: int, retry_limit: int
    ) -> None:
        """Poll until HWIL device is ready"""
        url = f"{self._host}/device/{device_id}"
        headers = self._get_auth_header()

        for _ in range(retry_limit):
            response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

            handle_server_errors(response)

            data = json.loads(response.text)
            if not response.ok:
                raise Exception("hwil: {}".format(response.text))

            device = munchify(data)
            if device.status != "IDLE":
                time.sleep(sleep_interval)
                continue

            return

        msg = f"Retries exhausted: Tried {retry_limit} times with {sleep_interval}s interval."
        raise RetriesExhausted(msg)

    def list_devices(self: Client, query: dict = None) -> Munch:
        """Fetch all HWIL devices"""
        url = f"{self._host}/device/"
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.GET)
            .headers(headers)
            .query_param(query or {})
            .execute()
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            raise Exception("hwil: {}".format(response.text))

        return munchify(data)

    def _get_auth_header(self: Client) -> dict:
        return dict(Authorization=f"Basic {self._token}")
