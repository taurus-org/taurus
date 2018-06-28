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

"""DEPRECATED since 4.0,4. Use `silx.gui.console`"""

__docformat__ = 'restructuredtext'


from taurus.core.util.log import deprecated

deprecated(dep='TaurusConsole', alt='silx.gui.console.IPythonWidget',
           rel='4.0.4')

try:
    from silx.gui.console import IPythonWidget as TaurusConsole
except Exception as e:
    from taurus.qt.qtgui.display import TaurusFallBackWidget

    class TaurusConsole(TaurusFallBackWidget):
        pass


