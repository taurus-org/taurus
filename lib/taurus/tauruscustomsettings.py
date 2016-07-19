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

# A map for using custom widgets for certain devices in TaurusForms. It is a
# dictionary with the following structure:
# device_class_name:(classname_with_full_module_path, args, kwargs)
# where the args and kwargs will be passed to the constructor of the class
T_FORM_CUSTOM_WIDGET_MAP = \
    {'SimuMotor': ('sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
     'Motor': ('sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
     'PseudoMotor': ('sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
     'PseudoCounter': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'CTExpChannel': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'ZeroDExpChannel': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'OneDExpChannel': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'TwoDExpChannel': ('sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'IORegister': ('sardana.taurus.qt.qtgui.extra_pool.PoolIORegisterTV', (), {})
     }

# Compact mode for widgets
# True sets the preferred mode of TaurusForms to use "compact" widgets
T_FORM_COMPACT = False

# Strict RFC3986 URI names in models
# True makes Taurus only use the strict URI names
# False enables a backwards-compatibility mode for pre-sep3 model names
STRICT_MODEL_NAMES = False


# Lightweight imports:
# True enables delayed imports (may break older code).
# False (or commented out) for backwards compatibility
LIGHTWEIGHT_IMPORTS = False

# Set your default scheme (if not defined, "tango" is assumed)
DEFAULT_SCHEME = "tango"

# Extra Taurus schemes. You can add a list of modules to be loaded for
# providing support to new schemes
# EXTRA_SCHEME_MODULES = ['myownschememodule']

# ----------------------------------------------------------------------------
# PLY (lex/yacc) optimization: 1=Active (default) , 0=disabled.
# Set PLY_OPTIMIZE = 0 if you are getting yacc exceptions while loading
# synoptics
# ----------------------------------------------------------------------------

PLY_OPTIMIZE = 1

# ----------------------------------------------------------------------------
# Taurus namespace
# ----------------------------------------------------------------------------

NAMESPACE = 'taurus'

# ----------------------------------------------------------------------------
# Qt configuration
# ----------------------------------------------------------------------------

#: Auto initialize Qt
DEFAULT_QT_AUTO_INIT = True

#: Set preffered API if not is already loaded
DEFAULT_QT_AUTO_API = 'PyQt4'

#: Whether or not should be strict in choosing Qt API
DEFAULT_QT_AUTO_STRICT = False

#: Auto initialize Qt logging to python logging
DEFAULT_QT_AUTO_INIT_LOG = True

#: Auto initialize taurus resources (icons)
DEFAULT_QT_AUTO_INIT_RES = True

#: Remove input hook (only valid for PyQt4)
DEFAULT_QT_AUTO_REMOVE_INPUTHOOK = True

#: Auto initialize Qt
QT_AUTO_INIT = DEFAULT_QT_AUTO_INIT

#: Set preffered API if not is already loaded
QT_AUTO_API = DEFAULT_QT_AUTO_API

#: Whether or not should be strict in choosing Qt API
QT_AUTO_STRICT = DEFAULT_QT_AUTO_STRICT

#: Auto initialize Qt logging to python logging
QT_AUTO_INIT_LOG = DEFAULT_QT_AUTO_INIT_LOG

#: Auto initialize taurus resources (icons)
QT_AUTO_INIT_RES = DEFAULT_QT_AUTO_INIT_RES

#: Remove input hook (only valid for PyQt4)
QT_AUTO_REMOVE_INPUTHOOK = DEFAULT_QT_AUTO_REMOVE_INPUTHOOK

#: Select the theme to be used: set the theme dir  and the theme name.
#: The path can be absolute or relative to the dir of taurus.qt.qtgui.icon
#: If not set, the dir of taurus.qt.qtgui.icon will be used
QT_THEME_DIR = ''
#: The name of the icon theme (e.g. 'Tango', 'Oxygen', etc). Default='Tango'
QT_THEME_NAME = 'Tango'
#: In Linux the QT_THEME_NAME is not applied (to respect the system theme)
#: setting QT_THEME_FORCE_ON_LINUX=True overrides this.
QT_THEME_FORCE_ON_LINUX = True


# ----------------------------------------------------------------------------
# Deprecation handling:
# Note: this API is still experimental and may be subject to change
# (hence the "_" in the options)
# ----------------------------------------------------------------------------

# set the maximum number of same-message deprecations to be logged.
# None (or not set) indicates no limit. -1 indicates that an exception should
# be raised instead of logging the message (useful for finding obsolete code)
_MAX_DEPRECATIONS_LOGGED = 1

# Custom organization logo. Set the absolute path to an image file to be used as your
# organization logo. Qt registered paths can also be used. 
# If not set, it defaults to 'logos:taurus.png" 
# (note that "logos:" is a Qt a registered path for "<taurus>/qt/qtgui/icon/logos/")
# ORGANIZATION_LOGO = "logos:taurus.png"
