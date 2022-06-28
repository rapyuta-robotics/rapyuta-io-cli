VERSION = "2.15.3"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^secret-[a-z]{24}$': re.compile('^secret-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}):
    validate___definitions_secret(data, custom_formats)
    return data

def validate___definitions_secret(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Secret'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/secretSpec'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("data must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Secret'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/secretSpec'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
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
            if data__kind != "Secret":
                raise JsonSchemaValueException("data.kind must be same as const definition: Secret", value=data__kind, name="data.kind", definition={'const': 'Secret'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats)
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_secretspec(data__spec, custom_formats)
    return data

def validate___definitions_secretspec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'type': {'type': 'string', 'default': 'Docker', 'enum': ['Docker', 'Git']}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['Docker']}, 'docker': {'type': 'object', '$ref': '#/definitions/docker', 'required': None}}}, {'properties': {'type': {'enum': ['Git']}, 'git': {'type': 'object', '$ref': '#/definitions/git'}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['type']):
            raise JsonSchemaValueException("data must contain ['type'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'type': {'type': 'string', 'default': 'Docker', 'enum': ['Docker', 'Git']}}, 'required': ['type'], 'dependencies': {'type': {'oneOf': [{'properties': {'type': {'enum': ['Docker']}, 'docker': {'type': 'object', '$ref': '#/definitions/docker', 'required': None}}}, {'properties': {'type': {'enum': ['Git']}, 'git': {'type': 'object', '$ref': '#/definitions/git'}}}]}}}, rule='required')
        if "type" in data:
            data_one_of_count1 = 0
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['Docker']:
                                raise JsonSchemaValueException("data.type must be one of ['Docker']", value=data__type, name="data.type", definition={'enum': ['Docker']}, rule='enum')
                        if "docker" in data_keys:
                            data_keys.remove("docker")
                            data__docker = data["docker"]
                            validate___definitions_docker(data__docker, custom_formats)
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "type" in data_keys:
                            data_keys.remove("type")
                            data__type = data["type"]
                            if data__type not in ['Git']:
                                raise JsonSchemaValueException("data.type must be one of ['Git']", value=data__type, name="data.type", definition={'enum': ['Git']}, rule='enum')
                        if "git" in data_keys:
                            data_keys.remove("git")
                            data__git = data["git"]
                            validate___definitions_git(data__git, custom_formats)
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 != 1:
                raise JsonSchemaValueException("data must be valid exactly by one of oneOf definition", value=data, name="data", definition={'oneOf': [{'properties': {'type': {'enum': ['Docker']}, 'docker': {'type': 'object', '$ref': '#/definitions/docker', 'required': None}}}, {'properties': {'type': {'enum': ['Git']}, 'git': {'type': 'object', '$ref': '#/definitions/git'}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "type" in data_keys:
            data_keys.remove("type")
            data__type = data["type"]
            if not isinstance(data__type, (str)):
                raise JsonSchemaValueException("data.type must be string", value=data__type, name="data.type", definition={'type': 'string', 'default': 'Docker', 'enum': ['Docker', 'Git']}, rule='type')
            if data__type not in ['Docker', 'Git']:
                raise JsonSchemaValueException("data.type must be one of ['Docker', 'Git']", value=data__type, name="data.type", definition={'type': 'string', 'default': 'Docker', 'enum': ['Docker', 'Git']}, rule='enum')
        else: data["type"] = 'Docker'
    return data

def validate___definitions_git(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'authMethod': {'type': 'string', 'default': 'HTTP/S Basic Auth', 'enum': ['HTTP/S Basic Auth', 'HTTP/S Token Auth', 'SSH Auth']}}, 'dependencies': {'authMethod': {'oneOf': [{'properties': {'authMethod': {'type': 'string', 'enum': ['HTTP/S Basic Auth']}, 'username': {'type': 'string'}, 'password': {'type': 'string'}, 'caCert': {'type': 'string'}}, 'required': ['username', 'password']}, {'properties': {'authMethod': {'type': 'string', 'enum': ['HTTP/S Token Auth']}, 'token': {'type': 'string'}, 'caCert': {'type': 'string'}}, 'required': ['token']}, {'properties': {'authMethod': {'type': 'string', 'enum': ['SSH Auth']}, 'privateKey': {'type': 'string'}}, 'required': ['privateKey']}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        if "authMethod" in data:
            data_one_of_count2 = 0
            if data_one_of_count2 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['username', 'password']):
                            raise JsonSchemaValueException("data must contain ['username', 'password'] properties", value=data, name="data", definition={'properties': {'authMethod': {'type': 'string', 'enum': ['HTTP/S Basic Auth']}, 'username': {'type': 'string'}, 'password': {'type': 'string'}, 'caCert': {'type': 'string'}}, 'required': ['username', 'password']}, rule='required')
                        data_keys = set(data.keys())
                        if "authMethod" in data_keys:
                            data_keys.remove("authMethod")
                            data__authMethod = data["authMethod"]
                            if not isinstance(data__authMethod, (str)):
                                raise JsonSchemaValueException("data.authMethod must be string", value=data__authMethod, name="data.authMethod", definition={'type': 'string', 'enum': ['HTTP/S Basic Auth']}, rule='type')
                            if data__authMethod not in ['HTTP/S Basic Auth']:
                                raise JsonSchemaValueException("data.authMethod must be one of ['HTTP/S Basic Auth']", value=data__authMethod, name="data.authMethod", definition={'type': 'string', 'enum': ['HTTP/S Basic Auth']}, rule='enum')
                        if "username" in data_keys:
                            data_keys.remove("username")
                            data__username = data["username"]
                            if not isinstance(data__username, (str)):
                                raise JsonSchemaValueException("data.username must be string", value=data__username, name="data.username", definition={'type': 'string'}, rule='type')
                        if "password" in data_keys:
                            data_keys.remove("password")
                            data__password = data["password"]
                            if not isinstance(data__password, (str)):
                                raise JsonSchemaValueException("data.password must be string", value=data__password, name="data.password", definition={'type': 'string'}, rule='type')
                        if "caCert" in data_keys:
                            data_keys.remove("caCert")
                            data__caCert = data["caCert"]
                            if not isinstance(data__caCert, (str)):
                                raise JsonSchemaValueException("data.caCert must be string", value=data__caCert, name="data.caCert", definition={'type': 'string'}, rule='type')
                    data_one_of_count2 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count2 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['token']):
                            raise JsonSchemaValueException("data must contain ['token'] properties", value=data, name="data", definition={'properties': {'authMethod': {'type': 'string', 'enum': ['HTTP/S Token Auth']}, 'token': {'type': 'string'}, 'caCert': {'type': 'string'}}, 'required': ['token']}, rule='required')
                        data_keys = set(data.keys())
                        if "authMethod" in data_keys:
                            data_keys.remove("authMethod")
                            data__authMethod = data["authMethod"]
                            if not isinstance(data__authMethod, (str)):
                                raise JsonSchemaValueException("data.authMethod must be string", value=data__authMethod, name="data.authMethod", definition={'type': 'string', 'enum': ['HTTP/S Token Auth']}, rule='type')
                            if data__authMethod not in ['HTTP/S Token Auth']:
                                raise JsonSchemaValueException("data.authMethod must be one of ['HTTP/S Token Auth']", value=data__authMethod, name="data.authMethod", definition={'type': 'string', 'enum': ['HTTP/S Token Auth']}, rule='enum')
                        if "token" in data_keys:
                            data_keys.remove("token")
                            data__token = data["token"]
                            if not isinstance(data__token, (str)):
                                raise JsonSchemaValueException("data.token must be string", value=data__token, name="data.token", definition={'type': 'string'}, rule='type')
                        if "caCert" in data_keys:
                            data_keys.remove("caCert")
                            data__caCert = data["caCert"]
                            if not isinstance(data__caCert, (str)):
                                raise JsonSchemaValueException("data.caCert must be string", value=data__caCert, name="data.caCert", definition={'type': 'string'}, rule='type')
                    data_one_of_count2 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count2 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_len = len(data)
                        if not all(prop in data for prop in ['privateKey']):
                            raise JsonSchemaValueException("data must contain ['privateKey'] properties", value=data, name="data", definition={'properties': {'authMethod': {'type': 'string', 'enum': ['SSH Auth']}, 'privateKey': {'type': 'string'}}, 'required': ['privateKey']}, rule='required')
                        data_keys = set(data.keys())
                        if "authMethod" in data_keys:
                            data_keys.remove("authMethod")
                            data__authMethod = data["authMethod"]
                            if not isinstance(data__authMethod, (str)):
                                raise JsonSchemaValueException("data.authMethod must be string", value=data__authMethod, name="data.authMethod", definition={'type': 'string', 'enum': ['SSH Auth']}, rule='type')
                            if data__authMethod not in ['SSH Auth']:
                                raise JsonSchemaValueException("data.authMethod must be one of ['SSH Auth']", value=data__authMethod, name="data.authMethod", definition={'type': 'string', 'enum': ['SSH Auth']}, rule='enum')
                        if "privateKey" in data_keys:
                            data_keys.remove("privateKey")
                            data__privateKey = data["privateKey"]
                            if not isinstance(data__privateKey, (str)):
                                raise JsonSchemaValueException("data.privateKey must be string", value=data__privateKey, name="data.privateKey", definition={'type': 'string'}, rule='type')
                    data_one_of_count2 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count2 != 1:
                raise JsonSchemaValueException("data must be valid exactly by one of oneOf definition", value=data, name="data", definition={'oneOf': [{'properties': {'authMethod': {'type': 'string', 'enum': ['HTTP/S Basic Auth']}, 'username': {'type': 'string'}, 'password': {'type': 'string'}, 'caCert': {'type': 'string'}}, 'required': ['username', 'password']}, {'properties': {'authMethod': {'type': 'string', 'enum': ['HTTP/S Token Auth']}, 'token': {'type': 'string'}, 'caCert': {'type': 'string'}}, 'required': ['token']}, {'properties': {'authMethod': {'type': 'string', 'enum': ['SSH Auth']}, 'privateKey': {'type': 'string'}}, 'required': ['privateKey']}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "authMethod" in data_keys:
            data_keys.remove("authMethod")
            data__authMethod = data["authMethod"]
            if not isinstance(data__authMethod, (str)):
                raise JsonSchemaValueException("data.authMethod must be string", value=data__authMethod, name="data.authMethod", definition={'type': 'string', 'default': 'HTTP/S Basic Auth', 'enum': ['HTTP/S Basic Auth', 'HTTP/S Token Auth', 'SSH Auth']}, rule='type')
            if data__authMethod not in ['HTTP/S Basic Auth', 'HTTP/S Token Auth', 'SSH Auth']:
                raise JsonSchemaValueException("data.authMethod must be one of ['HTTP/S Basic Auth', 'HTTP/S Token Auth', 'SSH Auth']", value=data__authMethod, name="data.authMethod", definition={'type': 'string', 'default': 'HTTP/S Basic Auth', 'enum': ['HTTP/S Basic Auth', 'HTTP/S Token Auth', 'SSH Auth']}, rule='enum')
        else: data["authMethod"] = 'HTTP/S Basic Auth'
    return data

def validate___definitions_docker(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'registry': {'type': 'string', 'default': 'https://index.docker.io/v1/'}, 'username': {'type': 'string'}, 'password': {'type': 'string'}, 'email': {'type': 'string'}}, 'required': ['username', 'password', 'email']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['username', 'password', 'email']):
            raise JsonSchemaValueException("data must contain ['username', 'password', 'email'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'registry': {'type': 'string', 'default': 'https://index.docker.io/v1/'}, 'username': {'type': 'string'}, 'password': {'type': 'string'}, 'email': {'type': 'string'}}, 'required': ['username', 'password', 'email']}, rule='required')
        data_keys = set(data.keys())
        if "registry" in data_keys:
            data_keys.remove("registry")
            data__registry = data["registry"]
            if not isinstance(data__registry, (str)):
                raise JsonSchemaValueException("data.registry must be string", value=data__registry, name="data.registry", definition={'type': 'string', 'default': 'https://index.docker.io/v1/'}, rule='type')
        else: data["registry"] = 'https://index.docker.io/v1/'
        if "username" in data_keys:
            data_keys.remove("username")
            data__username = data["username"]
            if not isinstance(data__username, (str)):
                raise JsonSchemaValueException("data.username must be string", value=data__username, name="data.username", definition={'type': 'string'}, rule='type')
        if "password" in data_keys:
            data_keys.remove("password")
            data__password = data["password"]
            if not isinstance(data__password, (str)):
                raise JsonSchemaValueException("data.password must be string", value=data__password, name="data.password", definition={'type': 'string'}, rule='type')
        if "email" in data_keys:
            data_keys.remove("email")
            data__email = data["email"]
            if not isinstance(data__email, (str)):
                raise JsonSchemaValueException("data.email must be string", value=data__email, name="data.email", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_metadata(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/secretGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("data must contain ['name'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/secretGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("data.name must be string", value=data__name, name="data.name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_secretguid(data__guid, custom_formats)
        if "creator" in data_keys:
            data_keys.remove("creator")
            data__creator = data["creator"]
            validate___definitions_uuid(data__creator, custom_formats)
        if "project" in data_keys:
            data_keys.remove("project")
            data__project = data["project"]
            validate___definitions_projectguid(data__project, custom_formats)
        if "labels" in data_keys:
            data_keys.remove("labels")
            data__labels = data["labels"]
            validate___definitions_stringmap(data__labels, custom_formats)
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

def validate___definitions_secretguid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^secret-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^secret-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^secret-[a-z]{24}$", value=data, name="data", definition={'type': 'string', 'pattern': '^secret-[a-z]{24}$'}, rule='pattern')
    return data