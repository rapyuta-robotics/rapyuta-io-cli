from riocli.config import new_client
from riocli.device.util import find_device_guid


def get_interface_ip(device: str, interface: str, wait: bool) -> str:
    client = new_client(with_project=True)
    device_id = find_device_guid(client, device)

    device = client.get_device(device_id)
    try:
        device.poll_deployment_till_ready(retry_count=50, sleep_interval=6)
    except Exception as e:
        raise e

    device.refresh()

    for name in device.ip_interfaces:
        if name == interface:
            return device.ip_interfaces[name][0]

    raise Exception('Interface is not available on the Device')
