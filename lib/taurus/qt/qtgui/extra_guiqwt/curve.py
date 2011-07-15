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

__all__=["TaurusCurveItem"]

from PyQt4 import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
import taurus
from guiqwt.curve import CurveItem
from taurus.qt.qtgui.extra_guiqwt.styles import TaurusCurveParam
import numpy
        
class TaurusCurveItem(CurveItem, TaurusBaseComponent):
    '''A CurveItem that autoupdates its values & params when x or y components change'''
    def __init__(self, curveparam=None, taurusparam=None):
        CurveItem.__init__(self, curveparam=curveparam)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self._signalGen = Qt.QObject()
        self._signalGen.connect(self._signalGen, Qt.SIGNAL('taurusEvent'), self.filterEvent) #I need to do this because I am not using the standard model attach mechanism
        self._xcomp = None
        self._ycomp = None
        if taurusparam is None:
            taurusparam = TaurusCurveParam()
        self.taurusparam = taurusparam
        

    def getSignaller(self):
        '''reimplemented from TaurusBaseComponent because TaurusCurveItem is 
        not (and cannot be) a QObject'''
        return self._signalGen  
        
    def setModels(self, x, y):
        #create/get new components
        if x is None:
            newX = None
        else:
            newX = taurus.Attribute(x)
        newY = taurus.Attribute(y)
        
        #stop listening to previous components (if they are not the same as the new)
        if self._xcomp is not None and self._xcomp is not newX:
            self._xcomp.removeListener(self)
        self._xcomp = newX
        if self._ycomp is not None and self._ycomp is not newY:
            self._ycomp.removeListener(self)
        self._ycomp = newY
        
        #start listening to new components
        if self._xcomp is not None:
            self._xcomp.addListener(self)
        self._ycomp.addListener(self)
        self.onCurveDataChanged()
        self.taurusparam.xModel = x
        self.taurusparam.yModel = y
        
    def getModels(self):
        return self.taurusparam.xModel, self.taurusparam.yModel
        
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
            
    def get_item_parameters(self, itemparams):
        CurveItem.get_item_parameters(self, itemparams)
        itemparams.add("TaurusParam", self, self.taurusparam)
        
    def updateTaurusParams(self):
        self.taurusparam.update_curve(self)

    def set_item_parameters(self, itemparams):
        CurveItem.set_item_parameters(self, itemparams)
        self.updateTaurusParams()
        

def plot(*items):
    '''from guiqwt plot.py example'''
    from guiqwt.plot import CurveDialog
    from guiqwt.tools import HRangeTool
    win = CurveDialog(edit=False, toolbar=True, wintitle="CurveDialog test",
                      options=dict(title="Title", xlabel="xlabel",
                                   ylabel="ylabel"))
    win.add_tool(HRangeTool)
    from taurus.qt.qtgui.extra_guiqwt.tools import TaurusCurveChooserTool
    win.add_tool(TaurusCurveChooserTool)
    plot = win.get_plot()
    for item in items:
        plot.add_item(item)
    win.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    win.exec_()


def test1():
    from taurus.qt.qtgui.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication()
    
    x = numpy.linspace(0, 1, 100)
    y = numpy.sqrt(x)
    
    model1 = None
    model2 = 'eval://linspace(0,1,len({sys/tg_test/1/wave}))'
    model3 = 'eval://rand((100,))'
    model4 = 'sys/tg_test/1/float_spectrum_ro'
    model5 = 'tango://sys/tg_test/1/wave'
    model6 = 'eval://{sys/tg_test/1/wave}*10+{sys/tg_test/1/float_spectrum_ro}/50'
    
    plot(make.curve(x, y, color='b'),
         make.curve(model2, model6, color='g', title='taurus curve'),
         make.legend('TR'))


def taurusCurveMain():
    from taurus.qt.qtgui.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    from guiqwt.plot import CurveDialog
    from guiqwt.tools import HRangeTool
    from taurus.qt.qtgui.extra_guiqwt.tools import TaurusCurveChooserTool, TimeAxisTool
    import taurus.core.util.argparse
    import sys
    
    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [<model1> [<model2>] ...]")
    parser.set_description("a taurus application for plotting 1D data sets")
    app = TaurusApplication(cmd_line_parser=parser, app_name="taurusplot2", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    
    win = CurveDialog(edit=False, toolbar=True, wintitle="TaurusPlot2",
                      options=dict(title="", xlabel="xlabel", ylabel="ylabel"))
    win.add_tool(HRangeTool)
    win.add_tool(TaurusCurveChooserTool)
    win.add_tool(TimeAxisTool)
    
    plot = win.get_plot()
      
    for a in args:
        mx_my = a.split('|')
        n = len(mx_my)
        if n == 1: 
            mx, my = None, mx_my[0]
        elif n == 2:
            mx, my = mx_my
        else:
            print "Invalid model: %s\n"%mx_my
            parser.print_help(sys.stderr)
            sys.exit(1)
        #cycle colors
        style = make.style.next()
        color=style[0]
        linestyle = style[1:]
        plot.add_item(make.curve(mx,my, color=color, linestyle=linestyle, linewidth=2))
        
    win.get_itemlist_panel().show()
    plot.set_items_readonly(False)
    win.show()
    win.exec_()    
    
    

if __name__ == "__main__":
#    test1()
    taurusCurveMain()    
