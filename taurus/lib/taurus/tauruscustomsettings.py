#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
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
    {'SimuMotor':('taurus.qt.qtgui.extra_pool.PoolMotorTV',(),{}),
     'Motor':('taurus.qt.qtgui.extra_pool.PoolMotorTV',(),{}),
     'PseudoMotor':('taurus.qt.qtgui.extra_pool.PoolMotorTV',(),{}),
     'PseudoCounter':('taurus.qt.qtgui.extra_pool.PoolChannelTV',(),{}),
     'CTExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV',(),{}),
     'ZeroDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV',(),{}),
     'OneDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV',(),{}),
     'TwoDExpChannel':('taurus.qt.qtgui.extra_pool.PoolChannelTV',(),{}),
     'IORegister':('taurus.qt.qtgui.extra_pool.PoolIORegisterTV',(),{})
    }

# Lightweight imports:
# True enables delayed imports (may break older code). 
# False (or commented out) for backwards compatibility
LIGHTWEIGHT_IMPORTS = False     

# Extra Taurus schemes. You can add a list of modules to be loaded for 
# providing support to new schemes
# EXTRA_SCHEME_MODULES = ['myownschememodule']