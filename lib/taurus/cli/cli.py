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
from taurus import Release, info

@click.group('taurus')
@click.version_option(version=Release.version)
def taurus_cmd():
    """The main taurus command"""
    pass


def main():
    # Add subcommands from the taurus_subcommands entry point
    for ep in pkg_resources.iter_entry_points('taurus.cli.subcommands'):
        try:
            subcommand = ep.load()
            taurus_cmd.add_command(subcommand)
        except Exception as e:
            info('Cannot load "%s" subcommand for taurus. Reason: %r',
                 ep.name, e)


    # launch the taurus command
    taurus_cmd()


if __name__ == '__main__':
    main()