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
import os
import typing
from socket import socket, AF_INET, SOCK_STREAM

import click

from riocli.utils import random_string, run_bash


def establish_ssh_tunnel(exec_remote_command: typing.Callable) -> None:
    input_path, output_path = random_string(8, 5), random_string(8, 5)
    free_port = get_free_tcp_port()

    remote_command = ["socat",
                      "'EXEC:curl -NsS https\://ppng.io/{}!!EXEC:curl -NsST - https\://ppng.io/{}'".format(input_path,
                                                                                                           output_path),
                      "TCP:127.0.0.1:22"]
    click.secho('$ {}'.format(' '.join(remote_command)))
    exec_remote_command(remote_command)

    local_command = ["socat",
                     "TCP-LISTEN:{}".format(free_port),
                     "'EXEC:curl -NsS https\://ppng.io/{}!!EXEC:curl -NsST - https\://ppng.io/{}'".format(output_path,
                                                                                                          input_path)]
    run_bash('pkill -9 socat')
    run_bash(' '.join(local_command), bg=True)
    os.system('ssh -p {} {}@localhost'.format(free_port, 'root'))


def get_free_tcp_port():
    tcp = socket(AF_INET, SOCK_STREAM)
    tcp.bind(('', 0))
    _, port = tcp.getsockname()
    tcp.close()
    return port
