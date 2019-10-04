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

import pkg_resources
import click
import taurus

@click.group('taurus')
@click.option('--log-level', 'log_level',
              type=click.Choice(['Critical', 'Error', 'Warning', 'Info',
                                 'Debug', 'Trace']),
              default='Info', show_default=True,
              help='Show only logs with priority LEVEL or above')
@click.option("--polling-period", "polling_period",
              type=click.INT, metavar="MILLISEC", default=None,
              help='Change the Default Taurus polling period')
@click.option("--serialization-mode", "serialization_mode",
              type=click.Choice(['Serial', 'Concurrent', 'TangoSerial']),
              default=None, show_default=True,
              help=("Set the default Taurus serialization mode for those "
                    + "models that do not explicitly define it)"))
@click.option("--rconsole", "rconsole_port", type=click.INT,
              metavar="PORT", default=None,
              help="Enable remote debugging with rfoo on the given PORT")
@click.option("--default-formatter", "default_formatter",
              type=click.STRING, metavar="FORMATTER", default=None,
              help="Override the default formatter (use with caution!)")
@click.version_option(version=taurus.Release.version)
def taurus_cmd(log_level, polling_period, serialization_mode, rconsole_port,
               default_formatter):
    """The main taurus command"""

    # set log level
    taurus.setLogLevel(getattr(taurus, log_level))

    # set polling period
    if polling_period is not None:
        taurus.changeDefaultPollingPeriod(polling_period)

    # set serialization mode
    if serialization_mode is not None:
        from taurus.core.taurusbasetypes import TaurusSerializationMode
        m = getattr(TaurusSerializationMode, serialization_mode)
        taurus.Manager().setSerializationMode(m)

    # enable the remote console port
    if rconsole_port is not None:
        try:
            import rfoo.utils.rconsole
            rfoo.utils.rconsole.spawn_server(port=rconsole_port)
            taurus.info(("rconsole started. "
                         + "You can connect to it by typing: rconsole -p %d"),
                        rconsole_port
                        )
        except Exception as e:
            taurus.warning("Cannot spawn debugger. Reason: %s", e)

    # set the default formatter
    if default_formatter is not None:
        from taurus import tauruscustomsettings
        setattr(tauruscustomsettings, 'DEFAULT_FORMATTER', default_formatter)


def register_subcommands():
    """Discover and add subcommands to taurus_cmd"""

    # Add subcommands from the taurus_subcommands entry point
    for ep in pkg_resources.iter_entry_points('taurus.cli.subcommands'):
        try:
            subcommand = ep.load()
            taurus_cmd.add_command(subcommand)
        except Exception as e:
            # -----------------------------------------------------------
            # Use info instead of warning in case of nonimportable Qwt5
            # (e.g. when using py3 or Qt5) to avoid spam
            # This special case can be removed when taurus.qt.qtgui.qwt5
            # is moved to a separate plugin, since the entry point will
            # be registered only if the plugin is installed
            if ep.name == 'qwt5':
                taurus.info(
                    'Cannot add "%s" subcommand to taurus. Reason: %r',
                    ep.name, e)
                continue
            # -----------------------------------------------------------
            taurus.warning('Cannot add "%s" subcommand to taurus. Reason: %r',
                           ep.name, e)


def main():
    """Register subcommands and run taurus_cmd"""

    # set the log level to WARNING avoid spamming the CLI while loading
    # subcommands
    # it will be restored to the desired one first thing in taurus_cmd()
    taurus.setLogLevel(taurus.Warning)

    #register the subcommands
    register_subcommands()

    # launch the taurus command
    taurus_cmd()


if __name__ == '__main__':
    main()