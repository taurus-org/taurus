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

"""
Examples on using the evaluation scheme for exposing icepap driver values
as taurus attributes
"""

from __future__ import print_function


ATTR_IPAP_POS = ( 'eval:@ipap=pyIcePAP.EthIcePAP("icepap06", port=5000)' +
                  '/float(ipap.readParameter(1,"POS"))')


def _test1():
    import taurus.core
    a = taurus.Attribute(ATTR_IPAP_POS)
    print("axis pos:", a.read().rvalue)


def _test2():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.display import TaurusLabel
    app = TaurusApplication(cmd_line_parser=None)

    tl = TaurusLabel()
    tl.setModel(ATTR_IPAP_POS)
    tl.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    _test1()
    _test2()
