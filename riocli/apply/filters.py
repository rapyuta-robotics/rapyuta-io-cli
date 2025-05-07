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
"""
Filters to use in the manifests.
"""

from functools import lru_cache
import os
from typing import Dict, List

from riocli.config import new_client
from riocli.device.util import find_device_guid


def getenv(default: str, env_var: str) -> str:
    """Get the value of an environment variable.

    Usage:
        "foo" : {{ "bar" | getenv('FOO') }}

    Args:
        env_var: The environment variable to get the value of.
        default: The default value to return if the environment variable is not set.

    Returns:
        The value of the environment variable.
    """
    return os.getenv(env_var, default)


def get_interface_ip(device_name: str, interface: str) -> str:
    """Get the IP address of an interface on a device.

    Usage:
        "ip" : {{ device_name | get_intf_ip(interface='intf-name') }}
        "ip" : {{ device_name | get_intf_ip(interface='intf1,intf2') }}

    Args:
        device_name: The name of the device.
        interface: The comma-separated list of the interfaces.

    Returns:
        The IP address of the first interface from the list that is available.

    Raises:
        Exception: If the interface is not available on the device.
    """

    splits = interface.split(",")

    ip_interfaces = get_device_ip_interfaces(device_name)

    for split in splits:
        ip_interface = ip_interfaces.get(split, None)
        if ip_interface is not None:
            if len(ip_interface) == 0 or len(ip_interface[0]) == 0:
                continue

            return ip_interface[0]

    raise Exception(f'interface "{interface}" not found on device "{device_name}"')


@lru_cache
def get_device_ip_interfaces(device_name: str) -> Dict[str, List[str]]:
    client = new_client(with_project=True)
    device_id = find_device_guid(client, device_name)

    device = client.get_device(device_id)
    try:
        device.poll_till_ready(retry_count=50, sleep_interval=10)
    except Exception as e:
        raise e

    device.refresh()

    return device.ip_interfaces
