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

# -----------------------------------------------------------------------------
#
# Configurations
# Args
#    path,  tree_names,  delete_existing=True|False
# -----------------------------------------------------------------------------
@io_client_required
def download_configurations(io_client, args, settings):
    """
    Download the configurations
    """

    path = getattr(args, 'path', None)

    if path is None:
        path = mkdtemp() # Temporary directory to hold the configurations

    try:
        io_client.download_configurations(path, tree_names=args.configurations, delete_existing_trees=True)
    except (APIError, InternalServerError) as e:
        print("failed API request", e.tree_path, e)
    except (IOError, OSError) as e:
        print("failed file/directory creation", e)

    log.debug("Downloaded IO configurations to '{}'".format(path))

    return path


