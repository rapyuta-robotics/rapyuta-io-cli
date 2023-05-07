# Copyright 2022 Rapyuta Robotics
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
import typing
from abc import ABC, abstractmethod
from datetime import datetime
from shutil import get_terminal_size

import click
from munch import Munch, munchify
from rapyuta_io import Client
from yaspin.api import Yaspin

from riocli.constants import Colors, Symbols
from riocli.project.util import find_project_guid

prompt = ">> {}{}{} [{}]"  # >> left_msg  spacer  right_msg time

DELETE_POLICY_LABEL = 'rapyuta.io/deletionPolicy'


def message_with_prompt(
        msg,
        right_msg='',
        fg=Colors.WHITE,
        with_time=True,
        spinner: Yaspin = None,
) -> None:
    columns, _ = get_terminal_size()
    t = datetime.now().isoformat('T')
    spacer = ' ' * (int(columns) - len(msg + right_msg + t) - 12)
    msg = prompt.format(msg, spacer, right_msg, t)
    msg = click.style(msg, fg=fg)
    if spinner:
        spinner.write(msg)
    else:
        click.echo(msg)


class Model(ABC, Munch):

    def apply(self, client: Client, *args, **kwargs) -> typing.Any:
        spinner = kwargs.get('spinner')
        try:
            self._set_project_in_client(client)
            obj = self.find_object(client)
            dryrun = kwargs.get("dryrun", False)
            if not obj:
                message_with_prompt("{} Create {}:{}".format(
                    Symbols.WAITING,
                    self.kind.lower(),
                    self.metadata.name), fg=Colors.YELLOW, spinner=spinner)
                if not dryrun:
                    result = self.create_object(client, **kwargs)
                    message_with_prompt("{} Created {}:{}".format(
                        Symbols.SUCCESS,
                        self.kind.lower(),
                        self.metadata.name), fg=Colors.GREEN, spinner=spinner)
                    return result
            else:
                message_with_prompt('{} {}:{} exists. will be updated'.format(
                    Symbols.INFO,
                    self.kind.lower(),
                    self.metadata.name), spinner=spinner)
                message_with_prompt("{} Update {}:{}".format(
                    Symbols.WAITING,
                    self.kind.lower(),
                    self.metadata.name), fg=Colors.YELLOW, spinner=spinner)
                if not dryrun:
                    result = self.update_object(client, obj)
                    message_with_prompt("{} Updated {}:{}".format(
                        Symbols.SUCCESS,
                        self.kind.lower(),
                        self.metadata.name), fg=Colors.GREEN, spinner=spinner)
                    return result
        except Exception as e:
            message_with_prompt("{} {}:{}. {} ‼".format(
                Symbols.ERROR,
                self.kind.lower(),
                self.metadata.name,
                str(e)), fg=Colors.RED, spinner=spinner)
            raise e

    def delete(self, client: Client, obj: typing.Any, *args, **kwargs):
        spinner = kwargs.get('spinner')
        dryrun = kwargs.get("dryrun", False)
        try:
            self._set_project_in_client(client)
            obj = self.find_object(client)

            if not obj:
                message_with_prompt(
                    '⁉ {}:{} does not exist'.format(
                        self.kind.lower(), self.metadata.name),
                    spinner=spinner)
                return

            message_with_prompt("{} Delete {}:{}".format(
                Symbols.WAITING,
                self.kind.lower(),
                self.metadata.name), fg=Colors.YELLOW, spinner=spinner)

            if not dryrun:
                labels = self.metadata.get('labels', {})
                if (DELETE_POLICY_LABEL in labels and
                        labels.get(DELETE_POLICY_LABEL) and
                        labels.get(DELETE_POLICY_LABEL).lower() == "retain"):
                    click.secho(
                        ">> {} Delete protection enabled on {}:{}. "
                        "Resource will be retained ".format(
                            Symbols.WARNING,
                            self.kind.lower(),
                            self.metadata.name), fg=Colors.YELLOW)
                    return

                self.delete_object(client, obj)
                message_with_prompt("{} Deleted {}:{}".format(
                    Symbols.SUCCESS,
                    self.kind.lower(),
                    self.metadata.name), fg=Colors.GREEN, spinner=spinner)
        except Exception as e:
            message_with_prompt("{} {}:{}. {} ‼".format(
                Symbols.ERROR,
                self.kind.lower(),
                self.metadata.name,
                str(e)), fg=Colors.RED, spinner=spinner)
            raise e

    @abstractmethod
    def find_object(self, client: Client) -> typing.Any:
        pass

    @abstractmethod
    def create_object(self, client: Client, **kwargs) -> typing.Any:
        pass

    @abstractmethod
    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    @staticmethod
    @abstractmethod
    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    @classmethod
    @abstractmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    @abstractmethod
    def validate(d):
        pass

    @classmethod
    def from_dict(cls, client: Client, d: typing.Dict):
        cls.pre_process(client, d)
        cls.validate(d)
        return cls(munchify(d))

    def _set_project_in_client(self, client: Client) -> Client:
        # If the Type is Project itself then no need to configure Client.
        if self.kind == 'Project':
            return client

        # If Project is not specified then no need to configure the Client. It
        # will use the pre-configured Project by default.
        #
        # TODO(ankit): Move this to the pre-processing step, once implemented.
        project = self.metadata.get('project', None)
        if not project:
            return client

        # This should work unless someone has a Project Name starting with
        # 'project-' prefix
        if not project.startswith('project-'):
            project = find_project_guid(client, project)

        client.set_project(project_guid=project)
        return client
