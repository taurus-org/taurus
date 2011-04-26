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

"""Extension of :mod:`guiqwt.curve`"""

from PyQt4 import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
import taurus
from guiqwt.curve import CurveItem
import numpy
        
class TaurusCurveItem(CurveItem, TaurusBaseComponent):
    '''A CurveItem that autoupdates its values & params when x or y components change'''
    def __init__(self, curveparam=None):
        CurveItem.__init__(self, curveparam=curveparam)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self._signalGen = Qt.QObject()
        self._signalGen.connect(self._signalGen, Qt.SIGNAL('taurusEvent'), self.filterEvent) #I need to do this because I am not using the standard model attach mechanism
        self._xcomp = None
        self._ycomp = None

    def getSignaller(self):
        '''reimplemented from TaurusBaseComponent because TaurusCurveItem is 
        not (and cannot be) a QObject'''
        return self._signalGen  
        
    def setModels(self, x, y):
        #stop listenening to previous components
        if self._xcomp is not None:
            self._xcomp.removeListener(self)
            
        if self._ycomp is not None:
            self._ycomp.removeListener(self)
        #create/get new components
        if x is None:
            self._xcomp = None
        else:
            self._xcomp = taurus.Attribute(x)
        self._ycomp = taurus.Attribute(y)
        #start listening to new components
        if self._xcomp is not None:
            self._xcomp.addListener(self)
        self._ycomp.addListener(self)
        self.onCurveDataChanged()
        
    def handleEvent(self, evt_src, ect_type, evt_value):
        if evt_value is None or getattr(evt_value,'value', None) is None:
            self.debug('Ignoring event from %s'%repr(evt_src))
            return
        if evt_src is self._xcomp or evt_src is self._ycomp:
            self.onCurveDataChanged()
            self.getSignaller().emit(Qt.SIGNAL('dataChanged'))
        
        
    def onCurveDataChanged(self):
        try: yvalue = self._ycomp.read().value
        except: yvalue = None
        
        if yvalue is None:
            return        
        
        try: xvalue = self._xcomp.read().value
        except: xvalue = None
        
        if xvalue is None:
            xvalue = numpy.arange(len(yvalue))
        
        self.setData(xvalue, yvalue)
        p = self.plot()
        if p is not None: 
            p.replot()
        

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
        model1 = 'eval://linspace(0,1,len({sys/tg_test/1/wave}))'
#        model2 = '=arange(10)**2'
#        model2 = 'sys/tg_test/1/float_spectrum_ro'
        model2 = 'eval://{sys/tg_test/1/wave}*10+{sys/tg_test/1/float_spectrum_ro}/50'
    
    #w = CurvePlotDialog()
    w = CurvePlotWidget()
    w.register_all_curve_tools()
    plot = w.get_plot()
#    w = CurvePlot()
    
    param = CurveParam()
    param.label = 'My curve'
    curve = TaurusCurveItem(param)
    curve.setModels(model1,model2)
    
    plot.add_item(curve)
    plot.set_items_readonly(False)
    
    #show the widget
    w.show()
    
    sys.exit(app.exec_())  
if __name__ == "__main__":
    main()     
"""
from PyQt4 import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
import taurus
from guiqwt.curve import CurveItem
import numpy
        
class TaurusCurveItem(CurveItem, TaurusBaseComponent):
    '''A CurveItem that autoupdates its values & params when x or y components change'''
    def __init__(self, curveparam=None):
        CurveItem.__init__(self, curveparam=curveparam)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self._signalGen = Qt.QObject()
        self._signalGen.connect(self._signalGen, Qt.SIGNAL('taurusEvent'), self.filterEvent) #I need to do this because I am not using the standard model attach mechanism
        self._xcomp = None
        self._ycomp = None

    def getSignaller(self):
        '''reimplemented from TaurusBaseComponent because TaurusCurveItem is 
        not (and cannot be) a QObject'''
        return self._signalGen  
        
    def setModels(self, x, y):
        #stop listenening to previous components
        if self._xcomp is not None:
            self._xcomp.removeListener(self)
            
        if self._ycomp is not None:
            self._ycomp.removeListener(self)
        #create/get new components
        if x is None:
            self._xcomp = None
        else:
            self._xcomp = taurus.Attribute(x)
        self._ycomp = taurus.Attribute(y)
        #start listening to new components
        if self._xcomp is not None:
            self._xcomp.addListener(self)
        self._ycomp.addListener(self)
        self.onCurveDataChanged()
        
    def handleEvent(self, evt_src, ect_type, evt_value):
        if evt_value is None or getattr(evt_value,'value', None) is None:
            self.debug('Ignoring event from %s'%repr(evt_src))
            return
        if evt_src is self._xcomp or evt_src is self._ycomp:
            self.onCurveDataChanged()
            self.getSignaller().emit(Qt.SIGNAL('dataChanged'))
        
        
    def onCurveDataChanged(self):
        try: yvalue = self._ycomp.read().value
        except: yvalue = None
        
        if yvalue is None:
            return        
        
        try: xvalue = self._xcomp.read().value
        except: xvalue = None
        
        if xvalue is None:
            xvalue = numpy.arange(len(yvalue))
        
        self.setData(xvalue, yvalue)
        p = self.plot()
        if p is not None: 
            p.replot()
        

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
        model1 = 'eval://linspace(0,1,len({sys/tg_test/1/wave}))'
#        model2 = '=arange(10)**2'
#        model2 = 'sys/tg_test/1/float_spectrum_ro'
        model2 = 'eval://{sys/tg_test/1/wave}*10+{sys/tg_test/1/float_spectrum_ro}/50'
    
    #w = CurvePlotDialog()
    w = CurvePlotWidget()
    w.register_all_curve_tools()
    plot = w.get_plot()
#    w = CurvePlot()
    
    param = CurveParam()
    param.label = 'My curve'
    curve = TaurusCurveItem(param)
    curve.setModels(model1,model2)
    
    plot.add_item(curve)
    plot.set_items_readonly(False)
    
    #show the widget
    w.show()
    
    sys.exit(app.exec_())  
if __name__ == "__main__":
    main()    

