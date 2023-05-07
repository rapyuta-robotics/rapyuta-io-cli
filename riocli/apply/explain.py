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
from pathlib import Path

import click
from click_help_colors import HelpColorsCommand

from riocli.constants import Colors, Symbols


@click.command(
    'explain',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    help='Generates a sample resource manifest for the given type'
)
@click.option('--templates', help='Alternate root for templates',
              default=None)
@click.argument('resource')
def explain(resource: str, templates: str = None) -> None:
    if templates:
        path = Path(templates)
    else:
        path = Path(__file__).parent.joinpath('manifests')

    for each in path.glob('**/*'):
        if resource + '.yaml' == each.name:
            with open(each) as f:
                click.echo_via_pager(f.readlines())
                raise SystemExit(0)

    click.secho('{} Resource "{}" not found'.format(Symbols.ERROR, resource),
                fg=Colors.RED)
    raise SystemExit(1)
