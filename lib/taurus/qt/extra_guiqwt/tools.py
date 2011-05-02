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

"""Extension of :mod:`guiqwt.builder`"""

__all__=["TaurusPlotItemBuilder", "make"]

__docformat__ = 'restructuredtext'

import guiqwt.builder

from guiqwt.tools import CommandTool, DefaultToolbarID, SaveAsTool, get_std_icon
from PyQt4 import Qt


class TaurusModelChooserTool(CommandTool):
    """
    A tool that shows the Taurus Model Chooser and creates curves/images associated with it
    """
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(TaurusModelChooserTool,self).__init__(manager, "Taurus Models...", get_std_icon("DialogSaveButton", 16), toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        """Activate tool"""
        Qt.QMessageBox.information(plot, 'DUMMY','THIS SHOULD BE A MODELCHOOSER')

#    def update_status(self, plot):
#        status = plot.get_plot_parameters_status(self.key)
#        self.action.setEnabled(status)

