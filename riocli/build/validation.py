VERSION = "2.15.3"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^secret-[a-z]{24}$': re.compile('^secret-[a-z]{24}\\Z'),
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}):
    validate___definitions_build(data, custom_formats)
    return data

def validate___definitions_build(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Build'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/buildSpec'}, 'status': {'$ref': '#/definitions/buildStatus'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("data must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Build'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/buildSpec'}, 'status': {'$ref': '#/definitions/buildStatus'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("data.apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="data.apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1'}, rule='const')
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "Build":
                raise JsonSchemaValueException("data.kind must be same as const definition: Build", value=data__kind, name="data.kind", definition={'const': 'Build'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats)
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_buildspec(data__spec, custom_formats)
        if "status" in data_keys:
            data_keys.remove("status")
            data__status = data["status"]
            validate___definitions_buildstatus(data__status, custom_formats)
    return data

def validate___definitions_buildstatus(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'status': {'$ref': '#/definitions/buildStatusType'}, 'generation': {'type': 'integer'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "status" in data_keys:
            data_keys.remove("status")
            data__status = data["status"]
            validate___definitions_buildstatustype(data__status, custom_formats)
        if "generation" in data_keys:
            data_keys.remove("generation")
            data__generation = data["generation"]
            if not isinstance(data__generation, (int)) and not (isinstance(data__generation, float) and data__generation.is_integer()) or isinstance(data__generation, bool):
                raise JsonSchemaValueException("data.generation must be integer", value=data__generation, name="data.generation", definition={'type': 'integer'}, rule='type')
    return data

def validate___definitions_buildstatustype(data, custom_formats={}):
    if data not in ['Complete', 'BuildFailed', 'BuildInProgress']:
        raise JsonSchemaValueException("data must be one of ['Complete', 'BuildFailed', 'BuildInProgress']", value=data, name="data", definition={'enum': ['Complete', 'BuildFailed', 'BuildInProgress']}, rule='enum')
    return data

def validate___definitions_buildspec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'recipe': {'$ref': '#/definitions/buildRecipe'}, 'architecture': {'$ref': '#/definitions/architecture'}, 'git': {'$ref': '#/definitions/gitInfo'}, 'contextDir': {'type': 'string'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'pushRepository': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}, 'allOf': [{'if': {'properties': {'recipe': {'const': 'Source'}}}, 'then': {'properties': {'catkinParameters': {'$ref': '#/definitions/catkinParameters'}}}}, {'if': {'properties': {'recipe': {'const': 'Docker'}}}, 'then': {'properties': {'dockerfile': {'type': 'string', 'default': 'Dockerfile'}, 'pullSecret': {'$ref': '#/definitions/secretGUID'}}}}], 'required': ['recipe', 'architecture', 'git'], 'dependencies': {'pushRepository': {'required': ['pushSecret']}}}, rule='type')
    try:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "recipe" in data_keys:
                data_keys.remove("recipe")
                data__recipe = data["recipe"]
                if data__recipe != "Source":
                    raise JsonSchemaValueException("data.recipe must be same as const definition: Source", value=data__recipe, name="data.recipe", definition={'const': 'Source'}, rule='const')
    except JsonSchemaValueException:
        pass
    else:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "catkinParameters" in data_keys:
                data_keys.remove("catkinParameters")
                data__catkinParameters = data["catkinParameters"]
                validate___definitions_catkinparameters(data__catkinParameters, custom_formats)
    try:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "recipe" in data_keys:
                data_keys.remove("recipe")
                data__recipe = data["recipe"]
                if data__recipe != "Docker":
                    raise JsonSchemaValueException("data.recipe must be same as const definition: Docker", value=data__recipe, name="data.recipe", definition={'const': 'Docker'}, rule='const')
    except JsonSchemaValueException:
        pass
    else:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "dockerfile" in data_keys:
                data_keys.remove("dockerfile")
                data__dockerfile = data["dockerfile"]
                if not isinstance(data__dockerfile, (str)):
                    raise JsonSchemaValueException("data.dockerfile must be string", value=data__dockerfile, name="data.dockerfile", definition={'type': 'string', 'default': 'Dockerfile'}, rule='type')
            else: data["dockerfile"] = 'Dockerfile'
            if "pullSecret" in data_keys:
                data_keys.remove("pullSecret")
                data__pullSecret = data["pullSecret"]
                validate___definitions_secretguid(data__pullSecret, custom_formats)
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['recipe', 'architecture', 'git']):
            raise JsonSchemaValueException("data must contain ['recipe', 'architecture', 'git'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'recipe': {'$ref': '#/definitions/buildRecipe'}, 'architecture': {'$ref': '#/definitions/architecture'}, 'git': {'$ref': '#/definitions/gitInfo'}, 'contextDir': {'type': 'string'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'pushRepository': {'type': 'string'}, 'pushSecret': {'type': 'string'}, 'tagName': {'type': 'string'}, 'triggerName': {'type': 'string'}, 'webhookURL': {'type': 'string'}}, 'allOf': [{'if': {'properties': {'recipe': {'const': 'Source'}}}, 'then': {'properties': {'catkinParameters': {'$ref': '#/definitions/catkinParameters'}}}}, {'if': {'properties': {'recipe': {'const': 'Docker'}}}, 'then': {'properties': {'dockerfile': {'type': 'string', 'default': 'Dockerfile'}, 'pullSecret': {'$ref': '#/definitions/secretGUID'}}}}], 'required': ['recipe', 'architecture', 'git'], 'dependencies': {'pushRepository': {'required': ['pushSecret']}}}, rule='required')
        if "pushRepository" in data:
            data_is_dict = isinstance(data, dict)
            if data_is_dict:
                data_len = len(data)
                if not all(prop in data for prop in ['pushSecret']):
                    raise JsonSchemaValueException("data must contain ['pushSecret'] properties", value=data, name="data", definition={'required': ['pushSecret']}, rule='required')
        data_keys = set(data.keys())
        if "recipe" in data_keys:
            data_keys.remove("recipe")
            data__recipe = data["recipe"]
            validate___definitions_buildrecipe(data__recipe, custom_formats)
        if "architecture" in data_keys:
            data_keys.remove("architecture")
            data__architecture = data["architecture"]
            validate___definitions_architecture(data__architecture, custom_formats)
        if "git" in data_keys:
            data_keys.remove("git")
            data__git = data["git"]
            validate___definitions_gitinfo(data__git, custom_formats)
        if "contextDir" in data_keys:
            data_keys.remove("contextDir")
            data__contextDir = data["contextDir"]
            if not isinstance(data__contextDir, (str)):
                raise JsonSchemaValueException("data.contextDir must be string", value=data__contextDir, name="data.contextDir", definition={'type': 'string'}, rule='type')
        if "rosDistro" in data_keys:
            data_keys.remove("rosDistro")
            data__rosDistro = data["rosDistro"]
            validate___definitions_rosdistro(data__rosDistro, custom_formats)
        if "pushRepository" in data_keys:
            data_keys.remove("pushRepository")
            data__pushRepository = data["pushRepository"]
            if not isinstance(data__pushRepository, (str)):
                raise JsonSchemaValueException("data.pushRepository must be string", value=data__pushRepository, name="data.pushRepository", definition={'type': 'string'}, rule='type')
        if "pushSecret" in data_keys:
            data_keys.remove("pushSecret")
            data__pushSecret = data["pushSecret"]
            if not isinstance(data__pushSecret, (str)):
                raise JsonSchemaValueException("data.pushSecret must be string", value=data__pushSecret, name="data.pushSecret", definition={'type': 'string'}, rule='type')
        if "tagName" in data_keys:
            data_keys.remove("tagName")
            data__tagName = data["tagName"]
            if not isinstance(data__tagName, (str)):
                raise JsonSchemaValueException("data.tagName must be string", value=data__tagName, name="data.tagName", definition={'type': 'string'}, rule='type')
        if "triggerName" in data_keys:
            data_keys.remove("triggerName")
            data__triggerName = data["triggerName"]
            if not isinstance(data__triggerName, (str)):
                raise JsonSchemaValueException("data.triggerName must be string", value=data__triggerName, name="data.triggerName", definition={'type': 'string'}, rule='type')
        if "webhookURL" in data_keys:
            data_keys.remove("webhookURL")
            data__webhookURL = data["webhookURL"]
            if not isinstance(data__webhookURL, (str)):
                raise JsonSchemaValueException("data.webhookURL must be string", value=data__webhookURL, name="data.webhookURL", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_rosdistro(data, custom_formats={}):
    if data not in ['melodic', 'kinetic', 'noetic']:
        raise JsonSchemaValueException("data must be one of ['melodic', 'kinetic', 'noetic']", value=data, name="data", definition={'enum': ['melodic', 'kinetic', 'noetic']}, rule='enum')
    return data

def validate___definitions_gitinfo(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'repository': {'type': 'string'}, 'gitRef': {'type': 'string'}, 'secret': {'$ref': '#/definitions/secretGUID'}}, 'required': ['repository']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['repository']):
            raise JsonSchemaValueException("data must contain ['repository'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'repository': {'type': 'string'}, 'gitRef': {'type': 'string'}, 'secret': {'$ref': '#/definitions/secretGUID'}}, 'required': ['repository']}, rule='required')
        data_keys = set(data.keys())
        if "repository" in data_keys:
            data_keys.remove("repository")
            data__repository = data["repository"]
            if not isinstance(data__repository, (str)):
                raise JsonSchemaValueException("data.repository must be string", value=data__repository, name="data.repository", definition={'type': 'string'}, rule='type')
        if "gitRef" in data_keys:
            data_keys.remove("gitRef")
            data__gitRef = data["gitRef"]
            if not isinstance(data__gitRef, (str)):
                raise JsonSchemaValueException("data.gitRef must be string", value=data__gitRef, name="data.gitRef", definition={'type': 'string'}, rule='type')
        if "secret" in data_keys:
            data_keys.remove("secret")
            data__secret = data["secret"]
            validate___definitions_secretguid(data__secret, custom_formats)
    return data

def validate___definitions_architecture(data, custom_formats={}):
    if data not in ['amd64', 'arm32v7', 'arm64v8']:
        raise JsonSchemaValueException("data must be one of ['amd64', 'arm32v7', 'arm64v8']", value=data, name="data", definition={'enum': ['amd64', 'arm32v7', 'arm64v8']}, rule='enum')
    return data

def validate___definitions_buildrecipe(data, custom_formats={}):
    if data not in ['Docker', 'Source']:
        raise JsonSchemaValueException("data must be one of ['Docker', 'Source']", value=data, name="data", definition={'enum': ['Docker', 'Source']}, rule='enum')
    return data

def validate___definitions_secretguid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^secret-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^secret-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^secret-[a-z]{24}$", value=data, name="data", definition={'type': 'string', 'pattern': '^secret-[a-z]{24}$'}, rule='pattern')
    return data

def validate___definitions_catkinparameters(data, custom_formats={}):
    if not isinstance(data, (list, tuple)):
        raise JsonSchemaValueException("data must be array", value=data, name="data", definition={'type': 'array', 'items': {'$ref': '#/definitions/catkinParameter'}}, rule='type')
    data_is_list = isinstance(data, (list, tuple))
    if data_is_list:
        data_len = len(data)
        for data_x, data_item in enumerate(data):
            validate___definitions_catkinparameter(data_item, custom_formats)
    return data

def validate___definitions_catkinparameter(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'rosPackages': {'type': 'string'}, 'cmakeArguments': {'type': 'string'}, 'makeArguments': {'type': 'string'}, 'catkinMakeArguments': {'type': 'string'}, 'blacklist': {'type': 'string'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "rosPackages" in data_keys:
            data_keys.remove("rosPackages")
            data__rosPackages = data["rosPackages"]
            if not isinstance(data__rosPackages, (str)):
                raise JsonSchemaValueException("data.rosPackages must be string", value=data__rosPackages, name="data.rosPackages", definition={'type': 'string'}, rule='type')
        if "cmakeArguments" in data_keys:
            data_keys.remove("cmakeArguments")
            data__cmakeArguments = data["cmakeArguments"]
            if not isinstance(data__cmakeArguments, (str)):
                raise JsonSchemaValueException("data.cmakeArguments must be string", value=data__cmakeArguments, name="data.cmakeArguments", definition={'type': 'string'}, rule='type')
        if "makeArguments" in data_keys:
            data_keys.remove("makeArguments")
            data__makeArguments = data["makeArguments"]
            if not isinstance(data__makeArguments, (str)):
                raise JsonSchemaValueException("data.makeArguments must be string", value=data__makeArguments, name="data.makeArguments", definition={'type': 'string'}, rule='type')
        if "catkinMakeArguments" in data_keys:
            data_keys.remove("catkinMakeArguments")
            data__catkinMakeArguments = data["catkinMakeArguments"]
            if not isinstance(data__catkinMakeArguments, (str)):
                raise JsonSchemaValueException("data.catkinMakeArguments must be string", value=data__catkinMakeArguments, name="data.catkinMakeArguments", definition={'type': 'string'}, rule='type')
        if "blacklist" in data_keys:
            data_keys.remove("blacklist")
            data__blacklist = data["blacklist"]
            if not isinstance(data__blacklist, (str)):
                raise JsonSchemaValueException("data.blacklist must be string", value=data__blacklist, name="data.blacklist", definition={'type': 'string'}, rule='type')
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