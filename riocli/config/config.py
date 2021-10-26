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
import errno
import json
import os

from click import get_app_dir
from rapyuta_io import Client

from riocli.exceptions import LoggedOut, NoProjectSelected


class Configuration(object):
    """
    Configuration defines a class to define operations on the CLI's configuration file centrally.
    The class can be initialized irrespective of if the actual file exists or not. The object will
    automatically read the file if one exists and exposes the data through the `data` field.

    Example config:
        {
            "email_id": "<user-email>",
            "password": "<user-password>",
            "auth_token": "<rapyuta-auth-token>",
            "project_id": "<project-guid>"
        }
    """
    APP_NAME = "rio-cli"

    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.exists = True

        # If config file does not exist, then initialize an empty dictionary instead.
        if not os.path.exists(self.filepath):
            self.exists = False
            self.data = dict()
            return

        with open(self.filepath, 'r') as config_file:
            self.data = json.load(config_file)

    def save(self):
        if not os.path.exists(self.filepath):
            try:
                os.makedirs(os.path.dirname(self.filepath))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(self.filepath, 'w') as config_file:
            json.dump(self.data, config_file)

    def new_client(self, with_project: bool = True) -> Client:
        if 'auth_token' not in self.data:
            raise LoggedOut

        if 'environment' in self.data:
            os.environ['RIO_CONFIG'] = self.filepath

        token = self.data.get('auth_token', None)
        project = self.data.get('project_id', None)
        if with_project and project is None:
            raise NoProjectSelected

        return Client(auth_token=token, project=project)

    def get_auth_header(self) -> dict:
        if not ('auth_token' in self.data and 'project_id' in self.data):
            raise LoggedOut

        token, project = self.data['auth_token'], self.data['project_id']
        if not token.startswith('Bearer'):
            token = 'Bearer {}'.format(token)

        return dict(Authorization=token, project=project)

    @property
    def filepath(self) -> str:
        path = self._filepath
        if path is None:
            path = os.path.join(get_app_dir(self.APP_NAME), "config.json")
        return os.path.abspath(path)

    @filepath.setter
    def filepath(self, value: str):
        self._filepath = value

    @property
    def piping_server(self):
        if 'piping_server' in self.data:
            return self.data['piping_server']
        
        return 'https://piping-axylr.ep-r.io'
