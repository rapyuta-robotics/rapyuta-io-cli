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
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory

import click
import requests
from munch import Munch

from riocli.apply import apply, delete


class Chart(Munch):
    def __init__(self, *args, **kwargs):
        super(Chart, self).__init__(*args, **kwargs)
        self.tmp_dir = None
        self.downloaded = False

    def apply_chart(self, values: str = None, secrets:str = None, dryrun: bool = None, workers: int = 6):
        if not self.downloaded:
            self.download_chart()

        templates_dir = Path(self.tmp_dir.name, self.name, 'templates')
        if not values:
            values = Path(self.tmp_dir.name, self.name, 'values.yaml').as_posix()

            
        apply.callback(values=values, files=[templates_dir], secrets=secrets, dryrun=dryrun, workers=workers)

    def delete_chart(self, values: str = None, secrets:str = None, dryrun: bool = None):
        if not self.downloaded:
            self.download_chart()

        templates_dir = Path(self.tmp_dir.name, self.name, 'templates')
        if not values:
            values = Path(self.tmp_dir.name, self.name, 'values.yaml').as_posix()

        delete.callback(values=values, files=[templates_dir], secrets=secrets, dryrun=dryrun)

    def download_chart(self):
        self._create_temp_directory()
        click.secho('Downloading {}:{} chart in {}'.format(self.name, self.version, self.tmp_dir.name), fg='yellow')
        chart_filepath = Path(self.tmp_dir.name, self._chart_filename())

        with open(chart_filepath, 'wb') as f:
            resp = requests.get(self.urls[0])
            f.write(resp.content)

        self.extract_chart()
        self.downloaded = True

    def extract_chart(self):
        try:
            chart_filepath = Path(self.tmp_dir.name, self._chart_filename())
            chart_tarball = tarfile.open(chart_filepath)
            chart_tarball.extractall(path=self.tmp_dir.name)
        finally:
            if chart_tarball:
                chart_tarball.close()

    def cleanup(self):
        if self.tmp_dir:
            self.tmp_dir.cleanup()

    def _chart_filename(self):
        return self.urls[0].split('/')[-1]

    def _create_temp_directory(self):
        prefix = 'rio-chart-{}-'.format(self.name)
        self.tmp_dir = TemporaryDirectory(prefix=prefix)
