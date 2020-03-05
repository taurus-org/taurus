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


from .plot import image_cmd
from .taurustrend2d import trend2d_cmd


def buffer(default):
    o = click.option(
        '-b', '--buffer', 'max_buffer_size',
        type=int,
        default=default,
        show_default=True,
        help=("Maximum number of values to be stacked "
              + "(when reached, the oldest values will be "
              + "discarded)"),
        )
    return o


@click.group('guiqwt')
def guiqwt():
    """guiqwt related commands (image, trend2d)"""
    pass


guiqwt.add_command(image_cmd)
guiqwt.add_command(trend2d_cmd)

if __name__ == '__main__':
    guiqwt()

