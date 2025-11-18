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


import click

from riocli.constants import Colors
from riocli.utils.constants import DEPLOYMENT_ERRORS as ERRORS


def process_errors(errors: list[str], no_action: bool = False) -> str:
    """Process the deployment errors and return the formatted error message"""
    err_fmt = "[{}] {}\nAction: {}"
    support_action = (
        "Report the issue together with the relevant details to the support team"
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
