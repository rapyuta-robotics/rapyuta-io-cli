import typing

import click

from riocli.constants import Colors
from riocli.v2client.errors import ERRORS


def process_errors(errors: typing.List[str]) -> str:
    err_fmt = '[{}] {}\nAction: {}'
    support_action = ('Report the issue together with the relevant'
                      ' details to the support team')

    action, description = '', ''
    msgs = []
    for code in errors:
        if code in ERRORS:
            description = ERRORS[code]['description']
            action = ERRORS[code]['action']
        elif code.startswith('DEP_E2'):
            description = 'Internal rapyuta.io error in the components deployed on cloud'
            action = support_action
        elif code.startswith('DEP_E3'):
            description = 'Internal rapyuta.io error in the components deployed on a device'
            action = support_action
        elif code.startswith('DEP_E4'):
            description = 'Internal rapyuta.io error'
            action = support_action

        code = click.style(code, fg=Colors.YELLOW)
        description = click.style(description, fg=Colors.RED)
        action = click.style(action, fg=Colors.GREEN)

        msgs.append(err_fmt.format(code, description, action))

    return '\n'.join(msgs)