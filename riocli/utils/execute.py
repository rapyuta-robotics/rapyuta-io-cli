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
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.config import Configuration, new_client

_CLOUD_RUN_REMOTE_COMMAND = '{}/serviceinstance/{}/cmd'


def run_on_cloud(deployment_guid: str, comp_id: str, exec_id: str, pod_name: str, command: typing.List[str]) -> (
        str, str):
    """
    run_on_cloud uses the RunCommand API of the IOBroker to execute arbitrary commands on the cloud deployment
    containers.
    """
    config = Configuration()
    rest = RestClient(_run_cloud_url(config, deployment_guid)).headers(config.get_auth_header()).method(HttpMethod.PUT)
    resp = rest.execute(payload=_run_cloud_data(comp_id, exec_id, pod_name, command))
    data = json.loads(resp.text)
    if 'err' in data and data['err']:
        raise Exception(data['err'])

    return data['stdout'], data['stderr']


def _run_cloud_data(comp_id: str, exec_id: str, pod_name: str, command: typing.List[str]) -> dict:
    return {
        'componentId': comp_id,
        'executableId': exec_id,
        'podName': pod_name,
        'command': command,
    }


def _run_cloud_url(config: Configuration, deployment_guid: str) -> str:
    host = config.data.get('catalog_host', 'https://gacatalog.apps.okd4v2.prod.rapyuta.io')
    return _CLOUD_RUN_REMOTE_COMMAND.format(host, deployment_guid)


def run_on_device(
        device_guid: str,
        command: typing.List[str],
        user: str = 'root',
        shell: str = '/bin/bash',
        background: bool = False,
) -> str:
    client = new_client()
    device = client.get_device(device_id=device_guid)
    cmd = ' '.join(command)
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
