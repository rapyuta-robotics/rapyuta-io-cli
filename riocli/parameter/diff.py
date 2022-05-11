# Copyright 2021 Rapyuta Robotics
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


# Args
#   cfg_dir = Path
#   tree_names = Array[String]
#   output_format  = yaml, gitdiff, patch 
# @io_client_required
def diff_configurations(io_client, args, settings):
    """
    Compare the local configurations with what is currently in IO
    """
    paths = args.paths

    cfg_dir = download_configurations(io_client=io_client, args=args, settings=settings)
    remote_configuration = parse_configurations(cfg_dir)

    local_configuration = compile_local_configurations(paths, tree_names=args.configurations)
    result = diff(remote_configuration, local_configuration)

    return yaml.safe_dump(list(result))

