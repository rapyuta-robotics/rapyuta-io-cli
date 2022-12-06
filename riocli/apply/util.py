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

import glob
import os


def parse_varidac_pathargs(pathItem):
    glob_files = []
    abs_path = os.path.abspath(pathItem)
    # make it absolte
    # does the path exist.
    #     is it a dir?  scan recursively
    #     not a dir but has  special charaters in it?  [*?^!]
    #        assume its a valid glob, use it to glob recursively
    #      if all else fails
    #        consider it a file path directly.
    if os.path.exists(abs_path):
        if os.path.isdir(abs_path):
            # TODO: Should we keep this recursive?
            glob_files = glob.glob(abs_path + "/**/*", recursive=True)
        else:
            glob_files = glob.glob(abs_path, recursive=True)
    return glob_files


def process_files_values_secrets(files, values, secrets):
    glob_files = []

    for pathItem in files:
        path_glob = parse_varidac_pathargs(pathItem)
        glob_files.extend(path_glob)

    abs_values = values
    if values and values != "":
        abs_values = os.path.abspath(values)
        if abs_values in glob_files:
            glob_files.remove(abs_values)

    abs_secret = secrets
    if secrets and secrets != "":
        abs_secrets = os.path.abspath(secrets)
        if abs_secrets in glob_files:
            glob_files.remove(abs_secrets)

    glob_files = list(set(glob_files))
    return glob_files, abs_values, abs_secret
