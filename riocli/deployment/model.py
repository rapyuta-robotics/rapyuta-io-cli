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
import os
import typing

import click
from rapyuta_io import Client
from rapyuta_io.clients import ObjDict
from rapyuta_io.clients.catalog_client import Package
from rapyuta_io.clients.deployment import DeploymentNotRunningException, DeploymentPhaseConstants
from rapyuta_io.clients.native_network import NativeNetwork
from rapyuta_io.clients.package import ExecutableMount, ProvisionConfiguration, RestartPolicy
from rapyuta_io.clients.rosbag import (OverrideOptions, ROSBagCompression, ROSBagJob, ROSBagOnDemandUploadOptions,
                                       ROSBagOptions, ROSBagTimeRange, ROSBagUploadTypes, TopicOverrideInfo,
                                       UploadOptions)
from rapyuta_io.clients.routed_network import RoutedNetwork
from rapyuta_io.clients.static_route import StaticRoute

from riocli.constants import Colors
from riocli.deployment.errors import ERRORS
from riocli.deployment.util import add_mount_volume_provision_config
from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.package.util import find_package_guid
from riocli.parameter.utils import list_trees
from riocli.static_route.util import find_static_route_guid
from riocli.utils.cache import get_cache


class Deployment(Model):
    RESTART_POLICY = {
        'always': RestartPolicy.Always,
        'never': RestartPolicy.Never,
        'onfailure': RestartPolicy.OnFailure
    }

    def find_object(self, client: Client) -> typing.Any:
        guid, obj = self.rc.find_depends({
            "kind": "deployment",
            "nameOrGUID": self.metadata.name,
        })

        return obj if guid else False

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        pkg_guid, pkg = self.rc.find_depends(
            self.metadata.depends,
            self.metadata.depends.version)

        if pkg_guid:
            pkg = client.get_package(pkg_guid)

        if not pkg:
            raise ValueError('package not found: {}'.format(self.metadata.depends))

        pkg.update()

        default_plan = pkg['plans'][0]
        plan_id = default_plan['planId']
        internal_component = default_plan['internalComponents'][0]
        component_name = internal_component.componentName
        component = default_plan['components']['components'][0]
        executables = component['executables']
        runtime = internal_component['runtime']

        retry_count = int(kwargs.get('retry_count'))
        retry_interval = int(kwargs.get('retry_interval'))

        if 'runtime' in self.spec and runtime != self.spec.runtime:
            raise Exception('>> runtime mismatch => deployment:{}.runtime !== package:{}.runtime '.format(
                self.metadata.name, pkg['packageName']
            ))

        provision_config = pkg.get_provision_configuration(plan_id)

        # add label
        if 'labels' in self.metadata:
            for key, value in self.metadata.labels.items():
                provision_config.add_label(key, value)

        # Add envArgs
        if 'envArgs' in self.spec:
            for items in self.spec.envArgs:
                provision_config.add_parameter(component_name, items.name,
                                               items.value)

        # Add Dependent Deployment
        if 'depends' in self.spec:
            for item in self.spec.depends:
                dep_guid, dep = self.rc.find_depends(item)
                if dep is None and dep_guid:
                    dep = client.get_deployment(dep_guid)
                provision_config.add_dependent_deployment(dep, ready_phases=[
                    DeploymentPhaseConstants.PROVISIONING.value,
                    DeploymentPhaseConstants.SUCCEEDED.value])

        # Add Network
        if 'rosNetworks' in self.spec:
            for network_depends in self.spec.rosNetworks:
                network_guid, network_obj = self.rc.find_depends(network_depends.depends)

                if type(network_obj) == RoutedNetwork:
                    provision_config.add_routed_network(
                        network_obj, network_interface=network_depends.get('interface', None))
                if type(network_obj) == NativeNetwork:
                    provision_config.add_native_network(
                        network_obj, network_interface=network_depends.get('interface', None))

        if 'rosBagJobs' in self.spec:
            for req_job in self.spec.rosBagJobs:
                provision_config.add_rosbag_job(component_name,
                                                self._form_rosbag_job(req_job))

        if self.spec.runtime == 'cloud':
            if 'staticRoutes' in self.spec:
                for stroute in self.spec.staticRoutes:
                    route_guid, route = self.rc.find_depends(stroute.depends)
                    # TODO: Remove this once we transition to v2
                    route = StaticRoute(ObjDict({"guid": route_guid}))
                    provision_config.add_static_route(component_name,
                                                      stroute.name, route)

            # Add Disk
            if 'volumes' in self.spec:
                disk_mounts = {}
                for vol in self.spec.volumes:
                    disk_guid, disk = self.rc.find_depends(vol.depends)
                    if disk_guid not in disk_mounts:
                        disk_mounts[disk_guid] = []

                    disk_mounts[disk_guid].append(
                        ExecutableMount(vol.execName, vol.mountPath, vol.subPath))

                for disk_guid in disk_mounts.keys():
                    disk = client.get_volume_instance(disk_guid)
                    provision_config.mount_volume(component_name, volume=disk,
                                                  executable_mounts=
                                                  disk_mounts[disk_guid])

            # TODO: Managed Services is currently limited to `cloud` deployments
            # since we don't expose `elasticsearch` outside Openshift. This may
            # change in the future.
            if 'managedServices' in self.spec:
                managed_services = []
                for managed_service in self.spec.managedServices:
                    managed_services.append({
                        'instance': managed_service.depends.nameOrGUID,
                    })
                provision_config.context['managedServices'] = managed_services

            # inject the vpn managedservice instance if the flag is set to
            # true. 'rio-internal-headscale' is the default vpn instance
            if 'features' in self.spec:
                if 'vpn' in self.spec.features and self.spec.features.vpn.enabled:
                    provision_config.context['managedServices'] = [{
                        "instance": "rio-internal-headscale"
                    }]

        if self.spec.runtime == 'device':
            device_guid, device = self.rc.find_depends(
                self.spec.device.depends)
            if device is None and device_guid:
                device = client.get_device(device_guid)

            provision_config.add_device(
                component_name,
                device=device,
                set_component_alias=False
            )

            if 'restart' in self.spec:
                provision_config.add_restart_policy(
                    component_name,
                    self.RESTART_POLICY[self.spec.restart.lower()])

            # Add Disk
            exec_mounts = []
            if 'volumes' in self.spec:
                for vol in self.spec.volumes:
                    exec_mounts.append(
                        ExecutableMount(vol.execName, vol.mountPath,
                                        vol.subPath))

            if len(exec_mounts) > 0:
                provision_config = add_mount_volume_provision_config(
                    provision_config, component_name, device, exec_mounts)

        if 'features' in self.spec:
            if 'params' in self.spec.features and self.spec.features.params.enabled:
                component_id = internal_component.componentId
                disable_sync = self.spec.features.params.get('disableSync', False)

                # Validate trees in the manifest with the ones available
                # to avoid misconfigurations.
                tree_names = self.spec.features.params.get('trees', [])

                # For multiple deployments in the same project, the list of
                # available config trees is going to remain the same. Hence,
                # we cache it once and keep fetching it from the cache.
                cache_key = '{}-trees'.format(pkg.get('ownerProject'))
                with get_cache() as c:
                    if c.get(cache_key) is None:
                        c.set(cache_key, set(list_trees()))

                    available_trees = c.get(cache_key)

                if not available_trees:
                    raise ValueError("One or more trees are incorrect. Please run `rio parameter list` to confirm.")

                if not set(tree_names).issubset(available_trees):
                    raise ValueError("One or more trees are incorrect. Please run `rio parameter list` to confirm.")

                args = []
                for e in executables:
                    args.append({
                        'executableId': e['id'],
                        'paramTreeNames': tree_names,
                        'enableParamSync': not disable_sync
                    })

                context = provision_config.context
                if 'component_context' not in context:
                    context['component_context'] = {}

                component_context = context['component_context']
                if component_id not in component_context:
                    component_context[component_id] = {}

                component_context[component_id]['param_sync_exec_args'] = args

        provision_config.set_component_alias(component_name,
                                             self.metadata.name)

        if os.environ.get('DEBUG'):
            print(provision_config)

        deployment = pkg.provision(self.metadata.name, provision_config)

        try:
            deployment.poll_deployment_till_ready(retry_count=retry_count, sleep_interval=retry_interval,
                                                  ready_phases=[DeploymentPhaseConstants.PROVISIONING.value,
                                                                DeploymentPhaseConstants.SUCCEEDED.value])
        except DeploymentNotRunningException as e:
            raise Exception(process_deployment_errors(e)) from e
        except Exception as e:
            raise e

        deployment.get_status()

        return deployment

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        obj.deprovision()

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

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


def process_deployment_errors(e: DeploymentNotRunningException):
    errors = e.deployment_status.errors
    err_fmt = '[{}] {}\nAction: {}'
    support_action = ('Report the issue together with the relevant'
                      ' details to the support team')

    action, description = '', ''
    msgs = []
    for code in errors:
        if code in ERRORS:
            description = ERRORS[code]['description']
            action = ERRORS[code]['action']
        elif code.startswith('DEP_E2'):
            description = 'Internal rapyuta.io error in the components deployed on cloud'
            action = support_action
        elif code.startswith('DEP_E3'):
            description = 'Internal rapyuta.io error in the components deployed on a device'
            action = support_action
        elif code.startswith('DEP_E4'):
            description = 'Internal rapyuta.io error'
            action = support_action

        code = click.style(code, fg=Colors.YELLOW)
        description = click.style(description, fg=Colors.RED)
        action = click.style(action, fg=Colors.GREEN)

        msgs.append(err_fmt.format(code, description, action))

    return '\n'.join(msgs)
