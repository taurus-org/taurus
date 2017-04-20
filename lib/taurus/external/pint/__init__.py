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

try:
    from pint import __version__
    if __version__.split('.') < ['0','8']:
        raise ImportError()
    from pint import *

except ImportError:
    import warnings
    warnings.warn("pint >=0.8 not available. Using local pint", ImportWarning)
    from .pint_local import *
    from .pint_local import __version__ as __local_pint_version
    __version__ = __local_pint_version + '-taurus'
    del warnings

# Ininitialize the unit registry for taurus
UR = UnitRegistry()
UR.default_format = '~' # use abbreviated units
Q_ = Quantity = UR.Quantity

