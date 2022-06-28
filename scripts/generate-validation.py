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
#
# Usage: python generate-validation.py
# Run it from the Root of the repository inside virtual-environment.

from yaml import safe_load
from pathlib import Path, PurePosixPath
from fastjsonschema import compile_to_code

schema_dir = Path('jsonschema')

# with open(schema_dir.joinpath('primitives.yaml')) as primitive:
#     primitives = safe_load(primitive.read())
#     primitives = primitives.get('definitions', None)

for schema in schema_dir.glob('*-schema.yaml'):
    print("processed {}".format(schema))
    base_path = Path('riocli').joinpath(schema)
    module_name = Path(base_path).stem.replace("-schema", "")
    module = Path('riocli').joinpath(module_name).\
        joinpath('validation.py')
    with open(schema) as f:
        body = safe_load(f.read())

    # Inject primitives
    # body['definitions'] = body['definitions'].extend(primitives)
    code = compile_to_code(body)
    module.write_text(code)
