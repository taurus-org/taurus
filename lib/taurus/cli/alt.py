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
This module provides several taurus CLI subcommands (plot, trend, image,...)
that show a widget which may have more than one alternative implementation.
The available registered implementations for each command can be listed with
the `--ls-alt` option. Specific implementations can be selected with the
`--use-alt` option.

These commands also honour the default implementation selection configured in
:mod:`taurus.tauruscustomsettings` via the `*_ALT` variables

The alternative implementations can be registered using the following
entry-point group names:

- `taurus.plot.alt`: the loaded object is expected to be a `TaurusPlot`
  implementation

- `taurus.trend.alt`: the loaded object is expected to be a `TaurusTrend`
  implementation

- `taurus.trend2d.alt`: the loaded object is expected to be a
  `TaurusTrend2dDialog` implementation

- `taurus.image.alt`: the loaded object is expected to be a `TaurusImageDialog`
  implementation


Expected API for alternative implementations
--------------------------------------------

When registering a widget class to be used for these commands, the classes need
to provide the following minimum API:

- For **all** the classes:
  - must be a Qt.QWidget
  - must implement `setModel()` and `getModel()` equivalent to those in
  :class:`taurus.qt.qtgui.base.TaurusBaseComponent`

- For TaurusPlot:
  - should implement `setXAxisMode(mode)` where mode is one of `"n"` or `"t"`
  - should implement `loadConfigFile(name)` equivalent to
  :meth:`taurus.qt.qtcore.configuration.BaseConfigurableClass.loadConfigFile`

- For TaurusTrend:
  - should implement `setXAxisMode(mode)` where mode is one of `"n"` or `"t"`
  - should implement  `loadConfigFile(name)` equivalent to
  :meth:`taurus.qt.qtcore.configuration.BaseConfigurableClass.loadConfigFile`
  - should implement `setMaxDataBufferSize(n)` where `n` is an integer
  - should implement `setForcedReadingPeriod(period)` where `period` is an
  integer

- For TaurusTrend2D:
  - should accept the following keyword arguments in its constructor:

    - stackMode=x_axis_mode where mode is one of `"d"` or `"n"` or `"t"`
    - wintitle=window_name,
    - buffersize=max_buffer_size

- For TaurusImage:
  - should accept the following keyword arguments in its constructor:

    - wintitle=window_name,

  - should implement `setRGBmode(mode)` where mode is one of `"gray"`, `"rgb"`

"""

import sys
import click
import taurus.cli.common
from taurus.core.util.plugin import selectEntryPoints
from taurus import tauruscustomsettings as _ts
from taurus import warning, info
from taurus.qt.qtgui.application import TaurusApplication


EP_GROUP_PLOT = "taurus.plot.alts"
EP_GROUP_TREND = "taurus.trend.alts"
EP_GROUP_TREND2D = "taurus.trend2d.alts"
EP_GROUP_IMAGE = "taurus.image.alts"


def _print_alts(group):
    alts = [ep.name for ep in selectEntryPoints(group)]
    print("Registered alternatives :\n {}\n".format("\n ".join(alts)))


def _load_class_from_group(group, include=(".*",), exclude=()):
    """
    Factory that returns the first available class from the group entry point.
    The selection is done among the classes registered in
    the `group` entry-point, prioritized according to the given
    `include` and `exclude` patterns
    (see :func:`taurus.core.util.plugin.selectEntryPoints`)
    """
    eps = selectEntryPoints(group, include=include, exclude=exclude)
    for ep in eps:
        try:
            return ep.load(), ep.name
        except:
            info("Cannot load %s", ep.name)
    raise ImportError("Could not load any class from {}".format(eps))


def x_axis_mode_option(choices=("t", "n")):
    hlp = {
        "n": "regular axis",
        "e": "event number",
        "t": "absolute time/date axis",
        "d": "delta time axis",
    }
    o = click.option(
        "-x",
        "--x-axis-mode",
        "x_axis_mode",
        type=click.Choice(choices),
        default=choices[0],
        show_default=True,
        help=(
            "X axis mode: "
            + ", ".join([k + " for " + hlp[k] for k in choices])
        ),
    )
    return o


def max_buffer_option(default):
    o = click.option(
        "-b",
        "--buffer",
        "max_buffer_size",
        type=int,
        default=default,
        show_default=True,
        help=(
            "Maximum number of values to be stacked "
            + "(when reached, the oldest values will be "
            + "discarded)"
        ),
    )
    return o


forced_read_option = click.option(
    "-r",
    "--forced-read",
    "forced_read_period",
    type=int,
    default=-1,
    metavar="MILLISECONDS",
    help="force re-reading of the attributes every MILLISECONDS ms",
)


@click.command("plot")
@taurus.cli.common.models
@taurus.cli.common.config_file
@x_axis_mode_option(["n", "t"])
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
        use_alt = getattr(_ts, "PLOT_ALT", ".*")

    try:
        TPlot, epname = _load_class_from_group(
            EP_GROUP_PLOT, include=[use_alt]
        )
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
            e,
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
                e,
            )
            sys.exit(1)

    if models:
        w.setModel(models)

    w.show()
    sys.exit(app.exec_())


@click.command("trend")
@taurus.cli.common.models
@taurus.cli.common.config_file
@x_axis_mode_option(["t", "n"])
@taurus.cli.common.demo
@taurus.cli.common.window_name("TaurusTrend")
@taurus.cli.common.use_alternative
@taurus.cli.common.list_alternatives
@max_buffer_option(None)
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
    forced_read_period,
):
    """Shows a trend for the given models"""

    # list alternatives option
    if ls_alt:
        _print_alts(EP_GROUP_TREND)
        sys.exit(0)

    # use alternative
    if use_alt is None:
        use_alt = getattr(_ts, "TREND_ALT", ".*")

    # get the selected alternative
    try:
        TTrend, epname = _load_class_from_group(
            EP_GROUP_TREND, include=[use_alt]
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
            e,
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
                e,
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
                e,
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


@click.command("trend2d")
@taurus.cli.common.model
@x_axis_mode_option(["d", "t", "n", "e"])
@taurus.cli.common.demo
@taurus.cli.common.window_name("TaurusTrend2D")
@taurus.cli.common.use_alternative
@taurus.cli.common.list_alternatives
@max_buffer_option(512)
def trend2d_cmd(
    model, x_axis_mode, demo, window_name, use_alt, ls_alt, max_buffer_size
):

    # list alternatives option
    if ls_alt:
        _print_alts(EP_GROUP_TREND2D)
        sys.exit(0)

    # use alternative
    if use_alt is None:
        use_alt = getattr(_ts, "TREND2D_ALT", ".*")

    # get the selected alternative
    try:
        TTrend2D, epname = _load_class_from_group(
            EP_GROUP_TREND2D, include=[use_alt]
        )
    except:
        _print_alts(EP_GROUP_TREND2D)
        sys.exit(1)

    app = TaurusApplication(app_name="Taurus Trend 2D ({})".format(epname))
    w = TTrend2D(
        stackMode=x_axis_mode, wintitle=window_name, buffersize=max_buffer_size
    )

    if demo:
        model = "eval:x=linspace(0,3,40);t=rand();sin(x+t)"

    if model:
        w.setModel(model)

    w.show()
    sys.exit(app.exec_())


@click.command("image")
@taurus.cli.common.model
@taurus.cli.common.demo
@taurus.cli.common.window_name("TaurusImage")
@taurus.cli.common.use_alternative
@taurus.cli.common.list_alternatives
@click.option(
    "-c",
    "--color-mode",
    "color_mode",
    type=click.Choice(["gray", "rgb"]),
    default="gray",
    show_default=True,
    help=("Color mode expected from the attribute"),
)
def image_cmd(model, demo, window_name, color_mode, use_alt, ls_alt):
    # list alternatives option
    if ls_alt:
        _print_alts(EP_GROUP_IMAGE)
        sys.exit(0)

    # use alternative
    if use_alt is None:
        use_alt = getattr(_ts, "IMAGE_ALT", ".*")

    # get the selected alternative
    try:
        TImage, epname = _load_class_from_group(
            EP_GROUP_IMAGE, include=[use_alt]
        )
    except:
        _print_alts(EP_GROUP_IMAGE)
        sys.exit(1)

    app = TaurusApplication(app_name="Taurus Image ({})".format(epname))

    rgb_mode = color_mode == "rgb"

    # TODO:  is "-c rgb --demo" doing the right thing?? Check it.
    if demo:
        if color_mode == "rgb":
            model = "eval:randint(0,256,(10,20,3))"
        else:
            model = "eval:rand(256,128)"

    w = TImage(wintitle=window_name)

    w.setRGBmode(rgb_mode)

    # set model
    if model:
        w.setModel(model)

    w.show()
    sys.exit(app.exec_())
