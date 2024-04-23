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
import typing

from munch import unmunchify
from rapyuta_io import Client
from rapyuta_io.clients.catalog_client import Package
from rapyuta_io.clients.package import ProvisionConfiguration, RestartPolicy
from rapyuta_io.clients.rosbag import (OverrideOptions, ROSBagCompression, ROSBagJob, ROSBagOnDemandUploadOptions,
                                       ROSBagOptions, ROSBagTimeRange, ROSBagUploadTypes, TopicOverrideInfo,
                                       UploadOptions)

from riocli.config import new_v2_client
from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.static_route.util import find_static_route_guid


class Deployment(Model):
    RESTART_POLICY = {
        'always': RestartPolicy.Always,
        'never': RestartPolicy.Never,
        'onfailure': RestartPolicy.OnFailure
    }

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> typing.Any:
        guid, obj = self.rc.find_depends({"kind": "deployment", "nameOrGUID": self.metadata.name})

        return obj if guid else False

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        deployment = unmunchify(self)
        deployment.pop("rc", None)
        r = client.create_deployment(deployment)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()
        client.delete_deployment(obj.metadata.name)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    def _get_provision_config(self, client: Client, pkg: Package):
        comp_name = pkg['plans']['components'][0]['name']
        prov_config = pkg.get_provision_configuration()
        self._configure_static_routes(client, prov_config, comp_name)

        return prov_config

    def _configure_networks(self, client: Client, prov_config: ProvisionConfiguration):
        if not self.spec.get('rosNetworks'):
            return

        native_networks = client.list_native_networks()
        routed_networks = client.get_all_routed_networks()

    def _configure_disks(self, client: Client, prov_config: ProvisionConfiguration, component: str):
        if not self.spec.get('volumes'):
            return

        # for volume in self.spec.volumes:
        #     # TODO: no support for the disk resource.
        #     # TODO: subpath is not there in the SDK.
        #     prov_config.mount_volume(component_name=component, volume='', mount_path=volume.mountPath)

    def _configure_static_routes(self, client: Client, prov_config: ProvisionConfiguration, component: str):
        if not self.spec.get('staticRoutes'):
            return

        # TODO: List instead of get calls again and again

        for route in self.spec.staticRoutes:
            name = route.depends.nameOrGUID
            if name.startswith('staticroute-'):
                guid = name
            else:
                guid = find_static_route_guid(client, name)
            static_route = client.get_static_route(route_guid=guid)
            prov_config.add_static_route(
                component_name=component, endpoint_name=route.name, static_route=static_route)

    def _form_rosbag_job(self, req_job):
        rosbag_job_kw_args = {
            'name': req_job.name,
            'rosbag_options': ROSBagOptions(
                all_topics=req_job.recordOptions.get('allTopics'),
                topics=req_job.recordOptions.get('topics'),
                topic_include_regex=req_job.recordOptions.get('topicIncludeRegex'),
                topic_exclude_regex=req_job.recordOptions.get('topicExcludeRegex'),
                max_message_count=req_job.recordOptions.get('maxMessageCount'),
                node=req_job.recordOptions.get('node'),
                compression=ROSBagCompression(req_job.recordOptions.compression) if hasattr(
                    req_job.recordOptions, 'compression'
                ) else None,
                max_splits=req_job.recordOptions.get('maxSplits'),
                max_split_size=req_job.recordOptions.get('maxSplitSize'),
                chunk_size=req_job.recordOptions.get('chunkSize'),
                max_split_duration=req_job.recordOptions.get('maxSplitDuration')
            )}

        if 'uploadOptions' in req_job:
            rosbag_job_kw_args['upload_options'] = self._form_rosbag_upload_options(req_job.uploadOptions)

        if 'overrideOptions' in req_job:
            rosbag_job_kw_args['override_options'] = self._form_rosbag_override_options(
                req_job.overrideOptions)

        return ROSBagJob(**rosbag_job_kw_args)

    @staticmethod
    def _form_rosbag_upload_options(upload_options):
        upload_options_kw_args = {
            'max_upload_rate': upload_options.maxUploadRate,
            'upload_type': ROSBagUploadTypes(upload_options.uploadType),
        }

        if 'purgeAfter' in upload_options:
            upload_options_kw_args['purge_after'] = upload_options.purgeAfter

        if 'onDemandOpts' in upload_options:
            time_range = ROSBagTimeRange(
                from_time=upload_options.onDemandOpts.timeRange['from'],
                to_time=upload_options.onDemandOpts.timeRange['to']
            )

            upload_options_kw_args['on_demand_options'] = ROSBagOnDemandUploadOptions(time_range)

        return UploadOptions(**upload_options_kw_args)

    @staticmethod
    def _form_rosbag_override_options(override_options):
        override_options_kw_args = {}

        if 'topicOverrideInfo' in override_options:
            override_infos = []
            for info in override_options.topicOverrideInfo:
                topic_override_info_kw_args = {
                    'topic_name': info.topicName
                }

                if 'recordFrequency' in info:
                    topic_override_info_kw_args['record_frequency'] = info.recordFrequency

                if 'latched' in info:
                    topic_override_info_kw_args['latched'] = info.latched

                override_info = TopicOverrideInfo(**topic_override_info_kw_args)

                override_infos.append(override_info)

            override_options_kw_args['topic_override_info'] = override_infos

        if 'excludeTopics' in override_options:
            override_options_kw_args['exclude_topics'] = override_options.excludeTopics

        return OverrideOptions(**override_options_kw_args)

    @staticmethod
    def validate(data):
        """
        Validates if deployment data is matching with its corresponding schema
        """
        schema = load_schema('deployment')
        schema.validate(data)
