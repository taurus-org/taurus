#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
##
## http://taurus-scada.org
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
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
    {'SimuMotor':('taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
     'Motor':('taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
     'PseudoMotor':('taurus.qt.qtgui.extra_pool.PoolMotorTV', (), {}),
     'PseudoCounter':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'CTExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'ZeroDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'OneDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'TwoDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV', (), {}),
     'IORegister':('taurus.qt.qtgui.extra_pool.PoolIORegisterTV', (), {})
    }

# Compact mode for widgets
# True sets the preferred mode of TaurusForms to use "compact" widgets
T_FORM_COMPACT = False

# Lightweight imports:
# True enables delayed imports (may break older code).
# False (or commented out) for backwards compatibility
LIGHTWEIGHT_IMPORTS = False

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
