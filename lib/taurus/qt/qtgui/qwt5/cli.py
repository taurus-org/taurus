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
from taurus.cli import common as cli_common


@click.group('qwt5')
def qwt5():
    """Qwt5 related commands"""
    pass


@qwt5.command('plot')
@cli_common.models
@cli_common.config_file
@cli_common.x_axis_mode
@cli_common.demo
@cli_common.window_name("TaurusPlot (qwt5)")
def plot_cmd(models, config_file, x_axis_mode, demo, window_name):
    """Shows a plot for the given models"""
    from .taurusplot import plot_main
    return plot_main(models=models,
                     config_file=config_file,
                     x_axis_mode=x_axis_mode,
                     demo=demo,
                     window_name=window_name
                     )


@qwt5.command('trend')
@cli_common.models
@cli_common.x_axis_mode
@cli_common.config_file
@cli_common.demo
@cli_common.window_name
@cli_common.buffer(TaurusTrend.DEFAULT_MAX_BUFFER_SIZE)
@click.option('-a', '--use-archiving', 'use_archiving',
              is_flag=True,
              default=False,
              help='enable automatic archiving queries')
@click.option('-r', '--forced-read', 'forced_read_period', type=int,
              default=-1,
              metavar="MILLISECONDS",
              help="force re-reading of the attributes every MILLISECONDS ms")
def trend_cmd(models, x_axis_mode, use_archiving, max_buffer_size,
              forced_read_period, config_file, demo, window_name):
    """Shows a trend for the given models"""
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
