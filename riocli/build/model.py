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

import click
from rapyuta_io import Build as v1Build, Client, BuildOptions, CatkinOption

from riocli.build.util import find_build_guid, BuildNotFound
from riocli.build.validation import validate
from riocli.model import Model


class Build(Model):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        guid, obj = self.rc.find_depends({"kind": "build", "nameOrGUID": self.metadata.name})
        if not guid:
            return False

        return obj

    def create_object(self, client: Client) -> v1Build:
        build = client.create_build(build=self.to_v1())
        return build

    def update_object(self, client: Client, obj: typing.Any) -> None:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        obj.delete()

    def to_v1(self) -> v1Build:
        build_opts = None
        if self.spec.recipe == 'Source' and self.spec.get('catkinParameters', None):
            catkin_opts = []
            for each in self.spec.catkinParameters:
                catkin_opt = CatkinOption(rosPkgs=each.get('rosPackages', None),
                                          makeArgs=each.get('makeArguments', None),
                                          cmakeArgs=each.get('cmakeArguments', None),
                                          catkinMakeArgs=each.get('catkinMakeArguments', None),
                                          blacklist=each.get('blacklist', None))
                catkin_opts.append(catkin_opt)
            build_opts = BuildOptions(catkin_opts)

        return v1Build(buildName=self.metadata.name, strategyType=self.spec.recipe, repository=self.spec.git.repository,
                       architecture=self.spec.architecture, rosDistro=self.spec.get('rosDistro', ''),
                       isRos=self.spec.get('rosDistro', '') != '', dockerPullSecret=self.spec.get('pullSecret', ''),
                       contextDir=self.spec.get('contextDir', ''), dockerFilePath=self.spec.get('dockerfile', ''),
                       dockerPushRepository=self.spec.get('pushSecret', ''), branch=self.spec.git.get('gitRef', ''),
                       triggerName=self.spec.get('triggerName', ''), tagName=self.spec.get('tagName', ''),
                       buildOptions=build_opts)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data) -> None:
        validate(data)
