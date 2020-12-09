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

"""The core module"""
from __future__ import absolute_import

import taurus.tauruscustomsettings

__docformat__ = "restructuredtext"


LIGHTWEIGHT_IMPORTS = getattr(
    taurus.tauruscustomsettings, 'LIGHTWEIGHT_IMPORTS', False)

if LIGHTWEIGHT_IMPORTS:
    from .init_lightweight import *
else:
    from .init_bkcomp import *
