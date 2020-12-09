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

__all__ = ['EvaluationDevice']

from taurus import Factory
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.util.safeeval import SafeEvaluator
from taurus.core.taurusbasetypes import TaurusDevState, TaurusAttrValue


class EvaluationDevice(TaurusDevice, SafeEvaluator):
    """The evaluator object. It is a :class:`TaurusDevice` and is used as the
    parent of :class:`EvaluationAttribute` objects for which it performs the
    mathematical evaluation.

    .. seealso:: :mod:`taurus.core.evaluation`

    .. warning:: In most cases this class should not be instantiated directly.
                 Instead it should be done via the
                 :meth:`EvaluationFactory.getDevice`
    """
    _symbols = []
    # helper class property that stores a reference to the corresponding
    # factory
    _factory = None
    _scheme = 'eval'

    def __init__(self, name='', **kw):
        """Object initialization."""
        self.call__init__(TaurusDevice, name, **kw)
        safedict = {}
        for s in self._symbols:
            if hasattr(self, s):
                safedict[s] = getattr(self, s)
        SafeEvaluator.__init__(self, safedict=safedict)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusDevice necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def _createHWObject(self):
        return 'Evaluation'

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def getAttribute(self, attrname):
        """Returns the attribute object given its name"""
        full_attrname = "%s;%s" % (self.getFullName(), attrname)
        return self.factory().getAttribute(full_attrname)

    def decode(self, event_value):
        # TODO: Is this method ever called? (or maybe just garbage from 3.x?)
        if isinstance(event_value, int):  # TaurusSWDevState
            new_sw_state = event_value
        else:
            self.info("Unexpected value to decode: %s" % str(event_value))
            new_sw_state = TaurusDevState.NotReady
        value = TaurusAttrValue()
        value.rvalue = new_sw_state
        return value
