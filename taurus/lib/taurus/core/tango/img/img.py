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

"""The img submodule. It contains specific device implementation for CCDs and
2D detectors"""

__all__ = ['ImageDevice', 'ImageCounterDevice', 'PyImageViewer', 'ImgGrabber',
           'CCDPVCAM', 'ImgBeamAnalyzer', 'Falcon']

__docformat__ = 'restructuredtext'


from taurus.core.taurusbasetypes import TaurusEventType
from taurus.core.tango import TangoDevice
from taurus.core.util.containers import CaselessDict, CaselessList

class ImageDevice(TangoDevice):
    """A class encapsulating a generic image device"""
    
    def __init__(self, name, image_name='image', **kw):
        self.call__init__(TangoDevice, name, **kw)
        self.setImageAttrName(image_name)

    def addImageAttrName(self, attr_name):
        if attr_name in self._image_attr_names:
            return
        self._image_attr_names.append(attr_name)
            
    def setImageAttrName(self, attr_name):
        self._image_attr_names = CaselessList()
        self.addImageAttrName(attr_name)
        
    def getImageAttrName(self, idx=0):
        return self._image_attr_names[0]
    
    def getImageAttrNames(self):
        return self._image_attr_names


class ImageCounterDevice(ImageDevice):
    """A class encapsulating a generic image device that has an image counter
    attribute"""
    
    def __init__(self, name, image_name='image', **kw):
        self._image_data = CaselessDict()
        self.call__init__(ImageDevice, name, **kw)
        self._image_id_attr = self.getAttribute(self.getImageIDAttrName())
        self._image_id_attr.addListener(self)

    def _setDirty(self, names=None):
        names = names or self.getImageAttrNames()
        for n in names:
            d = self._image_data.get(n, (True, None))
            self._image_data[n] = True, d[1]

    def _getDirty(self, names=None):
        names = names or self.getImageAttrNames()
        dirty = []
        for name in names:
            d = self._image_data.get(name)
            if d is None or d[0] == True:
                dirty.append(name)
        return names

    def getImageIDAttrName(self):
        return 'imagecounter'
    
    def eventReceived(self, evt_src, evt_type, evt_value):
        if evt_src == self._image_id_attr:
            if evt_type == TaurusEventType.Change:
                self._setDirty()
                self.fireEvent(evt_type, evt_value)
        else:
            ImageDevice.eventReceived(self, evt_src, evt_type, evt_value)
    
    def getImageData(self, names=None):
        if names is None:
            names = self.getImageAttrNames()
        elif isinstance(names, str):
            names = (names,)
        
        fetch = self._getDirty(names)
        
        try:
            data = self.read_attributes(fetch)
            for d in data:
                self._image_data[d.name] = False, d
        except:
            pass
        return self._image_data

PyImageViewer = ImageCounterDevice
ImgGrabber = ImageCounterDevice
CCDPVCAM = ImageCounterDevice

class Falcon(ImageCounterDevice):

    def __init__(self, name, image_name='image', **kw):
        self._color = False
        self.call__init__(ImageCounterDevice, name, image_name=image_name, **kw)
        self.imgFormat_Attr = self.getAttribute("imageformat")
        self.imgFormat_Attr.addListener(self)
    
    def eventReceived(self, evt_src, evt_type, evt_value):
        if evt_src == self.getAttribute("imageformat"):
            if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
                self._color = evt_value.value.lower() == "rgb24"
                return
        ImageCounterDevice.eventReceived(self, evt_src, evt_type, evt_value)

    def getImageData(self, names=None):
        data = ImageCounterDevice.getImageData(self, names=names)
        if self._color:
            for k, v in data.items():
                s = v[1].value.shape
                v[1].value = v[1].value.reshape((s[0], s[1]/3, 3))
        return data


class ImgBeamAnalyzer(ImageCounterDevice):
    
    def __init__(self, name, image_name='roiimage', **kw):
        self.call__init__(ImageCounterDevice, name, image_name, **kw)
    
