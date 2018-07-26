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
from sys import version_info as __vi
from taurus.core.util import log as __log

__log.deprecated(dep='taurus.external.unittest', rel='4.3.2', alt='unittest')


if __vi[:2] < (2,7):
    try:
        from unittest2 import *
    except ImportError:
        raise ImportError("With python <= 2.6 taurus requires unittest2 "
                          "which is not available")
else:
    from unittest import *
