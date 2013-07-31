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
monitor.py: Specialized mini-trend widget to monitor some scalar value
"""

from taurus.qt import Qt
from taurus.qt.qtgui.plot import TaurusTrend


class TaurusMonitorTiny(TaurusTrend):
    '''
    A specialised :class:`TaurusTrend` widget for monitoring scalar values and show
    their evolution over time. It is designed to be small (e.g. to fit in a
    toolbar). It is inspired by the SysMon applet in old KDE3.

    .. seealso:: :class:`TaurusTrend`,
                 :ref:`TaurusTrend User's Interface Guide <trend_ui>`, 
                 :ref:`The TaurusTrend coding examples <examples_taurustrend>`
    '''
    DEFAULT_MAX_BUFFER_SIZE = 8192 #(8K events))
    def __init__(self, parent = None, designMode = False):
        TaurusTrend.__init__(self, parent = parent, designMode = designMode)
        
        
        self.setXIsTime(True)
        self.setAxisScale(self.xBottom, 0, 5*60) #set a 5 minutes range by default
        self.setXDynScale(True)
        
        self.setCanvasBackground(Qt.Qt.black)
        
        self.showLegend(False)
        self.enableAxis(self.xBottom, False)
        self.enableAxis(self.xTop, False)
        self.enableAxis(self.yLeft, False)
        self.enableAxis(self.yRight, False)
        self.setAllowZoomers(False)
        self.toggleDataInspectorMode(enable=True)
        self.setMaximumSize(60,60)

    def autoShowYAxes(self):
        '''reimplemented to avoid auto-enabling of axes'''
        pass
    
    def event(self, event):
#        if event.type() == Qt.QEvent.ToolTip: print "!!!!!!!", event.type()
        if event.type() == Qt.QEvent.ToolTip:
#            info = self.getMonitorInfo()
#            self.setToolTip(info)
            event.accept()
        return TaurusTrend.event(self, event)
    
#    def getMonitorInfo(self):
#        time = datetime.datetime.now().isoformat()
##        for 
#        return time
#        #print "!!!!!!!!!", event.type()
#    #def mouse


if __name__ == "__main__":
    import sys
    app = Qt.QApplication(sys.argv)
    
    args=sys.argv[1:]
    
    KLASS = TaurusTrend
    SHOW = True
    EXPORT = None
    CONFIG = None
    MODELS = []
    XISTIME = True
    
    ## MANAGING ARGUMENTS 
    #----------------------------------------------    
    for a in args:
        if a == "-xt":  #argument "-xt" means interprete X values as time
            XISTIME = True
        elif a == "-xe":  #argument "-xe" means interprete X values as events
            XISTIME = False
        elif a.startswith('-config='): #argument "-conf=FILENAME" launches TaurusTrend/Plot with a predefined config file
            CONFIG = a.split('=')[-1]
        elif a.startswith('-'): #whatever other argument starting by "-"
            print "\n Usage: \n%s [-xe|-xt] [-config=configfilename] [model1 [model2] ...]\n"%sys.argv[0]
            sys.exit(1)
        else: #anything that is not a parameter is interpreted as a model
            MODELS.append(a)
    #----------------------------------------------
    
    form =  TaurusMonitorTiny()    
    form.setXIsTime(XISTIME)
    if CONFIG is not None: form.loadConfig(CONFIG)
    #form.setDefaultCurvesTitle("<dev_full_name><[trend_index]>")
    if MODELS: form.setModel(MODELS)  
     
    
    if SHOW:
        form.show()
        #if no models are passed, show the data import dialog
        if len(MODELS) == 0 and CONFIG is None:
            form.showDataImportDlg()
    sys.exit(app.exec_())
