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
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner
from riocli.v2client.error import DeploymentNotRunning, ImagePullError, RetriesExhausted


@click.command(
    "wait",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("deployment-name", type=str)
@with_spinner(text="Waiting for deployment...", timer=True)
def wait_for_deployment(
    deployment_name: str,
    spinner=None,
) -> None:
    """Wait until the deployment succeeds/fails

    This command is useful in scripts or automation when you
    explicitly want to wait for the deployment to succeed.
    """
    try:
        client = new_v2_client()
        deployment = client.poll_deployment(deployment_name)
        spinner.text = click.style(
            "Phase: Succeeded Status: {}".format(deployment.status.status),
            fg=Colors.GREEN,
        )
        spinner.green.ok(Symbols.SUCCESS)
    except RetriesExhausted as e:
        spinner.write(click.style(str(e), fg=Colors.RED))
        spinner.text = click.style("Try again", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
    except DeploymentNotRunning as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
    except ImagePullError as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
