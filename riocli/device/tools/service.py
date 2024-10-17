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

from riocli.device.util import name_to_guid
from riocli.utils.execute import run_on_device


@click.command("status-all")
@click.argument("device-name", type=str)
@name_to_guid
def status_all(device_name: str, device_guid: str) -> None:
    """Get the status of all services on the device."""
    try:
        remote_service_cmd_list = ["service", "--status-all"]
        response = run_on_device(device_guid=device_guid, command=remote_service_cmd_list)
        click.secho(response)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


def run_service_cmd(device_guid, service_name, service_cmd=""):
    """Run a service command on the device."""
    try:
        remote_service_cmd_list = ["service", service_name, service_cmd]
        response = run_on_device(device_guid=device_guid, command=remote_service_cmd_list)
        click.secho(response)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@click.command("status")
@click.argument("device-name", type=str)
@click.argument("service-name", nargs=1)
@name_to_guid
def status(device_name: str, device_guid: str, service_name) -> None:
    """Get the status of a service on the device."""
    run_service_cmd(device_guid, service_name, "status")


@click.command("start")
@click.argument("device-name", type=str)
@click.argument("service-name", nargs=1)
@name_to_guid
def start(device_name: str, device_guid: str, service_name) -> None:
    """Start a service on the device."""
    run_service_cmd(device_guid, service_name, "start")


@click.command("stop")
@click.argument("device-name", type=str)
@click.argument("service-name", nargs=1)
@name_to_guid
def stop(device_name: str, device_guid: str, service_name) -> None:
    """Stop a service on the device."""
    run_service_cmd(device_guid, service_name, "stop")


@click.command("reload")
@click.argument("device-name", type=str)
@click.argument("service-name", nargs=1)
@name_to_guid
def reload(device_name: str, device_guid: str, service_name) -> None:
    """Reload a service on the device."""
    run_service_cmd(device_guid, service_name, "reload")


@click.command("force-reload")
@click.argument("device-name", type=str)
@click.argument("service-name", nargs=1)
@name_to_guid
def force_reload(device_name: str, device_guid: str, service_name) -> None:
    """Force reload a service on the device."""
    run_service_cmd(device_guid, service_name, "force_reload")


@click.command("restart")
@click.argument("device-name", type=str)
@click.argument("service-name", nargs=1)
@name_to_guid
def restart(device_name: str, device_guid: str, service_name) -> None:
    """Restart a service on the device."""
    run_service_cmd(device_guid, service_name, "restart")


@click.group(hidden=True)
def service():
    """System management commands for services on the device.

    Offers a set of commands to manage services on the device.
    """
    pass


service.add_command(start)
service.add_command(stop)
service.add_command(status)
service.add_command(status_all)
service.add_command(reload)
service.add_command(force_reload)
service.add_command(restart)
