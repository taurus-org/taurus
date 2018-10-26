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

"""A pure Qt widget designed to be displayed when a real widget cannot be
loaded for any reason (example: a dependency library is not installed)"""

__all__ = ["create_fallback", "create_taurus_fallback", "QFallBackWidget",
           "TaurusFallBackWidget"]

__docformat__ = 'restructuredtext'

import sys
import functools
from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget


def create_fallback(widget_klass_name):
    return functools.partial(QFallBackWidget, replaces=widget_klass_name,
                             exc_info=sys.exc_info())


def create_taurus_fallback(widget_klass_name):
    return functools.partial(TaurusFallBackWidget, replaces=widget_klass_name,
                             exc_info=sys.exc_info())


class QFallBackWidget(Qt.QWidget):
    """A FallBack widget to be used when a real widget cannot be loaded for any
    reason (example: a dependency library is not installed)"""

    def __init__(self, replaces=None, parent=None, *args, **kwargs):
        Qt.QWidget.__init__(self, parent)
        if replaces is None:
            replaces = self.__class__.__name__
        self.replaces = replaces
        self.exc_info = exc_info = kwargs.get("exc_info")
        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        self.setLayout(layout)
        self.label = Qt.QLabel(self)
        self.label.setText("'{0}' could not be displayed".format(replaces))
        layout.addWidget(self.label, 0, Qt.Qt.AlignVCenter)
        if exc_info is not None and exc_info[0] is not None:
            self.details_button = Qt.QPushButton("Details...", self)
            layout.addWidget(self.details_button, 0, Qt.Qt.AlignTop)
            self.details_button.clicked.connect(self.onShowDetails)
        layout.addStretch(1)

    def onShowDetails(self):
        import taurus.qt.qtgui.dialog
        msgbox = taurus.qt.qtgui.dialog.TaurusMessageBox(*self.exc_info,
                                                         parent=self)
        msgbox.setWindowTitle("{0} Error".format(self.replaces))
        msgbox.setText(self.label.text())
        msgbox.exec_()


class TaurusFallBackWidget(QFallBackWidget, TaurusBaseWidget):

    def __init__(self, replaces=None, parent=None, *args, **kwargs):
        self.call__init__(QFallBackWidget, replaces=replaces,
                          parent=parent, *args, **kwargs)
        designMode = kwargs.get("designMode", False)
        self.call__init__(TaurusBaseWidget, replaces, designMode=designMode)
