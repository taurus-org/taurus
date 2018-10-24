#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""The img package. It contains specific part of tango devices dedicated to
images (CCDs, detectors, etc)"""
from __future__ import absolute_import

from .img import *

__docformat__ = 'restructuredtext'

def registerExtensions():
    """Registers the image extensions in the :class:`taurus.core.tango.TangoFactory`"""
    import taurus
    factory = taurus.Factory('tango')
    factory.registerDeviceClass('PyImageViewer', PyImageViewer)
    factory.registerDeviceClass('ImgGrabber', ImgGrabber)
    factory.registerDeviceClass('ImgBeamAnalyzer', ImgBeamAnalyzer)
    factory.registerDeviceClass('CCDPVCAM', CCDPVCAM)
    factory.registerDeviceClass('Falcon', Falcon)
    factory.registerDeviceClass('LimaCCDs', LimaCCDs)
