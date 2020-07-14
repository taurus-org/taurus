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
from .taurustrend import TaurusTrend
import taurus.cli.common


x_axis_mode = click.option(
    "-x", "--x-axis-mode", "x_axis_mode",
    type=click.Choice(['t', 'n']),
    default='n',
    show_default=True,
    help=('X axis mode. "t" implies using a Date axis'
          + '"n" uses the regular axis'),
)

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


@click.group('qwt5')
def qwt5():
    """[DEPRECATED] use "taurus plot" or "taurus trend" instead"""
    pass


@qwt5.command('plot')
@taurus.cli.common.models
@taurus.cli.common.config_file
@x_axis_mode
@taurus.cli.common.demo
@taurus.cli.common.window_name("TaurusPlot (qwt5)")
def plot_cmd(models, config_file, x_axis_mode, demo, window_name):
    """[DEPRECATED] use "taurus plot" instead"""
    from .taurusplot import plot_main
    return plot_main(models=models,
                     config_file=config_file,
                     x_axis_mode=x_axis_mode,
                     demo=demo,
                     window_name=window_name
                     )


@qwt5.command('trend')
@taurus.cli.common.models
@x_axis_mode
@taurus.cli.common.config_file
@taurus.cli.common.demo
@taurus.cli.common.window_name('TaurusTrend(qwt5)')
@buffer(TaurusTrend.DEFAULT_MAX_BUFFER_SIZE)
@click.option('-a', '--use-archiving', 'use_archiving',
              is_flag=True,
              default=False,
              help='enable automatic archiving queries')
@click.option('-r', '--forced-read', 'forced_read_period', type=int,
              default=-1,
              metavar="MILLISECONDS",
              help="force re-reading of the attributes every MILLISECONDS ms")
def trend_cmd(models, x_axis_mode, config_file, demo, window_name,
              max_buffer_size, use_archiving, forced_read_period):
    """[DEPRECATED] use "taurus trend" instead"""
    from .taurustrend import trend_main
    return trend_main(models=models,
                      config_file=config_file,
                      x_axis_mode=x_axis_mode,
                      use_archiving=use_archiving,
                      max_buffer_size=max_buffer_size,
                      forced_read_period=forced_read_period,
                      demo=demo,
                      window_name=window_name
                      )


if __name__ == '__main__':
    qwt5()
