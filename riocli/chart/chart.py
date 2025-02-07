# Copyright 2024 Rapyuta Robotics
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
from riocli.constants import Colors


class Chart(Munch):
    def __init__(self, *args, **kwargs):
        super(Chart, self).__init__(*args, **kwargs)
        self.tmp_dir = None
        self.downloaded = False

    def apply_chart(
        self,
        values: str = None,
        secrets: str = None,
        delete_existing: bool = False,
        dryrun: bool = False,
        workers: int = 6,
        retry_count: int = 50,
        retry_interval: int = 6,
        silent: bool = False,
    ):
        if not self.downloaded:
            self.download_chart()
        templates_dir = Path(self.tmp_dir.name, self.name, "templates")
        if not values:
            values = Path(self.tmp_dir.name, self.name, "values.yaml").as_posix()

        apply.callback(
            values=values,
            secrets=secrets,
            files=[templates_dir],
            retry_count=retry_count,
            retry_interval=retry_interval,
            delete_existing=delete_existing,
            dryrun=dryrun,
            workers=workers,
            silent=silent,
        )

    def delete_chart(
        self,
        values: str = None,
        secrets: str = None,
        dryrun: bool = None,
        silent: bool = False,
    ):
        if not self.downloaded:
            self.download_chart()

        templates_dir = Path(self.tmp_dir.name, self.name, "templates")
        if not values:
            values = Path(self.tmp_dir.name, self.name, "values.yaml").as_posix()

        delete.callback(
            values=values,
            files=[templates_dir],
            secrets=secrets,
            dryrun=dryrun,
            silent=silent,
        )

    def download_chart(self):
        self._create_temp_directory()
        click.secho(
            "Downloading {}:{} chart in {}".format(
                self.name, self.version, self.tmp_dir.name
            ),
            fg=Colors.CYAN,
        )
        chart_filepath = Path(self.tmp_dir.name, self._chart_filename())

        with open(chart_filepath, "wb") as f:
            resp = requests.get(self.urls[0])
            f.write(resp.content)

        self.extract_chart()
        self.downloaded = True

    def extract_chart(self):
        try:
            chart_filepath = Path(self.tmp_dir.name, self._chart_filename())
            with tarfile.open(chart_filepath) as tarball:
                tarball.extractall(path=self.tmp_dir.name)
        except Exception as e:
            raise e

    def cleanup(self):
        if self.tmp_dir:
            self.tmp_dir.cleanup()

    def _chart_filename(self):
        return self.urls[0].split("/")[-1]

    def _create_temp_directory(self):
        prefix = "rio-chart-{}-".format(self.name)
        self.tmp_dir = TemporaryDirectory(prefix=prefix)
