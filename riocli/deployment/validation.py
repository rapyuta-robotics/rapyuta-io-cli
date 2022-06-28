VERSION = "2.15.3"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^pkg-[a-z]{24}$': re.compile('^pkg-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}):
    validate___definitions_deployment(data, custom_formats)
    return data

def validate___definitions_deployment(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Deployment', 'default': 'Deployment'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/componentSpec'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("data must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Deployment', 'default': 'Deployment'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/componentSpec'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("data.apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="data.apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, rule='const')
        else: data["apiVersion"] = 'apiextensions.rapyuta.io/v1'
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "Deployment":
                raise JsonSchemaValueException("data.kind must be same as const definition: Deployment", value=data__kind, name="data.kind", definition={'const': 'Deployment', 'default': 'Deployment'}, rule='const')
        else: data["kind"] = 'Deployment'
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats)
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_componentspec(data__spec, custom_formats)
    return data

def validate___definitions_componentspec(data, custom_formats={}):
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
                                raise JsonSchemaValueException("data.runtime must be string", value=data__runtime, name="data.runtime", definition={'type': 'string', 'enum': ['device']}, rule='type')
                            if data__runtime not in ['device']:
                                raise JsonSchemaValueException("data.runtime must be one of ['device']", value=data__runtime, name="data.runtime", definition={'type': 'string', 'enum': ['device']}, rule='enum')
                        if "depends" in data_keys:
                            data_keys.remove("depends")
                            data__depends = data["depends"]
                            validate___definitions_devicedepends(data__depends, custom_formats)
                        if "restart" in data_keys:
                            data_keys.remove("restart")
                            data__restart = data["restart"]
                            if not isinstance(data__restart, (str)):
                                raise JsonSchemaValueException("data.restart must be string", value=data__restart, name="data.restart", definition={'type': 'string', 'enum': ['always', 'onFailure', 'never'], 'default': 'always'}, rule='type')
                            if data__restart not in ['always', 'onFailure', 'never']:
                                raise JsonSchemaValueException("data.restart must be one of ['always', 'onFailure', 'never']", value=data__restart, name="data.restart", definition={'type': 'string', 'enum': ['always', 'onFailure', 'never'], 'default': 'always'}, rule='enum')
                        else: data["restart"] = 'always'
                        if "envArgs" in data_keys:
                            data_keys.remove("envArgs")
                            data__envArgs = data["envArgs"]
                            if not isinstance(data__envArgs, (list, tuple)):
                                raise JsonSchemaValueException("data.envArgs must be array", value=data__envArgs, name="data.envArgs", definition={'type': 'array', 'items': {'$ref': '#/definitions/envArgsSpec'}}, rule='type')
                            data__envArgs_is_list = isinstance(data__envArgs, (list, tuple))
                            if data__envArgs_is_list:
                                data__envArgs_len = len(data__envArgs)
                                for data__envArgs_x, data__envArgs_item in enumerate(data__envArgs):
                                    validate___definitions_envargsspec(data__envArgs_item, custom_formats)
                        if "volumes" in data_keys:
                            data_keys.remove("volumes")
                            data__volumes = data["volumes"]
                            if not isinstance(data__volumes, (list, tuple)):
                                raise JsonSchemaValueException("data.volumes must be array", value=data__volumes, name="data.volumes", definition={'type': 'array', 'items': {'$ref': '#/definitions/deviceVolumeAttachSpec'}}, rule='type')
                            data__volumes_is_list = isinstance(data__volumes, (list, tuple))
                            if data__volumes_is_list:
                                data__volumes_len = len(data__volumes)
                                for data__volumes_x, data__volumes_item in enumerate(data__volumes):
                                    validate___definitions_devicevolumeattachspec(data__volumes_item, custom_formats)
                        if "rosNetworks" in data_keys:
                            data_keys.remove("rosNetworks")
                            data__rosNetworks = data["rosNetworks"]
                            if not isinstance(data__rosNetworks, (list, tuple)):
                                raise JsonSchemaValueException("data.rosNetworks must be array", value=data__rosNetworks, name="data.rosNetworks", definition={'type': 'array', 'items': {'$ref': '#/definitions/deviceNetworkAttachSpec'}}, rule='type')
                            data__rosNetworks_is_list = isinstance(data__rosNetworks, (list, tuple))
                            if data__rosNetworks_is_list:
                                data__rosNetworks_len = len(data__rosNetworks)
                                for data__rosNetworks_x, data__rosNetworks_item in enumerate(data__rosNetworks):
                                    validate___definitions_devicenetworkattachspec(data__rosNetworks_item, custom_formats)
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
                                raise JsonSchemaValueException("data.runtime must be string", value=data__runtime, name="data.runtime", definition={'type': 'string', 'enum': ['cloud']}, rule='type')
                            if data__runtime not in ['cloud']:
                                raise JsonSchemaValueException("data.runtime must be one of ['cloud']", value=data__runtime, name="data.runtime", definition={'type': 'string', 'enum': ['cloud']}, rule='enum')
                        if "envArgs" in data_keys:
                            data_keys.remove("envArgs")
                            data__envArgs = data["envArgs"]
                            if not isinstance(data__envArgs, (list, tuple)):
                                raise JsonSchemaValueException("data.envArgs must be array", value=data__envArgs, name="data.envArgs", definition={'type': 'array', 'items': {'$ref': '#/definitions/envArgsSpec'}}, rule='type')
                            data__envArgs_is_list = isinstance(data__envArgs, (list, tuple))
                            if data__envArgs_is_list:
                                data__envArgs_len = len(data__envArgs)
                                for data__envArgs_x, data__envArgs_item in enumerate(data__envArgs):
                                    validate___definitions_envargsspec(data__envArgs_item, custom_formats)
                        if "volumes" in data_keys:
                            data_keys.remove("volumes")
                            data__volumes = data["volumes"]
                            if not isinstance(data__volumes, (list, tuple)):
                                raise JsonSchemaValueException("data.volumes must be array", value=data__volumes, name="data.volumes", definition={'type': 'array', 'items': {'$ref': '#/definitions/cloudVolumeAttachSpec'}}, rule='type')
                            data__volumes_is_list = isinstance(data__volumes, (list, tuple))
                            if data__volumes_is_list:
                                data__volumes_len = len(data__volumes)
                                for data__volumes_x, data__volumes_item in enumerate(data__volumes):
                                    validate___definitions_cloudvolumeattachspec(data__volumes_item, custom_formats)
                        if "staticRoutes" in data_keys:
                            data_keys.remove("staticRoutes")
                            data__staticRoutes = data["staticRoutes"]
                            if not isinstance(data__staticRoutes, (list, tuple)):
                                raise JsonSchemaValueException("data.staticRoutes must be array", value=data__staticRoutes, name="data.staticRoutes", definition={'type': 'array', 'items': {'$ref': '#/definitions/endpointSpec'}}, rule='type')
                            data__staticRoutes_is_list = isinstance(data__staticRoutes, (list, tuple))
                            if data__staticRoutes_is_list:
                                data__staticRoutes_len = len(data__staticRoutes)
                                for data__staticRoutes_x, data__staticRoutes_item in enumerate(data__staticRoutes):
                                    validate___definitions_endpointspec(data__staticRoutes_item, custom_formats)
                        if "rosNetworks" in data_keys:
                            data_keys.remove("rosNetworks")
                            data__rosNetworks = data["rosNetworks"]
                            if not isinstance(data__rosNetworks, (list, tuple)):
                                raise JsonSchemaValueException("data.rosNetworks must be array", value=data__rosNetworks, name="data.rosNetworks", definition={'type': 'array', 'items': {'$ref': '#/definitions/cloudNetworkAttachSpec'}}, rule='type')
                            data__rosNetworks_is_list = isinstance(data__rosNetworks, (list, tuple))
                            if data__rosNetworks_is_list:
                                data__rosNetworks_len = len(data__rosNetworks)
                                for data__rosNetworks_x, data__rosNetworks_item in enumerate(data__rosNetworks):
                                    validate___definitions_cloudnetworkattachspec(data__rosNetworks_item, custom_formats)
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 != 1:
                raise JsonSchemaValueException("data must be valid exactly by one of oneOf definition", value=data, name="data", definition={'oneOf': [{'properties': {'runtime': {'type': 'string', 'enum': ['device']}, 'depends': {'type': 'object', '$ref': '#/definitions/deviceDepends'}, 'restart': {'type': 'string', 'enum': ['always', 'onFailure', 'never'], 'default': 'always'}, 'envArgs': {'type': 'array', 'items': {'$ref': '#/definitions/envArgsSpec'}}, 'volumes': {'type': 'array', 'items': {'$ref': '#/definitions/deviceVolumeAttachSpec'}}, 'rosNetworks': {'type': 'array', 'items': {'$ref': '#/definitions/deviceNetworkAttachSpec'}}}}, {'properties': {'runtime': {'type': 'string', 'enum': ['cloud']}, 'envArgs': {'type': 'array', 'items': {'$ref': '#/definitions/envArgsSpec'}}, 'volumes': {'type': 'array', 'items': {'$ref': '#/definitions/cloudVolumeAttachSpec'}}, 'staticRoutes': {'type': 'array', 'items': {'$ref': '#/definitions/endpointSpec'}}, 'rosNetworks': {'type': 'array', 'items': {'$ref': '#/definitions/cloudNetworkAttachSpec'}}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "runtime" in data_keys:
            data_keys.remove("runtime")
            data__runtime = data["runtime"]
            if not isinstance(data__runtime, (str)):
                raise JsonSchemaValueException("data.runtime must be string", value=data__runtime, name="data.runtime", definition={'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, rule='type')
            if data__runtime not in ['device', 'cloud']:
                raise JsonSchemaValueException("data.runtime must be one of ['device', 'cloud']", value=data__runtime, name="data.runtime", definition={'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, rule='enum')
        else: data["runtime"] = 'cloud'
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            if not isinstance(data__depends, (list, tuple)):
                raise JsonSchemaValueException("data.depends must be array", value=data__depends, name="data.depends", definition={'type': 'array', 'items': {'$ref': '#/definitions/deploymentDepends'}}, rule='type')
            data__depends_is_list = isinstance(data__depends, (list, tuple))
            if data__depends_is_list:
                data__depends_len = len(data__depends)
                for data__depends_x, data__depends_item in enumerate(data__depends):
                    validate___definitions_deploymentdepends(data__depends_item, custom_formats)
    return data

def validate___definitions_deploymentdepends(data, custom_formats={}):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "deployment":
                raise JsonSchemaValueException("data.kind must be same as const definition: deployment", value=data__kind, name="data.kind", definition={'const': 'deployment', 'default': 'deployment'}, rule='const')
        else: data["kind"] = 'deployment'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("data.nameOrGUID must be string", value=data__nameOrGUID, name="data.nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("data.guid must be string", value=data__guid, name="data.guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_cloudnetworkattachspec(data, custom_formats={}):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_networkdepends(data__depends, custom_formats)
        if "topics" in data_keys:
            data_keys.remove("topics")
            data__topics = data["topics"]
            if not isinstance(data__topics, (list, tuple)):
                raise JsonSchemaValueException("data.topics must be array", value=data__topics, name="data.topics", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__topics_is_list = isinstance(data__topics, (list, tuple))
            if data__topics_is_list:
                data__topics_len = len(data__topics)
                for data__topics_x, data__topics_item in enumerate(data__topics):
                    if not isinstance(data__topics_item, (str)):
                        raise JsonSchemaValueException(""+"data.topics[{data__topics_x}]".format(**locals())+" must be string", value=data__topics_item, name=""+"data.topics[{data__topics_x}]".format(**locals())+"", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_networkdepends(data, custom_formats={}):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "network":
                raise JsonSchemaValueException("data.kind must be same as const definition: network", value=data__kind, name="data.kind", definition={'const': 'network', 'default': 'network'}, rule='const')
        else: data["kind"] = 'network'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("data.nameOrGUID must be string", value=data__nameOrGUID, name="data.nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("data.guid must be string", value=data__guid, name="data.guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_endpointspec(data, custom_formats={}):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("data.name must be string", value=data__name, name="data.name", definition={'type': 'string'}, rule='type')
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
                        raise JsonSchemaValueException("data.depends.kind must be same as const definition: staticroute", value=data__depends__kind, name="data.depends.kind", definition={'const': 'staticroute', 'default': 'staticroute'}, rule='const')
                else: data__depends["kind"] = 'staticroute'
                if "nameOrGUID" in data__depends_keys:
                    data__depends_keys.remove("nameOrGUID")
                    data__depends__nameOrGUID = data__depends["nameOrGUID"]
                    if not isinstance(data__depends__nameOrGUID, (str)):
                        raise JsonSchemaValueException("data.depends.nameOrGUID must be string", value=data__depends__nameOrGUID, name="data.depends.nameOrGUID", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_cloudvolumeattachspec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'execName': {'type': 'string'}, 'mountPath': {'type': 'string'}, 'subPath': {'type': 'string'}, 'depends': {'$ref': '#/definitions/diskDepends'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "execName" in data_keys:
            data_keys.remove("execName")
            data__execName = data["execName"]
            if not isinstance(data__execName, (str)):
                raise JsonSchemaValueException("data.execName must be string", value=data__execName, name="data.execName", definition={'type': 'string'}, rule='type')
        if "mountPath" in data_keys:
            data_keys.remove("mountPath")
            data__mountPath = data["mountPath"]
            if not isinstance(data__mountPath, (str)):
                raise JsonSchemaValueException("data.mountPath must be string", value=data__mountPath, name="data.mountPath", definition={'type': 'string'}, rule='type')
        if "subPath" in data_keys:
            data_keys.remove("subPath")
            data__subPath = data["subPath"]
            if not isinstance(data__subPath, (str)):
                raise JsonSchemaValueException("data.subPath must be string", value=data__subPath, name="data.subPath", definition={'type': 'string'}, rule='type')
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_diskdepends(data__depends, custom_formats)
    return data

def validate___definitions_diskdepends(data, custom_formats={}):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "disk":
                raise JsonSchemaValueException("data.kind must be same as const definition: disk", value=data__kind, name="data.kind", definition={'const': 'disk', 'default': 'disk'}, rule='const')
        else: data["kind"] = 'disk'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("data.nameOrGUID must be string", value=data__nameOrGUID, name="data.nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("data.guid must be string", value=data__guid, name="data.guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_devicenetworkattachspec(data, custom_formats={}):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_networkdepends(data__depends, custom_formats)
        if "interface" in data_keys:
            data_keys.remove("interface")
            data__interface = data["interface"]
            if not isinstance(data__interface, (str)):
                raise JsonSchemaValueException("data.interface must be string", value=data__interface, name="data.interface", definition={'type': 'string'}, rule='type')
        if "topics" in data_keys:
            data_keys.remove("topics")
            data__topics = data["topics"]
            if not isinstance(data__topics, (list, tuple)):
                raise JsonSchemaValueException("data.topics must be array", value=data__topics, name="data.topics", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__topics_is_list = isinstance(data__topics, (list, tuple))
            if data__topics_is_list:
                data__topics_len = len(data__topics)
                for data__topics_x, data__topics_item in enumerate(data__topics):
                    if not isinstance(data__topics_item, (str)):
                        raise JsonSchemaValueException(""+"data.topics[{data__topics_x}]".format(**locals())+" must be string", value=data__topics_item, name=""+"data.topics[{data__topics_x}]".format(**locals())+"", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_devicevolumeattachspec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'execName': {'type': 'string'}, 'mountPath': {'type': 'string'}, 'subPath': {'type': 'string'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "execName" in data_keys:
            data_keys.remove("execName")
            data__execName = data["execName"]
            if not isinstance(data__execName, (str)):
                raise JsonSchemaValueException("data.execName must be string", value=data__execName, name="data.execName", definition={'type': 'string'}, rule='type')
        if "mountPath" in data_keys:
            data_keys.remove("mountPath")
            data__mountPath = data["mountPath"]
            if not isinstance(data__mountPath, (str)):
                raise JsonSchemaValueException("data.mountPath must be string", value=data__mountPath, name="data.mountPath", definition={'type': 'string'}, rule='type')
        if "subPath" in data_keys:
            data_keys.remove("subPath")
            data__subPath = data["subPath"]
            if not isinstance(data__subPath, (str)):
                raise JsonSchemaValueException("data.subPath must be string", value=data__subPath, name="data.subPath", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_envargsspec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'value': {'type': 'string'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("data.name must be string", value=data__name, name="data.name", definition={'type': 'string'}, rule='type')
        if "value" in data_keys:
            data_keys.remove("value")
            data__value = data["value"]
            if not isinstance(data__value, (str)):
                raise JsonSchemaValueException("data.value must be string", value=data__value, name="data.value", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_devicedepends(data, custom_formats={}):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "device":
                raise JsonSchemaValueException("data.kind must be same as const definition: device", value=data__kind, name="data.kind", definition={'const': 'device', 'default': 'device'}, rule='const')
        else: data["kind"] = 'device'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("data.nameOrGUID must be string", value=data__nameOrGUID, name="data.nameOrGUID", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("data.guid must be string", value=data__guid, name="data.guid", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_metadata(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'depends': {'$ref': '#/definitions/packageDepends'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}, 'guid': {'$ref': '#/definitions/packageGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}}, 'required': ['name', 'depends']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name', 'depends']):
            raise JsonSchemaValueException("data must contain ['name', 'depends'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'depends': {'$ref': '#/definitions/packageDepends'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}, 'guid': {'$ref': '#/definitions/packageGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}}, 'required': ['name', 'depends']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("data.name must be string", value=data__name, name="data.name", definition={'type': 'string'}, rule='type')
        if "depends" in data_keys:
            data_keys.remove("depends")
            data__depends = data["depends"]
            validate___definitions_packagedepends(data__depends, custom_formats)
        if "labels" in data_keys:
            data_keys.remove("labels")
            data__labels = data["labels"]
            validate___definitions_stringmap(data__labels, custom_formats)
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_packageguid(data__guid, custom_formats)
        if "creator" in data_keys:
            data_keys.remove("creator")
            data__creator = data["creator"]
            validate___definitions_uuid(data__creator, custom_formats)
        if "project" in data_keys:
            data_keys.remove("project")
            data__project = data["project"]
            validate___definitions_projectguid(data__project, custom_formats)
    return data

def validate___definitions_projectguid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^project-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^project-[a-z]{24}$", value=data, name="data", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='pattern')
    return data

def validate___definitions_uuid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data

def validate___definitions_packageguid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^pkg-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^pkg-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^pkg-[a-z]{24}$", value=data, name="data", definition={'type': 'string', 'pattern': '^pkg-[a-z]{24}$'}, rule='pattern')
    return data

def validate___definitions_stringmap(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'additionalProperties': {'type': 'string'}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        for data_key in data_keys:
            if data_key not in []:
                data_value = data.get(data_key)
                if not isinstance(data_value, (str)):
                    raise JsonSchemaValueException(""+"data.{data_key}".format(**locals())+" must be string", value=data_value, name=""+"data.{data_key}".format(**locals())+"", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_packagedepends(data, custom_formats={}):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "package":
                raise JsonSchemaValueException("data.kind must be same as const definition: package", value=data__kind, name="data.kind", definition={'const': 'package', 'default': 'package'}, rule='const')
        else: data["kind"] = 'package'
        if "nameOrGUID" in data_keys:
            data_keys.remove("nameOrGUID")
            data__nameOrGUID = data["nameOrGUID"]
            if not isinstance(data__nameOrGUID, (str)):
                raise JsonSchemaValueException("data.nameOrGUID must be string", value=data__nameOrGUID, name="data.nameOrGUID", definition={'type': 'string'}, rule='type')
        if "version" in data_keys:
            data_keys.remove("version")
            data__version = data["version"]
            if not isinstance(data__version, (str)):
                raise JsonSchemaValueException("data.version must be string", value=data__version, name="data.version", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            if not isinstance(data__guid, (str)):
                raise JsonSchemaValueException("data.guid must be string", value=data__guid, name="data.guid", definition={'type': 'string'}, rule='type')
    return data