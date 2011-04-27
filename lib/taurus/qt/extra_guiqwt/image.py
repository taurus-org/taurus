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
        


def test1():
    """Adapted from guiqwt cross_section.py example"""
    from guiqwt.plot import ImageDialog
    from taurus.qt.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication()
        
    #define a taurus image
    model1 = 'sys/tg_test/1/short_image_ro'
    taurusimage = make.image(taurusmodel= model1)
    
    #adefine normal image (guiqwt standard)
    data = numpy.random.rand(100,100)
    image = make.image(data=data)
    
    #create a dialog with a plot and add the images
    win = ImageDialog(edit=False, toolbar=True, wintitle="Taurus Cross sections test",
                      options=dict(show_xsection=True, show_ysection=True))
    plot = win.get_plot()
    plot.add_item(taurusimage)
    plot.add_item(image)
    win.get_itemlist_panel().show()
    
    #IMPORTANT: connect the cross section plots to the taurusimage so that they are updated when the taurus data changes
    win.connect(taurusimage.getSignaller(), Qt.SIGNAL("dataChanged"), win.update_cross_sections)
    
    win.exec_()


if __name__ == "__main__":
    test1()    

