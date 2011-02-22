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
Generic Image widget for Taurus. Based on guiqwt.plot.ImagePlotWidget: 
"""
from PyQt4 import Qt
from taurus.qt.qtgui.base import taurusQAttributeFactory
from guiqwt.curve import CurveItem
import numpy
        
class TaurusCurveItem(CurveItem):
    '''A CurveItem that autoupdates its values & params when x or y components change'''
    def __init__(self, curveparam=None):
        CurveItem.__init__(self, curveparam=curveparam)
        self._xcomp = None
        self._ycomp = None
        
    def setExtendedModels(self, x, y):
        #disconect previous component
        if self._xcomp is not None: Qt.QObject.disconnect(self._xcomp, Qt.SIGNAL('dataChanged'), self.onDataChanged)
        if self._ycomp is not None: Qt.QObject.disconnect(self._ycomp, Qt.SIGNAL('dataChanged'), self.onDataChanged)
        #create/get new components
        self._ycomp = taurusQAttributeFactory.getQAttr(xmodel=y)
        self._xcomp = taurusQAttributeFactory.getQAttr(xmodel=x)
        #connect the new components to the notification
        Qt.QObject.connect(self._xcomp, Qt.SIGNAL('dataChanged'), self.onDataChanged)
        Qt.QObject.connect(self._ycomp, Qt.SIGNAL('dataChanged'), self.onDataChanged)
        self.onDataChanged()
        
    def onDataChanged(self):
        if self._ycomp.value is None:
            return
        if self._xcomp.value is None:
            self._xcomp.value = numpy.arange(len(self._ycomp.value))
        self.setData(self._xcomp.value, self._ycomp.value)
        p = self.plot()
        if p is not None: p.replot()
        

def main():
    from guiqwt.plot import CurvePlotWidget,CurvePlotDialog
    from guiqwt.curve import  CurveParam
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication()
    args = app.get_command_line_args()
    if len (args)==2:
        model1,model2 = args
    else: 
#        model1 = None
        model1 = '=linspace(0,1,len(${sys/tg_test/1/wave}))'
#        model2 = '=arange(10)**2'
#        model2 = 'sys/tg_test/1/float_spectrum_ro'
        model2 = '=${sys/tg_test/1/wave}*10 +${sys/tg_test/1/float_spectrum_ro}/50'
    
    #w = CurvePlotDialog()
    w = CurvePlotWidget()
    w.register_all_curve_tools()
    plot = w.get_plot()
#    w = CurvePlot()
    
    param = CurveParam()
    param.label = 'My curve'
    curve = TaurusCurveItem(param)
    curve.setExtendedModels(model1,model2)
    
    plot.add_item(curve)
    plot.set_items_readonly(False)
    
    #show the widget
    w.show()
    
    sys.exit(app.exec_())  
    

if __name__ == "__main__":
    main()    

