import functools
import re
import typing
import click
from riocli.constants import Colors
from riocli.config import new_hwil_client
from riocli.hwilclient import Client
from riocli.device.util import DeviceNotFound


def name_to_id(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        try:
            client = new_hwil_client()
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1)

        name = kwargs.pop('device_name')

        # device_name is not specified
        if name is None:
            f(**kwargs)
            return

        guid = None
        if guid is None:
            try:
                guid = find_device_id(client, name)
            except Exception as e:
                click.secho(str(e), fg=Colors.RED)
                raise SystemExit(1)

        kwargs['device_name'] = name
        kwargs['device_id'] = guid
        f(**kwargs)

    return decorated


def get_device(client: Client, name: str) -> str:
    devices = client.list_devices()
    for device in devices:
        if device.name == name:
            return device

    raise DeviceNotFound()


def find_device_id(client: Client, name: str) -> str:
    devices = client.list_devices()
    for device in devices:
        if device.name == name:
            return device.id

    raise DeviceNotFound(message="Hwil Device not found")

