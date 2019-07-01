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

__all__ = ["DropDebugger"]
__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt


class DropDebugger(Qt.QLabel):
    '''A simple utility for debugging drag&drop.
    This widget will accept drops and show a pop-up with the contents
    of the MIME data passed in the drag&drop'''

    def __init__(self, parent=None):
        Qt.QLabel.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setText('Drop something here')
        self.setMinimumSize(300, 200)
        self.setWindowTitle('Drag&Drop Debugger')

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        '''reimplemented to support drag&drop of models. See :class:`QWidget`'''
        msg = '<b>MIMETYPE</b>: DATA. <ul>'
        mimedata = event.mimeData()
        for format in mimedata.formats():
            data = mimedata.data(format)
            msg += '<li><b>{0}</b>: "{1}"</li>'.format(format, data)
        msg += '</ul>'
        Qt.QMessageBox.information(self, "Drop event received", msg)


if __name__ == '__main__':
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None)
    w = DropDebugger()
    w.show()
    sys.exit(app.exec_())
