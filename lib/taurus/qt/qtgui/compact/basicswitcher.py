#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2013 CELLS / ALBA Synchrotron, Bellaterra, Spain
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

"""This module provides some basic usable widgets based on TaurusReadWriteSwitcher
"""

from __future__ import absolute_import

from taurus.qt.qtgui.display import TaurusLabel, TaurusLed
from taurus.qt.qtgui.input import TaurusValueLineEdit, TaurusValueCheckBox
from .abstractswitcher import TaurusReadWriteSwitcher

__all__ = ["TaurusLabelEditRW", "TaurusBoolRW"]

__docformat__ = 'restructuredtext'


class TaurusLabelEditRW(TaurusReadWriteSwitcher):
    '''A Switcher combining a TaurusLabel and a TaurusValueLineEdit'''
    readWClass = TaurusLabel
    writeWClass = TaurusValueLineEdit


class TaurusBoolRW(TaurusReadWriteSwitcher):
    '''A Switcher combining a TaurusLed and a TaurusValueCheckBox'''
    readWClass = TaurusLed
    writeWClass = TaurusValueCheckBox

    def setWriteWidget(self, widget):
        widget.setShowText(False)
        TaurusReadWriteSwitcher.setWriteWidget(self, widget)


def _demo():
    '''demo of integrability in a form'''
    import sys
    from taurus.qt.qtgui.panel import TaurusForm
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None)

    f = TaurusForm()
    f.model = ['sys/tg_test/1/long_scalar', 'sys/tg_test/1/long_scalar',
               'sys/tg_test/1/boolean_scalar', 'sys/tg_test/1/boolean_scalar']

    f[0].setReadWidgetClass(TaurusLabelEditRW)
    f[0].setWriteWidgetClass(None)
    f[2].setReadWidgetClass(TaurusBoolRW)
    f[2].setWriteWidgetClass(None)

    f.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    _demo()
