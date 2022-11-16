VERSION = "2.16.2"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^network-[a-z]{24}$': re.compile('^network-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}, name_prefix=None):
    validate___definitions_network(data, custom_formats, (name_prefix or "data") + "")
    return data

def validate___definitions_network(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Network'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/networkGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, 'spec': {'type': 'object', 'properties': {'type': {'$ref': '#/definitions/networkType'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'runtime': {'$ref': '#/definitions/runtime'}}, 'required': ['type', 'rosDistro', 'runtime'], 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['cloud']}, 'resourceLimits': {'$ref': '#/definitions/resourceLimits'}}, 'required': ['runtime', 'resourceLimits']}, {'properties': {'runtime': {'enum': ['device']}, 'deviceGUID': {'$ref': '#/definitions/uuid'}, 'networkInterface': {'type': 'string'}, 'restartPolicy': {'$ref': '#/definitions/restartPolicy', 'default': 'Always'}}, 'required': ['deviceGUID', 'networkInterface']}]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Network'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/networkGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, 'spec': {'type': 'object', 'properties': {'type': {'$ref': '#/definitions/networkType'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'runtime': {'$ref': '#/definitions/runtime'}}, 'required': ['type', 'rosDistro', 'runtime'], 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['cloud']}, 'resourceLimits': {'$ref': '#/definitions/resourceLimits'}}, 'required': ['runtime', 'resourceLimits']}, {'properties': {'runtime': {'enum': ['device']}, 'deviceGUID': {'$ref': '#/definitions/uuid'}, 'networkInterface': {'type': 'string'}, 'restartPolicy': {'$ref': '#/definitions/restartPolicy', 'default': 'Always'}}, 'required': ['deviceGUID', 'networkInterface']}]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="" + (name_prefix or "data") + ".apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1'}, rule='const')
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "Network":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: Network", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'Network'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats, (name_prefix or "data") + ".metadata")
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_networkspec(data__spec, custom_formats, (name_prefix or "data") + ".spec")
    return data

def validate___definitions_networkspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'type': {'enum': ['routed', 'native']}, 'rosDistro': {'enum': ['melodic', 'kinetic', 'noetic']}, 'runtime': {'enum': ['cloud', 'device']}}, 'required': ['type', 'rosDistro', 'runtime'], 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['cloud']}, 'resourceLimits': {'enum': ['xSmall', 'small', 'medium', 'large']}}, 'required': ['runtime', 'resourceLimits']}, {'properties': {'runtime': {'enum': ['device']}, 'deviceGUID': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'networkInterface': {'type': 'string'}, 'restartPolicy': {'enum': ['always', 'never', 'onFailure']}}, 'required': ['deviceGUID', 'networkInterface']}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['type', 'rosDistro', 'runtime']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['type', 'rosDistro', 'runtime'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'type': {'enum': ['routed', 'native']}, 'rosDistro': {'enum': ['melodic', 'kinetic', 'noetic']}, 'runtime': {'enum': ['cloud', 'device']}}, 'required': ['type', 'rosDistro', 'runtime'], 'dependencies': {'runtime': {'oneOf': [{'properties': {'runtime': {'enum': ['cloud']}, 'resourceLimits': {'enum': ['xSmall', 'small', 'medium', 'large']}}, 'required': ['runtime', 'resourceLimits']}, {'properties': {'runtime': {'enum': ['device']}, 'deviceGUID': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'networkInterface': {'type': 'string'}, 'restartPolicy': {'enum': ['always', 'never', 'onFailure']}}, 'required': ['deviceGUID', 'networkInterface']}]}}}, rule='required')
        if "runtime" in data:
            data_one_of_count1 = 0
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['runtime', 'resourceLimits']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['runtime', 'resourceLimits'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'runtime': {'enum': ['cloud']}, 'resourceLimits': {'enum': ['xSmall', 'small', 'medium', 'large']}}, 'required': ['runtime', 'resourceLimits']}, rule='required')
                        data_keys = set(data.keys())
                        if "runtime" in data_keys:
                            data_keys.remove("runtime")
                            data__runtime = data["runtime"]
                            if data__runtime not in ['cloud']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be one of ['cloud']", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'enum': ['cloud']}, rule='enum')
                        if "resourceLimits" in data_keys:
                            data_keys.remove("resourceLimits")
                            data__resourceLimits = data["resourceLimits"]
                            validate___definitions_resourcelimits(data__resourceLimits, custom_formats, (name_prefix or "data") + ".resourceLimits")
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['deviceGUID', 'networkInterface']):
                            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['deviceGUID', 'networkInterface'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'properties': {'runtime': {'enum': ['device']}, 'deviceGUID': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'networkInterface': {'type': 'string'}, 'restartPolicy': {'enum': ['always', 'never', 'onFailure']}}, 'required': ['deviceGUID', 'networkInterface']}, rule='required')
                        data_keys = set(data.keys())
                        if "runtime" in data_keys:
                            data_keys.remove("runtime")
                            data__runtime = data["runtime"]
                            if data__runtime not in ['device']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be one of ['device']", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'enum': ['device']}, rule='enum')
                        if "deviceGUID" in data_keys:
                            data_keys.remove("deviceGUID")
                            data__deviceGUID = data["deviceGUID"]
                            validate___definitions_uuid(data__deviceGUID, custom_formats, (name_prefix or "data") + ".deviceGUID")
                        if "networkInterface" in data_keys:
                            data_keys.remove("networkInterface")
                            data__networkInterface = data["networkInterface"]
                            if not isinstance(data__networkInterface, (str)):
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".networkInterface must be string", value=data__networkInterface, name="" + (name_prefix or "data") + ".networkInterface", definition={'type': 'string'}, rule='type')
                        if "restartPolicy" in data_keys:
                            data_keys.remove("restartPolicy")
                            data__restartPolicy = data["restartPolicy"]
                            validate___definitions_restartpolicy(data__restartPolicy, custom_formats, (name_prefix or "data") + ".restartPolicy")
                        else: data["restartPolicy"] = 'Always'
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count1) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'runtime': {'enum': ['cloud']}, 'resourceLimits': {'enum': ['xSmall', 'small', 'medium', 'large']}}, 'required': ['runtime', 'resourceLimits']}, {'properties': {'runtime': {'enum': ['device']}, 'deviceGUID': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'networkInterface': {'type': 'string'}, 'restartPolicy': {'enum': ['always', 'never', 'onFailure']}}, 'required': ['deviceGUID', 'networkInterface']}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "type" in data_keys:
            data_keys.remove("type")
            data__type = data["type"]
            validate___definitions_networktype(data__type, custom_formats, (name_prefix or "data") + ".type")
        if "rosDistro" in data_keys:
            data_keys.remove("rosDistro")
            data__rosDistro = data["rosDistro"]
            validate___definitions_rosdistro(data__rosDistro, custom_formats, (name_prefix or "data") + ".rosDistro")
        if "runtime" in data_keys:
            data_keys.remove("runtime")
            data__runtime = data["runtime"]
            validate___definitions_runtime(data__runtime, custom_formats, (name_prefix or "data") + ".runtime")
    return data

def validate___definitions_runtime(data, custom_formats={}, name_prefix=None):
    if data not in ['cloud', 'device']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['cloud', 'device']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['cloud', 'device']}, rule='enum')
    return data

def validate___definitions_rosdistro(data, custom_formats={}, name_prefix=None):
    if data not in ['melodic', 'kinetic', 'noetic']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['melodic', 'kinetic', 'noetic']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['melodic', 'kinetic', 'noetic']}, rule='enum')
    return data

def validate___definitions_networktype(data, custom_formats={}, name_prefix=None):
    if data not in ['routed', 'native']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['routed', 'native']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['routed', 'native']}, rule='enum')
    return data

def validate___definitions_restartpolicy(data, custom_formats={}, name_prefix=None):
    if data not in ['always', 'never', 'onFailure']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['always', 'never', 'onFailure']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['always', 'never', 'onFailure']}, rule='enum')
    return data

def validate___definitions_uuid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data

def validate___definitions_resourcelimits(data, custom_formats={}, name_prefix=None):
    if data not in ['xSmall', 'small', 'medium', 'large']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['xSmall', 'small', 'medium', 'large']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['xSmall', 'small', 'medium', 'large']}, rule='enum')
    return data

def validate___definitions_metadata(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^network-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^network-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_networkguid(data__guid, custom_formats, (name_prefix or "data") + ".guid")
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

def validate___definitions_networkguid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^network-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^network-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^network-[a-z]{24}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^network-[a-z]{24}$'}, rule='pattern')
    return data