# Copyright 2023 Rapyuta Robotics
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
from queue import Queue

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io.clients.deployment import Deployment

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.deployment.util import fetch_deployments
from riocli.deployment.util import print_deployments_for_confirmation
from riocli.utils import tabulate_data
from riocli.utils.execute import apply_func_with_result
from riocli.utils.spinner import with_spinner


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--force', '-f', '--silent', is_flag=True, default=False,
              help='Skip confirmation')
@click.option('-a', '--all', 'delete_all', is_flag=True, default=False,
              help='Deletes all deployments in the project')
@click.option('--workers', '-w',
              help="Number of parallel workers while running delete deployment "
                   "command. Defaults to 10.", type=int, default=10)
@click.argument('deployment-name-or-regex', type=str, default="")
@with_spinner(text="Deleting deployment...")
def delete_deployment(
        force: bool,
        deployment_name_or_regex: str,
        delete_all: bool = False,
        workers: int = 10,
        spinner=None,
) -> None:
    """
    Deletes one or more deployments given a name or a pattern
    """
    client = new_client()

    if not (deployment_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        deployments = fetch_deployments(
            client, deployment_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style(
            'Failed to delete deployment(s): {}'.format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not deployments:
        spinner.text = click.style("Deployment(s) not found", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    with spinner.hidden():
        print_deployments_for_confirmation(deployments)

    spinner.write('')

    if not force:
        with spinner.hidden():
            click.confirm('Do you want to delete the above deployment(s)?',
                          default=True, abort=True)
        spinner.write('')

    try:
        result = apply_func_with_result(
            f=_apply_delete, items=deployments,
            workers=workers, key=lambda x: x[0]
        )

        data, statuses = [], []
        for name, status in result:
            fg = Colors.GREEN if status else Colors.RED
            icon = Symbols.SUCCESS if status else Symbols.ERROR
            statuses.append(status)
            data.append([
                click.style(name, fg),
                click.style(icon, fg)
            ])

        with spinner.hidden():
            tabulate_data(data, headers=['Name', 'Status'])

        icon = Symbols.SUCCESS if all(statuses) else Symbols.WARNING
        fg = Colors.GREEN if all(statuses) else Colors.YELLOW
        text = "successfully" if all(statuses) else "partially"

        spinner.write('')
        spinner.text = click.style(
            'Deployment(s) deleted {}.'.format(text), fg)
        spinner.ok(click.style(icon, fg))
    except Exception as e:
        spinner.text = click.style(
            'Failed to delete deployment(s): {}'.format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _apply_delete(result: Queue, deployment: Deployment) -> None:
    try:
        deployment.deprovision()
        result.put((deployment.name, True))
    except Exception:
        result.put((deployment.name, False))
