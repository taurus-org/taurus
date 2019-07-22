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
arrayedit.py: Widget for editing a spectrum/array via control points
"""
from __future__ import absolute_import

from builtins import range
import numpy
from taurus.external.qt import Qt, Qwt5
from taurus.qt.qtgui.util.ui import UILoadable
from .curvesAppearanceChooserDlg import CurveAppearanceProperties


@UILoadable
class ControllerBox(Qt.QWidget):

    selected = Qt.pyqtSignal(int)

    def __init__(self, parent=None, x=0, y=0, corr=0):
        Qt.QWidget.__init__(self, parent)
        self.loadUi()
        self._x = x
        self.setY(y)
        self.box.setTitle('x=%6g' % self._x)
        self.corrSB.setValue(corr)
        self.ctrlObj = self.corrSB.ctrlObj = self.lCopyBT.ctrlObj = self.rCopyBT.ctrlObj = self.lScaleBT.ctrlObj = self.rScaleBT.ctrlObj = self
        # reimplementing the focusInEvent method for the spinbox
        self.corrSB.focusInEvent = self.corrSB_focusInEvent
        self.box.mousePressEvent = self.mousePressEvent
        #self.connect(self.corrSB, Qt.SIGNAL('valueChanged(double)'), self.enableScale)

    def mousePressEvent(self, event):
        self.selected.emit(self._x)
        # print 'SELECTED', self
        #Qt.QDoubleSpinBox.focusInEvent(self.corrSB, event)

    def corrSB_focusInEvent(self, event):
        self.selected.emit(self._x)
        # print 'GOT FOCUS', self
        Qt.QDoubleSpinBox.focusInEvent(self.corrSB, event)

    def setY(self, y):
        self._y = y
        self.enableScale()

    def enableScale(self, *args):
        enable = (self._y + self.corrSB.value()) != 0
        self.lScaleBT.setEnabled(enable)
        self.rScaleBT.setEnabled(enable)


@UILoadable
class EditCPointsDialog(Qt.QDialog):

    def __init__(self, parent=None, x=0):
        Qt.QDialog.__init__(self, parent)
        self.loadUi()


@UILoadable
class AddCPointsDialog(Qt.QDialog):

    def __init__(self, parent=None, x=0):
        Qt.QDialog.__init__(self, parent)
        self.loadUi()


@UILoadable
class ArrayEditor(Qt.QWidget):

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self.loadUi()

        self._controllers = []

        # construct the layout for controllers container
        self.ctrlLayout = Qt.QHBoxLayout(self.controllersContainer)
        self.ctrlLayout.setContentsMargins(5, 0, 5, 0)
        self.ctrlLayout.setSpacing(1)

        # implement scroll bars for the controllers container
        self.scrollArea = Qt.QScrollArea(self)
        self.scrollArea.setWidget(self.controllersContainer)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.cpointsGroupBox.layout().insertWidget(0, self.scrollArea)

        # initialize data
        cpoints = 2
        self.x = numpy.arange(256, dtype='double')
        self.y = numpy.zeros(256, dtype='double')
        self.xp = numpy.linspace(self.x[0], self.x[-1], cpoints)
        self.corrp = numpy.zeros(cpoints)
        self.yp = numpy.interp(self.xp, self.x, self.y)
        self.corr = numpy.zeros(self.x.size)

        # markers
        self.markerPos = self.xp[0]
        self.marker1 = Qwt5.QwtPlotMarker()
        self.marker1.setSymbol(Qwt5.QwtSymbol(Qwt5.QwtSymbol.Rect,
                                              Qt.QBrush(Qt.Qt.NoBrush),
                                              Qt.QPen(Qt.Qt.green),
                                              Qt.QSize(8, 8)))
        self.marker1.attach(self.plot1)
        self.marker2 = Qwt5.QwtPlotMarker()
        self.marker2.setSymbol(Qwt5.QwtSymbol(Qwt5.QwtSymbol.Rect,
                                              Qt.QBrush(Qt.Qt.NoBrush),
                                              Qt.QPen(Qt.Qt.green),
                                              Qt.QSize(8, 8)))
        self.marker2.attach(self.plot2)

        # cpointsPickers
        self._cpointMovingIndex = None
        self._cpointsPicker1 = Qwt5.QwtPicker(self.plot1.canvas())
        self._cpointsPicker1.setSelectionFlags(Qwt5.QwtPicker.PointSelection)
        self._cpointsPicker2 = Qwt5.QwtPicker(self.plot2.canvas())
        self._cpointsPicker2.setSelectionFlags(Qwt5.QwtPicker.PointSelection)
        self._cpointsPicker1.widgetMousePressEvent = self.plot1MousePressEvent
        self._cpointsPicker1.widgetMouseReleaseEvent = self.plot1MouseReleaseEvent
        self._cpointsPicker2.widgetMousePressEvent = self.plot2MousePressEvent
        self._cpointsPicker2.widgetMouseReleaseEvent = self.plot2MouseReleaseEvent
        self._cpointsPicker1.widgetMouseDoubleClickEvent = self.plot1MouseDoubleClickEvent
        self._cpointsPicker2.widgetMouseDoubleClickEvent = self.plot2MouseDoubleClickEvent
        self._populatePlots()
        self.resetCorrection()
        self._selectedController = self._controllers[0]

        self._addCPointsDialog = AddCPointsDialog(self)

        # Launch low-priority initializations (to speed up load time)
        # Qt.QTimer.singleShot(0, <method>)

        # connections
        self.addCPointsBT.clicked.connect(self._addCPointsDialog.show)
        self._addCPointsDialog.editBT.clicked.connect(self.showEditCPointsDialog)
        self._addCPointsDialog.cleanBT.clicked.connect(self.resetCorrection)
        self._addCPointsDialog.addSingleCPointBT.clicked.connect(self.onAddSingleCPointBT)
        self._addCPointsDialog.addRegEspCPointsBT.clicked.connect(self.onAddRegEspCPointsBT)

    def plot1MousePressEvent(self, event):
        self.plotMousePressEvent(event, self.plot1)

    def plot2MousePressEvent(self, event):
        self.plotMousePressEvent(event, self.plot2)

    def plotMousePressEvent(self, event, taurusplot):
        picked, pickedCurveName, pickedIndex = taurusplot.pickDataPoint(
            event.pos(), scope=20, showMarker=False, targetCurveNames=['Control Points'])
        if picked is not None:
            self.changeCPointSelection(picked.x())
            self.makeControllerVisible(self._controllers[pickedIndex])
            self._cpointMovingIndex = pickedIndex
            self._movingStartYPos = event.y()
            taurusplot.canvas().setCursor(Qt.Qt.SizeVerCursor)

    def plot1MouseReleaseEvent(self, event):
        self.plotMouseReleaseEvent(event, self.plot1)

    def plot2MouseReleaseEvent(self, event):
        self.plotMouseReleaseEvent(event, self.plot2)

    def plotMouseReleaseEvent(self, event, taurusplot):
        if self._cpointMovingIndex is None:
            return  # if no cpoint was picked, do nothing on release
        # no motion s performed if the y position is unchanged or if the mouse
        # release is out of the canvas
        validMotion = (self._movingStartYPos != event.pos().y()
                       ) and taurusplot.canvas().rect().contains(event.pos())
        if validMotion:
            # calculate the new correction
            newCorr = taurusplot.invTransform(
                taurusplot.getCurve('Control Points').yAxis(), event.y())
            if taurusplot is self.plot1:
                newCorr -= self.yp[self._cpointMovingIndex]
            # apply new correction
            self._controllers[self._cpointMovingIndex].corrSB.setValue(newCorr)
        # reset the moving state
        self._cpointMovingIndex = None
        taurusplot.canvas().setCursor(Qt.Qt.CrossCursor)

    def plot1MouseDoubleClickEvent(self, event):
        self.plotMouseDoubleClickEvent(event, self.plot1)

    def plot2MouseDoubleClickEvent(self, event):
        self.plotMouseDoubleClickEvent(event, self.plot2)

    def plotMouseDoubleClickEvent(self, event, taurusplot):
        picked, pickedCurveName, pickedIndex = taurusplot.pickDataPoint(
            event.pos(), scope=20, showMarker=False, targetCurveNames=['Control Points'])
        if picked is not None:
            return  # we dont want to create a control point too close of an existing one
        xp = taurusplot.invTransform(taurusplot.getCurve(
            'Control Points').xAxis(), event.x())
        if xp < self.xp[0] or xp > self.xp[-1]:
            return  # we dont want to create control points out of the curve range
        if Qt.QMessageBox.question(self, 'Create Control Point?', 'Insert a new control point at x=%g?' % xp, 'Yes', 'No') == 0:
            self.insertController(xp)
            self.changeCPointSelection(xp)
            # singleshot is used as a hack to get out of the eventhandler
            Qt.QTimer.singleShot(1, self.makeControllerVisible)

    def makeControllerVisible(self, ctrl=None):
        if ctrl is None:
            ctrl = self._selectedController
        self.scrollArea.ensureWidgetVisible(ctrl)

    def connectToController(self, ctrl):
        ctrl.selected.connect(self.changeCPointSelection)
        ctrl.corrSB.valueChanged.connect(self.onCorrSBChanged)
        ctrl.lCopyBT.clicked.connect(self.onLCopy)
        ctrl.rCopyBT.clicked.connect(self.onRCopy)
        ctrl.lScaleBT.clicked.connect(self.onLScale)
        ctrl.rScaleBT.clicked.connect(self.onRScale)

    def onAddSingleCPointBT(self):
        x = self._addCPointsDialog.singleCPointXSB.value()
        self.insertController(x)

    def onAddRegEspCPointsBT(self):
        cpoints = self._addCPointsDialog.regEspCPointsSB.value()
        positions = numpy.linspace(self.x[0], self.x[-1], cpoints + 2)[1:-1]
        for xp in positions:
            self.insertController(xp)

    def showEditCPointsDialog(self):
        dialog = EditCPointsDialog(self)
        table = dialog.tableTW
        table.setRowCount(self.xp.size)
        for i, (xp, corrp) in enumerate(zip(self.xp, self.corrp)):
            table.setItem(i, 0, Qt.QTableWidgetItem(str(xp)))
            table.setItem(i, 1, Qt.QTableWidgetItem(str(corrp)))

        # show dialog and update values if it is accepted
        if dialog.exec_():
            # delete previous controllers
            for c in self._controllers:
                c.setParent(None)
                c.deleteLater()
            self._controllers = []
            # and create them anew
            new_xp = numpy.zeros(table.rowCount())
            new_corrp = numpy.zeros(table.rowCount())
            try:
                for i in range(table.rowCount()):
                    new_xp[i] = float(table.item(i, 0).text())
                    new_corrp[i] = float(table.item(i, 1).text())
                self.setCorrection(new_xp, new_corrp)
            except:
                Qt.QMessageBox.warning(
                    self, 'Invalid data', 'Some values were not valid. Edition is ignored.')

    def _getInsertionIndex(self, xp):
        i = 0
        while (self.xp[i] < xp):
            i += 1
        return i

    def insertControllers(self, xplist):
        for xp in xplist:
            self.insertController(xp)

    def insertController(self, xp, index=None):
        if xp in self.xp:
            return None
        if index is None:
            index = self._getInsertionIndex(xp)
        # updating data (not in the most efficient way, but at least is clean)
        old_xp = self.xp
        self.xp = numpy.concatenate((self.xp[:index], (xp,), self.xp[index:]))
        self.yp = numpy.interp(self.xp, self.x, self.y)
        # the new correction is obtained by interpolation from the neighbouring
        # ones
        self.corrp = numpy.interp(self.xp, old_xp, self.corrp)
        # creating the controller
        ctrl = ControllerBox(parent=None, x=xp, y=self.yp[
                             index], corr=self.corrp[index])
        self.ctrlLayout.insertWidget(index, ctrl)
        self._controllers.insert(index, ctrl)
        self.connectToController(ctrl)
        self.updatePlots()
        return index

    def delController(self, index):
        c = self._controllers.pop(index)
        c.setParent(None)
        c.deleteLater()
        self.xp = numpy.concatenate((self.xp[:index], self.xp[index + 1:]))
        self.yp = numpy.interp(self.xp, self.x, self.y)
        self.corrp = numpy.concatenate(
            (self.corrp[:index], self.corrp[index + 1:]))

    def _populatePlots(self):
        # Curves appearance
        self._yAppearance = CurveAppearanceProperties(
            sStyle=Qwt5.QwtSymbol.NoSymbol,
            lStyle=Qt.Qt.SolidLine,
            lWidth=2,
            lColor='black',
            cStyle=Qwt5.QwtPlotCurve.Lines,
            yAxis=Qwt5.QwtPlot.yLeft)

        self._correctedAppearance = CurveAppearanceProperties(
            sStyle=Qwt5.QwtSymbol.NoSymbol,
            lStyle=Qt.Qt.DashLine,
            lWidth=1,
            lColor='blue',
            cStyle=Qwt5.QwtPlotCurve.Lines,
            yAxis=Qwt5.QwtPlot.yLeft)

        self._cpointsAppearance = CurveAppearanceProperties(
            sStyle=Qwt5.QwtSymbol.Rect,
            sSize=5,
            sColor='blue',
            sFill=True,
            lStyle=Qt.Qt.NoPen,
            yAxis=Qwt5.QwtPlot.yLeft)

        self._corrAppearance = CurveAppearanceProperties(
            sStyle=Qwt5.QwtSymbol.NoSymbol,
            lStyle=Qt.Qt.SolidLine,
            lWidth=1,
            lColor='blue',
            cStyle=Qwt5.QwtPlotCurve.Lines,
            yAxis=Qwt5.QwtPlot.yLeft)

        self.plot1.attachRawData({'x': self.x, 'y': self.y, 'title': 'Master'})
        self.plot1.setCurveAppearanceProperties({'Master': self._yAppearance})

        self.plot1.attachRawData(
            {'x': self.xp, 'y': self.yp + self.corrp, 'title': 'Control Points'})
        self.plot1.setCurveAppearanceProperties(
            {'Control Points': self._cpointsAppearance})

        self.plot1.attachRawData(
            {'x': self.x, 'y': self.y + self.corr, 'title': 'Corrected'})
        self.plot1.setCurveAppearanceProperties(
            {'Corrected': self._correctedAppearance})

        self.plot2.attachRawData(
            {'x': self.x, 'y': self.corr, 'title': 'Correction'})
        self.plot2.setCurveAppearanceProperties(
            {'Correction': self._corrAppearance})

        self.plot2.attachRawData(
            {'x': self.xp, 'y': self.corrp, 'title': 'Control Points'})
        self.plot2.setCurveAppearanceProperties(
            {'Control Points': self._cpointsAppearance})

    def updatePlots(self):
        self.plot1.getCurve('Control Points').setData(
            self.xp, self.yp + self.corrp)
        self.plot1.getCurve('Corrected').setData(self.x, self.y + self.corr)
        self.plot2.getCurve('Correction').setData(self.x, self.corr)
        self.plot2.getCurve('Control Points').setData(self.xp, self.corrp)
        index = self._getInsertionIndex(self.markerPos)
        self.marker1.setValue(self.xp[index], self.yp[
                              index] + self.corrp[index])
        self.marker2.setValue(self.xp[index], self.corrp[index])
        self.plot1.replot()
        self.plot2.replot()

    def onLCopy(self, checked):
        sender = self.sender().ctrlObj
        index = self._getInsertionIndex(sender._x)
        v = sender.corrSB.value()
        for ctrl in self._controllers[:index]:
            ctrl.corrSB.setValue(v)

    def onRCopy(self, checked):
        sender = self.sender().ctrlObj
        index = self._getInsertionIndex(sender._x)
        v = sender.corrSB.value()
        for ctrl in self._controllers[index + 1:]:
            ctrl.corrSB.setValue(v)

    def onLScale(self, checked):
        sender = self.sender().ctrlObj
        index = self._getInsertionIndex(sender._x)
        # y=numpy.interp(self.xp, self.x, self.y) #values of the master at the
        # control points
        if self.yp[index] == 0:
            Qt.QMessageBox.warning(
                self, 'Scaling Error', 'The master at this control point is zero-valued. This point cannot be used as reference for scaling')
            return
        v = sender.corrSB.value() / (self.yp[index])
        for i in range(0, index):
            self._controllers[i].corrSB.setValue(v * self.yp[i])

    def onRScale(self, checked):
        sender = self.sender().ctrlObj
        index = self._getInsertionIndex(sender._x)
        # y=numpy.interp(self.xp, self.x, self.y) #values of the master at the
        # control points
        if self.yp[index] == 0:
            Qt.QMessageBox.warning(
                self, 'Scaling Error', 'The master at this control point is zero-valued. This point cannot be used as reference for scaling')
            return
        v = sender.corrSB.value() / (self.yp[index])
        for i in range(index + 1, self.xp.size):
            self._controllers[i].corrSB.setValue(v * self.yp[i])

    def changeCPointSelection(self, newpos):
        index = self._getInsertionIndex(newpos)
        old_index = self._getInsertionIndex(self.markerPos)
        self.markerPos = self.xp[index]
        self.marker1.setValue(self.xp[index], self.yp[
                              index] + self.corrp[index])
        self.marker2.setValue(self.xp[index], self.corrp[index])
        self.plot1.replot()
        self.plot2.replot()
        self._controllers[old_index].corrSB.setStyleSheet('')
        self._controllers[index].corrSB.setStyleSheet('background:lightgreen')
        self._selectedController = self._controllers[index]

    def onCorrSBChanged(self, value=None):
        '''recalculates the position and value of the control points (self.xp and self.corrp)
        as well as the correction curve (self.corr)'''
        ctrl = self.sender().ctrlObj
        self.corrp[self._getInsertionIndex(ctrl._x)] = value
        # recalculate the correction curve
        self.corr = numpy.interp(self.x, self.xp, self.corrp)
        self.updatePlots()

    def setMaster(self, x, y, keepCP=False, keepCorr=False):
        # make sure that x,y are numpy arrays and that the values are sorted
        # for x
        x, y = numpy.array(x), numpy.array(y)
        if x.shape != y.shape or x.size == 0 or y.size == 0:
            raise ValueError('The master curve is not valid')
        sortedindexes = numpy.argsort(x)
        self.x, self.y = x[sortedindexes], y[sortedindexes]
        self.plot1.getCurve('Master').setData(self.x, self.y)
        xp = None
        corrp = None
        if self.x[0] == self.xp[0] and self.x[-1] == self.x[-1]:
            if keepCP:
                xp = self.xp
            if keepCorr:
                corrp = self.corrp
        self.setCorrection(xp, corrp)
        self._addCPointsDialog.singleCPointXSB.setRange(self.x[0], self.x[-1])

    def getMaster(self):
        '''returns x,m where x and m are numpy arrays representing the
        abcissas and ordinates for the master, respectively'''
        return self.x.copy(), self.y.copy()

    def resetMaster(self):
        x = numpy.arange(256, dtype='double')
        y = numpy.zeros(256, dtype='double')
        self.setMaster(x, y)

    def getCorrected(self):
        '''returns x,c where x and c are numpy arrays representing the
        abcissas and ordinates for the corrected curve, respectively'''
        return self.x.copy(), self.y + self.corr

    def getCorrection(self):
        '''returns xp,cp where xp and cp are numpy arrays representing the
        abcissas and ordinates for the correction points, respectively'''
        return self.xp.copy(), self.corrp.copy()

    def setCorrection(self, xp=None, corrp=None):
        '''sets control points at the points specified by xp and with the
        values specified by corrp. Example::

            setCorrection([1,2,8,9], [0,0,0,0])

        would set 4 control points with initial value 0 at x=1, 2, 8 and 9s
        '''
        for c in self._controllers:
            c.setParent(None)  # destroy previous controllers
            c.deleteLater()
        self._controllers = []
        if xp is None:
            xp = numpy.array((self.x[0], self.x[-1]))
            corrp = numpy.zeros(2)
        if corrp is None:
            corrp = numpy.zeros(xp.size)
        # make sure that the extremes are there
        if xp[0] > self.x[0]:
            xp = numpy.concatenate(((self.x[0],), xp))
            corrp = numpy.concatenate(((self.corrp[0],), corrp))
        if xp[-1] < self.x[-1]:
            xp = numpy.concatenate((xp, (self.x[-1],)))
            corrp = numpy.concatenate((corrp, (self.corrp[-1],)))

        # now create everything
        # make sure there are no repetitions and that it is sorted
        self.xp = numpy.unique(xp)
        # in case of repeated xp, take only one corrp
        self.corrp = numpy.interp(self.xp, xp, corrp)
        self.yp = numpy.interp(self.xp, self.x, self.y)
        for i, (x, c) in enumerate(zip(xp, corrp)):
            ctrl = ControllerBox(parent=None, x=xp[i], y=self.yp[i])
            self.ctrlLayout.insertWidget(i, ctrl)
            self._controllers.insert(i, ctrl)
            self.connectToController(ctrl)
        # recalculate the correction curve
        self.corr = numpy.interp(self.x, self.xp, self.corrp)
        self.updatePlots()
        self.changeCPointSelection(self.xp[0])

    def resetCorrection(self):
        self.setCorrection()
        #self.xp = numpy.linspace(self.x[0],self.x[-1], self.cpoints)
        #self.corrp = numpy.zeros(self.cpoints)
        # self._populateControllers()


if __name__ == "__main__":
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    form = ArrayEditor()
    #x = numpy.arange(100)-20
    #y = -(x-50)**2+50**2
    x = numpy.linspace(0.1, 0.9, 100)
    y = (x) ** 2 - 5 * x
    form.setMaster(x, y)
    # form.setCorrection([1,30,70,90,100],[0,44,88,22,-100])
    form.show()
    # sys.exit(app.exec_())
    status = app.exec_()
    # x,y=form.getCorrected()
    # print "CORRECTED:",x,y
    sys.exit(status)
