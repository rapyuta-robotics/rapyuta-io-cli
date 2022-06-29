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

from munch import Munch, munchify
from rapyuta_io import Client
from datetime import datetime

from riocli.project.util import find_project_guid
import click

class Model(ABC, Munch):

    def apply(self, client: Client, *args, **kwargs) -> typing.Any:
        try:
            self._set_project_in_client(client)
            obj = self.find_object(client)
            dryrun = kwargs.get("dryrun", False)
            prompt = ">> [{}]"
            prompt = prompt.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            if not obj:
                if dryrun:
                    click.secho("{} Create {}:{}".format(prompt, self.kind.lower(), self.metadata.name), fg='yellow')
                else:
                    result = self.create_object(client)
                    click.secho("{} Created {}:{}".format(prompt, self.kind.lower(), self.metadata.name), fg='green')
                    return result
            else:
                click.echo('{} [INFO] {}/{} {} exists'.format(prompt, self.apiVersion, self.kind, self.metadata.name))
                if dryrun:
                    click.secho("{} Update {}:{}".format(prompt, self.kind.lower(), self.metadata.name), fg='yellow')
                else:
                    result = self.update_object(client, obj)
                    click.secho("{} Updated {}:{}".format(prompt, self.kind.lower(), self.metadata.name), fg='green')
                    return result
        except Exception as e:
            click.secho("{} !!! [ERR {}:{}] {} !!!".format(prompt, self.kind.lower(), self.metadata.name, str(e)), fg="red")
            raise e

    def delete(self, client: Client, obj: typing.Any, *args, **kwargs):
        try:
            self._set_project_in_client(client)
            obj = self.find_object(client)
            dryrun = kwargs.get("dryrun", False)
            prompt = ">> [{}]"
            prompt = prompt.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

            if not obj:
                click.echo('{} {}/{} {} does not exists'.format(prompt, self.apiVersion, self.kind, self.metadata.name))
                return
            
            if not dryrun:
                self.delete_object(client, obj)
                click.secho("{} Deleted {}:{}".format(prompt, self.kind.lower(), self.metadata.name), fg='red')
            else:
                click.secho("{} Delete {}:{}".format(prompt, self.kind.lower(), self.metadata.name), fg='yellow')
        except Exception as e:
            click.secho("{} !!! [ERR {}:{}] {} !!!".format(prompt, self.kind.lower(), self.metadata.name, str(e)), fg="red")
            raise e

    @abstractmethod
    def find_object(self, client: Client) -> typing.Any:
        pass

    @abstractmethod
    def create_object(self, client: Client) -> typing.Any:
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
