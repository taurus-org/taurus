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

"""Extension of :mod:`guiqwt.tools`"""



__docformat__ = 'restructuredtext'


from guiqwt.tools import CommandTool, DefaultToolbarID
from PyQt4 import Qt
from taurus.qt.qtgui.resource import getIcon
from taurus.qt.extra_guiqwt.builder import make
from taurus.qt.extra_guiqwt.curve import TaurusCurveItem
from taurus.qt.extra_guiqwt.curvesmodel import CurveItemConfDlg, CurveItemConf
from taurus.qt.qtgui.panel import TaurusModelChooser
from taurus.core import TaurusElementType

class TaurusCurveChooserTool(CommandTool):
    """
    A tool that shows the Taurus Model Chooser to create/edit the taurus curves of a plot
    """
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(TaurusCurveChooserTool,self).__init__(manager, "Taurus Models...", getIcon(":/taurus.png"), toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        """Activate tool"""
        #retrieve current Taurus curves
        tauruscurves = [item for item in plot.get_public_items() if isinstance(item, TaurusCurveItem)]
        #show a dialog
        confs, ok = CurveItemConfDlg.showDlg(parent=plot, curves=tauruscurves)
        if ok:
            #remove previous taurus curves
            plot.del_items(tauruscurves)
            #create curve items and add them to the plot 
            for c in confs:
                if c.taurusparam.yModel:
                    item = make.pcurve(c.taurusparam.xModel or None, c.taurusparam.yModel, c.curveparam)
                    plot.add_item(item)
                    if c.axesparam is not None:
                        c.axesparam.update_axes(item)

class TaurusImageChooserTool(CommandTool):
    """
    A tool that shows the Taurus Model Chooser and adds new taurus image items to a plot
    """
    def __init__(self, manager, toolbar_id=DefaultToolbarID):
        super(TaurusImageChooserTool,self).__init__(manager, "Add Taurus images...", getIcon(":/taurus.png"), toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        """Activate tool"""
        #show a dialog
        models, ok = TaurusModelChooser.modelChooserDlg(parent=plot, selectables=[TaurusElementType.Attribute])
        if ok:
            #create image items and add them to the plot 
            for m in models:
                item = make.image(taurusmodel=m)
                plot.add_item(item)
