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
from taurus import warning
from taurus.qt.qtgui.application import TaurusApplication


EP_GROUP_PLOT = "taurus.alt.plots"


def _print_alts(group):
    alts = [ep.name for ep in selectEntryPoints(group)]
    print("Available alternatives :\n {}\n".format("\n ".join(alts)))


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
            pass
    raise ImportError("Could not load any class from {}".format(eps))


x_axis_mode_option = click.option(
    "-x",
    "--x-axis-mode",
    "x_axis_mode",
    type=click.Choice(["t", "n"]),
    default="n",
    show_default=True,
    help=(
        'X axis mode. "t" implies using a Date axis'
        + '"n" uses the regular axis'
    ),
)


@click.command("plot")
@taurus.cli.common.models
@taurus.cli.common.config_file
@x_axis_mode_option
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
        w.set_x_axis_mode(x_axis_mode)
    except Exception as e:
        warning(
            "Could not set X axis mode to '%s' on %s plot. Reason: %s",
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
                "Could not load config file '%s' on %s plot. Reason: %s",
                config_file,
                epname,
                e
            )
        sys.exit(1)

    if models:
        w.setModel(models)

    w.show()
    sys.exit(app.exec_())

