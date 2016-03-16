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
###########################################################################

"""
configuration file for an example of how to construct a GUI based on TaurusGUI

This configuration file determines the default, permanent, pre-defined
contents of the GUI. While the user may add/remove more elements at run
time and those customizations will also be stored, this file defines what a
user will find when launching the GUI for the first time.
"""

#==============================================================================
# Import section. You probably want to keep this line. Don't edit this block
# unless you know what you are doing
from taurus.qt.qtgui.taurusgui.utils import PanelDescription, ExternalApp, Qt_Qt
# (end of import section)
#==============================================================================


#=========================================================================
# General info.
#=========================================================================
GUI_NAME = 'MacroGUI'
ORGANIZATION = 'Taurus'
# CUSTOM_LOGO = <full path to GUI-specific logo>

#=========================================================================
# If you want to have a main synoptic panel, set the SYNOPTIC variable
# to the file name of a jdraw file. If a relative path is given, the directory
# containing this configuration file will be used as root
# (comment out or make SYNOPTIC=None to skip creating a synoptic panel)
#=========================================================================
# SYNOPTIC =

#=========================================================================
# Set INSTRUMENTS_FROM_POOL to True for enabling auto-creation of
# instrument panels based on the Pool Instrument info
#=========================================================================
#INSTRUMENTS_FROM_POOL = False

#=========================================================================
# Define panels to be shown.
# To define a panel, instantiate a PanelDescription object (see documentation
# for the gblgui_utils module)
#=========================================================================

# None defined

#=========================================================================
# Define which External Applications are to be inserted.
# To define an external application, instantiate an ExternalApp object
# See TaurusMainWindow.addExternalAppLauncher for valid values of ExternalApp
#=========================================================================
#xterm = ExternalApp(cmdargs=['xterm','spock'], text="Spock", icon='utilities-terminal')
#hdfview = ExternalApp(["hdfview"])
pymca = ExternalApp(['pymca'])

#=========================================================================
# Macro execution configuration
# Comment out or make MACRO_SERVER=None or set MACRO_PANELS=False to skip
# creating a macro execution infrastructure.
# Give empty strings if you want to select the values manually in the GUI
#=========================================================================
MACROSERVER_NAME = ''
DOOR_NAME = ''
MACROEDITORS_PATH = ''

#=========================================================================
# Define one or more embedded consoles in the GUI.
# Possible items for console are 'ipython', 'tango', 'spock'
#=========================================================================
CONSOLE = ['tango']

#=========================================================================
# Monitor widget
#=========================================================================
# MONITOR =
