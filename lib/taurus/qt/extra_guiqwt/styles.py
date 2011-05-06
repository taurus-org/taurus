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

"""Extension of :mod:`guiqwt.styles`"""



__docformat__ = 'restructuredtext'


from guidata.dataset.datatypes import DataSet
from guidata.dataset.dataitems import StringItem


# ===================================================
# Taurus Curve parameters
# ===================================================
class TaurusCurveParam(DataSet):
    xModel = StringItem("Model for X", default="")
    yModel = StringItem("Model for Y", default="")

    def update_param(self, curve):
        self.xModel.update_param(curve.taurusparam.xModel)
        self.yModel.update_param(curve.taurusparam.yModel)
#        DataSet.update_param(self, curve)
    
    def update_curve(self, curve):
        curve.setModels(self.xModel or None, self.yModel)
#        DataSet.update_curve(self, curve)
        