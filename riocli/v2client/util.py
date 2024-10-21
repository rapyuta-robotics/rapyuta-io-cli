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

import http
import json
import typing

import click
import requests

from riocli.constants import Colors
from riocli.v2client.constants import DEPLOYMENT_ERRORS as ERRORS
from riocli.v2client.error import HttpAlreadyExistsError, HttpNotFoundError


def process_errors(errors: typing.List[str], no_action: bool = False) -> str:
    """Process the deployment errors and return the formatted error message"""
    err_fmt = "[{}] {}\nAction: {}"
    support_action = (
        "Report the issue together with the relevant" " details to the support team"
    )

    action, description = "", ""
    msgs = []
    for code in errors:
        if code in ERRORS:
            description = ERRORS[code]["description"]
            action = ERRORS[code]["action"]
        elif code.startswith("DEP_E2"):
            description = "Internal rapyuta.io error in the components deployed on cloud"
            action = support_action
        elif code.startswith("DEP_E3"):
            description = (
                "Internal rapyuta.io error in the components deployed on a device"
            )
            action = support_action
        elif code.startswith("DEP_E4"):
            description = "Internal rapyuta.io error"
            action = support_action

        code = click.style(code, fg=Colors.YELLOW)
        description = click.style(description, fg=Colors.RED)
        action = click.style(action, fg=Colors.GREEN)

        if no_action:
            msgs.append(f"[{code}]: {description}")
        else:
            msgs.append(err_fmt.format(code, description, action))

    return "\n".join(msgs)


def handle_server_errors(response: requests.Response):
    status_code = response.status_code

    if status_code < 400:
        return

    err = ""
    try:
        err = response.json().get("error")
    except json.JSONDecodeError:
        err = response.text

    # 404 Not Found
    if status_code == http.HTTPStatus.NOT_FOUND:
        raise HttpNotFoundError(err)
    # 409 Conflict
    if status_code == http.HTTPStatus.CONFLICT:
        raise HttpAlreadyExistsError()
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
