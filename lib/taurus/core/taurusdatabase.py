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

"""Do not use. Deprecated. Backwards compatibility module for transition from
TaurusDatabase to TaurusAuthority"""


from logging import warning
warning('taurusdatabase module is deprecated. Use taurusauthority instead')

import traceback
traceback.print_stack()

from .taurusauthority import *

TaurusDatabase = TaurusAuthority

# The following block is commented out because it produces a circular import
# try:
#     from taurus.core.tango.tangodatabase import TangoInfo as TaurusInfo
#     from taurus.core.tango.tangodatabase import TangoAttrInfo as TaurusAttrInfo
#     from taurus.core.tango.tangodatabase import TangoDevInfo as TaurusDevInfo
#     from taurus.core.tango.tangodatabase import TangoDevClassInfo as \
#                                                             TaurusDevClassInfo
#     from taurus.core.tango.tangodatabase import TangoServInfo as TaurusServInfo
# except ImportError, e:
#     warning('taurusdatabase: Cannot import tango info objects: %s', repr(e))
#
