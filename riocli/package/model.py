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
import os
import typing

from munch import munchify, unmunchify

from rapyuta_io import Client
from rapyuta_io.clients.package import RestartPolicy

from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.config import new_v2_client

class Package(Model):
    RESTART_POLICY = {
        'always': RestartPolicy.Always,
        'never': RestartPolicy.Never,
        'onfailure': RestartPolicy.OnFailure
    }

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client):
        guid, obj = self.rc.find_depends({"kind": self.kind.lower(), "nameOrGUID": self.metadata.name},
                                         self.metadata.version)
        if not guid:
            return False

        return obj

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        package = unmunchify(self)
        package.pop("rc", None)
        r = client.create_package(package)
        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:

        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()
        client.delete_package(obj.metadata.name, query={"version": obj.metadata.version})

    def to_v1(self):
        # return v1Project(self.metadata.name)
        pass

    def _get_rosendpoint_struct(self, rosEndpoints, filter_type):
        topic_list = filter(lambda x: x.type == filter_type, rosEndpoints)
        return_list = []
        for topic in topic_list:
            if topic.compression is False:
                topic.compression = ""
            else:
                topic.compression = "snappy"
            return_list.append(topic)
        return return_list

    def _map_executable(self, exec):
        exec_object = munchify({
            "name": exec.name,
            "simulationOptions": {
                "simulation": exec.simulation if 'simulation' in exec else False
            }
        })

        if 'limits' in exec:
            exec_object.limits = {
                'cpu': exec.limits.get('cpu', 0.0),
                'memory': exec.limits.get('memory', 0)
            }

        if 'livenessProbe' in exec:
            exec_object.livenessProbe = exec.livenessProbe

        if exec.get('runAsBash'):
            if 'command' in exec:
                exec_object.cmd = ['/bin/bash', '-c', exec.command]
        else:
            # TODO verify this is right for secret?
            if 'command' in exec:
                exec_object.cmd = [exec.command]

        if exec.type == 'docker':
            exec_object.docker = exec.docker.image
            if 'pullSecret' in exec.docker and exec.docker.pullSecret.depends:
                secret_guid, secret = self.rc.find_depends(exec.docker.pullSecret.depends)
                exec_object.secret = secret_guid

            if exec.docker.get('imagePullPolicy'):
                exec_object.imagePullPolicy = exec.docker.imagePullPolicy

        # TODO handle preinstalled

        return exec_object

    def _map_endpoints(self, endpoint):
        exposedExternally = endpoint.type.split("-")[0] == 'external'
        proto = "-".join(endpoint.type.split("-")[1:])
        if 'tls-tcp' in proto:
            proto = 'tcp'

        if 'range' in endpoint.type:
            proto = proto.replace("-range", '')
            return {
                "name": endpoint.name, "exposeExternally": exposedExternally,
                "portRange": endpoint.portRange, "proto": proto.upper()}
        else:
            return {
                "name": endpoint.name, "exposeExternally": exposedExternally,
                "port": endpoint.port, "targetPort": endpoint.targetPort, "proto": proto.upper()}

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        """
        Validates if package data is matching with its corresponding schema
        """
        schema = load_schema('package')
        schema.validate(data)
