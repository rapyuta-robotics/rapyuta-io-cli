VERSION = "2.16.2"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^secret-[a-z]{24}$': re.compile('^secret-[a-z]{24}\\Z'),
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^build-[a-z]{24}$': re.compile('^build-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}, name_prefix=None):
    validate___definitions_build(data, custom_formats, (name_prefix or "data") + "")
    return data

def validate___definitions_build(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Build'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/buildGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, 'spec': {'type': 'object', 'properties': {'repository': {'type': 'object', 'properties': {'url': {'type': 'string'}, 'ref': {'type': 'string'}, 'contextDir': {'type': 'string'}, 'gitSecret': {'$ref': '#/definitions/secretGUID'}}}, 'buildMethod': {'$ref': '#/definitions/buildRecipe'}}, 'required': ['buildMethod', 'repository'], 'dependencies': {'buildMethod': {'oneOf': [{'properties': {'buildMethod': {'enum': ['Docker']}, 'docker': {'type': 'object', '$ref': '#/definitions/docker'}, 'image': {'$ref': '#/definitions/imageArtifact'}}}, {'properties': {'buildMethod': {'enum': ['Source']}, 'catkin': {'type': 'object', '$ref': '#/definitions/catkin'}, 'image': {'$ref': '#/definitions/imageArtifact'}}}]}}}, 'status': {'type': 'object', 'properties': {'status': {'$ref': '#/definitions/buildStatusType'}, 'generation': {'type': 'integer'}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Build'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/buildGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, 'spec': {'type': 'object', 'properties': {'repository': {'type': 'object', 'properties': {'url': {'type': 'string'}, 'ref': {'type': 'string'}, 'contextDir': {'type': 'string'}, 'gitSecret': {'$ref': '#/definitions/secretGUID'}}}, 'buildMethod': {'$ref': '#/definitions/buildRecipe'}}, 'required': ['buildMethod', 'repository'], 'dependencies': {'buildMethod': {'oneOf': [{'properties': {'buildMethod': {'enum': ['Docker']}, 'docker': {'type': 'object', '$ref': '#/definitions/docker'}, 'image': {'$ref': '#/definitions/imageArtifact'}}}, {'properties': {'buildMethod': {'enum': ['Source']}, 'catkin': {'type': 'object', '$ref': '#/definitions/catkin'}, 'image': {'$ref': '#/definitions/imageArtifact'}}}]}}}, 'status': {'type': 'object', 'properties': {'status': {'$ref': '#/definitions/buildStatusType'}, 'generation': {'type': 'integer'}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="" + (name_prefix or "data") + ".apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1'}, rule='const')
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "Build":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: Build", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'Build'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats, (name_prefix or "data") + ".metadata")
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_buildspec(data__spec, custom_formats, (name_prefix or "data") + ".spec")
        if "status" in data_keys:
            data_keys.remove("status")
            data__status = data["status"]
            validate___definitions_buildstatus(data__status, custom_formats, (name_prefix or "data") + ".status")
    return data

def validate___definitions_buildstatus(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'status': {'enum': ['Complete', 'BuildFailed', 'BuildInProgress']}, 'generation': {'type': 'integer'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "status" in data_keys:
            data_keys.remove("status")
            data__status = data["status"]
            validate___definitions_buildstatustype(data__status, custom_formats, (name_prefix or "data") + ".status")
        if "generation" in data_keys:
            data_keys.remove("generation")
            data__generation = data["generation"]
            if not isinstance(data__generation, (int)) and not (isinstance(data__generation, float) and data__generation.is_integer()) or isinstance(data__generation, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".generation must be integer", value=data__generation, name="" + (name_prefix or "data") + ".generation", definition={'type': 'integer'}, rule='type')
    return data

def validate___definitions_buildstatustype(data, custom_formats={}, name_prefix=None):
    if data not in ['Complete', 'BuildFailed', 'BuildInProgress']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['Complete', 'BuildFailed', 'BuildInProgress']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['Complete', 'BuildFailed', 'BuildInProgress']}, rule='enum')
    return data

def validate___definitions_buildspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'repository': {'type': 'object', 'properties': {'url': {'type': 'string'}, 'ref': {'type': 'string'}, 'contextDir': {'type': 'string'}, 'gitSecret': {'type': 'string', 'pattern': '^secret-[a-z]{24}$'}}}, 'buildMethod': {'enum': ['Docker', 'Source']}}, 'required': ['buildMethod', 'repository'], 'dependencies': {'buildMethod': {'oneOf': [{'properties': {'buildMethod': {'enum': ['Docker']}, 'docker': {'type': 'object', 'properties': {'architecture': {'$ref': '#/definitions/architecture'}, 'dockerfile': {'type': 'string', 'default': 'Dockerfile'}, 'pullSecret': {'$ref': '#/definitions/secretGUID'}, 'isRos': {'type': 'boolean'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'simulation': {'type': 'boolean', 'default': False}}, 'dependentRequired': {'isRos': ['rosDistro', 'simulation']}}, 'image': {'type': 'object', 'properties': {'registry': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}}}}, {'properties': {'buildMethod': {'enum': ['Source']}, 'catkin': {'type': 'object', 'properties': {'architecture': {'$ref': '#/definitions/architecture'}, 'isRos': {'type': 'boolean', 'const': True, 'default': True}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'simulation': {'type': 'boolean', 'default': False}, 'catkinParameters': {'$ref': '#/definitions/catkinParameters'}}, 'required': ['isRos', 'rosDistro', 'simulation', 'architecture']}, 'image': {'type': 'object', 'properties': {'registry': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['buildMethod', 'repository']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['buildMethod', 'repository'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'repository': {'type': 'object', 'properties': {'url': {'type': 'string'}, 'ref': {'type': 'string'}, 'contextDir': {'type': 'string'}, 'gitSecret': {'type': 'string', 'pattern': '^secret-[a-z]{24}$'}}}, 'buildMethod': {'enum': ['Docker', 'Source']}}, 'required': ['buildMethod', 'repository'], 'dependencies': {'buildMethod': {'oneOf': [{'properties': {'buildMethod': {'enum': ['Docker']}, 'docker': {'type': 'object', 'properties': {'architecture': {'$ref': '#/definitions/architecture'}, 'dockerfile': {'type': 'string', 'default': 'Dockerfile'}, 'pullSecret': {'$ref': '#/definitions/secretGUID'}, 'isRos': {'type': 'boolean'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'simulation': {'type': 'boolean', 'default': False}}, 'dependentRequired': {'isRos': ['rosDistro', 'simulation']}}, 'image': {'type': 'object', 'properties': {'registry': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}}}}, {'properties': {'buildMethod': {'enum': ['Source']}, 'catkin': {'type': 'object', 'properties': {'architecture': {'$ref': '#/definitions/architecture'}, 'isRos': {'type': 'boolean', 'const': True, 'default': True}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'simulation': {'type': 'boolean', 'default': False}, 'catkinParameters': {'$ref': '#/definitions/catkinParameters'}}, 'required': ['isRos', 'rosDistro', 'simulation', 'architecture']}, 'image': {'type': 'object', 'properties': {'registry': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}}}}]}}}, rule='required')
        if "buildMethod" in data:
            data_one_of_count1 = 0
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "buildMethod" in data_keys:
                            data_keys.remove("buildMethod")
                            data__buildMethod = data["buildMethod"]
                            if data__buildMethod not in ['Docker']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".buildMethod must be one of ['Docker']", value=data__buildMethod, name="" + (name_prefix or "data") + ".buildMethod", definition={'enum': ['Docker']}, rule='enum')
                        if "docker" in data_keys:
                            data_keys.remove("docker")
                            data__docker = data["docker"]
                            validate___definitions_docker(data__docker, custom_formats, (name_prefix or "data") + ".docker")
                        if "image" in data_keys:
                            data_keys.remove("image")
                            data__image = data["image"]
                            validate___definitions_imageartifact(data__image, custom_formats, (name_prefix or "data") + ".image")
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "buildMethod" in data_keys:
                            data_keys.remove("buildMethod")
                            data__buildMethod = data["buildMethod"]
                            if data__buildMethod not in ['Source']:
                                raise JsonSchemaValueException("" + (name_prefix or "data") + ".buildMethod must be one of ['Source']", value=data__buildMethod, name="" + (name_prefix or "data") + ".buildMethod", definition={'enum': ['Source']}, rule='enum')
                        if "catkin" in data_keys:
                            data_keys.remove("catkin")
                            data__catkin = data["catkin"]
                            validate___definitions_catkin(data__catkin, custom_formats, (name_prefix or "data") + ".catkin")
                        if "image" in data_keys:
                            data_keys.remove("image")
                            data__image = data["image"]
                            validate___definitions_imageartifact(data__image, custom_formats, (name_prefix or "data") + ".image")
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 != 1:
                raise JsonSchemaValueException("" + (name_prefix or "data") + " must be valid exactly by one definition" + (" (" + str(data_one_of_count1) + " matches found)"), value=data, name="" + (name_prefix or "data") + "", definition={'oneOf': [{'properties': {'buildMethod': {'enum': ['Docker']}, 'docker': {'type': 'object', 'properties': {'architecture': {'$ref': '#/definitions/architecture'}, 'dockerfile': {'type': 'string', 'default': 'Dockerfile'}, 'pullSecret': {'$ref': '#/definitions/secretGUID'}, 'isRos': {'type': 'boolean'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'simulation': {'type': 'boolean', 'default': False}}, 'dependentRequired': {'isRos': ['rosDistro', 'simulation']}}, 'image': {'type': 'object', 'properties': {'registry': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}}}}, {'properties': {'buildMethod': {'enum': ['Source']}, 'catkin': {'type': 'object', 'properties': {'architecture': {'$ref': '#/definitions/architecture'}, 'isRos': {'type': 'boolean', 'const': True, 'default': True}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'simulation': {'type': 'boolean', 'default': False}, 'catkinParameters': {'$ref': '#/definitions/catkinParameters'}}, 'required': ['isRos', 'rosDistro', 'simulation', 'architecture']}, 'image': {'type': 'object', 'properties': {'registry': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "repository" in data_keys:
            data_keys.remove("repository")
            data__repository = data["repository"]
            if not isinstance(data__repository, (dict)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".repository must be object", value=data__repository, name="" + (name_prefix or "data") + ".repository", definition={'type': 'object', 'properties': {'url': {'type': 'string'}, 'ref': {'type': 'string'}, 'contextDir': {'type': 'string'}, 'gitSecret': {'type': 'string', 'pattern': '^secret-[a-z]{24}$'}}}, rule='type')
            data__repository_is_dict = isinstance(data__repository, dict)
            if data__repository_is_dict:
                data__repository_keys = set(data__repository.keys())
                if "url" in data__repository_keys:
                    data__repository_keys.remove("url")
                    data__repository__url = data__repository["url"]
                    if not isinstance(data__repository__url, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".repository.url must be string", value=data__repository__url, name="" + (name_prefix or "data") + ".repository.url", definition={'type': 'string'}, rule='type')
                if "ref" in data__repository_keys:
                    data__repository_keys.remove("ref")
                    data__repository__ref = data__repository["ref"]
                    if not isinstance(data__repository__ref, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".repository.ref must be string", value=data__repository__ref, name="" + (name_prefix or "data") + ".repository.ref", definition={'type': 'string'}, rule='type')
                if "contextDir" in data__repository_keys:
                    data__repository_keys.remove("contextDir")
                    data__repository__contextDir = data__repository["contextDir"]
                    if not isinstance(data__repository__contextDir, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".repository.contextDir must be string", value=data__repository__contextDir, name="" + (name_prefix or "data") + ".repository.contextDir", definition={'type': 'string'}, rule='type')
                if "gitSecret" in data__repository_keys:
                    data__repository_keys.remove("gitSecret")
                    data__repository__gitSecret = data__repository["gitSecret"]
                    validate___definitions_secretguid(data__repository__gitSecret, custom_formats, (name_prefix or "data") + ".repository.gitSecret")
        if "buildMethod" in data_keys:
            data_keys.remove("buildMethod")
            data__buildMethod = data["buildMethod"]
            validate___definitions_buildrecipe(data__buildMethod, custom_formats, (name_prefix or "data") + ".buildMethod")
    return data

def validate___definitions_buildrecipe(data, custom_formats={}, name_prefix=None):
    if data not in ['Docker', 'Source']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['Docker', 'Source']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['Docker', 'Source']}, rule='enum')
    return data

def validate___definitions_secretguid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^secret-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^secret-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^secret-[a-z]{24}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^secret-[a-z]{24}$'}, rule='pattern')
    return data

def validate___definitions_catkin(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'architecture': {'enum': ['amd64', 'arm32v7', 'arm64v8']}, 'isRos': {'type': 'boolean', 'const': True, 'default': True}, 'rosDistro': {'enum': ['melodic', 'kinetic', 'noetic']}, 'simulation': {'type': 'boolean', 'default': False}, 'catkinParameters': {'type': 'array', 'items': {'$ref': '#/definitions/catkinParameter'}}}, 'required': ['isRos', 'rosDistro', 'simulation', 'architecture']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['isRos', 'rosDistro', 'simulation', 'architecture']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['isRos', 'rosDistro', 'simulation', 'architecture'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'architecture': {'enum': ['amd64', 'arm32v7', 'arm64v8']}, 'isRos': {'type': 'boolean', 'const': True, 'default': True}, 'rosDistro': {'enum': ['melodic', 'kinetic', 'noetic']}, 'simulation': {'type': 'boolean', 'default': False}, 'catkinParameters': {'type': 'array', 'items': {'$ref': '#/definitions/catkinParameter'}}}, 'required': ['isRos', 'rosDistro', 'simulation', 'architecture']}, rule='required')
        data_keys = set(data.keys())
        if "architecture" in data_keys:
            data_keys.remove("architecture")
            data__architecture = data["architecture"]
            validate___definitions_architecture(data__architecture, custom_formats, (name_prefix or "data") + ".architecture")
        if "isRos" in data_keys:
            data_keys.remove("isRos")
            data__isRos = data["isRos"]
            if not isinstance(data__isRos, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".isRos must be boolean", value=data__isRos, name="" + (name_prefix or "data") + ".isRos", definition={'type': 'boolean', 'const': True, 'default': True}, rule='type')
            if data__isRos != True:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".isRos must be same as const definition: True", value=data__isRos, name="" + (name_prefix or "data") + ".isRos", definition={'type': 'boolean', 'const': True, 'default': True}, rule='const')
        else: data["isRos"] = True
        if "rosDistro" in data_keys:
            data_keys.remove("rosDistro")
            data__rosDistro = data["rosDistro"]
            validate___definitions_rosdistro(data__rosDistro, custom_formats, (name_prefix or "data") + ".rosDistro")
        if "simulation" in data_keys:
            data_keys.remove("simulation")
            data__simulation = data["simulation"]
            if not isinstance(data__simulation, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".simulation must be boolean", value=data__simulation, name="" + (name_prefix or "data") + ".simulation", definition={'type': 'boolean', 'default': False}, rule='type')
        else: data["simulation"] = False
        if "catkinParameters" in data_keys:
            data_keys.remove("catkinParameters")
            data__catkinParameters = data["catkinParameters"]
            validate___definitions_catkinparameters(data__catkinParameters, custom_formats, (name_prefix or "data") + ".catkinParameters")
    return data

def validate___definitions_catkinparameters(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (list, tuple)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be array", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'rosPackages': {'type': 'string'}, 'cmakeArguments': {'type': 'string'}, 'makeArguments': {'type': 'string'}, 'catkinMakeArguments': {'type': 'string'}, 'blacklist': {'type': 'string'}}}}, rule='type')
    data_is_list = isinstance(data, (list, tuple))
    if data_is_list:
        data_len = len(data)
        for data_x, data_item in enumerate(data):
            validate___definitions_catkinparameter(data_item, custom_formats, (name_prefix or "data") + "[{data_x}]")
    return data

def validate___definitions_catkinparameter(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'rosPackages': {'type': 'string'}, 'cmakeArguments': {'type': 'string'}, 'makeArguments': {'type': 'string'}, 'catkinMakeArguments': {'type': 'string'}, 'blacklist': {'type': 'string'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "rosPackages" in data_keys:
            data_keys.remove("rosPackages")
            data__rosPackages = data["rosPackages"]
            if not isinstance(data__rosPackages, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".rosPackages must be string", value=data__rosPackages, name="" + (name_prefix or "data") + ".rosPackages", definition={'type': 'string'}, rule='type')
        if "cmakeArguments" in data_keys:
            data_keys.remove("cmakeArguments")
            data__cmakeArguments = data["cmakeArguments"]
            if not isinstance(data__cmakeArguments, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".cmakeArguments must be string", value=data__cmakeArguments, name="" + (name_prefix or "data") + ".cmakeArguments", definition={'type': 'string'}, rule='type')
        if "makeArguments" in data_keys:
            data_keys.remove("makeArguments")
            data__makeArguments = data["makeArguments"]
            if not isinstance(data__makeArguments, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".makeArguments must be string", value=data__makeArguments, name="" + (name_prefix or "data") + ".makeArguments", definition={'type': 'string'}, rule='type')
        if "catkinMakeArguments" in data_keys:
            data_keys.remove("catkinMakeArguments")
            data__catkinMakeArguments = data["catkinMakeArguments"]
            if not isinstance(data__catkinMakeArguments, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".catkinMakeArguments must be string", value=data__catkinMakeArguments, name="" + (name_prefix or "data") + ".catkinMakeArguments", definition={'type': 'string'}, rule='type')
        if "blacklist" in data_keys:
            data_keys.remove("blacklist")
            data__blacklist = data["blacklist"]
            if not isinstance(data__blacklist, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".blacklist must be string", value=data__blacklist, name="" + (name_prefix or "data") + ".blacklist", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_rosdistro(data, custom_formats={}, name_prefix=None):
    if data not in ['melodic', 'kinetic', 'noetic']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['melodic', 'kinetic', 'noetic']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['melodic', 'kinetic', 'noetic']}, rule='enum')
    return data

def validate___definitions_architecture(data, custom_formats={}, name_prefix=None):
    if data not in ['amd64', 'arm32v7', 'arm64v8']:
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be one of ['amd64', 'arm32v7', 'arm64v8']", value=data, name="" + (name_prefix or "data") + "", definition={'enum': ['amd64', 'arm32v7', 'arm64v8']}, rule='enum')
    return data

def validate___definitions_imageartifact(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'registry': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "registry" in data_keys:
            data_keys.remove("registry")
            data__registry = data["registry"]
            if not isinstance(data__registry, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".registry must be string", value=data__registry, name="" + (name_prefix or "data") + ".registry", definition={'type': 'string'}, rule='type')
        if "pushSecret" in data_keys:
            data_keys.remove("pushSecret")
            data__pushSecret = data["pushSecret"]
            if not isinstance(data__pushSecret, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".pushSecret must be string", value=data__pushSecret, name="" + (name_prefix or "data") + ".pushSecret", definition={'type': 'string'}, rule='type')
        if "tagName" in data_keys:
            data_keys.remove("tagName")
            data__tagName = data["tagName"]
            if not isinstance(data__tagName, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".tagName must be string", value=data__tagName, name="" + (name_prefix or "data") + ".tagName", definition={'type': 'string'}, rule='type')
        if "triggerName" in data_keys:
            data_keys.remove("triggerName")
            data__triggerName = data["triggerName"]
            if not isinstance(data__triggerName, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".triggerName must be string", value=data__triggerName, name="" + (name_prefix or "data") + ".triggerName", definition={'type': 'string'}, rule='type')
        if "webhookURL" in data_keys:
            data_keys.remove("webhookURL")
            data__webhookURL = data["webhookURL"]
            if not isinstance(data__webhookURL, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".webhookURL must be string", value=data__webhookURL, name="" + (name_prefix or "data") + ".webhookURL", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_docker(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'architecture': {'enum': ['amd64', 'arm32v7', 'arm64v8']}, 'dockerfile': {'type': 'string', 'default': 'Dockerfile'}, 'pullSecret': {'type': 'string', 'pattern': '^secret-[a-z]{24}$'}, 'isRos': {'type': 'boolean'}, 'rosDistro': {'enum': ['melodic', 'kinetic', 'noetic']}, 'simulation': {'type': 'boolean', 'default': False}}, 'dependentRequired': {'isRos': ['rosDistro', 'simulation']}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "architecture" in data_keys:
            data_keys.remove("architecture")
            data__architecture = data["architecture"]
            validate___definitions_architecture(data__architecture, custom_formats, (name_prefix or "data") + ".architecture")
        if "dockerfile" in data_keys:
            data_keys.remove("dockerfile")
            data__dockerfile = data["dockerfile"]
            if not isinstance(data__dockerfile, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".dockerfile must be string", value=data__dockerfile, name="" + (name_prefix or "data") + ".dockerfile", definition={'type': 'string', 'default': 'Dockerfile'}, rule='type')
        else: data["dockerfile"] = 'Dockerfile'
        if "pullSecret" in data_keys:
            data_keys.remove("pullSecret")
            data__pullSecret = data["pullSecret"]
            validate___definitions_secretguid(data__pullSecret, custom_formats, (name_prefix or "data") + ".pullSecret")
        if "isRos" in data_keys:
            data_keys.remove("isRos")
            data__isRos = data["isRos"]
            if not isinstance(data__isRos, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".isRos must be boolean", value=data__isRos, name="" + (name_prefix or "data") + ".isRos", definition={'type': 'boolean'}, rule='type')
        if "rosDistro" in data_keys:
            data_keys.remove("rosDistro")
            data__rosDistro = data["rosDistro"]
            validate___definitions_rosdistro(data__rosDistro, custom_formats, (name_prefix or "data") + ".rosDistro")
        if "simulation" in data_keys:
            data_keys.remove("simulation")
            data__simulation = data["simulation"]
            if not isinstance(data__simulation, (bool)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".simulation must be boolean", value=data__simulation, name="" + (name_prefix or "data") + ".simulation", definition={'type': 'boolean', 'default': False}, rule='type')
        else: data["simulation"] = False
    return data

def validate___definitions_metadata(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^build-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^build-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_buildguid(data__guid, custom_formats, (name_prefix or "data") + ".guid")
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

def validate___definitions_buildguid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^build-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^build-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^build-[a-z]{24}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^build-[a-z]{24}$'}, rule='pattern')
    return data