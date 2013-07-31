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
from taurus.qt.qtgui.taurusgui.utils import PanelDescription, ExternalApp, ToolBarDescription, AppletDescription
# (end of import section)
#==============================================================================


#===============================================================================
# General info.
#===============================================================================
GUI_NAME = 'EXAMPLE 01'
ORGANIZATION = 'Taurus'

#===============================================================================
# Specific logo. It can be an absolute path,or relative to the app dir or a 
# resource path. If commented out, ":/taurus.png" will be used
#===============================================================================
#CUSTOM_LOGO = <path GUI-specific logo 

#===============================================================================
# You can provide an URI for a manual in html format
# (comment out or make MANUAL_URI=None to skip creating a Manual panel) 
#===============================================================================
MANUAL_URI = 'http://packages.python.org/taurus'

#===============================================================================
# If you want to have a main synoptic panel, set the SYNOPTIC variable
# to the file name of a jdraw file. If a relative path is given, the directory
# containing this configuration file will be used as root
# (comment out or make SYNOPTIC=None to skip creating a synoptic panel)
#===============================================================================
SYNOPTIC = ['images/example01.jdw','images/syn2.jdw']

#===============================================================================
# Set INSTRUMENTS_FROM_POOL to True for enabling auto-creation of
# instrument panels based on the Pool Instrument info
#===============================================================================
INSTRUMENTS_FROM_POOL = False

#===============================================================================
# Define panels to be shown.  
# To define a panel, instantiate a PanelDescription object (see documentation
# for the gblgui_utils module)
#===============================================================================

nxbrowser = PanelDescription('NeXus Browser',
                       classname = 'TaurusNeXusBrowser',
                       area = None)

i0 = PanelDescription('BigInstrument',
                       classname = 'TaurusAttrForm',
                       model = 'sys/tg_test/1')

i1 = PanelDescription('instrument1',
                       classname = 'TaurusForm',
                       model = ['sys/tg_test/1/double_scalar',
                                'sys/tg_test/1/short_scalar_ro',
                                'sys/tg_test/1/float_spectrum_ro',
                                'sys/tg_test/1/double_spectrum'])

i2 = PanelDescription('instrument2',
                       classname = 'TaurusForm',
                       model = ['sys/tg_test/1/wave',
                                'sys/tg_test/1/boolean_scalar'])

trend = PanelDescription('Trend',
                        classname = 'TaurusTrend',
                        model = ['sys/tg_test/1/double_scalar'])

connectionDemo = PanelDescription('Selected Instrument',
                        classname = 'PyQt4.Qt.QLineEdit',
                        sharedDataRead={'SelectedInstrument':'setText'},
                        sharedDataWrite={'SelectedInstrument':'textEdited(QString)'})

#===============================================================================
# Define custom toolbars to be shown. To define a toolbar, instantiate a
# ToolbarDescription object (see documentation for the gblgui_utils module)
#===============================================================================

dummytoolbar = ToolBarDescription('Empty Toolbar',
                        classname = 'QToolBar',
                        modulename = 'PyQt4.Qt')

#panictoolbar = ToolBarDescription('Panic Toolbar',
#                        classname = 'PanicToolbar',
#                        modulename = 'tangopanic')

#===============================================================================
# Define custom applets to be shown in the applets bar (the wide bar that
# contains the logos). To define an applet, instantiate an AppletDescription
# object (see documentation for the gblgui_utils module)
#===============================================================================

mon2 = AppletDescription('Dummy Monitor',
                        classname = 'TaurusMonitorTiny',
                        model='eval://1000*rand(2)')


#===============================================================================
# Define which External Applications are to be inserted.
# To define an external application, instantiate an ExternalApp object
# See TaurusMainWindow.addExternalAppLauncher for valid values of ExternalApp
#===============================================================================
xterm = ExternalApp(cmdargs=['xterm','spock'], text="Spock", icon='utilities-terminal')
hdfview = ExternalApp(["hdfview"])
pymca = ExternalApp(['pymca'])

#===============================================================================
# Macro execution configuration
# Comment out or make MACRO_SERVER=None or set MACRO_PANELS=False to skip 
# creating a macro execution infrastructure.
# Give empty strings if you want to select the values manually in the GUI
#===============================================================================
#MACROSERVER_NAME = 
#DOOR_NAME = 
#MACROEDITORS_PATH = 

#===============================================================================
# Monitor widget (This is *obsolete* now, you can get the same result defining a
# custom applet with classname='TaurusMonitorTiny')
#===============================================================================
# MONITOR = ['sys/tg_test/1/double_scalar_rww']

#===============================================================================
# Adding other widgets to the catalog of the "new panel" dialog.
# pass a tuple of (classname,screenshot)
# -classname may contain the module name.
# -screenshot can either be a file name relative to the application dir or 
# a resource URL or None
#===============================================================================
EXTRA_CATALOG_WIDGETS = [('PyQt4.Qt.QLineEdit',':/taurus.png'),
                        ('PyQt4.Qt.QSpinBox','images/syn2.jpg'),
                        ('PyQt4.Qt.QTextEdit','/tmp/kk.png'),
                        ('PyQt4.Qt.QLabel',None)]

#===============================================================================
# Define one or more embedded consoles in the GUI.
# Possible items for console are 'ipython', 'tango', 'spock'
# Note: This is still experimental
#===============================================================================
#CONSOLE = ['tango']