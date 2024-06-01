import json

import click
import yaml
from click_help_colors import HelpColorsCommand
from riocli.constants import Colors
from riocli.hwil.util import name_to_id
from riocli.config import new_hwil_client


@click.command(
    'inspect',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--format', '-f', 'format_type',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.option('--filter', 'filter', multiple=True,
              type=click.Choice(['static_ip', 'ip_address', 'status'], case_sensitive=True),
              default=['static_ip', 'ip_address'])
@click.argument('device-name', type=str)
@name_to_id
def inspect_device(format_type: str,
                   filter: [],
                   device_name: str,
                   device_id: str) -> None:
    """
    Inspect the device resource
    """
    try:
        client = new_hwil_client()
        device = client.get_device(device_id)
        click.secho('{}'.format(",".join([getattr(device, f) for f in filter])))
        if format_type:
            if format_type == 'json':
                click.echo_via_pager(json.dumps(device, indent=4))
            elif format_type == 'yaml':
                click.echo_via_pager(yaml.dump(device, allow_unicode=True))
            else:
                raise Exception('Invalid format')
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
