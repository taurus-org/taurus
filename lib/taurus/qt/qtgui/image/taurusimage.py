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
from taurus.qt.qtgui.base import TaurusBaseComponent
from guiqwt.image import ImageItem
import numpy

class TaurusImageItem(ImageItem, TaurusBaseComponent):
    '''A ImageItem that gets its data from a taurus attribute'''
    def __init__(self, param=None):
        ImageItem.__init__(self, numpy.zeros((1,1)), param=param)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self._signalGen = Qt.QObject()

    def getSignaller(self):
        '''reimplemented from TaurusBaseComponent because TaurusImageItem is 
        not (and cannot be) a QObject'''
        return self._signalGen   
        
    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_value is None or getattr(evt_value,'value', None) is None:
            self.warning('Ignoring event from %s'%repr(evt_src))
            return
        self.set_data(evt_value.value)
        self.getSignaller().emit(Qt.SIGNAL('dataChanged'))
        p = self.plot()
        if p is not None: 
            p.replot()
        
def main():
    '''launch'''
    from guiqwt.plot import ImagePlotWidget,ImagePlotDialog
    import sys
    from guiqwt.image import  ImageParam
    from taurus.qt.qtgui.application import TaurusApplication
    
    app = TaurusApplication()
    args = app.get_command_line_args()
    if len (args)==1:
        model = args[0]
    else:
        model = 'sys/tg_test/1/short_image_ro'
        #model = 'eval://{sys/tg_test/1/short_image_ro}+10*rand(251,251)'
        #model = 'eval://{sys/tg_test/1/short_image_ro}+10*rand(*shape({sys/tg_test/1/short_image_ro}))' #we can iven do this!!

    w = ImagePlotDialog(toolbar=True)
    #w = ImagePlotWidget()
    #w.register_all_image_tools()
    plot = w.get_plot()
    
    param = ImageParam()
   
    param.label = model
    img = TaurusImageItem(param)
    img.setModel(model)
    
       
    plot.add_item(img)
    plot.do_autoscale(replot=True)
    #connect the cross section plots so that they are updated on signal changes
    w.connect(img.getSignaller(), Qt.SIGNAL("dataChanged"), w.update_cross_sections)

    #show the widget
    w.show()
    
    sys.exit(app.exec_()) 

if __name__ == "__main__":
    main()    

