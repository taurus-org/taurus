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

"""Extension of :mod:`guiqwt.styles`"""


__docformat__ = 'restructuredtext'


from guidata.dataset.datatypes import DataSet
from guidata.dataset.dataitems import StringItem, IntItem, ChoiceItem, BoolItem


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


class TaurusTrendParam(DataSet):
    model = StringItem("Model", default="")
    maxBufferSize = IntItem("Buffer Size", default=16384)
    useArchiving = BoolItem("Use Archiving", default=False)
    stackMode = ChoiceItem("Stack Mode",
                           [("datetime",  "Absolute Time"),
                            ("timedelta", "Relative Time"),
                               ("event", "Event")],
                           default="datetime")

    def update_param(self, curve):
        self.model.update_param(curve.taurusparam.model)
        self.maxBufferSize.update_param(curve.taurusparam.maxBufferSize)
        self.stackMode.update_param(curve.taurusparam.stackMode)

    def update_curve(self, curve):
        curve.setModel(self.model)
        curve.setBufferSize(self.maxBufferSize)
        # the stackMode is directly used from the param, so there is no need to
        # update
