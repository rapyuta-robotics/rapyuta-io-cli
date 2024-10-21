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
import click
from click_help_colors import HelpColorsGroup
from click_spinner import spinner
from rapyuta_io import TopicsStatus
from rapyuta_io.clients.device import QoS, TopicKind

from riocli.config import new_client
from riocli.device.util import name_to_guid
from riocli.utils import tabulate_data


@click.group(
    "topics",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def device_topics():
    """
    ROS Topics on the Device
    """
    pass


@device_topics.command("list")
@click.argument("device-name", type=str)
@name_to_guid
def list_topics(device_name: str, device_guid: str) -> None:
    """
    Lists all the available topics for the Device
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        _display_topic_list(device.topic_status())
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@device_topics.command("subscribe")
@click.argument("device-name", type=str)
@click.argument("topic", type=str)
@click.argument("kind", type=click.Choice(["metric", "log"]))
@name_to_guid
def subscribe_topic(device_name: str, device_guid: str, topic: str, kind: str) -> None:
    """
    Subscribes the topics to start collecting it
    """
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            kind = TopicKind(kind.upper())
            device.subscribe_topic(topic, qos=QoS.LOW.value, kind=kind)
        click.secho("Topic subscribed successfully", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@device_topics.command("unsubscribe")
@click.argument("device-name", type=str)
@click.argument("topic", type=str)
@click.argument("kind", type=click.Choice(["metric", "log"]))
@name_to_guid
def unsubscribe_topic(device_name: str, device_guid: str, topic: str, kind: str) -> None:
    """
    Un-subscribes the topics to stop collecting it
    """
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            kind = TopicKind(kind.upper())
            device.unsubscribe_topic(topic, kind=kind)
        click.secho("Topic un-subscribed successfully", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


def _display_topic_list(status: TopicsStatus, show_header: bool = True) -> None:
    if status.master_up:
        click.secho("ROS Master is {}".format(click.style("Up", fg="green")))
    else:
        click.secho("ROS Master is {}".format(click.style("Down", fg="red")))

    headers = []
    if show_header:
        headers = ("Name", "Type", "Status")

    data = []
    for topic in status.Subscribed.metric:
        data.append([topic.name, "Metric", "Subscribed"])

    for topic in status.Subscribed.log:
        data.append([topic.name, "Log", "Subscribed"])

    for topic in status.Unsubscribed:
        data.append([topic, "", "Un-Subscribed"])

    tabulate_data(data, headers)
