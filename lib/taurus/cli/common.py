#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
This module provides the taurus Command Line Interface common options.

It is based on the click module to provide commonly used flags/options.
They are used by taurus commands and can be used by plugin to easily
extend its functionality.

Example 1: Add custom subcommand
script::

    import click

    import taurus.cli.common


    @click.command("bar")
    @taurus.cli.common.poll_period
    @taurus.cli.common.default_formatter
    @taurus.cli.common.window_name("Super Bar")
    def bar(poll_period, default_formatter, window_name):
        ...


    if __name__ == '__main__':
        bar()

Example 2: Add custom subcommands' group
script::

    import click

    import taurus.cli.common


    @click.group("foo")
    def foo():
        pass


    @foo.command('cmd1')
    @taurus.cli.common.models
    @taurus.cli.common.config_file
    @taurus.cli.common.window_name("Super Foo (cmd1)")
    def cmd1(models, config_file, window_name):
        ...


    @foo.command('trend')
    @taurus.cli.common.model
    @taurus.cli.common.serial_mode
    @taurus.cli.common.poll_period
    @taurus.cli.common.default_formatter
    def cmd2(model, serial_mode, poll_period, default_formatter):
        ...


    if __name__ == '__main__':
        foo()

"""

import click


__levels = ["Critical", "Error", "Warning", "Info", "Debug", "Trace"]
try:
    __log_choice = click.Choice(__levels, case_sensitive=False)
except TypeError:  # click v< 7 does not allow case_sensitive option
    __log_choice = click.Choice(__levels)


log_level = click.option(
    "--log-level",
    "log_level",
    type=__log_choice,
    default="Info",
    show_default=True,
    help="Show only logs with priority LEVEL or above",
)

config_file = click.option(
    "--config",
    "config_file",
    type=click.File("rb"),
    help="Configuration file for initialization",
)


def window_name(default):
    window_name = click.option(
        "--window-name",
        "window_name",
        default=default,
        help="Name of the window",
    )
    return window_name


models = click.argument("models", nargs=-1,)

demo = click.option("--demo", is_flag=True, help="Show a demo of the widget",)

model = click.argument("model", nargs=1, required=False,)

poll_period = click.option(
    "--polling-period",
    "polling_period",
    type=click.INT,
    metavar="MILLISEC",
    default=None,
    help="Change the Default Taurus polling period",
)

serial_mode = click.option(
    "--serialization-mode",
    "serialization_mode",
    type=click.Choice(["Serial", "Concurrent", "TangoSerial"]),
    default=None,
    show_default=True,
    help=(
        "Set the default Taurus serialization mode for those "
        + "models that do not explicitly define it)"
    ),
)

default_formatter = click.option(
    "--default-formatter",
    "default_formatter",
    type=click.STRING,
    metavar="FORMATTER",
    default=None,
    help="Override the default formatter (use with caution!)",
)

list_alternatives = click.option(
    "--ls-alt",
    is_flag=True,
    help="List the available alternative implementations",
)

use_alternative = click.option(
    "--use-alt",
    metavar="ALT",
    type=click.STRING,
    default=None,
    help="Use ALT alternative implementation",
)
