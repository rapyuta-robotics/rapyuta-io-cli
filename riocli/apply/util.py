# Copyright 2023 Rapyuta Robotics
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


def parse_variadic_path_args(path_item):
    glob_files = []
    abs_path = os.path.abspath(path_item)
    # make it absolute
    # does the path exist.
    #     is it a dir?  scan recursively
    #     not a dir but has  special characters in it?  [*?^!]
    #        assume it's a valid glob, use it to glob recursively
    #      if all else fails
    #        consider it a file path directly.
    if not os.path.exists(abs_path):
        return glob_files

    if os.path.isdir(abs_path):
        # TODO: Should we keep this recursive?
        return glob.glob(abs_path + "/**/*", recursive=True)

    return glob.glob(abs_path, recursive=True)


def process_files_values_secrets(files, values, secrets):
    glob_files = []

    for path_item in files:
        path_glob = parse_variadic_path_args(path_item)
        glob_files.extend([
            f for f in path_glob if os.path.isfile(f)
        ])

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
