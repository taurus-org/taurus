#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This package contains a collection of taurus widgets designed to connect
to sardana"""

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.resource import getIcon, getThemeIcon


class CommandLineHistory(list):
    pass

class CommandLine(Qt.QComboBox):

    def __init__(self, qt_parent=None, designMode=False):
        Qt.QComboBox.__init__(self, qt_parent)
        self.setEditable(True)
        self.setFrame(False)

class TaurusCommandLineWidget(Qt.QWidget):

    def __init__(self, qt_parent=None, designMode=False):
        Qt.QWidget.__init__(self, qt_parent)

        self._history = CommandLineHistory()

        l = Qt.QHBoxLayout()
        self.setLayout(l)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(0)

        self._detailsButton = Qt.QToolButton()
        self._detailsButton.setText("...")

        self._cmdLine = Qt.QComboBox()
        self._cmdLine.setEditable(True)

        self._applyButton = Qt.QToolButton()
        self._applyButton.setIcon(getIcon(":/actions/media_playback_start.svg"))

        self._stopButton = Qt.QToolButton()
        self._stopButton.setIcon(getIcon(":/actions/media_playback_stop.svg"))

        self._clearButton = Qt.QToolButton()
        self._clearButton.setIcon(getThemeIcon("edit-clear"))

        l.addWidget(self._detailsButton, 0)
        l.addWidget(self._cmdLine, 1)
        l.addWidget(self._applyButton, 0)
        l.addWidget(self._stopButton, 0)
        l.addWidget(self._clearButton, 0)



    def run(self):
        pass

def demo():
    pass

def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        app = Application(sys.argv, cmd_line_parser=parser,
                          app_name="Taurus command line demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    w = TaurusCommandLineWidget()
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()
