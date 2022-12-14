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

import click
from rapyuta_io import Client
from rapyuta_io.clients.catalog_client import Package
from rapyuta_io.clients.native_network import NativeNetwork
from rapyuta_io.clients.package import ProvisionConfiguration, RestartPolicy, ExecutableMount
from rapyuta_io.clients.routed_network import RoutedNetwork
from rapyuta_io.clients.rosbag import ROSBagJob, ROSBagOptions, ROSBagCompression, UploadOptions, \
    ROSBagOnDemandUploadOptions, ROSBagTimeRange, ROSBagUploadTypes, OverrideOptions, TopicOverrideInfo

from riocli.deployment.util import add_mount_volume_provision_config
from riocli.deployment.validation import validate
from riocli.model import Model
from riocli.package.util import find_package_guid
from riocli.static_route.util import find_static_route_guid


class Deployment(Model):
    RESTART_POLICY = {
        'always': RestartPolicy.Always,
        'never': RestartPolicy.Never,
        'onfailure': RestartPolicy.OnFailure
    }

    def find_object(self, client: Client) -> typing.Any:
        guid, obj = self.rc.find_depends({"kind": "deployment", "nameOrGUID": self.metadata.name})
        if not guid:
            return False

        return obj

    def create_object(self, client: Client) -> typing.Any:
        pkg_guid, pkg = self.rc.find_depends(self.metadata.depends, self.metadata.depends.version)

        if pkg_guid:
            pkg = client.get_package(pkg_guid)
        pkg.update()

        default_plan = pkg['plans'][0]
        internal_component = default_plan['internalComponents'][0]

        __planId = default_plan['planId']
        __componentName = internal_component.componentName
        runtime = internal_component['runtime']

        if 'runtime' in self.spec and runtime != self.spec.runtime:
            click.secho('>> runtime mismatch => ' + \
                        'deployment:{}.runtime !== package:{}.runtime '.format(
                            self.metadata.name, pkg['packageName']
                        ), fg="red"
                        )
            return

        provision_config = pkg.get_provision_configuration(__planId)

        # add label
        if 'labels' in self.metadata:
            for key, value in self.metadata.labels.items():
                provision_config.add_label(key, value)

        # Add envArgs
        if 'envArgs' in self.spec:
            for items in self.spec.envArgs:
                provision_config.add_parameter(__componentName, items.name, items.value)

        # Add Dependent Deployment
        if 'depends' in self.spec:
            for item in self.spec.depends:
                dep_guid, dep = self.rc.find_depends(item)
                if dep is None and dep_guid:
                    dep = client.get_deployment(dep_guid)
                provision_config.add_dependent_deployment(dep)

        # Add Network
        if 'rosNetworks' in self.spec:
            for network_depends in self.spec.rosNetworks:
                network_guid, network_obj = self.rc.find_depends(network_depends.depends)

                if type(network_obj) == RoutedNetwork:
                    provision_config.add_routed_network(network_obj,
                                                        network_interface=network_depends.get('interface', None))
                if type(network_obj) == NativeNetwork:
                    provision_config.add_native_network(network_obj,
                                                        network_interface=network_depends.get('interface', None))

        if 'rosBagJobs' in self.spec:
            for req_job in self.spec.rosBagJobs:
                provision_config.add_rosbag_job(__componentName, self._form_rosbag_job(req_job))

        if self.spec.runtime == 'cloud':
            if 'staticRoutes' in self.spec:
                for stroute in self.spec.staticRoutes:
                    route_guid, route = self.rc.find_depends(stroute.depends)
                    if route is None and route_guid:
                        route = client.get_static_route(route_guid)
                    provision_config.add_static_route(__componentName, stroute.name, route)

            # Add Disk
            if 'volumes' in self.spec:
                disk_mounts = {}
                for vol in self.spec.volumes:
                    disk_guid, disk = self.rc.find_depends(vol.depends)
                    if disk_guid not in disk_mounts:
                        disk_mounts[disk_guid] = []

                    disk_mounts[disk_guid].append(ExecutableMount(vol.execName, vol.mountPath, vol.subPath))

                for disk_guid in disk_mounts.keys():
                    disk = client.get_volume_instance(disk_guid)
                    provision_config.mount_volume(__componentName, volume=disk,
                                                  executable_mounts=disk_mounts[disk_guid])

            # TODO: Managed Services is currently limited to `cloud` deployments
            # since we don't expose `elasticsearch` outside Openshift. This may
            # change in the future.
            if 'managedServices' in self.spec:
                managed_services = []
                for managed_service in self.spec.managedServices:
                    managed_services.append({
                        "instance": managed_service.depends.nameOrGUID,
                    })
                provision_config.context["managedServices"] = managed_services

        if self.spec.runtime == 'device':
            device_guid, device = self.rc.find_depends(self.spec.device.depends)
            if device is None and device_guid:
                device = client.get_device(device_guid)
            provision_config.add_device(__componentName, device=device)

            if 'restart' in self.spec:
                provision_config.add_restart_policy(__componentName, self.RESTART_POLICY[self.spec.restart.lower()])

            # Add Network
            # if self.spec.rosNetworks:
            # for network in self.spec.rosNetworks:
            # network_type =

            # Add Disk
            exec_mounts = []
            if 'volumes' in self.spec:
                for vol in self.spec.volumes:
                    exec_mounts.append(ExecutableMount(vol.execName, vol.mountPath, vol.subPath))
            if len(exec_mounts) > 0:
                provision_config = add_mount_volume_provision_config(provision_config, __componentName, device,
                                                                     exec_mounts)

        if os.environ.get('DEBUG'):
            print(provision_config)
        deployment = pkg.provision(self.metadata.name, provision_config)
        deployment.poll_deployment_till_ready()
        deployment.get_status()
        return deployment

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        if 'depends' in self.spec:
            pass
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        obj.deprovision()

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        validate(data)

    def _get_package(self, client: Client) -> Package:
        name = self.metadata.depends.nameOrGUID
        if name.startswith('pkg-') or name.startswith('io-'):
            guid = name
        else:
            guid = find_package_guid(client, name, self.metadata.depends.version)

        return client.get_package(package_id=guid)

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
            prov_config.add_static_route(component_name=component, endpoint_name=route.name, static_route=static_route)

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
            rosbag_job_kw_args['override_options'] = self._form_rosbag_override_options(req_job.overrideOptions)

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
