#!/usr/bin/env python

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
This module contains some Taurus-wide default configurations.

The idea is that the final user may edit the values here to customize certain
aspects of Taurus.
"""

#: Widget alternatives. Some widgets may be have alternative implementations
#: (e.g. the `TaurusPlot` is implemented both by the qwt5 submodule and by the
#: taurus_pyqtgraph plugin). The different implementations are registered in
#: entry point groups (`taurus.plot.alt`, `taurus.trend.alt`, ...) and they
#: are tried in alphabetical order of their registered  entry point names
#: (the first one that works is used). You can restrict the set of available
#: implementation alternatives to be tried (or even just select a given
#: alternative) by setting the corresponding *_ALT variable with a name
#: regexp pattern that must be matched by the entry point name in order to be
#: tried. For example, to force the `taurus_pyqtgraph` implementation for the
#: plots, set `PLOT_ALT = "tpg"`.
#: Leaving the variable undefined is equivalent to setting it to `".*"`
PLOT_ALT = ".*"
TREND_ALT = ".*"
TREND2D_ALT = ".*"
IMAGE_ALT = ".*"

#: Default include and exclude patterns for TaurusForm item factories
#: See `TaurusForm.setItemFactories` docs. By default, all available
#: factories are enabled (and tried alphabetically)
T_FORM_ITEM_FACTORIES = {"include": (".*",), "exclude": ()}

#: Compact mode for widgets
#: True sets the preferred mode of TaurusForms to use "compact" widgets
T_FORM_COMPACT = False

#: Strict RFC3986 URI names in models.
#: True makes Taurus only use the strict URI names
#: False enables a backwards-compatibility mode for pre-sep3 model names
STRICT_MODEL_NAMES = False

#: Lightweight imports:
#: True enables delayed imports (may break older code).
#: False (or commented out) for backwards compatibility
LIGHTWEIGHT_IMPORTS = False

#: Default scheme (if not defined, "tango" is assumed)
DEFAULT_SCHEME = "tango"

#: Filter old tango events:
#: Sometimes TangoAttribute can receive an event with an older timestamp
#: than its current one. See https://github.com/taurus-org/taurus/issues/216
#: True discards (Tango) events whose timestamp is older than the cached one.
#: False (or commented out) for backwards (pre 4.1) compatibility
FILTER_OLD_TANGO_EVENTS = True

#: Extra Taurus schemes. You can add a list of modules to be loaded for
#: providing support to new schemes
#: (e.g. EXTRA_SCHEME_MODULES = ['myownschememodule']
EXTRA_SCHEME_MODULES = []

#: Custom formatter. Taurus widgets use a default formatter based on the
#: attribute type, but sometimes a custom formatter is needed.
#: IMPORTANT: setting this option in this file will affect ALL widgets
#: of ALL applications (which is probably **not** what you want, since it
#: may have unexpected effects in some applications).
#: Consider using the API for modifying this on a per-widget or per-class
#: basis at runtime, or using the related `--default-formatter` parameter
#: from TaurusApplication, e.g.:
#:     $ taurus form MODEL --default-formatter='{:2.3f}'
#: The formatter can be a python format string or the name of a formatter
#: callable, e.g.
#: DEFAULT_FORMATTER = '{0}'
#: DEFAULT_FORMATTER = 'taurus.core.tango.util.tangoFormatter'
#: If not defined, taurus.qt.qtgui.base.defaultFormatter will be used


#: Default serialization mode **for the tango scheme**. Possible values are:
#: 'Serial', 'Concurrent', or 'TangoSerial' (default)
TANGO_SERIALIZATION_MODE = 'TangoSerial'

#: Whether TangoAttribute is subscribed to configuration events by default.
#: Setting to True (or not setting it) makes the TangoAttribute auto-subscribe
#: Setting to False avoids this subscription, which prevents issues such as
#: https://github.com/taurus-org/taurus/issues/1118
#: but it also prevents clients to be notified when configurations (e.g.,
#: units, format) change.
TANGO_AUTOSUBSCRIBE_CONF = True

#: PLY (lex/yacc) optimization: 1=Active (default) , 0=disabled.
#: Set PLY_OPTIMIZE = 0 if you are getting yacc exceptions while loading
#: synoptics
PLY_OPTIMIZE = 1

# Taurus namespace  # TODO: NAMESPACE setting seems to be unused. remove?
NAMESPACE = 'taurus'

# ----------------------------------------------------------------------------
# Qt configuration
# ----------------------------------------------------------------------------

#: Set preferred API (if one is not already loaded). Accepted values are
#: pyqt5, pyqt, pyside2, pyside. Set to an empty string to let taurus choose
#: the first that works from the accepted values.
DEFAULT_QT_API = ''

#: Auto initialize Qt logging to python logging
QT_AUTO_INIT_LOG = True

#: Remove input hook (only valid for PyQt4)
QT_AUTO_REMOVE_INPUTHOOK = True

#: Avoid application abort on unhandled python exceptions
#: (which happens since PyQt 5.5).
#: http://pyqt.sf.net/Docs/PyQt5/incompatibilities.html#unhandled-python-exceptions
#: If True (or commented out) an except hook is added to force the old
# behaviour (exception is just printed) on pyqt5
QT_AVOID_ABORT_ON_EXCEPTION = True

#: Select the theme to be used: set the theme dir  and the theme name.
#: The path can be absolute or relative to the dir of taurus.qt.qtgui.icon
#: If not set, the dir of taurus.qt.qtgui.icon will be used
QT_THEME_DIR = ''

#: The name of the icon theme (e.g. 'Tango', 'Oxygen', etc). Default='Tango'
QT_THEME_NAME = 'Tango'

#: In Linux the QT_THEME_NAME is not applied (to respect the system theme)
#: setting QT_THEME_FORCE_ON_LINUX=True overrides this.
QT_THEME_FORCE_ON_LINUX = False

#: Full Qt designer path (including filename. Default is None, meaning:
#: - linux: look for the system designer following Qt.QLibraryInfo.BinariesPath
#: - windows: look for the system designer following
#: Qt.QLibraryInfo.BinariesPath. If this fails, taurus tries to locate binary
#: manually
QT_DESIGNER_PATH = None

#: Custom organization logo. Set the absolute path to an image file to be used as your
#: organization logo. Qt registered paths can also be used.
#: If not set, it defaults to 'logos:taurus.png"
#: (note that "logos:" is a Qt a registered path for "<taurus>/qt/qtgui/icon/logos/")
ORGANIZATION_LOGO = "logos:taurus.png"

#: Implicit optparse legacy support:
#: In taurus < 4.6.5 if TaurusApplication did not receive an explicit
#: `cmd_line_parser` keyword argument, it implicitly used a
#: `optparse.OptionParser` instance. This was inconvenient because it forced
#: the user to explicitly pass `cmd_line_parser=None` when using other
#: mechanisms such as `click` or `argparse` to parse CLI options.
#: In taurus >=4.6.5 this is no longer the case by default, but the old
#: behaviour can be restored by setting IMPLICIT_OPTPARSE=True
IMPLICIT_OPTPARSE = False

# ----------------------------------------------------------------------------
# Deprecation handling:
# Note: this API is still experimental and may be subject to change
# (hence the "_" in the options)
# ----------------------------------------------------------------------------

#: set the maximum number of same-message deprecations to be logged.
#: None (or not set) indicates no limit. -1 indicates that an exception should
#: be raised instead of logging the message (useful for finding obsolete code)
_MAX_DEPRECATIONS_LOGGED = 1

# ----------------------------------------------------------------------------
# DEPRECATED SETTINGS
# ----------------------------------------------------------------------------

#: DEPRECATED. Use "taurus.form.item_factories" plugin group instead
#: A map for using custom widgets for certain devices in TaurusForms. It is a
#: dictionary with the following structure:
#: device_class_name:(classname_with_full_module_path, args, kwargs)
#: where the args and kwargs will be passed to the constructor of the class
T_FORM_CUSTOM_WIDGET_MAP = {}
_OLD_T_FORM_CUSTOM_WIDGET_MAP = {
    'SimuMotor': ('sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
    'Motor': ('sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
    'PseudoMotor': ('sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
    'PseudoCounter': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
    'CTExpChannel': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
    'ZeroDExpChannel': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
    'OneDExpChannel': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
    'TwoDExpChannel': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
    'IORegister': ('sardana.taurus.qt.qtgui.extra_pool.PoolIORegisterTV', (), {}),
}
try:  # just for backwards compatibility. This will be removed.
    import sardana
    if sardana.release.version < '3':
        T_FORM_CUSTOM_WIDGET_MAP = _OLD_T_FORM_CUSTOM_WIDGET_MAP
except:
    pass
