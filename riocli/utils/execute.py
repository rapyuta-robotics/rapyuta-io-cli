# Copyright 2021 Rapyuta Robotics
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
import functools
import json
import typing
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from rapyuta_io import Command

from riocli.utils.selector import show_selection
from riocli.config import Configuration, new_client

from riocli.config import new_v2_client


def run_on_device(
        device_guid: str,
        command: typing.List[str],
        user: str = 'root',
        shell: str = '/bin/bash',
        background: bool = False,
        deployment: str = None,
        exec_name: str = None
) -> str:
    client = new_client()
    device = client.get_device(device_id=device_guid)

    client = new_v2_client()
    package = client.get_package(deployment.metadata.depends.nameOrGUID, query={"version": deployment.metadata.depends.version})

    if exec_name is None:
        executables = [e.name for e in package.spec.executables]
        exec_name = show_selection(executables, '\nChoose the executable')

    cmd = ' '.join(command)
    if deployment:
        cmd = 'script -q -c "dectl exec {} -- {}"'.format(exec_name, cmd)

    return device.execute_command(Command(cmd, shell=shell, bg=background, runas=user))

def apply_func(
        f: typing.Callable,
        items: typing.List[typing.Any],
        workers: int = 5
) -> None:
    """Apply a function to a list of items in parallel

    Parameters
    ----------
    f : typing.Callable
        The function to apply
    items : typing.List
        The list of items to apply the function to
    workers : int
        The number of workers to use
    """
    with ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix='exec'
    ) as e:
        e.map(f, items)


def apply_func_with_result(
        f: typing.Callable,
        items: typing.List[typing.Any],
        workers: int = 5,
        key: typing.Callable = None
) -> typing.List[typing.Any]:
    """Apply a function to a list of items in parallel and return the result

    The function to apply must use the queue to return the result. For example,

    def _apply_delete(result: Queue, deployment: Deployment) -> None:
          try:
                deployment.deprovision()
                result.put((deployment.name, True))
          except Exception:
                result.put((deployment.name, False))

    Here's another example,

    def _apply_update(client: Client, result: Queue, deployment: Deployment) -> None
        try:
            client.update_deployment(deployment)
            result.put((deployment.name, True))
        except Exception:
            result.put((deployment.name, False))

    Note that the second last argument of the function must be the queue and
    the last must be the item. This requirement must be adhered to for this
    function to work correctly.

    Parameters
    ----------
    f : typing.Callable
        The function to apply
    items : typing.List
        The list of items to apply the function to
    workers : int
        The number of workers to use
    key : typing.Callable
        The function to use to sort the result
    """
    r = Queue()
    f = functools.partial(f, r)

    apply_func(f, items, workers)

    if key:
        return sorted(list(r.queue), key=key)

    return list(r.queue)
