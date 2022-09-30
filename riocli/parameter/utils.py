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
import os
import yaml
from copy import copy, deepcopy
import six


# To run docstring tests
# python -m doctest -v doctest_simple.py

# Copyright Ferry Boender, released under the MIT license.
def deep_merge(tgt, src):
	"""Deep update target dict with src
	For each k,v in src: if k doesn't exist in target, it is deep copied from
	src to target. Otherwise, if v is a list, target[k] is replaced with
	src[k]. If v is a set, target[k] is updated with v, If v is a dict,
	recursively deep-update it.

	Examples:
	>>> t = {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi']}
	>>> print deep_merge(t, {'hobbies': ['gaming']})
	{'name': 'Ferry', 'hobbies': ['gaming']}
	"""
	target = deepcopy(tgt)
	for k, v in six.iteritems(src):
		if type(v) == list:
			target[k] = deepcopy(v)
		elif type(v) == dict:
			if not k in target:
				target[k] = deepcopy(v)
			else:
				target[k] = deep_merge(target[k], v)
		elif type(v) == set:
			if not k in target:
				target[k] = v.copy()
			else:
				target[k].update(v.copy())
		else:
			target[k] = copy(v)
	return target


def compile_local_configurations(paths, tree_names=None):
    """
    Iterate over each path in "paths" and merge each
    Read the configuration files from the repository, merging the warehouse-specific configs
    over the top of the default configurations. Returns a single dict where the root keys
    are the relative file path for each config.
    """
    configurations = {}
    print(paths)
    for path in paths:
        abs_path = os.path.abspath(path)
        # log.debug("Compiling local configuration directory '{}'".format(abs_path))
        cfg = parse_configurations(abs_path, tree_names)
        print(configurations)
        print(cfg)
        configurations = deep_merge(configurations, cfg)

    return configurations



def parse_configurations(root_dir, tree_names=None):
    """
    Parse the configurations and return as a dict
    """
    configurations = {}

    for root, dirs, files in os.walk(root_dir, followlinks=True):
        for f in files:
            file_name, file_extension = os.path.splitext(f) # f is a file name with extension

            relpath = root[len(root_dir)+1:] # get relative path without leading /

            # Only upload certain sub-directories
            if tree_names:
                # Check top-level directory against list
                if relpath.split(os.sep)[0] not in tree_names:
                    continue

            contents = ""
            if file_extension == '.yaml':
                with open(os.path.join(root, f), 'r') as fp:
                    contents = yaml.safe_load(fp)

            configurations[os.path.join(relpath, f)] = contents

    return configurations



def show_configurations(args):
    """
    Show the local IO configuration
    """
    return compile_local_configurations(paths=args.paths, tree_names=args.configurations)

