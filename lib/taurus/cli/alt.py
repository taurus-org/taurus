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

import sys
import click
import taurus.cli.common
from taurus.core.util.plugin import selectEntryPoints
from taurus import tauruscustomsettings as _ts
from taurus import warning, info
from taurus.qt.qtgui.application import TaurusApplication


EP_GROUP_PLOT = "taurus.plot.alts"
EP_GROUP_TREND = "taurus.trend.alts"


def _print_alts(group):
    alts = [ep.name for ep in selectEntryPoints(group)]
    print("Registered alternatives :\n {}\n".format("\n ".join(alts)))


def _load_class_from_group(group, include=(".*",), exclude=()):
    """
    Factory that returns the first available class from the group entry point.
    The selection is done among the classes registered in
    the `group` entry-point, prioritized according to the given
    `include` and `exclude` patterns
    (see :function:`taurus.core.util.plugin.selectEntryPoints`)
    """
    eps = selectEntryPoints(group, include=include, exclude=exclude)
    for ep in eps:
        try:
            return ep.load(), ep.name
        except:
            info("Cannot load %s", ep.name)
    raise ImportError("Could not load any class from {}".format(eps))


def x_axis_mode_option(default="n"):
    x_axis_mode_option = click.option(
        "-x",
        "--x-axis-mode",
        "x_axis_mode",
        type=click.Choice(["t", "n"]),
        default=default,
        show_default=True,
        help=('X axis mode. Use "t" for a time axis or "n" for a regular one'),
    )
    return x_axis_mode_option


def max_buffer_option(default):
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

forced_read_option = click.option(
    '-r',
    '--forced-read',
    'forced_read_period',
    type=int,
    default=-1,
    metavar="MILLISECONDS",
    help="force re-reading of the attributes every MILLISECONDS ms"
)


@click.command("plot")
@taurus.cli.common.models
@taurus.cli.common.config_file
@x_axis_mode_option("n")
@taurus.cli.common.demo
@taurus.cli.common.window_name("TaurusPlot")
@taurus.cli.common.use_alternative
@taurus.cli.common.list_alternatives
def plot_cmd(
        models, config_file, x_axis_mode, demo, window_name, use_alt, ls_alt
):
    """Shows a plot for the given models"""

    if ls_alt:
        _print_alts(EP_GROUP_PLOT)
        sys.exit(0)

    if use_alt is None:
        use_alt = getattr(_ts, "PLOT_IMPL", ".*")

    try:
        TPlot, epname = _load_class_from_group(EP_GROUP_PLOT, include=[use_alt])
    except:
        _print_alts(EP_GROUP_PLOT)
        sys.exit(1)

    app = TaurusApplication(app_name="taurusplot({})".format(epname))

    w = TPlot()
    w.setWindowTitle(window_name)

    if demo:
        models = list(models)
        models.extend(["eval:rand(100)", "eval:0.5*sqrt(arange(100))"])

    try:
        w.setXAxisMode(x_axis_mode)
    except Exception as e:
        warning(
            'Could not set X axis mode to "%s" on %s plot. Reason: "%s"',
            x_axis_mode,
            epname,
            e
        )
        sys.exit(1)

    if config_file is not None:
        try:
            w.loadConfigFile(config_file)
        except Exception as e:
            warning(
                'Could not load config file "%s" on %s plot. Reason: "%s"',
                config_file,
                epname,
                e
            )
        sys.exit(1)

    if models:
        w.setModel(models)

    w.show()
    sys.exit(app.exec_())


@click.command("trend")
@taurus.cli.common.models
@taurus.cli.common.config_file
@x_axis_mode_option("t")
@taurus.cli.common.demo
@taurus.cli.common.window_name("TaurusTrend")
@taurus.cli.common.use_alternative
@taurus.cli.common.list_alternatives
@max_buffer_option(None )
@forced_read_option
def trend_cmd(
        models,
        config_file,
        x_axis_mode,
        demo,
        window_name,
        use_alt,
        ls_alt,
        max_buffer_size,
        forced_read_period
):
    """Shows a trend for the given models"""

    # list alternatives option
    if ls_alt:
        _print_alts(EP_GROUP_TREND)
        sys.exit(0)

    # use alternative
    if use_alt is None:
        use_alt = getattr(_ts, "TREND_IMPL", ".*")

    # get the selected alternative
    try:
        TTrend, epname = _load_class_from_group(
            EP_GROUP_TREND,
            include=[use_alt]
        )
    except:
        _print_alts(EP_GROUP_TREND)
        sys.exit(1)

    app = TaurusApplication(app_name="taurustrend({})".format(epname))
    w = TTrend()

    # window title option
    w.setWindowTitle(window_name)

    # demo option
    if demo:
        models = list(models)
        models.extend(["eval:rand()", "eval:1+rand(2)"])

    # x axis mode option
    try:
        w.setXAxisMode(x_axis_mode)
    except Exception as e:
        warning(
            'Could not set X axis mode to "%s" on %s plot. Reason: "%s"',
            x_axis_mode,
            epname,
            e
        )
        sys.exit(1)

    # configuration file option
    if config_file is not None:
        try:
            w.loadConfigFile(config_file)
        except Exception as e:
            warning(
                'Could not load config file "%s" on %s plot. Reason: "%s"',
                config_file,
                epname,
                e
            )
        sys.exit(1)

    # max buffer size option
    if max_buffer_size is not None:
        try:
            w.setMaxDataBufferSize(max_buffer_size)
        except Exception as e:
            warning(
                'Could not set max buffer size on %s trend. Reason: "%s"',
                epname,
                e
            )
        sys.exit(1)

    # set models
    if models:
        w.setModel(list(models))

    # period option
    if forced_read_period > 0:
        w.setForcedReadingPeriod(forced_read_period)

    w.show()
    sys.exit(app.exec_())

