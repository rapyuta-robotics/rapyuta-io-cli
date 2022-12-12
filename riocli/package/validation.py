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
    validate___definitions_package(data, custom_formats, (name_prefix or "data") + "")
    return data

def validate___definitions_package(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Package', 'default': 'Package'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'version': {'type': 'string'}, 'tag': {'type': 'string'}, 'description': {'type': 'string'}, 'guid': {'$ref': '#/definitions/packageGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name', 'version']}, 'spec': {'type': 'object', 'properties': {'runtime': {'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, 'ros': {'type': 'object', '$ref': '#/definitions/rosComponentSpec'}}, 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['device']}, 'device': {'type': 'object', '$ref': '#/definitions/deviceComponentInfoSpec'}, 'executables': {'type': 'array', 'items': {'$ref': '#/definitions/deviceExecutableSpec'}}, 'environmentArgs': {'type': 'array', 'items': {'$ref': '#/definitions/environmentSpec'}}, 'rosBagJobs': {'type': 'array', 'items': {'$ref': '#/definitions/deviceROSBagJobSpec'}}}}, {'properties': {'runtime': {'enum': ['cloud']}, 'cloud': {'type': 'object', '$ref': '#/definitions/cloudComponentInfoSpec'}, 'executables': {'type': 'array', 'items': {'$ref': '#/definitions/cloudExecutableSpec'}}, 'environmentVars': {'type': 'array', 'items': {'$ref': '#/definitions/environmentSpec'}}, 'endpoints': {'type': 'array', 'items': {'$ref': '#/definitions/endpointSpec'}}, 'rosBagJobs': {'type': 'array', 'items': {'$ref': '#/definitions/cloudROSBagJobSpec'}}}}]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Package', 'default': 'Package'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'version': {'type': 'string'}, 'tag': {'type': 'string'}, 'description': {'type': 'string'}, 'guid': {'$ref': '#/definitions/packageGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name', 'version']}, 'spec': {'type': 'object', 'properties': {'runtime': {'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, 'ros': {'type': 'object', '$ref': '#/definitions/rosComponentSpec'}}, 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['device']}, 'device': {'type': 'object', '$ref': '#/definitions/deviceComponentInfoSpec'}, 'executables': {'type': 'array', 'items': {'$ref': '#/definitions/deviceExecutableSpec'}}, 'environmentArgs': {'type': 'array', 'items': {'$ref': '#/definitions/environmentSpec'}}, 'rosBagJobs': {'type': 'array', 'items': {'$ref': '#/definitions/deviceROSBagJobSpec'}}}}, {'properties': {'runtime': {'enum': ['cloud']}, 'cloud': {'type': 'object', '$ref': '#/definitions/cloudComponentInfoSpec'}, 'executables': {'type': 'array', 'items': {'$ref': '#/definitions/cloudExecutableSpec'}}, 'environmentVars': {'type': 'array', 'items': {'$ref': '#/definitions/environmentSpec'}}, 'endpoints': {'type': 'array', 'items': {'$ref': '#/definitions/endpointSpec'}}, 'rosBagJobs': {'type': 'array', 'items': {'$ref': '#/definitions/cloudROSBagJobSpec'}}}}]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
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
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'runtime': {'type': 'string', 'enum': ['device', 'cloud'], 'default': 'cloud'}, 'ros': {'type': 'object', 'properties': {'enabled': {'type': 'boolean', 'default': False}}, 'dependencies': {'enabled': {'oneOf': [{'properties': {'enabled': {'enum': [False]}}}, {'properties': {'enabled': {'type': 'boolean', 'enum': [True]}, 'version': {'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, 'inboundScopedTargeted': {'type': 'boolean', 'default': False}, 'rosEndpoints': {'type': 'array', 'items': {'$ref': '#/definitions/rosEndpointSpec'}}}}]}}}}, 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['device']}, 'device': {'type': 'object', 'properties': {'arch': {'type': 'string', 'enum': ['arm32v7', 'arm64v8', 'amd64'], 'default': 'amd64'}, 'restart': {'type': 'string', 'default': 'always', 'enum': ['always', 'never', 'onfailure']}}}, 'executables': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'$ref': '#/definitions/secretDepends'}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/buildDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, 'environmentArgs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}, 'rosBagJobs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'$ref': '#/definitions/rosbagRecordOptionsSpec'}, 'uploadOptions': {'$ref': '#/definitions/rosbagUploadOptionsSpec'}, 'overrideOptions': {'$ref': '#/definitions/rosbagOverrideOptionsSpec'}}, 'required': ['name', 'recordOptions']}}}}, {'properties': {'runtime': {'enum': ['cloud']}, 'cloud': {'type': 'object', 'properties': {'replicas': {'type': 'number', 'default': 1}}}, 'executables': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32768}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/buildDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, 'environmentVars': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}, 'endpoints': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}}, 'rosBagJobs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'$ref': '#/definitions/rosbagRecordOptionsSpec'}, 'overrideOptions': {'$ref': '#/definitions/rosbagOverrideOptionsSpec'}}, 'required': ['name', 'recordOptions']}}}}]}}}, rule='type')
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
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".executables must be array", value=data__executables, name="" + (name_prefix or "data") + ".executables", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32768}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/buildDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, rule='type')
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
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count1) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'runtime': {'enum': ['device']}, 'device': {'type': 'object', 'properties': {'arch': {'type': 'string', 'enum': ['arm32v7', 'arm64v8', 'amd64'], 'default': 'amd64'}, 'restart': {'type': 'string', 'default': 'always', 'enum': ['always', 'never', 'onfailure']}}}, 'executables': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build', 'preInstalled']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'$ref': '#/definitions/secretDepends'}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/buildDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, 'environmentArgs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}, 'rosBagJobs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'$ref': '#/definitions/rosbagRecordOptionsSpec'}, 'uploadOptions': {'$ref': '#/definitions/rosbagUploadOptionsSpec'}, 'overrideOptions': {'$ref': '#/definitions/rosbagOverrideOptionsSpec'}}, 'required': ['name', 'recordOptions']}}}}, {'properties': {'runtime': {'enum': ['cloud']}, 'cloud': {'type': 'object', 'properties': {'replicas': {'type': 'number', 'default': 1}}}, 'executables': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32768}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/secretDepends'}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'$ref': '#/definitions/buildDepends'}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}}, 'environmentVars': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'description': {'type': 'string'}, 'default': {'type': 'string'}, 'exposed': {'type': 'boolean', 'default': False}}, 'required': ['name'], 'dependencies': {'exposed': {'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}}}}, 'endpoints': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 443}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'$ref': '#/definitions/portNumber', 'default': 80}, 'targetPort': {'$ref': '#/definitions/portNumber'}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}}, 'rosBagJobs': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'recordOptions': {'$ref': '#/definitions/rosbagRecordOptionsSpec'}, 'overrideOptions': {'$ref': '#/definitions/rosbagOverrideOptionsSpec'}}, 'required': ['name', 'recordOptions']}}}}]}, rule='oneOf')
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
    data_one_of_count4 = 0
    if data_one_of_count4 < 2:
        try:
            data_is_dict = isinstance(data, dict)
            if data_is_dict:
                data_len = len(data)
                if not all(prop in data for prop in ['topicName', 'recordFrequency']):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['topicName', 'recordFrequency'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['topicName', 'recordFrequency']}, rule='required')
            data_one_of_count4 += 1
        except JsonSchemaValueException: pass
    if data_one_of_count4 < 2:
        try:
            data_is_dict = isinstance(data, dict)
            if data_is_dict:
                data_len = len(data)
                if not all(prop in data for prop in ['topicName', 'latched']):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['topicName', 'latched'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['topicName', 'latched']}, rule='required')
            data_one_of_count4 += 1
        except JsonSchemaValueException: pass
    if data_one_of_count4 != 1:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count4) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'oneOf': [{'required': ['topicName', 'recordFrequency']}, {'required': ['topicName', 'latched']}], 'properties': {'topicName': {'type': 'string'}, 'recordFrequency': {'type': 'integer'}, 'latched': {'type': 'boolean'}}}, rule='oneOf')
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
    data_one_of_count5 = 0
    if data_one_of_count5 < 2:
        try:
            data_is_dict = isinstance(data, dict)
            if data_is_dict:
                data_len = len(data)
                if not all(prop in data for prop in ['allTopics']):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['allTopics'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['allTopics']}, rule='required')
            data_one_of_count5 += 1
        except JsonSchemaValueException: pass
    if data_one_of_count5 < 2:
        try:
            data_any_of_count6 = 0
            if not data_any_of_count6:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['topics']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['topics'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['topics']}, rule='required')
                    data_any_of_count6 += 1
                except JsonSchemaValueException: pass
            if not data_any_of_count6:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['topicIncludeRegex']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['topicIncludeRegex'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'required': ['topicIncludeRegex']}, rule='required')
                    data_any_of_count6 += 1
                except JsonSchemaValueException: pass
            if not data_any_of_count6:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " cannot be validated by any definition", value=data, name="" + (name_prefix or "data") + "", definition={'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}, rule='anyOf')
            data_one_of_count5 += 1
        except JsonSchemaValueException: pass
    if data_one_of_count5 != 1:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count5) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'oneOf': [{'required': ['allTopics']}, {'anyOf': [{'required': ['topics']}, {'required': ['topicIncludeRegex']}]}], 'properties': {'allTopics': {'type': 'boolean'}, 'topics': {'type': 'array', 'items': {'type': 'string'}}, 'topicIncludeRegex': {'type': 'array', 'items': {'type': 'string'}}, 'topicExcludeRegex': {'type': 'string'}, 'maxMessageCount': {'type': 'integer'}, 'node': {'type': 'string'}, 'compression': {'type': 'string', 'enum': ['BZ2', 'LZ4']}, 'maxSplits': {'type': 'integer'}, 'maxSplitSize': {'type': 'integer'}, 'chunkSize': {'type': 'integer'}, 'prefix': {'type': 'string'}, 'maxSplitDuration': {'type': 'integer'}}}, rule='oneOf')
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

def validate___definitions_endpointspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name', 'type']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name', 'type'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'external-http', 'enum': ['external-http', 'external-https', 'external-tls-tcp', 'internal-tcp', 'internal-udp', 'internal-tcp-range', 'internal-udp-range']}}, 'required': ['name', 'type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}}}, rule='required')
        if "type" in data:
            data_one_of_count7 = 0
            if data_one_of_count7 < 2:
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
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 < 2:
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
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 < 2:
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
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 < 2:
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
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 < 2:
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
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 < 2:
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
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 < 2:
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
                    data_one_of_count7 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count7 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count7) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'type': {'enum': ['external-http']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-https']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['external-tls-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-udp']}, 'port': {'type': 'integer', 'min': 1, 'max': 65531}, 'targetPort': {'type': 'integer', 'min': 1, 'max': 65531}}, 'required': ['port', 'targetPort']}, {'properties': {'type': {'enum': ['internal-tcp-range']}, 'portRange': {'type': 'string', 'default': '22,80, 1024-1030'}}, 'required': ['portRange']}, {'properties': {'type': {'enum': ['internal-udp-range']}, 'portRange': {'type': 'string', 'default': '53,1024-1025'}}, 'required': ['portRange']}]}, rule='oneOf')
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
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32768}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['type']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['type'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'type': {'type': 'string', 'default': 'docker', 'enum': ['docker', 'build']}, 'command': {'type': 'string'}, 'runAsBash': {'type': 'boolean', 'default': True}, 'simulation': {'type': 'boolean', 'default': False}, 'limits': {'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32768}}}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}}}, rule='required')
        if "type" in data:
            data_one_of_count8 = 0
            if data_one_of_count8 < 2:
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
                    data_one_of_count8 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count8 < 2:
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
                    data_one_of_count8 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count8 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['preInstalled']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['preInstalled']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['preInstalled']}, rule='enum')
                    data_one_of_count8 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count8 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count8) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}, rule='oneOf')
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
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".limits must be object", value=data__limits, name="" + (name_prefix or "data") + ".limits", definition={'type': 'object', 'properties': {'cpu': {'type': 'number', 'min': 0.1, 'max': 8}, 'memory': {'type': 'number', 'min': 256, 'max': 32768}}}, rule='type')
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
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".limits.memory must be number", value=data__limits__memory, name="" + (name_prefix or "data") + ".limits.memory", definition={'type': 'number', 'min': 256, 'max': 32768}, rule='type')
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
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'maxUploadRate': {'type': 'integer', 'default': 1048576}, 'purgeAfter': {'type': 'boolean'}, 'uploadType': {'type': 'string', 'enum': ['OnStop', 'Continuous', 'OnDemand'], 'default': 'OnDemand'}, 'onDemandOpts': {'type': 'object', 'properties': {'timeRange': {'type': 'object', 'properties': {'from': {'type': 'integer'}, 'to': {'type': 'integer'}}, 'required': ['from', 'to']}}, 'required': ['timeRange']}}}, rule='type')
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
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'timeRange': {'type': 'object', 'properties': {'from': {'type': 'integer'}, 'to': {'type': 'integer'}}, 'required': ['from', 'to']}}, 'required': ['timeRange']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['timeRange']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['timeRange'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'timeRange': {'type': 'object', 'properties': {'from': {'type': 'integer'}, 'to': {'type': 'integer'}}, 'required': ['from', 'to']}}, 'required': ['timeRange']}, rule='required')
        data_keys = set(data.keys())
        if "timeRange" in data_keys:
            data_keys.remove("timeRange")
            data__timeRange = data["timeRange"]
            if not isinstance(data__timeRange, (dict)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeRange must be object", value=data__timeRange, name="" + (name_prefix or "data") + ".timeRange", definition={'type': 'object', 'properties': {'from': {'type': 'integer'}, 'to': {'type': 'integer'}}, 'required': ['from', 'to']}, rule='type')
            data__timeRange_is_dict = isinstance(data__timeRange, dict)
            if data__timeRange_is_dict:
                data__timeRange_len = len(data__timeRange)
                if not all(prop in data__timeRange for prop in ['from', 'to']):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeRange must contain ['from', 'to'] properties", value=data__timeRange, name="" + (name_prefix or "data") + ".timeRange", definition={'type': 'object', 'properties': {'from': {'type': 'integer'}, 'to': {'type': 'integer'}}, 'required': ['from', 'to']}, rule='required')
                data__timeRange_keys = set(data__timeRange.keys())
                if "from" in data__timeRange_keys:
                    data__timeRange_keys.remove("from")
                    data__timeRange__from = data__timeRange["from"]
                    if not isinstance(data__timeRange__from, (int)) and not (isinstance(data__timeRange__from, float) and data__timeRange__from.is_integer()) or isinstance(data__timeRange__from, bool):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeRange.from must be integer", value=data__timeRange__from, name="" + (name_prefix or "data") + ".timeRange.from", definition={'type': 'integer'}, rule='type')
                if "to" in data__timeRange_keys:
                    data__timeRange_keys.remove("to")
                    data__timeRange__to = data__timeRange["to"]
                    if not isinstance(data__timeRange__to, (int)) and not (isinstance(data__timeRange__to, float) and data__timeRange__to.is_integer()) or isinstance(data__timeRange__to, bool):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".timeRange.to must be integer", value=data__timeRange__to, name="" + (name_prefix or "data") + ".timeRange.to", definition={'type': 'integer'}, rule='type')
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
            data_one_of_count9 = 0
            if data_one_of_count9 < 2:
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
                    data_one_of_count9 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count9 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "exposed" in data_keys:
                            data_keys.remove("exposed")
                            data__exposed = data["exposed"]
                            if data__exposed not in [False]:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".exposed must be one of [False]", value=data__exposed, name="" + (name_prefix or "data") + ".exposed", definition={'enum': [False]}, rule='enum')
                    data_one_of_count9 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count9 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count9) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'exposed': {'enum': [True]}, 'exposedName': {'type': 'string'}}, 'required': ['exposedName']}, {'properties': {'exposed': {'enum': [False]}}}]}, rule='oneOf')
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
            data_one_of_count10 = 0
            if data_one_of_count10 < 2:
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
                    data_one_of_count10 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count10 < 2:
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
                    data_one_of_count10 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count10 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['preInstalled']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".type must be one of ['preInstalled']", value=data__type, name="" + (name_prefix or "data") + ".type", definition={'enum': ['preInstalled']}, rule='enum')
                    data_one_of_count10 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count10 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count10) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'type': {'enum': ['docker']}, 'docker': {'type': 'object', 'properties': {'image': {'type': 'string'}, 'pullSecret': {'properties': {'kind': {'const': 'secret', 'default': 'secret'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['image']}}}, {'properties': {'type': {'enum': ['build']}, 'build': {'type': 'object', 'properties': {'depends': {'properties': {'kind': {'const': 'build', 'default': 'build'}, 'nameOrGUID': {'type': 'string'}, 'guid': {'type': 'string'}}}}, 'required': ['depends']}}}, {'properties': {'type': {'enum': ['preInstalled']}}}]}, rule='oneOf')
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