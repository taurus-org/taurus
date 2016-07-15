# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Taurus
##
## http://taurus-scada.org
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
##############################################################################

from __future__ import absolute_import

from taurus.core.util.log import deprecated


deprecated(dep='taurus.external.ordereddict', rel='4.0', alt='ordereddict')


try:
    # ordereddict from python 2.7 or from ordereddict installed package?
    from ordereddict import *
except ImportError:
    # ordereddict from local import
    import os
    import sys
    import warnings
    warnings.warn("ordereddict not available. Using local ordereddict",
                  ImportWarning)
    sys.path.append(os.path.dirname(__file__))
    from ordereddict import *
    del warnings
    del sys
    del os
