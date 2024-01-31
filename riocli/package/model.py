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

from munch import munchify
from rapyuta_io import Client
from rapyuta_io.clients.package import RestartPolicy

from riocli.jsonschema.validate import load_schema
from riocli.model import Model


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

    def create_object(self, client: Client, **kwargs):
        pkg_object = munchify({
            'name': 'default',
            'packageVersion': 'v1.0.0',
            'apiVersion': "2.1.0",
            'description': '',
            'bindable': True,
            'plans': [
                {
                    "inboundROSInterfaces": {
                        "anyIncomingScopedOrTargetedRosConfig": False
                    },
                    'singleton': False,
                    'metadata': {},
                    'name': 'default',
                    'dependentDeployments': [],
                    'exposedParameters': [],
                    'includePackages': [],
                    'components': [
                    ]
                }
            ],
        })
        component_obj = munchify({
            'requiredRuntime': 'cloud',
            'architecture': 'amd64',
            'executables': [],
            'parameters': [],
            'ros': {'services': [], 'topics': [], 'isROS': False, 'actions': []},
            'exposedParameters': [],
            'includePackages': [],
            'rosBagJobDefs': []
        })

        # metadata
        # ✓ name, ✓ description, ✓ version

        pkg_object.name = self.metadata.name
        pkg_object.packageVersion = self.metadata.version

        if 'description' in self.metadata:
            pkg_object.description = self.metadata.description

        # spec
        # executables
        component_obj.name = 'default'  # self.metadata.name #package == component in the single component model

        # TODO validate transform.  specially nested secret. 
        component_obj.executables = list(map(self._map_executable, self.spec.executables))
        for exec in component_obj.executables:
            if hasattr(exec, 'cmd') is False:
                setattr(exec, 'cmd', [])
        component_obj.requiredRuntime = self.spec.runtime

        # ✓ parameters
        # TODO validate transform.  
        if 'environmentVars' in self.spec:
            fixed_default = []
            for envVar in self.spec.environmentVars:
                obj = envVar.copy()
                if 'defaultValue' in obj:
                    obj['default'] = obj['defaultValue']
                    del obj['default']

                fixed_default.append(obj)
            component_obj.parameters = fixed_default
            # handle exposed params
            exposed_parameters = []
            for entry in filter(lambda x: 'exposed' in x and x.exposed, self.spec.environmentVars):
                if os.environ.get('DEBUG'):
                    print(entry.name)
                exposed_parameters.append(
                    {'component': component_obj.name, 'param': entry.name, 'targetParam': entry.exposedName})
            pkg_object.plans[0].exposedParameters = exposed_parameters

        # device
        #  ✓ arch, ✓ restart
        if self.spec.runtime == 'device':
            component_obj.required_runtime = 'device'
            component_obj.architecture = self.spec.device.arch
            if 'restart' in self.spec.device:
                component_obj.restart_policy = self.RESTART_POLICY[self.spec.device.restart.lower()]

        # cloud
        #  ✓ replicas
        #  ✓ endpoints
        if 'cloud' in self.spec:
            component_obj.cloudInfra = munchify(dict())
            if 'replicas' in self.spec.cloud:
                component_obj.cloudInfra.replicas = self.spec.cloud.replicas
            else:
                component_obj.cloudInfra.replicas = 1

        if 'endpoints' in self.spec:
            endpoints = list(map(self._map_endpoints, self.spec.endpoints))
            component_obj.cloudInfra.endpoints = endpoints

        # ros:
        #  ✓ isros
        #  ✓ topic
        #  ✓ service
        #  ✓ action
        #   rosbagjob
        if 'ros' in self.spec and self.spec.ros.enabled:
            component_obj.ros.isROS = True
            component_obj.ros.ros_distro = self.spec.ros.version
            pkg_object.plans[0].inboundROSInterfaces = munchify({})

            pkg_object.plans[
                0].inboundROSInterfaces.anyIncomingScopedOrTargetedRosConfig = self.spec.ros.inboundScopedTargeted if 'inboundScopedTargeted' in self.spec.ros else False
            if 'rosEndpoints' in self.spec.ros:
                component_obj.ros.topics = list(self._get_rosendpoint_struct(self.spec.ros.rosEndpoints, 'topic'))
                component_obj.ros.services = list(self._get_rosendpoint_struct(self.spec.ros.rosEndpoints, 'service'))
                component_obj.ros.actions = list(self._get_rosendpoint_struct(self.spec.ros.rosEndpoints, 'action'))

        if 'rosBagJobs' in self.spec:
            component_obj.rosBagJobDefs = self.spec.rosBagJobs

        pkg_object.plans[0].components = [component_obj]
        return client.create_package(pkg_object)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client.delete_package(obj.packageId)

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
