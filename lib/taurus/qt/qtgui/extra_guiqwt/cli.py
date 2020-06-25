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

import click
import sys

@click.group('guiqwt')
def guiqwt():
    """[DEPRECATED] use "taurus image" or "taurus trend2d" instead"""
    print('"taurus guiqwt" subcommand is deprecated. '
          + 'Use "taurus image" or "taurus trend2d" instead\n')
    sys.exit(1)


@guiqwt.command()
def image():
    """[DEPRECATED] use "taurus image" instead"""
    sys.exit(1)


@guiqwt.command()
def trend2d():
    """[DEPRECATED] use "taurus trend2d" instead"""
    sys.exit(1)


if __name__ == '__main__':
    guiqwt()

