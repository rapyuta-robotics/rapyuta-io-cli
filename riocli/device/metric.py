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
import typing

import click
from click_help_colors import HelpColorsGroup
from click_spinner import spinner
from rapyuta_io.clients import Metric
from rapyuta_io.clients.device import SystemMetric

from riocli.config import new_client
from riocli.device.util import name_to_guid


@click.group(
    'metrics',
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def device_metrics():
    """
    Device Metrics
    """
    pass


@device_metrics.command('list')
@click.argument('device-name', type=str)
@name_to_guid
def list_metrics(device_name: str, device_guid: str) -> None:
    """
    Lists all the available metrics for the Device
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        metrics = device.metrics()
        _display_metric_list(metrics, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_metrics.command('subscribe')
@click.argument('device-name', type=str)
@click.argument('metric', type=click.Choice(['cpu', 'memory', 'disk', 'diskio', 'network', 'wireless']))
@name_to_guid
def subscribe_metrics(device_name: str, device_guid: str, metric: str) -> None:
    """
    Subscribes the metrics to start collecting it
    """
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            device.subscribe_metric(SystemMetric(metric))
        click.secho('Metrics subscribed successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_metrics.command('unsubscribe')
@click.argument('device-name', type=str)
@click.argument('metric', type=click.Choice(['cpu', 'memory', 'disk', 'diskio', 'network', 'wireless']))
@name_to_guid
def unsubscribe_metrics(device_name: str, device_guid: str, metric: str) -> None:
    """
    Un-subscribes the metrics to stop collecting it
    """
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            device.unsubscribe_metric(SystemMetric(metric))
        click.secho('Metrics un-subscribed successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_metric_list(metrics: typing.List[Metric], show_header: bool = True) -> None:
    if show_header:
        click.secho('{:30} {:10} {:15}'.format('Name', 'Type', 'Status'), fg='yellow')

    for metric in metrics:
        click.secho('{:30} {:10} {:15}'.format(metric.name, metric.kind.capitalize(),
                                              metric.status.capitalize()))
