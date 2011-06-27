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
Extension of :mod:`guiqwt.image`
"""
__all__=["TaurusImageItem"]

from PyQt4 import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
import taurus.core
from taurus.core.util import ArrayBuffer

from guiqwt.image import ImageItem, XYImageItem, INTERP_NEAREST, INTERP_LINEAR

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
    
    def setModel(self, model):
        #do the standard stuff
        TaurusBaseComponent.setModel(self, model)
        #... and fire a fake event for initialization
        try:
            value = self.getModelObj().read()
            self.fireEvent(self, taurus.core.TaurusEventType.Change, value)
        except:
            pass

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_value is None or getattr(evt_value,'value', None) is None:
            self.debug('Ignoring event from %s'%repr(evt_src))
            return
        self.set_data(evt_value.value)
        self.getSignaller().emit(Qt.SIGNAL('dataChanged'))
        p = self.plot()
        if p is not None: 
            p.replot()
        
class TaurusTrend2DItem(XYImageItem, TaurusBaseComponent):
    '''A XYImageItem that is constructed by stacking 1D arrays from events from a Taurus 1D attribute'''
    def __init__(self, param=None, buffersize=512, xIsTime=False):
        XYImageItem.__init__(self, numpy.arange(2), numpy.arange(2), numpy.zeros((2,2)), param=param)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self._signalGen = Qt.QObject()
        self.maxBufferSize = buffersize
        self.__yValues = None
        self.__xBuffer = None
        self.__zBuffer = None
        self.xIsTime = xIsTime
        self.set_interpolation(INTERP_NEAREST)

    def getSignaller(self):
        '''reimplemented from TaurusBaseComponent because TaurusImageItem is 
        not (and cannot be) a QObject'''
        return self._signalGen  
    
    def setBufferSize(self, buffersize):
        '''sets the size of the stack
        
        :param buffersize: (int) size of the stack
        '''
        self.maxBufferSize = buffersize
        try:
            if self.__xBuffer is not None:
                self.__xBuffer.setMaxSize(buffersize)
            if self.__zBuffer is not None:
                self.__zBuffer.setMaxSize(buffersize)
        except ValueError:
            self.info('buffer downsizing  requested. Current contents will be discarded')
            self.__xBuffer = None
            self.__zBuffer = None
        
    def setModel(self, model):
        #do the standard stuff
        TaurusBaseComponent.setModel(self, model)
        #... and fire a fake event for initialization
        try:
            value = self.getModelObj().read()
            self.fireEvent(self, taurus.core.TaurusEventType.Change, value)
        except:
            pass

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_value is None or getattr(evt_value,'value', None) is None:
            self.debug('Ignoring event from %s'%repr(evt_src))
            return
        
        plot = self.plot()
            
        #initialization
        ySize = len(evt_value.value)
        if self.__yValues is None:
            self.__yValues = numpy.arange(ySize,dtype='d')
        if self.__xBuffer is None:
            self.__xBuffer = ArrayBuffer(numpy.zeros(min(128,self.maxBufferSize), dtype='d'), maxSize=self.maxBufferSize )
        if self.__zBuffer is None:
            self.__zBuffer = ArrayBuffer(numpy.zeros((min(128,self.maxBufferSize), ySize),dtype='d'), maxSize=self.maxBufferSize )
            return
        
        #check that new data is compatible with previous data    
        if ySize != self.__yValues.size:
            self.info('Incompatible shape in data from event (orig=%i, current=%i). Ignoring'%(self.__yValues.size, ySize))
            return
        
        #update x values
        if self.xIsTime:
            self.__xBuffer.append(evt_value.time.totime())
            print "!!!", evt_value.time.totime(), evt_value.time.isoformat()
        else:  
            try:
                step = 1 # +numpy.random.randint(0,4) #for debugging we can put a variable step
                self.__xBuffer.append(self.__xBuffer[-1]+step) 
            except IndexError: #this will happen when the x buffer is empty
                self.__xBuffer.append(0) 
        
        #update z
        self.__zBuffer.append(evt_value.value)
        
        #check if there is enough data to start plotting
        if len(self.__xBuffer)<2:
            self.info('waiting for at least 2 values to start plotting') 
            return
        
        x = self.__xBuffer.contents()
        y = self.__yValues
        z = self.__zBuffer.contents().transpose()
        
        if x.size == 2:
            plot.set_axis_limits('left',y.min(), y.max())
            xmax = x[0]+(x[1]-x[0])*self.maxBufferSize #guess the max of the scale allowed by the buffer
            plot.set_axis_limits('bottom', x.min(), xmax)
        
        #update the plot data
        self.set_data(z)
        self.set_xy(x, y)
        
        #signal data changed and replot
        self.getSignaller().emit(Qt.SIGNAL('dataChanged'))
        
        if plot is not None: 
            plot.replot()
            



def taurusImageMain():
    from guiqwt.tools import (RectangleTool, EllipseTool, HRangeTool, PlaceAxesTool,
                          MultiLineTool, FreeFormTool, SegmentTool, CircleTool,
                          AnnotatedRectangleTool, AnnotatedEllipseTool,
                          AnnotatedSegmentTool, AnnotatedCircleTool, LabelTool,
                          AnnotatedPointTool, VCursorTool, HCursorTool,
                          AnnotatedVCursorTool, AnnotatedHCursorTool,
                          ObliqueRectangleTool, AnnotatedObliqueRectangleTool)
    from taurus.qt.extra_guiqwt.tools import TaurusImageChooserTool
    from guiqwt.plot import ImageDialog
    from taurus.qt.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    import taurus.core.util.argparse
    import sys
    
    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [<model1> [<model2>] ...]")
    parser.set_description("a taurus application for plotting 2D data sets")
    app = TaurusApplication(cmd_line_parser=parser, app_name="taurusimage", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    
    #create a dialog with a plot and add the images
    win = ImageDialog(edit=False, toolbar=True, wintitle="Taurus Image",
                      options=dict(show_xsection=False, show_ysection=False))
    
    #add tools
    for toolklass in (TaurusImageChooserTool,
                      LabelTool, HRangeTool, 
                      MultiLineTool, FreeFormTool, PlaceAxesTool,
                      AnnotatedObliqueRectangleTool,
                      AnnotatedEllipseTool, AnnotatedSegmentTool,
                      AnnotatedPointTool, AnnotatedVCursorTool,
                      AnnotatedHCursorTool):
        win.add_tool(toolklass)
    
    #add images from given models
    plot = win.get_plot()
    for m in args:
        img = make.image(taurusmodel= m)
        plot.add_item(img)
        win.connect(img.getSignaller(), Qt.SIGNAL("dataChanged"), win.update_cross_sections) #IMPORTANT: connect the cross section plots to the taurusimage so that they are updated when the taurus data changes
        
    win.exec_()

def test1():
    """Adapted from guiqwt cross_section.py example"""
    from guiqwt.plot import ImageDialog
    from taurus.qt.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication()
        
    #define a taurus image
    model1 = 'sys/tg_test/1/short_image_ro'
    taurusimage = make.image(taurusmodel= model1)
    
    #define normal image (guiqwt standard)
    data = numpy.random.rand(100,100)
    image = make.image(data=data)
    
    #create a dialog with a plot and add the images
    win = ImageDialog(edit=False, toolbar=True, wintitle="Taurus Cross sections test",
                      options=dict(show_xsection=False, show_ysection=False))
    from taurus.qt.extra_guiqwt.tools import TaurusImageChooserTool
    win.add_tool(TaurusImageChooserTool)
    plot = win.get_plot()
    plot.add_item(taurusimage)
    plot.add_item(image)
#    win.get_itemlist_panel().show()
    
    #IMPORTANT: connect the cross section plots to the taurusimage so that they are updated when the taurus data changes
    win.connect(taurusimage.getSignaller(), Qt.SIGNAL("dataChanged"), win.update_cross_sections)
    
    win.exec_()


if __name__ == "__main__":
    taurusImageMain()   

