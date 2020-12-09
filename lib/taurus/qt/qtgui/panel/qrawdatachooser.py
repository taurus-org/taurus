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
RawDataChooser.py:  widget for importing RawData (from file or from a function)
"""

__all__ = ["QRawDataWidget"]

import numpy

from taurus.external.qt import Qt
from taurus.core.util.safeeval import SafeEvaluator
from taurus.qt.qtgui.util.ui import UILoadable


@UILoadable
class QRawDataWidget(Qt.QWidget):

    ReadFromFiles = Qt.pyqtSignal(int, int)
    AddCurve = Qt.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(QRawDataWidget, self).__init__(parent)
        self.loadUi()

        # connecttions
        self.openFilesBT.clicked.connect(self.onOpenFilesButtonClicked)
        self.addCurveBT.clicked.connect(self.onAddCurveButtonClicked)

        # set validators in LE's
        self.xFromLE.setValidator(Qt.QDoubleValidator(self))
        self.xToLE.setValidator(Qt.QDoubleValidator(self))
        self.xStepLE.setValidator(Qt.QDoubleValidator(self))

    def onOpenFilesButtonClicked(self):
        """ Emit a ReadFromFiles signal with the selected xcol and skiprows as parameters"""
        xcol = self.xcolSB.value()
        if xcol == self.xcolSB.minimum():
            xcol = None
        skiprows = self.headerSB.value()
        self.ReadFromFiles.emit(xcol, skiprows)

    def onAddCurveButtonClicked(self):
        """ Emit a AddCurve signal with a rawdata dictionary as a parameter.
        The rawdata dictionary is prepared from the from the GUI's selection."""
        rawdata = {}
        if self.xRangeRB.isChecked():
            rawdata['x'] = numpy.arange(float(self.xFromLE.text()), float(
                self.xToLE.text()), float(self.xStepLE.text()))
        else:
            sev = SafeEvaluator()
            try:
                rawdata['x'] = sev.eval(str(self.xValuesLE.text()))
            except:
                Qt.QMessageBox.warning(
                    self, 'Invalid x values' 'Cannot interpret the x values.\n Use Python expressions like "[1, 3 , 67]" or "arange(100)")')
                return
        rawdata['f(x)'] = str(self.f_xLE.text())
        self.AddCurve.emit(rawdata)

if __name__ == "__main__":
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    form = QRawDataWidget()
    form.show()
    sys.exit(app.exec_())
