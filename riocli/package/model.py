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
from textwrap import indent
import typing
import json

import click
from munch import munchify
from rapyuta_io import Project as v1Project, Client

from riocli.model import Model
# from riocli.package.util import find_project_guid, ProjectNotFound
from riocli.package.validation import validate


class Package(Model):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client):
        guid, obj = self.rc.find_depends({"kind":  self.kind.lower(), "nameOrGUID": self.metadata.name},
                                         self.metadata.version)
        if not guid:
            return False

        return obj

    def create_object(self, client: Client):
        # click.secho('{}/{} {} created'.format(self.apiVersion, self.kind, self.metadata.name), fg='green')
        pkg_object = munchify({
            'name': 'default',
            'packageVersion': 'v1.0.0',
            'apiVersion': "2.1.0",
            'plans': [
                {
                     "inboundROSInterfaces": {
                        "anyIncomingScopedOrTargetedRosConfig": False
                    },
                    'singleton': False,
                    'bindable': True,
                    'name' : 'default',
                    'dependentDeployments': [],
                    'exposedParameters': [],
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
                            'metadata': {},
                        })
        
        # metadata
        # ✓ name, ✓ description, ✓ version
        
        pkg_object.name = self.metadata.name
        pkg_object.packageVersion = self.metadata.version
        
        if 'description' in self.metadata:
            pkg_object.description = self.metadata.description
        
        
        # spec
        # executables
        component_obj.name = 'default' #self.metadata.name #package == component in the single component model
        
        # TODO validate transform.  specially nested secret. 
        component_obj.executables = list(map(self._map_executable, self.spec.executables))
        component_obj.requiredRuntime = self.spec.runtime
        


        # ✓ parameters
        # TODO validate transform.  
        component_obj.parameters = self.spec.environmentVars
        # handle exposed params
        exposed_parameters = []
        for entry in filter(lambda x: 'exposed' in x and x.exposed, self.spec.environmentVars):
            exposed_parameters.append({'component': component_obj.name, 'param': entry.name, 'targetParam': entry.exposedName})
        component_obj.exposedParameters = exposed_parameters
            
        # device
        #  ✓ arch, ✓ restart
        if self.spec.runtime == 'device':
            component_obj.required_runtime = 'device'
            component_obj.architecture = self.spec.device.arch
            component_obj.restartPolicy = self.spec.device.restart
        
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
            endpoints =  list(map(self._map_endpoints, self.spec.endpoints))
            component_obj.cloudInfra.endpoints = endpoints
        
        # ros:
        #  ✓ isros
        #  ✓ topic
        #  ✓ service
        #  ✓ action
        #   rosbagjob
        if 'ros' in self.spec:
            component_obj.ros.isRos = True
            component_obj.ros.ros_distro  = self.spec.ros.version
            pkg_object.inboundROSInterfaces = munchify({})
            
            pkg_object.inboundROSInterfaces.anyIncomingScopedOrTargetedRosConfig = self.spec.ros.inboundScopedTargeted if 'inboundScopedTargeted' in self.spec.ros else False
            if 'rosEndpoints' in self.spec.ros:
                component_obj.ros.topics = list(self._get_rosendpoint_struct(self.spec.ros.rosEndpoints, 'topic'))
                component_obj.ros.services = list(self._get_rosendpoint_struct(self.spec.ros.rosEndpoints, 'service'))
                component_obj.ros.actions = list(self._get_rosendpoint_struct(self.spec.ros.rosEndpoints, 'action'))
        
        pkg_object.plans[0].components = [component_obj]
        # return package
        # print(json.dumps(pkg_object))
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
                "simulation": exec.simulation if 'simulation' in exec  else False
            }
        })
        
        if 'limits' in exec:
            exec_object.limits = {
                "cpu": exec.limits.cpu,
                "memory": exec.limits.memory
            }
            
        if exec.runAsBash:
            if 'command' in exec:
                exec_object.cmd = ['/bin/bash', '-c', exec.command]
        else:
            #TODO verify this is right for secret?
            if 'command' in exec:
                exec_object.cmd = [exec.command]

        
        if exec.type == 'docker':
            exec_object.docker = exec.docker.image
            if 'pullSecret' in exec.docker and exec.docker.pullSecret.depends:
                secret_guid, secret =  self.rc.find_depends(exec.docker.pullSecret.depends)
                exec_object.secret = secret_guid
            
        if exec.type == 'build':
            exec_object.buildGUID = exec.build.depends.guid
            #TODO verify this is right for secret?
            # if exec.docker.pullSecret and exec.docker.pullSecret.depends and exec.docker.pullSecret.depends.guid:
                # exec_object.secret = exec.docker.pullSecret.depends.guid
        
        #TODO handle preinstalled
        
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
    def validate(data) -> None:
        validate(data)
