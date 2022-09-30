VERSION = "2.16.1"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^pkg-[a-z]{24}$': re.compile('^pkg-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}, name_prefix=None):
    validate___definitions_package(data, custom_formats, (name_prefix or "data") + "")
    return data

def validate___definitions_package(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Package', 'default': 'Package'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'version': {'type': 'string'}, 'tag': {'type': 'string'}, 'description': {'type': 'string'}, 'guid': {'$ref': '#/definitions/packageGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name', 'version']}, 'spec': {'type': 'object', 'properties': {'runtime': {'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, 'ros': {'type': 'object', '$ref': '#/definitions/rosComponentSpec'}}, 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['device']}, 'device': {'type': 'object', '$ref': '#/definitions/deviceComponentInfoSpec'}, 'executables': {'type': 'array', 'items': {'$ref': '#/definitions/deviceExecutableSpec'}}, 'environmentArgs': {'type': 'array', 'items': {'$ref': '#/definitions/environmentSpec'}}}}, {'properties': {'runtime': {'enum': ['cloud']}, 'cloud': {'type': 'object', '$ref': '#/definitions/cloudComponentInfoSpec'}, 'executables': {'type': 'array', 'items': {'$ref': '#/definitions/cloudExecutableSpec'}}, 'environmentVars': {'type': 'array', 'items': {'$ref': '#/definitions/environmentSpec'}}, 'endpoints': {'type': 'array', 'items': {'$ref': '#/definitions/endpointSpec'}}}}]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Package', 'default': 'Package'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'version': {'type': 'string'}, 'tag': {'type': 'string'}, 'description': {'type': 'string'}, 'guid': {'$ref': '#/definitions/packageGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name', 'version']}, 'spec': {'type': 'object', 'properties': {'runtime': {'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, 'ros': {'type': 'object', '$ref': '#/definitions/rosComponentSpec'}}, 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['device']}, 'device': {'type': 'object', '$ref': '#/definitions/deviceComponentInfoSpec'}, 'executables': {'type': 'array', 'items': {'$ref': '#/definitions/deviceExecutableSpec'}}, 'environmentArgs': {'type': 'array', 'items': {'$ref': '#/definitions/environmentSpec'}}}}, {'properties': {'runtime': {'enum': ['cloud']}, 'cloud': {'type': 'object', '$ref': '#/definitions/cloudComponentInfoSpec'}, 'executables': {'type': 'array', 'items': {'$ref': '#/definitions/cloudExecutableSpec'}}, 'environmentVars': {'type': 'array', 'items': {'$ref': '#/definitions/environmentSpec'}}, 'endpoints': {'type': 'array', 'items': {'$ref': '#/definitions/endpointSpec'}}}}]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
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
            if data__kind != "Package":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: Package", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'Package', 'default': 'Package'}, rule='const')
        else: data["kind"] = 'Package'
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
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'runtime': {'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, 'ros': {'type': 'object', 'properties': {'enabled': {'type': 'boolean', 'default': False}}, 'dependencies': {'enabled': {'oneOf': [{'properties': {'enabled': {'enum': [False]}}}, {'properties': {'enabled': {'type': 'boolean', 'enum': [True]}, 'version': {'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, 'inboundScopedTargeted': {'type': 'boolean', 'default': False}, 'rosEndpoints': {'type': 'array', 'items': {'$ref': '#/definitions/rosEndpointSpec'}}}}]}}}}, 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['device']}, 'device': {'type': 'object', 'properties': {'arch': {'type': 'string', 'enum': ['arm32v7', 'arm64v8', 'amd64'], 'default': 'amd64'}, 'restart': {'type': 'string', 'default': 'always', 'enum': ['always', 'never', 'onfailure']}}}, 'executables': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'$ref': '#/definitions/secretDepends'}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/buildDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, 'environmentArgs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}}}, {'properties': {'runtime': {'enum': ['cloud']}, 'cloud': {'type': 'object', 'properties': {'replicas': {'type': 'number', 'default': 1}}}, 'executables': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32678}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, 'environmentVars': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}, 'endpoints': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}}}}]}}}, rule='type')
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
                            if data__runtime not in ['device']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be one of ['device']", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'enum': ['device']}, rule='enum')
                        if "device" in data_keys:
                            data_keys.remove("device")
                            data__device = data["device"]
                            validate___definitions_devicecomponentinfospec(data__device, custom_formats, (name_prefix or "data") + ".device")
                        if "executables" in data_keys:
                            data_keys.remove("executables")
                            data__executables = data["executables"]
                            if not isinstance(data__executables, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".executables must be array", value=data__executables, name="" + (name_prefix or "data") + ".executables", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'$ref': '#/definitions/secretDepends'}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/buildDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, rule='type')
                            data__executables_is_list = isinstance(data__executables, (list, tuple))
                            if data__executables_is_list:
                                data__executables_len = len(data__executables)
                                for data__executables_x, data__executables_item in enumerate(data__executables):
                                    validate___definitions_deviceexecutablespec(data__executables_item, custom_formats, (name_prefix or "data") + ".executables[{data__executables_x}]")
                        if "environmentArgs" in data_keys:
                            data_keys.remove("environmentArgs")
                            data__environmentArgs = data["environmentArgs"]
                            if not isinstance(data__environmentArgs, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".environmentArgs must be array", value=data__environmentArgs, name="" + (name_prefix or "data") + ".environmentArgs", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}, rule='type')
                            data__environmentArgs_is_list = isinstance(data__environmentArgs, (list, tuple))
                            if data__environmentArgs_is_list:
                                data__environmentArgs_len = len(data__environmentArgs)
                                for data__environmentArgs_x, data__environmentArgs_item in enumerate(data__environmentArgs):
                                    validate___definitions_environmentspec(data__environmentArgs_item, custom_formats, (name_prefix or "data") + ".environmentArgs[{data__environmentArgs_x}]")
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
                            if data__runtime not in ['cloud']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be one of ['cloud']", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'enum': ['cloud']}, rule='enum')
                        if "cloud" in data_keys:
                            data_keys.remove("cloud")
                            data__cloud = data["cloud"]
                            validate___definitions_cloudcomponentinfospec(data__cloud, custom_formats, (name_prefix or "data") + ".cloud")
                        if "executables" in data_keys:
                            data_keys.remove("executables")
                            data__executables = data["executables"]
                            if not isinstance(data__executables, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".executables must be array", value=data__executables, name="" + (name_prefix or "data") + ".executables", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32678}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, rule='type')
                            data__executables_is_list = isinstance(data__executables, (list, tuple))
                            if data__executables_is_list:
                                data__executables_len = len(data__executables)
                                for data__executables_x, data__executables_item in enumerate(data__executables):
                                    validate___definitions_cloudexecutablespec(data__executables_item, custom_formats, (name_prefix or "data") + ".executables[{data__executables_x}]")
                        if "environmentVars" in data_keys:
                            data_keys.remove("environmentVars")
                            data__environmentVars = data["environmentVars"]
                            if not isinstance(data__environmentVars, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".environmentVars must be array", value=data__environmentVars, name="" + (name_prefix or "data") + ".environmentVars", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}, rule='type')
                            data__environmentVars_is_list = isinstance(data__environmentVars, (list, tuple))
                            if data__environmentVars_is_list:
                                data__environmentVars_len = len(data__environmentVars)
                                for data__environmentVars_x, data__environmentVars_item in enumerate(data__environmentVars):
                                    validate___definitions_environmentspec(data__environmentVars_item, custom_formats, (name_prefix or "data") + ".environmentVars[{data__environmentVars_x}]")
                        if "endpoints" in data_keys:
                            data_keys.remove("endpoints")
                            data__endpoints = data["endpoints"]
                            if not isinstance(data__endpoints, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".endpoints must be array", value=data__endpoints, name="" + (name_prefix or "data") + ".endpoints", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}}, rule='type')
                            data__endpoints_is_list = isinstance(data__endpoints, (list, tuple))
                            if data__endpoints_is_list:
                                data__endpoints_len = len(data__endpoints)
                                for data__endpoints_x, data__endpoints_item in enumerate(data__endpoints):
                                    validate___definitions_endpointspec(data__endpoints_item, custom_formats, (name_prefix or "data") + ".endpoints[{data__endpoints_x}]")
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count1) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'runtime': {'enum': ['device']}, 'device': {'type': 'object', 'properties': {'arch': {'type': 'string', 'enum': ['arm32v7', 'arm64v8', 'amd64'], 'default': 'amd64'}, 'restart': {'type': 'string', 'default': 'always', 'enum': ['always', 'never', 'onfailure']}}}, 'executables': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'$ref': '#/definitions/secretDepends'}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/buildDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, 'environmentArgs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}}}, {'properties': {'runtime': {'enum': ['cloud']}, 'cloud': {'type': 'object', 'properties': {'replicas': {'type': 'number', 'default': 1}}}, 'executables': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32678}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, 'environmentVars': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}, 'endpoints': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "runtime" in data_keys:
            data_keys.remove("runtime")
            data__runtime = data["runtime"]
            if not isinstance(data__runtime, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be string", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, rule='type')
            if data__runtime not in ['device', 'cloud']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be one of ['device', 'cloud']", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, rule='enum')
        else: data["runtime"] = 'cloud'
        if "ros" in data_keys:
            data_keys.remove("ros")
            data__ros = data["ros"]
            validate___definitions_roscomponentspec(data__ros, custom_formats, (name_prefix or "data") + ".ros")
    return data

def validate___definitions_roscomponentspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'enabled': {'type': 'boolean', 'default': False}}, 'dependencies': {'enabled': {'oneOf': [{'properties': {'enabled': {'enum': [False]}}}, {'properties': {'enabled': {'type': 'boolean', 'enum': [True]}, 'version': {'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, 'inboundScopedTargeted': {'type': 'boolean', 'default': False}, 'rosEndpoints': {'type': 'array', 'items': {'type': 'object', 'properties': {'type': {'type': 'string', 'default': 'topic', 'enum': ['topic', 'service', 'action']}, 'name': {'type': 'string'}, 'compression': {'type': 'boolean', 'default': False}, 'scoped': {'type': 'boolean', 'default': False}, 'targeted': {'type': 'boolean', 'default': False}}, 'required': ['type', 'name'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['topic']}, 'qos': {'type': 'string', 'enum': ['low', 'medium', 'hi', 'max'], 'default': 'low'}}}, {'properties': {'type': {'enum': ['service']}, 'timeout': {'type': 'number', 'default': 120, 'min': 0}}}, {'properties': {'type': {'enum': ['action']}}}]}}}}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        if "enabled" in data:
            data_one_of_count2 = 0
            if data_one_of_count2 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "enabled" in data_keys:
                            data_keys.remove("enabled")
                            data__enabled = data["enabled"]
                            if data__enabled not in [False]:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".enabled must be one of [False]", value=data__enabled, name="" + (name_prefix or "data") + ".enabled", definition={'enum': [False]}, rule='enum')
                    data_one_of_count2 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count2 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "enabled" in data_keys:
                            data_keys.remove("enabled")
                            data__enabled = data["enabled"]
                            if not isinstance(data__enabled, (bool)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".enabled must be boolean", value=data__enabled, name="" + (name_prefix or "data") + ".enabled", definition={'type': 'boolean', 'enum': [True]}, rule='type')
                            if data__enabled not in [True]:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".enabled must be one of [True]", value=data__enabled, name="" + (name_prefix or "data") + ".enabled", definition={'type': 'boolean', 'enum': [True]}, rule='enum')
                        if "version" in data_keys:
                            data_keys.remove("version")
                            data__version = data["version"]
                            if not isinstance(data__version, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".version must be string", value=data__version, name="" + (name_prefix or "data") + ".version", definition={'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, rule='type')
                            if data__version not in ['kinetic', 'melodic', 'noetic']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".version must be one of ['kinetic', 'melodic', 'noetic']", value=data__version, name="" + (name_prefix or "data") + ".version", definition={'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, rule='enum')
                        else: data["version"] = 'melodic'
                        if "inboundScopedTargeted" in data_keys:
                            data_keys.remove("inboundScopedTargeted")
                            data__inboundScopedTargeted = data["inboundScopedTargeted"]
                            if not isinstance(data__inboundScopedTargeted, (bool)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".inboundScopedTargeted must be boolean", value=data__inboundScopedTargeted, name="" + (name_prefix or "data") + ".inboundScopedTargeted", definition={'type': 'boolean', 'default': False}, rule='type')
                        else: data["inboundScopedTargeted"] = False
                        if "rosEndpoints" in data_keys:
                            data_keys.remove("rosEndpoints")
                            data__rosEndpoints = data["rosEndpoints"]
                            if not isinstance(data__rosEndpoints, (list, tuple)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".rosEndpoints must be array", value=data__rosEndpoints, name="" + (name_prefix or "data") + ".rosEndpoints", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'type': {'type': 'string', 'default': 'topic', 'enum': ['topic', 'service', 'action']}, 'name': {'type': 'string'}, 'compression': {'type': 'boolean', 'default': False}, 'scoped': {'type': 'boolean', 'default': False}, 'targeted': {'type': 'boolean', 'default': False}}, 'required': ['type', 'name'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['topic']}, 'qos': {'type': 'string', 'enum': ['low', 'medium', 'hi', 'max'], 'default': 'low'}}}, {'properties': {'type': {'enum': ['service']}, 'timeout': {'type': 'number', 'default': 120, 'min': 0}}}, {'properties': {'type': {'enum': ['action']}}}]}}}}, rule='type')
                            data__rosEndpoints_is_list = isinstance(data__rosEndpoints, (list, tuple))
                            if data__rosEndpoints_is_list:
                                data__rosEndpoints_len = len(data__rosEndpoints)
                                for data__rosEndpoints_x, data__rosEndpoints_item in enumerate(data__rosEndpoints):
                                    validate___definitions_rosendpointspec(data__rosEndpoints_item, custom_formats, (name_prefix or "data") + ".rosEndpoints[{data__rosEndpoints_x}]")
                    data_one_of_count2 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count2 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count2) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'enabled': {'enum': [False]}}}, {'properties': {'enabled': {'type': 'boolean', 'enum': [True]}, 'version': {'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, 'inboundScopedTargeted': {'type': 'boolean', 'default': False}, 'rosEndpoints': {'type': 'array', 'items': {'type': 'object', 'properties': {'type': {'type': 'string', 'default': 'topic', 'enum': ['topic', 'service', 'action']}, 'name': {'type': 'string'}, 'compression': {'type': 'boolean', 'default': False}, 'scoped': {'type': 'boolean', 'default': False}, 'targeted': {'type': 'boolean', 'default': False}}, 'required': ['type', 'name'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['topic']}, 'qos': {'type': 'string', 'enum': ['low', 'medium', 'hi', 'max'], 'default': 'low'}}}, {'properties': {'type': {'enum': ['service']}, 'timeout': {'type': 'number', 'default': 120, 'min': 0}}}, {'properties': {'type': {'enum': ['action']}}}]}}}}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "enabled" in data_keys:
            data_keys.remove("enabled")
            data__enabled = data["enabled"]
            if not isinstance(data__enabled, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".enabled must be boolean", value=data__enabled, name="" + (name_prefix or "data") + ".enabled", definition={'type': 'boolean', 'default': False}, rule='type')
        else: data["enabled"] = False
    return data

def validate___definitions_rosendpointspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'type': {'type': 'string', 'default': 'topic', 'enum': ['topic', 'service', 'action']}, 'name': {'type': 'string'}, 'compression': {'type': 'boolean', 'default': False}, 'scoped': {'type': 'boolean', 'default': False}, 'targeted': {'type': 'boolean', 'default': False}}, 'required': ['type', 'name'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['topic']}, 'qos': {'type': 'string', 'enum': ['low', 'medium', 'hi', 'max'], 'default': 'low'}}}, {'properties': {'type': {'enum': ['service']}, 'timeout': {'type': 'number', 'default': 120, 'min': 0}}}, {'properties': {'type': {'enum': ['action']}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['type', 'name']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['type', 'name'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'type': {'type': 'string', 'default': 'topic', 'enum': ['topic', 'service', 'action']}, 'name': {'type': 'string'}, 'compression': {'type': 'boolean', 'default': False}, 'scoped': {'type': 'boolean', 'default': False}, 'targeted': {'type': 'boolean', 'default': False}}, 'required': ['type', 'name'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['topic']}, 'qos': {'type': 'string', 'enum': ['low', 'medium', 'hi', 'max'], 'default': 'low'}}}, {'properties': {'type': {'enum': ['service']}, 'timeout': {'type': 'number', 'default': 120, 'min': 0}}}, {'properties': {'type': {'enum': ['action']}}}]}}}, rule='required')
        if "type" in data:
            data_one_of_count3 = 0
            if data_one_of_count3 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['topic']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['topic']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['topic']}, rule='enum')
                        if "qos" in data_keys:
                            data_keys.remove("qos")
                            data__qos = data["qos"]
                            if not isinstance(data__qos, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".qos must be string", value=data__qos, name="" + (name_prefix or "data") + ".qos", definition={'type': 'string', 'enum': ['low', 'medium', 'hi', 'max'], 'default': 'low'}, rule='type')
                            if data__qos not in ['low', 'medium', 'hi', 'max']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".qos must be one of ['low', 'medium', 'hi', 'max']", value=data__qos, name="" + (name_prefix or "data") + ".qos", definition={'type': 'string', 'enum': ['low', 'medium', 'hi', 'max'], 'default': 'low'}, rule='enum')
                        else: data["qos"] = 'low'
                    data_one_of_count3 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count3 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['service']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['service']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['service']}, rule='enum')
                        if "timeout" in data_keys:
                            data_keys.remove("timeout")
                            data__timeout = data["timeout"]
                            if not isinstance(data__timeout, (int, float)) or isinstance(data__timeout, bool):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeout must be number", value=data__timeout, name="" + (name_prefix or "data") + ".timeout", definition={'type': 'number', 'default': 120, 'min': 0}, rule='type')
                        else: data["timeout"] = 120
                    data_one_of_count3 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count3 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['action']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['action']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['action']}, rule='enum')
                    data_one_of_count3 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count3 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count3) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'type': {'enum': ['topic']}, 'qos': {'type': 'string', 'enum': ['low', 'medium', 'hi', 'max'], 'default': 'low'}}}, {'properties': {'type': {'enum': ['service']}, 'timeout': {'type': 'number', 'default': 120, 'min': 0}}}, {'properties': {'type': {'enum': ['action']}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "type" in data_keys:
            data_keys.remove("type")
            data__type = data["type"]
            if not isinstance(data__type, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be string", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'type': 'string', 'default': 'topic', 'enum': ['topic', 'service', 'action']}, rule='type')
            if data__type not in ['topic', 'service', 'action']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['topic', 'service', 'action']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'type': 'string', 'default': 'topic', 'enum': ['topic', 'service', 'action']}, rule='enum')
        else: data["type"] = 'topic'
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "compression" in data_keys:
            data_keys.remove("compression")
            data__compression = data["compression"]
            if not isinstance(data__compression, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".compression must be boolean", value=data__compression, name="" + (name_prefix or "data") + ".compression", definition={'type': 'boolean', 'default': False}, rule='type')
        else: data["compression"] = False
        if "scoped" in data_keys:
            data_keys.remove("scoped")
            data__scoped = data["scoped"]
            if not isinstance(data__scoped, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".scoped must be boolean", value=data__scoped, name="" + (name_prefix or "data") + ".scoped", definition={'type': 'boolean', 'default': False}, rule='type')
        else: data["scoped"] = False
        if "targeted" in data_keys:
            data_keys.remove("targeted")
            data__targeted = data["targeted"]
            if not isinstance(data__targeted, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".targeted must be boolean", value=data__targeted, name="" + (name_prefix or "data") + ".targeted", definition={'type': 'boolean', 'default': False}, rule='type')
        else: data["targeted"] = False
    return data

def validate___definitions_endpointspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name', 'type']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name', 'type'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}, rule='required')
        if "type" in data:
            data_one_of_count4 = 0
            if data_one_of_count4 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['port', 'targetPort']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['port', 'targetPort'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'type': {'enum': ['external-http']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, rule='required')
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['external-http']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['external-http']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['external-http']}, rule='enum')
                        if "port" in data_keys:
                            data_keys.remove("port")
                            data__port = data["port"]
                            validate___definitions_portnumber(data__port, custom_formats, (name_prefix or "data") + ".port")
                        else: data["port"] = 80
                        if "targetPort" in data_keys:
                            data_keys.remove("targetPort")
                            data__targetPort = data["targetPort"]
                            validate___definitions_portnumber(data__targetPort, custom_formats, (name_prefix or "data") + ".targetPort")
                    data_one_of_count4 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count4 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['port', 'targetPort']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['port', 'targetPort'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'type': {'enum': ['external-https']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, rule='required')
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['external-https']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['external-https']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['external-https']}, rule='enum')
                        if "port" in data_keys:
                            data_keys.remove("port")
                            data__port = data["port"]
                            validate___definitions_portnumber(data__port, custom_formats, (name_prefix or "data") + ".port")
                        else: data["port"] = 443
                        if "targetPort" in data_keys:
                            data_keys.remove("targetPort")
                            data__targetPort = data["targetPort"]
                            validate___definitions_portnumber(data__targetPort, custom_formats, (name_prefix or "data") + ".targetPort")
                    data_one_of_count4 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count4 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['port', 'targetPort']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['port', 'targetPort'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, rule='required')
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['external-tls-tcp']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['external-tls-tcp']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['external-tls-tcp']}, rule='enum')
                        if "port" in data_keys:
                            data_keys.remove("port")
                            data__port = data["port"]
                            validate___definitions_portnumber(data__port, custom_formats, (name_prefix or "data") + ".port")
                        else: data["port"] = 443
                        if "targetPort" in data_keys:
                            data_keys.remove("targetPort")
                            data__targetPort = data["targetPort"]
                            validate___definitions_portnumber(data__targetPort, custom_formats, (name_prefix or "data") + ".targetPort")
                    data_one_of_count4 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count4 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['port', 'targetPort']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['port', 'targetPort'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, rule='required')
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['internal-tcp']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['internal-tcp']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['internal-tcp']}, rule='enum')
                        if "port" in data_keys:
                            data_keys.remove("port")
                            data__port = data["port"]
                            validate___definitions_portnumber(data__port, custom_formats, (name_prefix or "data") + ".port")
                        else: data["port"] = 80
                        if "targetPort" in data_keys:
                            data_keys.remove("targetPort")
                            data__targetPort = data["targetPort"]
                            validate___definitions_portnumber(data__targetPort, custom_formats, (name_prefix or "data") + ".targetPort")
                    data_one_of_count4 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count4 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['port', 'targetPort']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['port', 'targetPort'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'type': {'enum': ['internal-udp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, rule='required')
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['internal-udp']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['internal-udp']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['internal-udp']}, rule='enum')
                        if "port" in data_keys:
                            data_keys.remove("port")
                            data__port = data["port"]
                            validate___definitions_portnumber(data__port, custom_formats, (name_prefix or "data") + ".port")
                        else: data["port"] = 80
                        if "targetPort" in data_keys:
                            data_keys.remove("targetPort")
                            data__targetPort = data["targetPort"]
                            validate___definitions_portnumber(data__targetPort, custom_formats, (name_prefix or "data") + ".targetPort")
                    data_one_of_count4 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count4 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['portRange']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['portRange'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, rule='required')
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['internal-tcp-range']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['internal-tcp-range']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['internal-tcp-range']}, rule='enum')
                        if "portRange" in data_keys:
                            data_keys.remove("portRange")
                            data__portRange = data["portRange"]
                            if not isinstance(data__portRange, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".portRange must be string", value=data__portRange, name="" + (name_prefix or "data") + ".portRange", definition={'type': 'string', 'default': '22,80, 1024-1030'}, rule='type')
                        else: data["portRange"] = '22,80, 1024-1030'
                    data_one_of_count4 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count4 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['portRange']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['portRange'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}, rule='required')
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['internal-udp-range']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['internal-udp-range']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['internal-udp-range']}, rule='enum')
                        if "portRange" in data_keys:
                            data_keys.remove("portRange")
                            data__portRange = data["portRange"]
                            if not isinstance(data__portRange, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".portRange must be string", value=data__portRange, name="" + (name_prefix or "data") + ".portRange", definition={'type': 'string', 'default': '53,1024-1025'}, rule='type')
                        else: data["portRange"] = '53,1024-1025'
                    data_one_of_count4 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count4 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count4) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "type" in data_keys:
            data_keys.remove("type")
            data__type = data["type"]
            if not isinstance(data__type, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be string", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}, rule='type')
            if data__type not in ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}, rule='enum')
        else: data["type"] = 'external-http'
    return data

def validate___definitions_portnumber(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (int)) and not (isinstance(data, float) and data.is_integer()) or isinstance(data, bool):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be integer", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'integer', 'min': 1, 'max': 65531}, rule='type')
    return data

def validate___definitions_cloudexecutablespec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32678}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['type']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['type'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32678}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}, rule='required')
        if "type" in data:
            data_one_of_count5 = 0
            if data_one_of_count5 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['docker']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['docker']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['docker']}, rule='enum')
                        if "docker" in data_keys:
                            data_keys.remove("docker")
                            data__docker = data["docker"]
                            if not isinstance(data__docker, (dict)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".docker must be object", value=data__docker, name="" + (name_prefix or "data") + ".docker", definition={'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}, 'required': ['image']}, rule='type')
                            data__docker_is_dict = isinstance(data__docker, dict)
                            if data__docker_is_dict:
                                data__docker_len = len(data__docker)
                                if not all(prop in data__docker for prop in ['image']):
                                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".docker must contain ['image'] properties", value=data__docker, name="" + (name_prefix or "data") + ".docker", definition={'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}, 'required': ['image']}, rule='required')
                                data__docker_keys = set(data__docker.keys())
                                if "image" in data__docker_keys:
                                    data__docker_keys.remove("image")
                                    data__docker__image = data__docker["image"]
                                    if not isinstance(data__docker__image, (str)):
                                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".docker.image must be string", value=data__docker__image, name="" + (name_prefix or "data") + ".docker.image", definition={'type': 'string'}, rule='type')
                                if "pullSecret" in data__docker_keys:
                                    data__docker_keys.remove("pullSecret")
                                    data__docker__pullSecret = data__docker["pullSecret"]
                                    if not isinstance(data__docker__pullSecret, (dict)):
                                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".docker.pullSecret must be object", value=data__docker__pullSecret, name="" + (name_prefix or "data") + ".docker.pullSecret", definition={'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}, rule='type')
                                    data__docker__pullSecret_is_dict = isinstance(data__docker__pullSecret, dict)
                                    if data__docker__pullSecret_is_dict:
                                        data__docker__pullSecret_len = len(data__docker__pullSecret)
                                        if not all(prop in data__docker__pullSecret for prop in ['depends']):
                                            raise JsonSchemaValueException("" + (name_prefix or "data") + ".docker.pullSecret must contain ['depends'] properties", value=data__docker__pullSecret, name="" + (name_prefix or "data") + ".docker.pullSecret", definition={'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}, rule='required')
                                        data__docker__pullSecret_keys = set(data__docker__pullSecret.keys())
                                        if "depends" in data__docker__pullSecret_keys:
                                            data__docker__pullSecret_keys.remove("depends")
                                            data__docker__pullSecret__depends = data__docker__pullSecret["depends"]
                                            validate___definitions_secretdepends(data__docker__pullSecret__depends, custom_formats, (name_prefix or "data") + ".docker.pullSecret.depends")
                    data_one_of_count5 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count5 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['build']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['build']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['build']}, rule='enum')
                        if "build" in data_keys:
                            data_keys.remove("build")
                            data__build = data["build"]
                            if not isinstance(data__build, (dict)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".build must be object", value=data__build, name="" + (name_prefix or "data") + ".build", definition={'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}, rule='type')
                            data__build_is_dict = isinstance(data__build, dict)
                            if data__build_is_dict:
                                data__build_len = len(data__build)
                                if not all(prop in data__build for prop in ['depends']):
                                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".build must contain ['depends'] properties", value=data__build, name="" + (name_prefix or "data") + ".build", definition={'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}, rule='required')
                                data__build_keys = set(data__build.keys())
                                if "depends" in data__build_keys:
                                    data__build_keys.remove("depends")
                                    data__build__depends = data__build["depends"]
                                    validate___definitions_secretdepends(data__build__depends, custom_formats, (name_prefix or "data") + ".build.depends")
                    data_one_of_count5 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count5 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['preInstalled']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['preInstalled']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['preInstalled']}, rule='enum')
                    data_one_of_count5 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count5 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count5) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "type" in data_keys:
            data_keys.remove("type")
            data__type = data["type"]
            if not isinstance(data__type, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be string", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, rule='type')
            if data__type not in ['docker', 'build']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['docker', 'build']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, rule='enum')
        else: data["type"] = 'docker'
        if "command" in data_keys:
            data_keys.remove("command")
            data__command = data["command"]
            if not isinstance(data__command, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".command must be string", value=data__command, name="" + (name_prefix or "data") + ".command", definition={'type': 'string'}, rule='type')
        if "runAsBash" in data_keys:
            data_keys.remove("runAsBash")
            data__runAsBash = data["runAsBash"]
            if not isinstance(data__runAsBash, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runAsBash must be boolean", value=data__runAsBash, name="" + (name_prefix or "data") + ".runAsBash", definition={'type': 'boolean', 'default': True}, rule='type')
        else: data["runAsBash"] = True
        if "simulation" in data_keys:
            data_keys.remove("simulation")
            data__simulation = data["simulation"]
            if not isinstance(data__simulation, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".simulation must be boolean", value=data__simulation, name="" + (name_prefix or "data") + ".simulation", definition={'type': 'boolean', 'default': False}, rule='type')
        else: data["simulation"] = False
        if "limits" in data_keys:
            data_keys.remove("limits")
            data__limits = data["limits"]
            if not isinstance(data__limits, (dict)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".limits must be object", value=data__limits, name="" + (name_prefix or "data") + ".limits", definition={'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32678}}}, rule='type')
            data__limits_is_dict = isinstance(data__limits, dict)
            if data__limits_is_dict:
                data__limits_keys = set(data__limits.keys())
                if "cpu" in data__limits_keys:
                    data__limits_keys.remove("cpu")
                    data__limits__cpu = data__limits["cpu"]
                    if not isinstance(data__limits__cpu, (int, float)) or isinstance(data__limits__cpu, bool):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".limits.cpu must be number", value=data__limits__cpu, name="" + (name_prefix or "data") + ".limits.cpu", definition={'type': 'number', 'min': 0.1, 'max': 8}, rule='type')
                if "memory" in data__limits_keys:
                    data__limits_keys.remove("memory")
                    data__limits__memory = data__limits["memory"]
                    if not isinstance(data__limits__memory, (int, float)) or isinstance(data__limits__memory, bool):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".limits.memory must be number", value=data__limits__memory, name="" + (name_prefix or "data") + ".limits.memory", definition={'type': 'number', 'min': 256, 'max': 32678}, rule='type')
    return data

def validate___definitions_secretdepends(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "secret":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: secret", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'secret', 'default': 'secret'}, rule='const')
        else: data["kind"] = 'secret'
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

def validate___definitions_cloudcomponentinfospec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'replicas': {'type': 'number', 'default': 1}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "replicas" in data_keys:
            data_keys.remove("replicas")
            data__replicas = data["replicas"]
            if not isinstance(data__replicas, (int, float)) or isinstance(data__replicas, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".replicas must be number", value=data__replicas, name="" + (name_prefix or "data") + ".replicas", definition={'type': 'number', 'default': 1}, rule='type')
        else: data["replicas"] = 1
    return data

def validate___definitions_environmentspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}, rule='required')
        if "exposed" in data:
            data_one_of_count6 = 0
            if data_one_of_count6 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['exposedName']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['exposedName'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, rule='required')
                        data_keys = set(data.keys())
                        if "exposed" in data_keys:
                            data_keys.remove("exposed")
                            data__exposed = data["exposed"]
                            if data__exposed not in [True]:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".exposed must be one of [True]", value=data__exposed, name="" + (name_prefix or "data") + ".exposed", definition={'enum': [True]}, rule='enum')
                        if "exposedName" in data_keys:
                            data_keys.remove("exposedName")
                            data__exposedName = data["exposedName"]
                            if not isinstance(data__exposedName, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".exposedName must be string", value=data__exposedName, name="" + (name_prefix or "data") + ".exposedName", definition={'type': 'string'}, rule='type')
                    data_one_of_count6 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count6 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "exposed" in data_keys:
                            data_keys.remove("exposed")
                            data__exposed = data["exposed"]
                            if data__exposed not in [False]:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".exposed must be one of [False]", value=data__exposed, name="" + (name_prefix or "data") + ".exposed", definition={'enum': [False]}, rule='enum')
                    data_one_of_count6 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count6 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count6) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "description" in data_keys:
            data_keys.remove("description")
            data__description = data["description"]
            if not isinstance(data__description, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".description must be string", value=data__description, name="" + (name_prefix or "data") + ".description", definition={'type': 'string'}, rule='type')
        if "default" in data_keys:
            data_keys.remove("default")
            data__default = data["default"]
            if not isinstance(data__default, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".default must be string", value=data__default, name="" + (name_prefix or "data") + ".default", definition={'type': 'string'}, rule='type')
        if "exposed" in data_keys:
            data_keys.remove("exposed")
            data__exposed = data["exposed"]
            if not isinstance(data__exposed, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".exposed must be boolean", value=data__exposed, name="" + (name_prefix or "data") + ".exposed", definition={'type': 'boolean', 'default': False}, rule='type')
        else: data["exposed"] = False
    return data

def validate___definitions_deviceexecutablespec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['type']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['type'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}, rule='required')
        if "type" in data:
            data_one_of_count7 = 0
            if data_one_of_count7 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['docker']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['docker']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['docker']}, rule='enum')
                        if "docker" in data_keys:
                            data_keys.remove("docker")
                            data__docker = data["docker"]
                            if not isinstance(data__docker, (dict)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".docker must be object", value=data__docker, name="" + (name_prefix or "data") + ".docker", definition={'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['image']}, rule='type')
                            data__docker_is_dict = isinstance(data__docker, dict)
                            if data__docker_is_dict:
                                data__docker_len = len(data__docker)
                                if not all(prop in data__docker for prop in ['image']):
                                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".docker must contain ['image'] properties", value=data__docker, name="" + (name_prefix or "data") + ".docker", definition={'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['image']}, rule='required')
                                data__docker_keys = set(data__docker.keys())
                                if "image" in data__docker_keys:
                                    data__docker_keys.remove("image")
                                    data__docker__image = data__docker["image"]
                                    if not isinstance(data__docker__image, (str)):
                                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".docker.image must be string", value=data__docker__image, name="" + (name_prefix or "data") + ".docker.image", definition={'type': 'string'}, rule='type')
                                if "pullSecret" in data__docker_keys:
                                    data__docker_keys.remove("pullSecret")
                                    data__docker__pullSecret = data__docker["pullSecret"]
                                    validate___definitions_secretdepends(data__docker__pullSecret, custom_formats, (name_prefix or "data") + ".docker.pullSecret")
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['build']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['build']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['build']}, rule='enum')
                        if "build" in data_keys:
                            data_keys.remove("build")
                            data__build = data["build"]
                            if not isinstance(data__build, (dict)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".build must be object", value=data__build, name="" + (name_prefix or "data") + ".build", definition={'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}, rule='type')
                            data__build_is_dict = isinstance(data__build, dict)
                            if data__build_is_dict:
                                data__build_len = len(data__build)
                                if not all(prop in data__build for prop in ['depends']):
                                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".build must contain ['depends'] properties", value=data__build, name="" + (name_prefix or "data") + ".build", definition={'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}, rule='required')
                                data__build_keys = set(data__build.keys())
                                if "depends" in data__build_keys:
                                    data__build_keys.remove("depends")
                                    data__build__depends = data__build["depends"]
                                    validate___definitions_builddepends(data__build__depends, custom_formats, (name_prefix or "data") + ".build.depends")
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['preInstalled']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['preInstalled']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['preInstalled']}, rule='enum')
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count7) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "type" in data_keys:
            data_keys.remove("type")
            data__type = data["type"]
            if not isinstance(data__type, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be string", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, rule='type')
            if data__type not in ['docker', 'build', 'preInstalled']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['docker', 'build', 'preInstalled']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, rule='enum')
        else: data["type"] = 'docker'
        if "command" in data_keys:
            data_keys.remove("command")
            data__command = data["command"]
            if not isinstance(data__command, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".command must be string", value=data__command, name="" + (name_prefix or "data") + ".command", definition={'type': 'string'}, rule='type')
        if "runAsBash" in data_keys:
            data_keys.remove("runAsBash")
            data__runAsBash = data["runAsBash"]
            if not isinstance(data__runAsBash, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runAsBash must be boolean", value=data__runAsBash, name="" + (name_prefix or "data") + ".runAsBash", definition={'type': 'boolean', 'default': True}, rule='type')
        else: data["runAsBash"] = True
    return data

def validate___definitions_builddepends(data, custom_formats={}, name_prefix=None):
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "build":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: build", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'build', 'default': 'build'}, rule='const')
        else: data["kind"] = 'build'
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

def validate___definitions_devicecomponentinfospec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'arch': {'type': 'string', 'enum': ['arm32v7', 'arm64v8', 'amd64'], 'default': 'amd64'}, 'restart': {'type': 'string', 'default': 'always', 'enum': ['always', 'never', 'onfailure']}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "arch" in data_keys:
            data_keys.remove("arch")
            data__arch = data["arch"]
            if not isinstance(data__arch, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".arch must be string", value=data__arch, name="" + (name_prefix or "data") + ".arch", definition={'type': 'string', 'enum': ['arm32v7', 'arm64v8', 'amd64'], 'default': 'amd64'}, rule='type')
            if data__arch not in ['arm32v7', 'arm64v8', 'amd64']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".arch must be one of ['arm32v7', 'arm64v8', 'amd64']", value=data__arch, name="" + (name_prefix or "data") + ".arch", definition={'type': 'string', 'enum': ['arm32v7', 'arm64v8', 'amd64'], 'default': 'amd64'}, rule='enum')
        else: data["arch"] = 'amd64'
        if "restart" in data_keys:
            data_keys.remove("restart")
            data__restart = data["restart"]
            if not isinstance(data__restart, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".restart must be string", value=data__restart, name="" + (name_prefix or "data") + ".restart", definition={'type': 'string', 'default': 'always', 'enum': ['always', 'never', 'onfailure']}, rule='type')
            if data__restart not in ['always', 'never', 'onfailure']:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".restart must be one of ['always', 'never', 'onfailure']", value=data__restart, name="" + (name_prefix or "data") + ".restart", definition={'type': 'string', 'default': 'always', 'enum': ['always', 'never', 'onfailure']}, rule='enum')
        else: data["restart"] = 'always'
    return data

def validate___definitions_metadata(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'version': {'type': 'string'}, 'tag': {'type': 'string'}, 'description': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^pkg-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name', 'version']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name', 'version']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name', 'version'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'version': {'type': 'string'}, 'tag': {'type': 'string'}, 'description': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^pkg-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name', 'version']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "version" in data_keys:
            data_keys.remove("version")
            data__version = data["version"]
            if not isinstance(data__version, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".version must be string", value=data__version, name="" + (name_prefix or "data") + ".version", definition={'type': 'string'}, rule='type')
        if "tag" in data_keys:
            data_keys.remove("tag")
            data__tag = data["tag"]
            if not isinstance(data__tag, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".tag must be string", value=data__tag, name="" + (name_prefix or "data") + ".tag", definition={'type': 'string'}, rule='type')
        if "description" in data_keys:
            data_keys.remove("description")
            data__description = data["description"]
            if not isinstance(data__description, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".description must be string", value=data__description, name="" + (name_prefix or "data") + ".description", definition={'type': 'string'}, rule='type')
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
        if "labels" in data_keys:
            data_keys.remove("labels")
            data__labels = data["labels"]
            validate___definitions_stringmap(data__labels, custom_formats, (name_prefix or "data") + ".labels")
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