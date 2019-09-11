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


log_port = click.option('--port', 'port', type=int,
              default=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
              show_default=True,
              help='port where log server is running')

log_name = click.option('--log-name', 'log_name', default=None,
              help='filter specific log object')

log_level = click.option('--log-level', 'log_level',
              type=click.Choice(['critical', 'error', 'warning', 'info',
                                 'debug', 'trace']),
              default='debug', show_default=True,
              help='filter specific log level')

config_file = click.option('--config', 'config_file', type=click.File('rb'),
              help='configuration file for initialization')

def window_name(help):
    window_name = click.option('--window-name', 'window_name',
              default='TaurusPlot ' + help,
              help='Name of the window')
    return window_name

models = click.argument('models', nargs=-1)

x_axis_mode = click.option("-x", "--x-axis-mode", "x_axis_mode",
              type=click.Choice(['t', 'n']),
              default='n',
              show_default=True,
              help=('X axis mode. "t" implies using a Date axis'
                    + '"n" uses the regular axis')
              )

demo = click.option("--demo", is_flag=True, help="show a demo of the widget")
