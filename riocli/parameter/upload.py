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
#   tree_names, paths?
#   delete_existing? 

#   If dry_run:
#      then do a diff
#   else 
#     upload

@io_client_required
def upload_configurations(io_client, args, settings):
    """
    Upload a set of configurations to IO.

    Compile the IO configurations from the paths provided. Output to a temporary directory. Upload the directory.
    """
    paths = args.paths

    configurations = compile_local_configurations(paths, tree_names=args.configurations)

    d_tmp = mkdtemp() # Temporary directory to hold the merged configurations

    rev_paths = list(reversed(paths)) # path list in reverse order

    for rel_file_path, configuration in configurations.items():
        file_path = os.path.join(d_tmp, rel_file_path)
        file_name, file_extension = os.path.splitext(file_path) # f is a file name with extension

        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError:
            pass

        if file_extension == '.yaml':
            with open(file_path, 'w') as fp:
                fp.write(yaml.safe_dump(configuration, indent=4))
                log.debug("Wrote file '{}'".format(file_path))
        else:
            for src_path in rev_paths:
                src = os.path.abspath(os.path.join(src_path, rel_file_path))
                try:
                    copyfile(src, file_path)
                except IOError:
                    # file not found in this directory, try the next
                    pass
                else:
                    # copied the file, break out of the loop
                    log.debug("Copied file '{}' to '{}'".format(src, file_path))
                    break

    # Download the current configurations to diff against later
    tmp_dir = download_configurations(io_client=io_client, args=args, settings=settings)
    remote_configuration = parse_configurations(tmp_dir)

    # Upload the temporary directory
    if args.test is False:
        return io_client.upload_configurations(d_tmp, delete_existing_trees=True)

    return list(diff(remote_configuration, configurations))

