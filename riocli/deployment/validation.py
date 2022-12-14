VERSION = "2.16.2"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^pkg-[a-z]{24}$': re.compile('^pkg-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}, name_prefix=None):
    validate___definitions_deployment(data, custom_formats, (name_prefix or "data") + "")
    return data

def validate___definitions_deployment(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Deployment', 'default': 'Deployment'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'depends': {'$ref': '#/definitions/packageDepends'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}, 'guid': {'$ref': '#/definitions/packageGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}}, 'required': ['name', 'depends']}, 'spec': {'properties': {'runtime': {'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, 'depends': {'type': 'array', 'items': {'$ref': '#/definitions/deploymentDepends'}}}, 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'type': 'string', 'enum': ['device']}, 'depends': {'type': 'object', '$ref': '#/definitions/deviceDepends'}, 'restart': {'type': 'string', 'enum': ['always', 'onfailure', 'never'], 'default': 'always'}, 'envArgs': {'type': 'array', 'items': {'$ref': '#/definitions/envArgsSpec'}}, 'volumes': {'type': 'array', 'items': {'$ref': '#/definitions/deviceVolumeAttachSpec'}}, 'rosNetworks': {'type': 'array', 'items': {'$ref': '#/definitions/deviceNetworkAttachSpec'}}, 'rosBagJobs': {'type': 'array', 'items': {'$ref': '#/definitions/deviceROSBagJobSpec'}}}}, {'properties': {'runtime': {'type': 'string', 'enum': ['cloud']}, 'envArgs': {'type': 'array', 'items': {'$ref': '#/definitions/envArgsSpec'}}, 'volumes': {'type': 'array', 'items': {'$ref': '#/definitions/cloudVolumeAttachSpec'}}, 'staticRoutes': {'type': 'array', 'items': {'$ref': '#/definitions/endpointSpec'}}, 'rosNetworks': {'type': 'array', 'items': {'$ref': '#/definitions/cloudNetworkAttachSpec'}}, 'managedServices': {'type': 'array', 'items': {'$ref': '#/definitions/managedServiceSpec'}}, 'rosBagJobs': {'type': 'array', 'items': {'$ref': '#/definitions/cloudROSBagJobSpec'}}}}]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Deployment', 'default': 'Deployment'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'depends': {'$ref': '#/definitions/packageDepends'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}, 'guid': {'$ref': '#/definitions/packageGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}}, 'required': ['name', 'depends']}, 'spec': {'properties': {'runtime': {'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, 'depends': {'type': 'array', 'items': {'$ref': '#/definitions/deploymentDepends'}}}, 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'type': 'string', 'enum': ['device']}, 'depends': {'type': 'object', '$ref': '#/definitions/deviceDepends'}, 'restart': {'type': 'string', 'enum': ['always', 'onfailure', 'never'], 'default': 'always'}, 'envArgs': {'type': 'array', 'items': {'$ref': '#/definitions/envArgsSpec'}}, 'volumes': {'type': 'array', 'items': {'$ref': '#/definitions/deviceVolumeAttachSpec'}}, 'rosNetworks': {'type': 'array', 'items': {'$ref': '#/definitions/deviceNetworkAttachSpec'}}, 'rosBagJobs': {'type': 'array', 'items': {'$ref': '#/definitions/deviceROSBagJobSpec'}}}}, {'properties': {'runtime': {'type': 'string', 'enum': ['cloud']}, 'envArgs': {'type': 'array', 'items': {'$ref': '#/definitions/envArgsSpec'}}, 'volumes': {'type': 'array', 'items': {'$ref': '#/definitions/cloudVolumeAttachSpec'}}, 'staticRoutes': {'type': 'array', 'items': {'$ref': '#/definitions/endpointSpec'}}, 'rosNetworks': {'type': 'array', 'items': {'$ref': '#/definitions/cloudNetworkAttachSpec'}}, 'managedServices': {'type': 'array', 'items': {'$ref': '#/definitions/managedServiceSpec'}}, 'rosBagJobs': {'type': 'array', 'items': {'$ref': '#/definitions/cloudROSBagJobSpec'}}}}]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="" + (name_prefix or "data") + ".apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, rule='const')
        else: data["apiVersion"] = 'apiextensions.rapyuta.io/v1'
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "Deployment":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: Deployment", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'Deployment', 'default': 'Deployment'}, rule='const')
        else: data["kind"] = 'Deployment'
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats, (name_prefix or "data") + ".metadata")
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_componentspec(data__spec, custom_formats, (name_prefix or "data") + ".spec")
    return data

def validate___definitions_componentspec(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        if "runtime" in data:
            data_one_of_count1 = 0
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "runtime" in data_keys:
                            data_keys.remove("runtime")
                            data__runtime = data["runtime"]
                            if not isinstance(data__runtime, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be string", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'type': 'string', 'enum': ['device']}, rule='type')
                            if data__runtime not in ['device']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be one of ['device']", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'type': 'string', 'enum': ['device']}, rule='enum')
                        if "depends" in data_keys:
                            data_keys.remove("depends")
                            data__depends = data["depends"]
                            validate___definitions_devicedepends(data__depends, custom_formats, (name_prefix or "data") + ".depends")
                        if "restart" in data_keys:
                            data_keys.remove("restart")
                            data__restart = data["restart"]
                            if not isinstance(data__restart, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".restart must be string", value=data__restart, name="" + (name_prefix or "data") + ".restart", definition={'type': 'string', 'enum': ['always', 'onfailure', 'never'], 'default': 'always'}, rule='type')
                            if data__restart not in ['always', 'onfailure', 'never']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".restart must be one of ['always', 'onfailure', 'never']", value=data__restart, name="" + (name_prefix or "data") + ".restart", definition={'type': 'string', 'enum': ['always', 'onfailure', 'never'], 'default': 'always'}, rule='enum')
                        else: data["restart"] = 'always'
                        if "envArgs" in data_keys:
                            data_keys.remove("envArgs")
                            data__envArgs = data["envArgs"]
                            if not isinstance(data__envArgs, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".envArgs must be array", value=data__envArgs, name="" + (name_prefix or "data") + ".envArgs", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'string'}}}}, rule='type')
                            data__envArgs_is_list = isinstance(data__envArgs, (list, tuple))
                            if data__envArgs_is_list:
                                data__envArgs_len = len(data__envArgs)
                                for data__envArgs_x, data__envArgs_item in enumerate(data__envArgs):
                                    validate___definitions_envargsspec(data__envArgs_item, custom_formats, (name_prefix or "data") + ".envArgs[{data__envArgs_x}]")
                        if "volumes" in data_keys:
                            data_keys.remove("volumes")
                            data__volumes = data["volumes"]
                            if not isinstance(data__volumes, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".volumes must be array", value=data__volumes, name="" + (name_prefix or "data") + ".volumes", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'execName': {'type': 'string'}, 'mountPath': {'type': 'string'}, 'subPath': {'type': 'string'}}}}, rule='type')
                            data__volumes_is_list = isinstance(data__volumes, (list, tuple))
                            if data__volumes_is_list:
                                data__volumes_len = len(data__volumes)
                                for data__volumes_x, data__volumes_item in enumerate(data__volumes):
                                    validate___definitions_devicevolumeattachspec(data__volumes_item, custom_formats, (name_prefix or "data") + ".volumes[{data__volumes_x}]")
                        if "rosNetworks" in data_keys:
                            data_keys.remove("rosNetworks")
                            data__rosNetworks = data["rosNetworks"]
                            if not isinstance(data__rosNetworks, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".rosNetworks must be array", value=data__rosNetworks, name="" + (name_prefix or "data") + ".rosNetworks", definition={'type': 'array', 'items': {'properties': {'depends': {'$ref': '#/definitions/networkDepends'}, 'interface': {'type': 'string'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}}}}, rule='type')
                            data__rosNetworks_is_list = isinstance(data__rosNetworks, (list, tuple))
                            if data__rosNetworks_is_list:
                                data__rosNetworks_len = len(data__rosNetworks)
                                for data__rosNetworks_x, data__rosNetworks_item in enumerate(data__rosNetworks):
                                    validate___definitions_devicenetworkattachspec(data__rosNetworks_item, custom_formats, (name_prefix or "data") + ".rosNetworks[{data__rosNetworks_x}]")
                        if "rosBagJobs" in data_keys:
                            data_keys.remove("rosBagJobs")
                            data__rosBagJobs = data["rosBagJobs"]
                            if not isinstance(data__rosBagJobs, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".rosBagJobs must be array", value=data__rosBagJobs, name="" + (name_prefix or "data") + ".rosBagJobs", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'$ref': '#/definitions/rosbagRecordOptionsSpec'}, 'uploadOptions': {'$ref': '#/definitions/rosbagUploadOptionsSpec'}, 'overrideOptions': {'$ref': '#/definitions/rosbagOverrideOptionsSpec'}}, 'required': ['name', 'recordOptions']}}, rule='type')
                            data__rosBagJobs_is_list = isinstance(data__rosBagJobs, (list, tuple))
                            if data__rosBagJobs_is_list:
                                data__rosBagJobs_len = len(data__rosBagJobs)
                                for data__rosBagJobs_x, data__rosBagJobs_item in enumerate(data__rosBagJobs):
                                    validate___definitions_devicerosbagjobspec(data__rosBagJobs_item, custom_formats, (name_prefix or "data") + ".rosBagJobs[{data__rosBagJobs_x}]")
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "runtime" in data_keys:
                            data_keys.remove("runtime")
                            data__runtime = data["runtime"]
                            if not isinstance(data__runtime, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be string", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'type': 'string', 'enum': ['cloud']}, rule='type')
                            if data__runtime not in ['cloud']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be one of ['cloud']", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'type': 'string', 'enum': ['cloud']}, rule='enum')
                        if "envArgs" in data_keys:
                            data_keys.remove("envArgs")
                            data__envArgs = data["envArgs"]
                            if not isinstance(data__envArgs, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".envArgs must be array", value=data__envArgs, name="" + (name_prefix or "data") + ".envArgs", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'string'}}}}, rule='type')
                            data__envArgs_is_list = isinstance(data__envArgs, (list, tuple))
                            if data__envArgs_is_list:
                                data__envArgs_len = len(data__envArgs)
                                for data__envArgs_x, data__envArgs_item in enumerate(data__envArgs):
                                    validate___definitions_envargsspec(data__envArgs_item, custom_formats, (name_prefix or "data") + ".envArgs[{data__envArgs_x}]")
                        if "volumes" in data_keys:
                            data_keys.remove("volumes")
                            data__volumes = data["volumes"]
                            if not isinstance(data__volumes, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".volumes must be array", value=data__volumes, name="" + (name_prefix or "data") + ".volumes", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'execName': {'type': 'string'}, 'mountPath': {'type': 'string'}, 'subPath': {'type': 'string'}, 'depends': {'$ref': '#/definitions/diskDepends'}}}}, rule='type')
                            data__volumes_is_list = isinstance(data__volumes, (list, tuple))
                            if data__volumes_is_list:
                                data__volumes_len = len(data__volumes)
                                for data__volumes_x, data__volumes_item in enumerate(data__volumes):
                                    validate___definitions_cloudvolumeattachspec(data__volumes_item, custom_formats, (name_prefix or "data") + ".volumes[{data__volumes_x}]")
                        if "staticRoutes" in data_keys:
                            data_keys.remove("staticRoutes")
                            data__staticRoutes = data["staticRoutes"]
                            if not isinstance(data__staticRoutes, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".staticRoutes must be array", value=data__staticRoutes, name="" + (name_prefix or "data") + ".staticRoutes", definition={'type': 'array', 'items': {'properties': {'name': {'type': 'string'}, 'depends': {'properties': {'kind': {'const': 'staticroute', 'default': 'staticroute'}, 'nameOrGUID': {'type': 'string'}}}}}}, rule='type')
                            data__staticRoutes_is_list = isinstance(data__staticRoutes, (list, tuple))
                            if data__staticRoutes_is_list:
                                data__staticRoutes_len = len(data__staticRoutes)
                                for data__staticRoutes_x, data__staticRoutes_item in enumerate(data__staticRoutes):
                                    validate___definitions_endpointspec(data__staticRoutes_item, custom_formats, (name_prefix or "data") + ".staticRoutes[{data__staticRoutes_x}]")
                        if "rosNetworks" in data_keys:
                            data_keys.remove("rosNetworks")
                            data__rosNetworks = data["rosNetworks"]
                            if not isinstance(data__rosNetworks, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".rosNetworks must be array", value=data__rosNetworks, name="" + (name_prefix or "data") + ".rosNetworks", definition={'type': 'array', 'items': {'properties': {'depends': {'$ref': '#/definitions/networkDepends'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}}}}, rule='type')
                            data__rosNetworks_is_list = isinstance(data__rosNetworks, (list, tuple))
                            if data__rosNetworks_is_list:
                                data__rosNetworks_len = len(data__rosNetworks)
                                for data__rosNetworks_x, data__rosNetworks_item in enumerate(data__rosNetworks):
                                    validate___definitions_cloudnetworkattachspec(data__rosNetworks_item, custom_formats, (name_prefix or "data") + ".rosNetworks[{data__rosNetworks_x}]")
                        if "managedServices" in data_keys:
                            data_keys.remove("managedServices")
                            data__managedServices = data["managedServices"]
                            if not isinstance(data__managedServices, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".managedServices must be array", value=data__managedServices, name="" + (name_prefix or "data") + ".managedServices", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/managedServiceDepends'}}}}, rule='type')
                            data__managedServices_is_list = isinstance(data__managedServices, (list, tuple))
                            if data__managedServices_is_list:
                                data__managedServices_len = len(data__managedServices)
                                for data__managedServices_x, data__managedServices_item in enumerate(data__managedServices):
                                    validate___definitions_managedservicespec(data__managedServices_item, custom_formats, (name_prefix or "data") + ".managedServices[{data__managedServices_x}]")
                        if "rosBagJobs" in data_keys:
                            data_keys.remove("rosBagJobs")
                            data__rosBagJobs = data["rosBagJobs"]
                            if not isinstance(data__rosBagJobs, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".rosBagJobs must be array", value=data__rosBagJobs, name="" + (name_prefix or "data") + ".rosBagJobs", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'$ref': '#/definitions/rosbagRecordOptionsSpec'}, 'overrideOptions': {'$ref': '#/definitions/rosbagOverrideOptionsSpec'}}, 'required': ['name', 'recordOptions']}}, rule='type')
                            data__rosBagJobs_is_list = isinstance(data__rosBagJobs, (list, tuple))
                            if data__rosBagJobs_is_list:
                                data__rosBagJobs_len = len(data__rosBagJobs)
                                for data__rosBagJobs_x, data__rosBagJobs_item in enumerate(data__rosBagJobs):
                                    validate___definitions_cloudrosbagjobspec(data__rosBagJobs_item, custom_formats, (name_prefix or "data") + ".rosBagJobs[{data__rosBagJobs_x}]")
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count1) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'runtime': {'type': 'string', 'enum': ['device']}, 'depends': {'properties': {'kind': {'const': 'device', 'default': 'device'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}, 'restart': {'type': 'string', 'enum': ['always', 'onfailure', 'never'], 'default': 'always'}, 'envArgs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'string'}}}}, 'volumes': {'type': 'array', 'items': {'type': 'object', 'properties': {'execName': {'type': 'string'}, 'mountPath': {'type': 'string'}, 'subPath': {'type': 'string'}}}}, 'rosNetworks': {'type': 'array', 'items': {'properties': {'depends': {'$ref': '#/definitions/networkDepends'}, 'interface': {'type': 'string'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}}}}, 'rosBagJobs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'$ref': '#/definitions/rosbagRecordOptionsSpec'}, 'uploadOptions': {'$ref': '#/definitions/rosbagUploadOptionsSpec'}, 'overrideOptions': {'$ref': '#/definitions/rosbagOverrideOptionsSpec'}}, 'required': ['name', 'recordOptions']}}}}, {'properties': {'runtime': {'type': 'string', 'enum': ['cloud']}, 'envArgs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'string'}}}}, 'volumes': {'type': 'array', 'items': {'type': 'object', 'properties': {'execName': {'type': 'string'}, 'mountPath': {'type': 'string'}, 'subPath': {'type': 'string'}, 'depends': {'$ref': '#/definitions/diskDepends'}}}}, 'staticRoutes': {'type': 'array', 'items': {'properties': {'name': {'type': 'string'}, 'depends': {'properties': {'kind': {'const': 'staticroute', 'default': 'staticroute'}, 'nameOrGUID': {'type': 'string'}}}}}}, 'rosNetworks': {'type': 'array', 'items': {'properties': {'depends': {'$ref': '#/definitions/networkDepends'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}}}}, 'managedServices': {'type': 'array', 'items': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/managedServiceDepends'}}}}, 'rosBagJobs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'$ref': '#/definitions/rosbagRecordOptionsSpec'}, 'overrideOptions': {'$ref': '#/definitions/rosbagOverrideOptionsSpec'}}, 'required': ['name', 'recordOptions']}}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "runtime" in data_keys:
            data_keys.remove("runtime")
            data__runtime = data["runtime"]
            if not isinstance(data__runtime, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be string", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, rule='type')
            if data__runtime not in ['device', 'cloud']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be one of ['device', 'cloud']", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, rule='enum')
        else: data["runtime"] = 'cloud'
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            if not isinstance(data__depends, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".depends must be array", value=data__depends, name="" + (name_prefix or "data") + ".depends", definition={'type': 'array', 'items': {'properties': {'kind': {'const': 'deployment', 'default': 'deployment'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, rule='type')
            data__depends_is_list = isinstance(data__depends, (list, tuple))
            if data__depends_is_list:
                data__depends_len = len(data__depends)
                for data__depends_x, data__depends_item in enumerate(data__depends):
                    validate___definitions_deploymentdepends(data__depends_item, custom_formats, (name_prefix or "data") + ".depends[{data__depends_x}]")
    return data

def validate___definitions_deploymentdepends(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "deployment":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: deployment", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'deployment', 'default': 'deployment'}, rule='const')
        else: data["kind"] = 'deployment'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".nameOrGUID must be string", value=data__nameOrGUID, name="" + (name_prefix or "data") + ".nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".guid must be string", value=data__guid, name="" + (name_prefix or "data") + ".guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_cloudrosbagjobspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'type': 'object', 'oneOf': [{'required': ['allTopics']}, {'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}], 'properties': {'allTopics': {'type': 'boolean'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}, 'topicIncludeRegex': {'type': 'array', 'items': {'type': 'string'}}, 'topicExcludeRegex': {'type': 'string'}, 'maxMessageCount': {'type': 'integer'}, 'node': {'type': 'string'}, 'compression': {'type': 'string', 'enum': ['BZ2', 'LZ4']}, 'maxSplits': {'type': 'integer'}, 'maxSplitSize': {'type': 'integer'}, 'chunkSize': {'type': 'integer'}, 'prefix': {'type': 'string'}, 'maxSplitDuration': {'type': 'integer'}}}, 'overrideOptions': {'type': 'object', 'properties': {'topicOverrideInfo': {'type': 'array', 'items': {'$ref': '#/definitions/rosbagTopicOverrideInfoSpec'}}, 'excludeTopics': {'type': 'array', 'items': {'type': 'string'}}}}}, 'required': ['name', 'recordOptions']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name', 'recordOptions']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name', 'recordOptions'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'type': 'object', 'oneOf': [{'required': ['allTopics']}, {'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}], 'properties': {'allTopics': {'type': 'boolean'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}, 'topicIncludeRegex': {'type': 'array', 'items': {'type': 'string'}}, 'topicExcludeRegex': {'type': 'string'}, 'maxMessageCount': {'type': 'integer'}, 'node': {'type': 'string'}, 'compression': {'type': 'string', 'enum': ['BZ2', 'LZ4']}, 'maxSplits': {'type': 'integer'}, 'maxSplitSize': {'type': 'integer'}, 'chunkSize': {'type': 'integer'}, 'prefix': {'type': 'string'}, 'maxSplitDuration': {'type': 'integer'}}}, 'overrideOptions': {'type': 'object', 'properties': {'topicOverrideInfo': {'type': 'array', 'items': {'$ref': '#/definitions/rosbagTopicOverrideInfoSpec'}}, 'excludeTopics': {'type': 'array', 'items': {'type': 'string'}}}}}, 'required': ['name', 'recordOptions']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "recordOptions" in data_keys:
            data_keys.remove("recordOptions")
            data__recordOptions = data["recordOptions"]
            validate___definitions_rosbagrecordoptionsspec(data__recordOptions, custom_formats, (name_prefix or "data") + ".recordOptions")
        if "overrideOptions" in data_keys:
            data_keys.remove("overrideOptions")
            data__overrideOptions = data["overrideOptions"]
            validate___definitions_rosbagoverrideoptionsspec(data__overrideOptions, custom_formats, (name_prefix or "data") + ".overrideOptions")
    return data

def validate___definitions_rosbagoverrideoptionsspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'topicOverrideInfo': {'type': 'array', 'items': {'type': 'object', 'oneOf': [{'required': ['topicName', 'recordFrequency']}, {'required': ['topicName', 'latched']}], 'properties': {'topicName': {'type': 'string'}, 'recordFrequency': {'type': 'integer'}, 'latched': {'type': 'boolean'}}}}, 'excludeTopics': {'type': 'array', 'items': {'type': 'string'}}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "topicOverrideInfo" in data_keys:
            data_keys.remove("topicOverrideInfo")
            data__topicOverrideInfo = data["topicOverrideInfo"]
            if not isinstance(data__topicOverrideInfo, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".topicOverrideInfo must be array", value=data__topicOverrideInfo, name="" + (name_prefix or "data") + ".topicOverrideInfo", definition={'type': 'array', 'items': {'type': 'object', 'oneOf': [{'required': ['topicName', 'recordFrequency']}, {'required': ['topicName', 'latched']}], 'properties': {'topicName': {'type': 'string'}, 'recordFrequency': {'type': 'integer'}, 'latched': {'type': 'boolean'}}}}, rule='type')
            data__topicOverrideInfo_is_list = isinstance(data__topicOverrideInfo, (list, tuple))
            if data__topicOverrideInfo_is_list:
                data__topicOverrideInfo_len = len(data__topicOverrideInfo)
                for data__topicOverrideInfo_x, data__topicOverrideInfo_item in enumerate(data__topicOverrideInfo):
                    validate___definitions_rosbagtopicoverrideinfospec(data__topicOverrideInfo_item, custom_formats, (name_prefix or "data") + ".topicOverrideInfo[{data__topicOverrideInfo_x}]")
        if "excludeTopics" in data_keys:
            data_keys.remove("excludeTopics")
            data__excludeTopics = data["excludeTopics"]
            if not isinstance(data__excludeTopics, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".excludeTopics must be array", value=data__excludeTopics, name="" + (name_prefix or "data") + ".excludeTopics", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__excludeTopics_is_list = isinstance(data__excludeTopics, (list, tuple))
            if data__excludeTopics_is_list:
                data__excludeTopics_len = len(data__excludeTopics)
                for data__excludeTopics_x, data__excludeTopics_item in enumerate(data__excludeTopics):
                    if not isinstance(data__excludeTopics_item, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".excludeTopics[{data__excludeTopics_x}]".format(**locals()) + " must be string", value=data__excludeTopics_item, name="" + (name_prefix or "data") + ".excludeTopics[{data__excludeTopics_x}]".format(**locals()) + "", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_rosbagtopicoverrideinfospec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'oneOf': [{'required': ['topicName', 'recordFrequency']}, {'required': ['topicName', 'latched']}], 'properties': {'topicName': {'type': 'string'}, 'recordFrequency': {'type': 'integer'}, 'latched': {'type': 'boolean'}}}, rule='type')
    data_one_of_count2 = 0
    if data_one_of_count2 < 2:
        try:
            data_is_dict = isinstance(data, dict)
            if data_is_dict:
                data_len = len(data)
                if not all(prop in data for prop in ['topicName', 'recordFrequency']):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['topicName', 'recordFrequency'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['topicName', 'recordFrequency']}, rule='required')
            data_one_of_count2 += 1
        except JsonSchemaValueException: pass
    if data_one_of_count2 < 2:
        try:
            data_is_dict = isinstance(data, dict)
            if data_is_dict:
                data_len = len(data)
                if not all(prop in data for prop in ['topicName', 'latched']):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['topicName', 'latched'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['topicName', 'latched']}, rule='required')
            data_one_of_count2 += 1
        except JsonSchemaValueException: pass
    if data_one_of_count2 != 1:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count2) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'oneOf': [{'required': ['topicName', 'recordFrequency']}, {'required': ['topicName', 'latched']}], 'properties': {'topicName': {'type': 'string'}, 'recordFrequency': {'type': 'integer'}, 'latched': {'type': 'boolean'}}}, rule='oneOf')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "topicName" in data_keys:
            data_keys.remove("topicName")
            data__topicName = data["topicName"]
            if not isinstance(data__topicName, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".topicName must be string", value=data__topicName, name="" + (name_prefix or "data") + ".topicName", definition={'type': 'string'}, rule='type')
        if "recordFrequency" in data_keys:
            data_keys.remove("recordFrequency")
            data__recordFrequency = data["recordFrequency"]
            if not isinstance(data__recordFrequency, (int)) and not (isinstance(data__recordFrequency, float) and data__recordFrequency.is_integer()) or isinstance(data__recordFrequency, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".recordFrequency must be integer", value=data__recordFrequency, name="" + (name_prefix or "data") + ".recordFrequency", definition={'type': 'integer'}, rule='type')
        if "latched" in data_keys:
            data_keys.remove("latched")
            data__latched = data["latched"]
            if not isinstance(data__latched, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".latched must be boolean", value=data__latched, name="" + (name_prefix or "data") + ".latched", definition={'type': 'boolean'}, rule='type')
    return data

def validate___definitions_rosbagrecordoptionsspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'oneOf': [{'required': ['allTopics']}, {'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}], 'properties': {'allTopics': {'type': 'boolean'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}, 'topicIncludeRegex': {'type': 'array', 'items': {'type': 'string'}}, 'topicExcludeRegex': {'type': 'string'}, 'maxMessageCount': {'type': 'integer'}, 'node': {'type': 'string'}, 'compression': {'type': 'string', 'enum': ['BZ2', 'LZ4']}, 'maxSplits': {'type': 'integer'}, 'maxSplitSize': {'type': 'integer'}, 'chunkSize': {'type': 'integer'}, 'prefix': {'type': 'string'}, 'maxSplitDuration': {'type': 'integer'}}}, rule='type')
    data_one_of_count3 = 0
    if data_one_of_count3 < 2:
        try:
            data_is_dict = isinstance(data, dict)
            if data_is_dict:
                data_len = len(data)
                if not all(prop in data for prop in ['allTopics']):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['allTopics'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['allTopics']}, rule='required')
            data_one_of_count3 += 1
        except JsonSchemaValueException: pass
    if data_one_of_count3 < 2:
        try:
            data_any_of_count4 = 0
            if not data_any_of_count4:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['topics']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['topics'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['topics']}, rule='required')
                    data_any_of_count4 += 1
                except JsonSchemaValueException: pass
            if not data_any_of_count4:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['topicIncludeRegex']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['topicIncludeRegex'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['topicIncludeRegex']}, rule='required')
                    data_any_of_count4 += 1
                except JsonSchemaValueException: pass
            if not data_any_of_count4:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " cannot be validated by any definition", value=data, name="" + (name_prefix or "data") + "", definition={'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}, rule='anyOf')
            data_one_of_count3 += 1
        except JsonSchemaValueException: pass
    if data_one_of_count3 != 1:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count3) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'oneOf': [{'required': ['allTopics']}, {'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}], 'properties': {'allTopics': {'type': 'boolean'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}, 'topicIncludeRegex': {'type': 'array', 'items': {'type': 'string'}}, 'topicExcludeRegex': {'type': 'string'}, 'maxMessageCount': {'type': 'integer'}, 'node': {'type': 'string'}, 'compression': {'type': 'string', 'enum': ['BZ2', 'LZ4']}, 'maxSplits': {'type': 'integer'}, 'maxSplitSize': {'type': 'integer'}, 'chunkSize': {'type': 'integer'}, 'prefix': {'type': 'string'}, 'maxSplitDuration': {'type': 'integer'}}}, rule='oneOf')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "allTopics" in data_keys:
            data_keys.remove("allTopics")
            data__allTopics = data["allTopics"]
            if not isinstance(data__allTopics, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".allTopics must be boolean", value=data__allTopics, name="" + (name_prefix or "data") + ".allTopics", definition={'type': 'boolean'}, rule='type')
        if "topics" in data_keys:
            data_keys.remove("topics")
            data__topics = data["topics"]
            if not isinstance(data__topics, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".topics must be array", value=data__topics, name="" + (name_prefix or "data") + ".topics", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__topics_is_list = isinstance(data__topics, (list, tuple))
            if data__topics_is_list:
                data__topics_len = len(data__topics)
                for data__topics_x, data__topics_item in enumerate(data__topics):
                    if not isinstance(data__topics_item, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".topics[{data__topics_x}]".format(**locals()) + " must be string", value=data__topics_item, name="" + (name_prefix or "data") + ".topics[{data__topics_x}]".format(**locals()) + "", definition={'type': 'string'}, rule='type')
        if "topicIncludeRegex" in data_keys:
            data_keys.remove("topicIncludeRegex")
            data__topicIncludeRegex = data["topicIncludeRegex"]
            if not isinstance(data__topicIncludeRegex, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".topicIncludeRegex must be array", value=data__topicIncludeRegex, name="" + (name_prefix or "data") + ".topicIncludeRegex", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__topicIncludeRegex_is_list = isinstance(data__topicIncludeRegex, (list, tuple))
            if data__topicIncludeRegex_is_list:
                data__topicIncludeRegex_len = len(data__topicIncludeRegex)
                for data__topicIncludeRegex_x, data__topicIncludeRegex_item in enumerate(data__topicIncludeRegex):
                    if not isinstance(data__topicIncludeRegex_item, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".topicIncludeRegex[{data__topicIncludeRegex_x}]".format(**locals()) + " must be string", value=data__topicIncludeRegex_item, name="" + (name_prefix or "data") + ".topicIncludeRegex[{data__topicIncludeRegex_x}]".format(**locals()) + "", definition={'type': 'string'}, rule='type')
        if "topicExcludeRegex" in data_keys:
            data_keys.remove("topicExcludeRegex")
            data__topicExcludeRegex = data["topicExcludeRegex"]
            if not isinstance(data__topicExcludeRegex, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".topicExcludeRegex must be string", value=data__topicExcludeRegex, name="" + (name_prefix or "data") + ".topicExcludeRegex", definition={'type': 'string'}, rule='type')
        if "maxMessageCount" in data_keys:
            data_keys.remove("maxMessageCount")
            data__maxMessageCount = data["maxMessageCount"]
            if not isinstance(data__maxMessageCount, (int)) and not (isinstance(data__maxMessageCount, float) and data__maxMessageCount.is_integer()) or isinstance(data__maxMessageCount, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".maxMessageCount must be integer", value=data__maxMessageCount, name="" + (name_prefix or "data") + ".maxMessageCount", definition={'type': 'integer'}, rule='type')
        if "node" in data_keys:
            data_keys.remove("node")
            data__node = data["node"]
            if not isinstance(data__node, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".node must be string", value=data__node, name="" + (name_prefix or "data") + ".node", definition={'type': 'string'}, rule='type')
        if "compression" in data_keys:
            data_keys.remove("compression")
            data__compression = data["compression"]
            if not isinstance(data__compression, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".compression must be string", value=data__compression, name="" + (name_prefix or "data") + ".compression", definition={'type': 'string', 'enum': ['BZ2', 'LZ4']}, rule='type')
            if data__compression not in ['BZ2', 'LZ4']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".compression must be one of ['BZ2', 'LZ4']", value=data__compression, name="" + (name_prefix or "data") + ".compression", definition={'type': 'string', 'enum': ['BZ2', 'LZ4']}, rule='enum')
        if "maxSplits" in data_keys:
            data_keys.remove("maxSplits")
            data__maxSplits = data["maxSplits"]
            if not isinstance(data__maxSplits, (int)) and not (isinstance(data__maxSplits, float) and data__maxSplits.is_integer()) or isinstance(data__maxSplits, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".maxSplits must be integer", value=data__maxSplits, name="" + (name_prefix or "data") + ".maxSplits", definition={'type': 'integer'}, rule='type')
        if "maxSplitSize" in data_keys:
            data_keys.remove("maxSplitSize")
            data__maxSplitSize = data["maxSplitSize"]
            if not isinstance(data__maxSplitSize, (int)) and not (isinstance(data__maxSplitSize, float) and data__maxSplitSize.is_integer()) or isinstance(data__maxSplitSize, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".maxSplitSize must be integer", value=data__maxSplitSize, name="" + (name_prefix or "data") + ".maxSplitSize", definition={'type': 'integer'}, rule='type')
        if "chunkSize" in data_keys:
            data_keys.remove("chunkSize")
            data__chunkSize = data["chunkSize"]
            if not isinstance(data__chunkSize, (int)) and not (isinstance(data__chunkSize, float) and data__chunkSize.is_integer()) or isinstance(data__chunkSize, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".chunkSize must be integer", value=data__chunkSize, name="" + (name_prefix or "data") + ".chunkSize", definition={'type': 'integer'}, rule='type')
        if "prefix" in data_keys:
            data_keys.remove("prefix")
            data__prefix = data["prefix"]
            if not isinstance(data__prefix, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".prefix must be string", value=data__prefix, name="" + (name_prefix or "data") + ".prefix", definition={'type': 'string'}, rule='type')
        if "maxSplitDuration" in data_keys:
            data_keys.remove("maxSplitDuration")
            data__maxSplitDuration = data["maxSplitDuration"]
            if not isinstance(data__maxSplitDuration, (int)) and not (isinstance(data__maxSplitDuration, float) and data__maxSplitDuration.is_integer()) or isinstance(data__maxSplitDuration, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".maxSplitDuration must be integer", value=data__maxSplitDuration, name="" + (name_prefix or "data") + ".maxSplitDuration", definition={'type': 'integer'}, rule='type')
    return data

def validate___definitions_managedservicespec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'managedservice', 'default': 'managedservice'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_managedservicedepends(data__depends, custom_formats, (name_prefix or "data") + ".depends")
    return data

def validate___definitions_managedservicedepends(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "managedservice":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: managedservice", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'managedservice', 'default': 'managedservice'}, rule='const')
        else: data["kind"] = 'managedservice'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".nameOrGUID must be string", value=data__nameOrGUID, name="" + (name_prefix or "data") + ".nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".guid must be string", value=data__guid, name="" + (name_prefix or "data") + ".guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_cloudnetworkattachspec(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_networkdepends(data__depends, custom_formats, (name_prefix or "data") + ".depends")
        if "topics" in data_keys:
            data_keys.remove("topics")
            data__topics = data["topics"]
            if not isinstance(data__topics, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".topics must be array", value=data__topics, name="" + (name_prefix or "data") + ".topics", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__topics_is_list = isinstance(data__topics, (list, tuple))
            if data__topics_is_list:
                data__topics_len = len(data__topics)
                for data__topics_x, data__topics_item in enumerate(data__topics):
                    if not isinstance(data__topics_item, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".topics[{data__topics_x}]".format(**locals()) + " must be string", value=data__topics_item, name="" + (name_prefix or "data") + ".topics[{data__topics_x}]".format(**locals()) + "", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_networkdepends(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "network":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: network", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'network', 'default': 'network'}, rule='const')
        else: data["kind"] = 'network'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".nameOrGUID must be string", value=data__nameOrGUID, name="" + (name_prefix or "data") + ".nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".guid must be string", value=data__guid, name="" + (name_prefix or "data") + ".guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_endpointspec(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            data__depends_is_dict = isinstance(data__depends, dict)
            if data__depends_is_dict:
                data__depends_keys = set(data__depends.keys())
                if "kind" in data__depends_keys:
                    data__depends_keys.remove("kind")
                    data__depends__kind = data__depends["kind"]
                    if data__depends__kind != "staticroute":
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".depends.kind must be same as const definition: staticroute", value=data__depends__kind, name="" + (name_prefix or "data") + ".depends.kind", definition={'const': 'staticroute', 'default': 'staticroute'}, rule='const')
                else: data__depends["kind"] = 'staticroute'
                if "nameOrGUID" in data__depends_keys:
                    data__depends_keys.remove("nameOrGUID")
                    data__depends__nameOrGUID = data__depends["nameOrGUID"]
                    if not isinstance(data__depends__nameOrGUID, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".depends.nameOrGUID must be string", value=data__depends__nameOrGUID, name="" + (name_prefix or "data") + ".depends.nameOrGUID", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_cloudvolumeattachspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'execName': {'type': 'string'}, 'mountPath': {'type': 'string'}, 'subPath': {'type': 'string'}, 'depends': {'properties': {'kind': {'const': 'disk', 'default': 'disk'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "execName" in data_keys:
            data_keys.remove("execName")
            data__execName = data["execName"]
            if not isinstance(data__execName, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".execName must be string", value=data__execName, name="" + (name_prefix or "data") + ".execName", definition={'type': 'string'}, rule='type')
        if "mountPath" in data_keys:
            data_keys.remove("mountPath")
            data__mountPath = data["mountPath"]
            if not isinstance(data__mountPath, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".mountPath must be string", value=data__mountPath, name="" + (name_prefix or "data") + ".mountPath", definition={'type': 'string'}, rule='type')
        if "subPath" in data_keys:
            data_keys.remove("subPath")
            data__subPath = data["subPath"]
            if not isinstance(data__subPath, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".subPath must be string", value=data__subPath, name="" + (name_prefix or "data") + ".subPath", definition={'type': 'string'}, rule='type')
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_diskdepends(data__depends, custom_formats, (name_prefix or "data") + ".depends")
    return data

def validate___definitions_diskdepends(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "disk":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: disk", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'disk', 'default': 'disk'}, rule='const')
        else: data["kind"] = 'disk'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".nameOrGUID must be string", value=data__nameOrGUID, name="" + (name_prefix or "data") + ".nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".guid must be string", value=data__guid, name="" + (name_prefix or "data") + ".guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_devicerosbagjobspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'type': 'object', 'oneOf': [{'required': ['allTopics']}, {'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}], 'properties': {'allTopics': {'type': 'boolean'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}, 'topicIncludeRegex': {'type': 'array', 'items': {'type': 'string'}}, 'topicExcludeRegex': {'type': 'string'}, 'maxMessageCount': {'type': 'integer'}, 'node': {'type': 'string'}, 'compression': {'type': 'string', 'enum': ['BZ2', 'LZ4']}, 'maxSplits': {'type': 'integer'}, 'maxSplitSize': {'type': 'integer'}, 'chunkSize': {'type': 'integer'}, 'prefix': {'type': 'string'}, 'maxSplitDuration': {'type': 'integer'}}}, 'uploadOptions': {'type': 'object', 'properties': {'maxUploadRate': {'type': 'integer', 'default': 1048576}, 'purgeAfter': {'type': 'boolean'}, 'uploadType': {'type': 'string', 'enum': ['OnStop', 'Continuous', 'OnDemand'], 'default': 'OnDemand'}, 'onDemandOpts': {'type': 'object', '$ref': '#/definitions/rosbagOnDemandUploadOptionsSpec'}}}, 'overrideOptions': {'type': 'object', 'properties': {'topicOverrideInfo': {'type': 'array', 'items': {'$ref': '#/definitions/rosbagTopicOverrideInfoSpec'}}, 'excludeTopics': {'type': 'array', 'items': {'type': 'string'}}}}}, 'required': ['name', 'recordOptions']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name', 'recordOptions']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name', 'recordOptions'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'type': 'object', 'oneOf': [{'required': ['allTopics']}, {'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}], 'properties': {'allTopics': {'type': 'boolean'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}, 'topicIncludeRegex': {'type': 'array', 'items': {'type': 'string'}}, 'topicExcludeRegex': {'type': 'string'}, 'maxMessageCount': {'type': 'integer'}, 'node': {'type': 'string'}, 'compression': {'type': 'string', 'enum': ['BZ2', 'LZ4']}, 'maxSplits': {'type': 'integer'}, 'maxSplitSize': {'type': 'integer'}, 'chunkSize': {'type': 'integer'}, 'prefix': {'type': 'string'}, 'maxSplitDuration': {'type': 'integer'}}}, 'uploadOptions': {'type': 'object', 'properties': {'maxUploadRate': {'type': 'integer', 'default': 1048576}, 'purgeAfter': {'type': 'boolean'}, 'uploadType': {'type': 'string', 'enum': ['OnStop', 'Continuous', 'OnDemand'], 'default': 'OnDemand'}, 'onDemandOpts': {'type': 'object', '$ref': '#/definitions/rosbagOnDemandUploadOptionsSpec'}}}, 'overrideOptions': {'type': 'object', 'properties': {'topicOverrideInfo': {'type': 'array', 'items': {'$ref': '#/definitions/rosbagTopicOverrideInfoSpec'}}, 'excludeTopics': {'type': 'array', 'items': {'type': 'string'}}}}}, 'required': ['name', 'recordOptions']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "recordOptions" in data_keys:
            data_keys.remove("recordOptions")
            data__recordOptions = data["recordOptions"]
            validate___definitions_rosbagrecordoptionsspec(data__recordOptions, custom_formats, (name_prefix or "data") + ".recordOptions")
        if "uploadOptions" in data_keys:
            data_keys.remove("uploadOptions")
            data__uploadOptions = data["uploadOptions"]
            validate___definitions_rosbaguploadoptionsspec(data__uploadOptions, custom_formats, (name_prefix or "data") + ".uploadOptions")
        if "overrideOptions" in data_keys:
            data_keys.remove("overrideOptions")
            data__overrideOptions = data["overrideOptions"]
            validate___definitions_rosbagoverrideoptionsspec(data__overrideOptions, custom_formats, (name_prefix or "data") + ".overrideOptions")
    return data

def validate___definitions_rosbaguploadoptionsspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'maxUploadRate': {'type': 'integer', 'default': 1048576}, 'purgeAfter': {'type': 'boolean'}, 'uploadType': {'type': 'string', 'enum': ['OnStop', 'Continuous', 'OnDemand'], 'default': 'OnDemand'}, 'onDemandOpts': {'type': 'object', 'properties': {'timeRange': {'type': 'object', 'properties': {'from': {'type': 'integer', 'default': 0}, 'to': {'type': 'integer', 'default': 0}}, 'required': ['from', 'to']}}, 'required': ['timeRange']}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "maxUploadRate" in data_keys:
            data_keys.remove("maxUploadRate")
            data__maxUploadRate = data["maxUploadRate"]
            if not isinstance(data__maxUploadRate, (int)) and not (isinstance(data__maxUploadRate, float) and data__maxUploadRate.is_integer()) or isinstance(data__maxUploadRate, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".maxUploadRate must be integer", value=data__maxUploadRate, name="" + (name_prefix or "data") + ".maxUploadRate", definition={'type': 'integer', 'default': 1048576}, rule='type')
        else: data["maxUploadRate"] = 1048576
        if "purgeAfter" in data_keys:
            data_keys.remove("purgeAfter")
            data__purgeAfter = data["purgeAfter"]
            if not isinstance(data__purgeAfter, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".purgeAfter must be boolean", value=data__purgeAfter, name="" + (name_prefix or "data") + ".purgeAfter", definition={'type': 'boolean'}, rule='type')
        if "uploadType" in data_keys:
            data_keys.remove("uploadType")
            data__uploadType = data["uploadType"]
            if not isinstance(data__uploadType, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".uploadType must be string", value=data__uploadType, name="" + (name_prefix or "data") + ".uploadType", definition={'type': 'string', 'enum': ['OnStop', 'Continuous', 'OnDemand'], 'default': 'OnDemand'}, rule='type')
            if data__uploadType not in ['OnStop', 'Continuous', 'OnDemand']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".uploadType must be one of ['OnStop', 'Continuous', 'OnDemand']", value=data__uploadType, name="" + (name_prefix or "data") + ".uploadType", definition={'type': 'string', 'enum': ['OnStop', 'Continuous', 'OnDemand'], 'default': 'OnDemand'}, rule='enum')
        else: data["uploadType"] = 'OnDemand'
        if "onDemandOpts" in data_keys:
            data_keys.remove("onDemandOpts")
            data__onDemandOpts = data["onDemandOpts"]
            validate___definitions_rosbagondemanduploadoptionsspec(data__onDemandOpts, custom_formats, (name_prefix or "data") + ".onDemandOpts")
    return data

def validate___definitions_rosbagondemanduploadoptionsspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'timeRange': {'type': 'object', 'properties': {'from': {'type': 'integer', 'default': 0}, 'to': {'type': 'integer', 'default': 0}}, 'required': ['from', 'to']}}, 'required': ['timeRange']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['timeRange']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['timeRange'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'timeRange': {'type': 'object', 'properties': {'from': {'type': 'integer', 'default': 0}, 'to': {'type': 'integer', 'default': 0}}, 'required': ['from', 'to']}}, 'required': ['timeRange']}, rule='required')
        data_keys = set(data.keys())
        if "timeRange" in data_keys:
            data_keys.remove("timeRange")
            data__timeRange = data["timeRange"]
            if not isinstance(data__timeRange, (dict)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeRange must be object", value=data__timeRange, name="" + (name_prefix or "data") + ".timeRange", definition={'type': 'object', 'properties': {'from': {'type': 'integer', 'default': 0}, 'to': {'type': 'integer', 'default': 0}}, 'required': ['from', 'to']}, rule='type')
            data__timeRange_is_dict = isinstance(data__timeRange, dict)
            if data__timeRange_is_dict:
                data__timeRange_len = len(data__timeRange)
                if not all(prop in data__timeRange for prop in ['from', 'to']):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeRange must contain ['from', 'to'] properties", value=data__timeRange, name="" + (name_prefix or "data") + ".timeRange", definition={'type': 'object', 'properties': {'from': {'type': 'integer', 'default': 0}, 'to': {'type': 'integer', 'default': 0}}, 'required': ['from', 'to']}, rule='required')
                data__timeRange_keys = set(data__timeRange.keys())
                if "from" in data__timeRange_keys:
                    data__timeRange_keys.remove("from")
                    data__timeRange__from = data__timeRange["from"]
                    if not isinstance(data__timeRange__from, (int)) and not (isinstance(data__timeRange__from, float) and data__timeRange__from.is_integer()) or isinstance(data__timeRange__from, bool):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeRange.from must be integer", value=data__timeRange__from, name="" + (name_prefix or "data") + ".timeRange.from", definition={'type': 'integer', 'default': 0}, rule='type')
                else: data__timeRange["from"] = 0
                if "to" in data__timeRange_keys:
                    data__timeRange_keys.remove("to")
                    data__timeRange__to = data__timeRange["to"]
                    if not isinstance(data__timeRange__to, (int)) and not (isinstance(data__timeRange__to, float) and data__timeRange__to.is_integer()) or isinstance(data__timeRange__to, bool):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeRange.to must be integer", value=data__timeRange__to, name="" + (name_prefix or "data") + ".timeRange.to", definition={'type': 'integer', 'default': 0}, rule='type')
                else: data__timeRange["to"] = 0
    return data

def validate___definitions_devicenetworkattachspec(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_networkdepends(data__depends, custom_formats, (name_prefix or "data") + ".depends")
        if "interface" in data_keys:
            data_keys.remove("interface")
            data__interface = data["interface"]
            if not isinstance(data__interface, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".interface must be string", value=data__interface, name="" + (name_prefix or "data") + ".interface", definition={'type': 'string'}, rule='type')
        if "topics" in data_keys:
            data_keys.remove("topics")
            data__topics = data["topics"]
            if not isinstance(data__topics, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".topics must be array", value=data__topics, name="" + (name_prefix or "data") + ".topics", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__topics_is_list = isinstance(data__topics, (list, tuple))
            if data__topics_is_list:
                data__topics_len = len(data__topics)
                for data__topics_x, data__topics_item in enumerate(data__topics):
                    if not isinstance(data__topics_item, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".topics[{data__topics_x}]".format(**locals()) + " must be string", value=data__topics_item, name="" + (name_prefix or "data") + ".topics[{data__topics_x}]".format(**locals()) + "", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_devicevolumeattachspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'execName': {'type': 'string'}, 'mountPath': {'type': 'string'}, 'subPath': {'type': 'string'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "execName" in data_keys:
            data_keys.remove("execName")
            data__execName = data["execName"]
            if not isinstance(data__execName, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".execName must be string", value=data__execName, name="" + (name_prefix or "data") + ".execName", definition={'type': 'string'}, rule='type')
        if "mountPath" in data_keys:
            data_keys.remove("mountPath")
            data__mountPath = data["mountPath"]
            if not isinstance(data__mountPath, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".mountPath must be string", value=data__mountPath, name="" + (name_prefix or "data") + ".mountPath", definition={'type': 'string'}, rule='type')
        if "subPath" in data_keys:
            data_keys.remove("subPath")
            data__subPath = data["subPath"]
            if not isinstance(data__subPath, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".subPath must be string", value=data__subPath, name="" + (name_prefix or "data") + ".subPath", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_envargsspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'string'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "value" in data_keys:
            data_keys.remove("value")
            data__value = data["value"]
            if not isinstance(data__value, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".value must be string", value=data__value, name="" + (name_prefix or "data") + ".value", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_devicedepends(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "device":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: device", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'device', 'default': 'device'}, rule='const')
        else: data["kind"] = 'device'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".nameOrGUID must be string", value=data__nameOrGUID, name="" + (name_prefix or "data") + ".nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".guid must be string", value=data__guid, name="" + (name_prefix or "data") + ".guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_metadata(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'depends': {'properties': {'kind': {'const': 'package', 'default': 'package'}, 'nameOrGUID': {'type': 'string'}, 'version': {'type': 'string'}, 'guid': {'type': 'string'}}}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}, 'guid': {'type': 'string', 'pattern': '^pkg-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}}, 'required': ['name', 'depends']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name', 'depends']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name', 'depends'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'depends': {'properties': {'kind': {'const': 'package', 'default': 'package'}, 'nameOrGUID': {'type': 'string'}, 'version': {'type': 'string'}, 'guid': {'type': 'string'}}}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}, 'guid': {'type': 'string', 'pattern': '^pkg-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}}, 'required': ['name', 'depends']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_packagedepends(data__depends, custom_formats, (name_prefix or "data") + ".depends")
        if "labels" in data_keys:
            data_keys.remove("labels")
            data__labels = data["labels"]
            validate___definitions_stringmap(data__labels, custom_formats, (name_prefix or "data") + ".labels")
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_packageguid(data__guid, custom_formats, (name_prefix or "data") + ".guid")
        if "creator" in data_keys:
            data_keys.remove("creator")
            data__creator = data["creator"]
            validate___definitions_uuid(data__creator, custom_formats, (name_prefix or "data") + ".creator")
        if "project" in data_keys:
            data_keys.remove("project")
            data__project = data["project"]
            validate___definitions_projectguid(data__project, custom_formats, (name_prefix or "data") + ".project")
    return data

def validate___definitions_projectguid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^project-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^project-[a-z]{24}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='pattern')
    return data

def validate___definitions_uuid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data

def validate___definitions_packageguid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^pkg-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^pkg-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^pkg-[a-z]{24}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^pkg-[a-z]{24}$'}, rule='pattern')
    return data

def validate___definitions_stringmap(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'additionalProperties': {'type': 'string'}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        for data_key in data_keys:
            if data_key not in []:
                data_value = data.get(data_key)
                if not isinstance(data_value, (str)):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".{data_key}".format(**locals()) + " must be string", value=data_value, name="" + (name_prefix or "data") + ".{data_key}".format(**locals()) + "", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_packagedepends(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "package":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: package", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'package', 'default': 'package'}, rule='const')
        else: data["kind"] = 'package'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".nameOrGUID must be string", value=data__nameOrGUID, name="" + (name_prefix or "data") + ".nameOrGUID", definition={'type': 'string'}, rule='type')
        if "version" in data_keys:
            data_keys.remove("version")
            data__version = data["version"]
            if not isinstance(data__version, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".version must be string", value=data__version, name="" + (name_prefix or "data") + ".version", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".guid must be string", value=data__guid, name="" + (name_prefix or "data") + ".guid", definition={'type': 'string'}, rule='type')
    return data