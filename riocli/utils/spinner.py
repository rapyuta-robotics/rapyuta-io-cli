# Copyright 2023 Rapyuta Robotics
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

import functools

from yaspin import kbi_safe_yaspin


def with_spinner(**spin_kwargs):
    """
    Decorator for wrapping your function with a spinner

    Add `spinner=None` in your function's arguments. You can use the
    `yaspin` spinner object as it and don't have to worry about starting
    and stopping the spinner

        @with_spinner(text="Do something..", timer=True)
        def do_something(arg1, spinner=None):
            with spinner.hidden(): # doesn't break spinner
                click.secho("Fetching something...")

            ok = does_something(arg1)

            if ok:
                spinner.ok("✅")
            else:
                spinner.fail("✘")
                raise SystemExit(1)
    """

    def decorated(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with kbi_safe_yaspin(**spin_kwargs) as spinner:
                kwargs['spinner'] = spinner
                return func(*args, **kwargs)

        return wrapper

    return decorated
