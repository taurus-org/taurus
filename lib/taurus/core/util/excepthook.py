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

"""This module contains a base class for exception hooks"""

import sys
from builtins import object

__all__ = ["BaseExceptHook"]

__docformat__ = "restructuredtext"


class BaseExceptHook(object):
    """A callable class that acts as an excepthook that handles an exception.
    This base class simply calls the :obj:`sys.__excepthook__`

    :param hook_to: callable excepthook that will be called at the end of
                    this hook handling [default: None]
    :type hook_to: callable"""

    def __init__(self, hook_to=None):
        self._excepthook = hook_to

    def __call__(self, *exc_info):
        self.report(*exc_info)
        if self._excepthook is not None:
            return self._excepthook(*exc_info)

    def report(self, *exc_info):
        """Report an exception. Overwrite as necessary"""
        return sys.__excepthook__(*exc_info)
