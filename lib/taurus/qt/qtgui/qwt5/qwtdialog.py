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
qwtdialog.py: Dialogs for Taurusplot
"""
from __future__ import print_function
from __future__ import absolute_import

import time
from functools import partial

from taurus.external.qt import Qt, Qwt5
from taurus.qt.qtgui.util.ui import UILoadable


__all__ = ["TaurusPlotConfigDialog"]


# class TaurusPlotConfigCapable:
#    """This class is aimed to act as an interface for class TaurusPlot. Every class that uses
#    TaurusPlotConfigDialog class (as TaurusPlot does) should inherit TaurusPlotConfigCapable class
#    and overwrite the methods defined below in order to avoid firing exceptions"""
#    def __init__(self, parent = None):
#        pass
#
#    def showConfigDialog(self):
#        raise NotImplementedError, "TaurusPlotConfigCapable: method showConfigDialog() not implemented in child class"
#
#    def setAxisScale(self,axis,min,max):
#        raise NotImplementedError, "TaurusPlotConfigCapable: method setAxisScale() not implemented in child class"
#
#    def setAxisAutoScale(self, axis=None):
#        raise NotImplementedError, "TaurusPlotConfigCapable: method setAxisAutoScale() not implemented in child class"
#
#    def setAxisScaleType(self, axis=None, scale=None):
#        raise NotImplementedError, "TaurusPlotConfigCapable: method setAxisScaleType() not implemented in child class"


@UILoadable(with_ui='ui')
class TaurusPlotConfigDialog(Qt.QDialog):
    """This class is used to build and manage the plot configuration dialog. It
    has been designed using the qt designer application, and then loaded to this
    widget. Hence, if you need to modify the dialog, you can use the
    TaurusPlotConfigDialog.ui file (under ui directory) to make it easier."""

    def __init__(self, parent=None, flags=Qt.Qt.WindowFlags()):
        self.parent = parent
        # if parent==None or not isinstance(parent, TaurusPlotConfigCapable):
        #    raise NotImplementedError, "Parent object doesn't implement TaurusPlotConfigCapable class"
        # call qt designer generated functions to initialize GUI
        Qt.QDialog.__init__(self, parent, flags)
        self.loadUi()

        # insert the CurvesAppearanceWidget
        #(@TODO:must be changed to be done directly in the ui, but I couldn't make the widget available to TaurusDesigner)
        from .curvesAppearanceChooserDlg import CurvesAppearanceChooser
        layout = Qt.QVBoxLayout()
        self.curvesAppearanceChooser = CurvesAppearanceChooser(None)
        layout.addWidget(self.curvesAppearanceChooser)
        self.ui.curveAppearanceGB.setLayout(layout)

        # set the values for the CurvesAppearanceChooser
        self.curvesAppearanceChooser.setCurves(
            self.parent.getCurveAppearancePropertiesDict())

        # insert valid values into mode combobox (linear or logarihtmic) and
        # set selected one in combobox
        self.ui.xModeComboBox.insertItem(0, "Linear")
        self.ui.xModeComboBox.insertItem(1, "Logarithmic")
        self.ui.y1ModeComboBox.insertItem(0, "Linear")
        self.ui.y1ModeComboBox.insertItem(1, "Logarithmic")
        self.ui.y2ModeComboBox.insertItem(0, "Linear")
        self.ui.y2ModeComboBox.insertItem(1, "Logarithmic")

        # insert valid values into peaks combobox (max, min or both) and set
        # selected one in combobox
        self.ui.peaksComboBox.insertItem(0, "Both")
        self.ui.peaksComboBox.insertItem(1, "Max")
        self.ui.peaksComboBox.insertItem(2, "Min")
        self.ui.peaksComboBox.insertItem(3, "None")

        # Init X axis group
        self.ui.xRangeCB.setVisible(False)
        self.ui.xLabelRange.setVisible(False)
        if self.parent.getXIsTime():
            # adapt the X axis group for time-based measurements
            self.ui.xRangeCB.addItems(["",
                                       "1 m",
                                       "1 h",
                                       "1 d",
                                       "1 w",
                                       "30 d",
                                       "1 y"])
            self.ui.xGroupBox.setTitle("Time")
            self.ui.xLabelMin.setText("Start")
            self.ui.xLabelMax.setText("End")
            timetooltip = """It accepts both absolute data-times (e.g. "25/10/1917 21:45:01") \n"""\
                """or relative ones with format <+|-><number><s|m|h|d|w|y> (e.g. "-12h").\n"""\
                """The keyword "now" is also accepted."""
            self.ui.xEditMin.setToolTip(timetooltip)
            self.ui.xEditMax.setToolTip(timetooltip)
        else:
            # The default settings are ok for non-time plots
            self.ui.xEditMin.setValidator(Qt.QDoubleValidator(self))
            self.ui.xEditMax.setValidator(Qt.QDoubleValidator(self))
            self.ui.xRangeCB.setValidator(Qt.QDoubleValidator(self))
            self.ui.xRangeCB.addItems(["",
                                       "10",
                                       "100",
                                       "1000",
                                       "10000",
                                       "100000",
                                       "1000000"])

        self.ui.xDynScaleCheckBox.setChecked(self.parent.getXDynScale())
        auto = self.parent.axisAutoScale(Qwt5.QwtPlot.xBottom)
        self.ui.xAutoGroupBox.setChecked(not auto)

        # this call already initialises the edit boxes of the X axis
        self.setXDynScale(self.parent.getXDynScale())
        self.ui.xDynScaleCheckBox.setVisible(
            self.parent.isXDynScaleSupported())

        # Init Y axes groups
        self._populateYAxisScales()
        self.ui.y1AutoGroupBox.setChecked(
            not self.parent.axisAutoScale(Qwt5.QwtPlot.yLeft))
        self.ui.y2AutoGroupBox.setChecked(
            not self.parent.axisAutoScale(Qwt5.QwtPlot.yRight))

        # set validators for Y min/max edits
        self.ui.y1EditMin.setValidator(Qt.QDoubleValidator(self))
        self.ui.y1EditMax.setValidator(Qt.QDoubleValidator(self))
        self.ui.y2EditMin.setValidator(Qt.QDoubleValidator(self))
        self.ui.y2EditMax.setValidator(Qt.QDoubleValidator(self))

        # populate initial axis mode (linear or logarithmic) values from plot. Warning!: we're using
        # qwt QwtPlot.axis enum type to relate our GUI combo name and qwt axis
        # name (enum type).
        axes = [self.ui.y1ModeComboBox,
                self.ui.y2ModeComboBox, self.ui.xModeComboBox]
        for axis in range(len(axes)):
            scaleType = self.parent.getAxisTransformationType(axis)
            if scaleType == Qwt5.QwtScaleTransformation.Linear:
                axes[axis].setCurrentIndex(0)
            elif scaleType == Qwt5.QwtScaleTransformation.Log10:
                axes[axis].setCurrentIndex(1)
            else:
                raise TypeError("TaurusPlotConfigDialog::__init__(): unexpected axis scale type (linear or logarihtmic expected)")
        self.ui.xModeComboBox.setEnabled(not self.parent.getXIsTime())

        # determine which axes are visible
        if not self.parent.axisEnabled(Qwt5.QwtPlot.xBottom):
            self.ui.xGroupBox.setVisible(False)

        # populate initial peaks from parent
        if self.parent._showMaxPeaks and self.parent._showMinPeaks:
            self.ui.peaksComboBox.setCurrentIndex(0)
        elif self.parent._showMaxPeaks:
            self.ui.peaksComboBox.setCurrentIndex(1)
        elif self.parent._showMinPeaks:
            self.ui.peaksComboBox.setCurrentIndex(2)
        else:
            self.ui.peaksComboBox.setCurrentIndex(3)

        # put focus on Apply button by default (otherwise, on some desktop
        # environments, the "close" button would be focused by default, 
        # causing the dialog to close when using "ENTER" while editing values
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Close).setAutoDefault(False)
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Close).setDefault(False)
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Apply).setAutoDefault(True)
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Apply).setDefault(True)

        # connect signals
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Close).clicked.connect(self.hide)
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Apply).clicked.connect(self.apply)
        self.ui.xAutoGroupBox.toggled.connect(self.toggledAutoScale)
        self.ui.y1AutoGroupBox.toggled.connect(self.toggledAutoScale)
        self.ui.y2AutoGroupBox.toggled.connect(self.toggledAutoScale)
#        self.connect(self.ui.xEditMin,  Qt.SIGNAL("returnPressed()"),self.apply)
#        self.connect(self.ui.xEditMax,  Qt.SIGNAL("returnPressed()"),self.apply)
#        self.connect(self.ui.y1EditMin, Qt.SIGNAL("returnPressed()"),self.apply)
#        self.connect(self.ui.y1EditMax, Qt.SIGNAL("returnPressed()"),self.apply)
#        self.connect(self.ui.y2EditMin, Qt.SIGNAL("returnPressed()"),self.apply)
#        self.connect(self.ui.y2EditMax, Qt.SIGNAL("returnPressed()"),self.apply)
        self.ui.xModeComboBox.currentIndexChanged.connect(self.modeComboChanged)
        self.ui.xDynScaleCheckBox.toggled.connect(self.setXDynScale)
        #self.connect(self.ui.xRangeCB, Qt.SIGNAL("currentIndexChanged(const QString&)"),self.apply)
        self.ui.y1ModeComboBox.currentIndexChanged.connect(self.modeComboChanged)
        self.ui.y2ModeComboBox.currentIndexChanged.connect(self.modeComboChanged)
        self.ui.peaksComboBox.currentIndexChanged.connect(self.peaksComboChanged)
        # self.connect(self.curvesAppearanceChooser,
        # Qt.SIGNAL("controlChanged"),self.apply) #"autoapply" mode for *all*
        # the curve appearance controls
        self.curvesAppearanceChooser.assignToY1BT.clicked.connect(
            partial(self.setCurvesYAxis, curvesNamesList=None, axis=None))
        self.curvesAppearanceChooser.assignToY2BT.clicked.connect(
            partial(self.setCurvesYAxis, curvesNamesList=None, axis=None))
        self.curvesAppearanceChooser.bckgndBT.clicked.connect(self.changeBackgroundColor)
        self.curvesAppearanceChooser.changeTitlesBT.clicked.connect(self.onChangeTitles)
        self.curvesAppearanceChooser.CurveTitleEdited.connect(self.onCurveTitleEdited)

        # finally adjust size
        self.adjustSize()

    def _populateXAxisScales(self):
        xMin = self.parent.axisScaleDiv(Qwt5.QwtPlot.xBottom).lowerBound()
        xMax = self.parent.axisScaleDiv(Qwt5.QwtPlot.xBottom).upperBound()
        if self.parent.getXIsTime():
            self.ui.xEditMin.setText(time.strftime(
                '%Y/%m/%d %H:%M:%S', time.localtime(int(xMin))))
            self.ui.xEditMax.setText(time.strftime(
                '%Y/%m/%d %H:%M:%S', time.localtime(int(xMax))))
        else:
            self.ui.xEditMin.setText(str(xMin))
            self.ui.xEditMax.setText(str(xMax))

    def _populateYAxisScales(self, axis=None):
        if axis is None or axis == Qwt5.QwtPlot.yLeft:
            self.ui.y1EditMin.setText(
                str(self.parent.axisScaleDiv(Qwt5.QwtPlot.yLeft).lowerBound()))
            self.ui.y1EditMax.setText(
                str(self.parent.axisScaleDiv(Qwt5.QwtPlot.yLeft).upperBound()))
        if axis is None or axis == Qwt5.QwtPlot.yRight:
            self.ui.y2EditMin.setText(
                str(self.parent.axisScaleDiv(Qwt5.QwtPlot.yRight).lowerBound()))
            self.ui.y2EditMax.setText(
                str(self.parent.axisScaleDiv(Qwt5.QwtPlot.yRight).upperBound()))

    def deltatime2str(self, dt, fuzzy=False):
        '''converts a time diff in secs to a string.
        If fuzzy=True it returns an approx time diff in s, min, hours or days'''
        dt = float(dt)
        if not fuzzy:
            return "%g s" % dt
        if dt < 2:
            return "%3.3g s" % dt
        elif dt < 120:
            return "%g s" % round(dt, 0)
        elif dt < 7200:
            return "%g m" % round(dt / 60, 0)
        elif dt < 172800:
            return "%g h" % round(dt / 3600, 0)
        else:
            return "%g d" % round(dt / 86400, 0)

    def str2deltatime(self, strtime):
        '''Translates a time string to seconds
        examples of valid relative times are: "now", "NOW", "Now", "-1d", "3w", "- 3.6e3 s",...
        examples of non-valid relative times:, "now + 2h", "-5", "3H" (unit names are case-sensitive)
        '''
        strtime = str(strtime).strip()
        timeunits = {'s': 1, 'm': 60, 'h': 3600, 'd': 3600 *
                     24, 'w': 3600 * 24 * 7, 'y': 3600 * 24 * 365}
        if strtime.lower() == "now":
            return time.time()
        if strtime[-1] in timeunits:
            try:
                return float(strtime[:-1]) * timeunits[strtime[-1]]
            except Exception as e:
                print('[str2deltatime] No format could be applied to "%s"' % strtime)
                return None
        else:
            print('[str2deltatime] Non-supported unit "%s"' % strtime[-1])
            return None

    def strtime2epoch(self, strtime):
        '''
        Translates a str into an epoch value. It accepts "absolute" time notation as well as
        "relative to current time notation" (by expliciting a "+" or "-" prefix)
        (see str2deltatime for relative time notation).

        examples of valid absolute times: "2008-3-25 14:21:59", "25/03/08 14:21", "03-25-2008",...

        It returns None if strtime couldn't be interpreted
        '''
        import time
        t = None
        strtime = str(strtime).strip()

        # try with relative time keywords
        if strtime[0] in ['+', '-']:
            reltime = self.str2deltatime(strtime)
            if reltime is not None:
                return time.time() + reltime

        if strtime.lower() == "now":
            return time.time()

        # try with absolute time
        hour_fts = ['%H:%M:%S', '%H:%M', '']  # ,"%M'",'%S"'
        date_fts = ['%Y-%m-%d', '%y-%m-%d', '%Y/%m/%d', '%y/%m/%d',
                    '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y']

        tfs = []
        for d in date_fts:
            for h in hour_fts:
                if h:
                    tfs.append('%s %s' % (d, h))
                else:
                    tfs.append(d)

        for tf in tfs:
            try:
                # print 'trying ',tf
                t = time.strptime(strtime, tf)
                if t[0] < 1970:
                    lt = time.localtime()
                    #    (2008,  9,    23,  15,  44,   24,    1,   267, 1)
                    t = (lt[0], lt[1], lt[2], t[3], t[
                         4], lt[5], lt[6], lt[7], lt[8])
                    break
            except Exception as e:
                pass
        if t:
            return time.mktime(t)
        else:
            print('No format could be applied to "%s"' % strtime)
            return None

    def validate(self):
        '''validates the inputs in the dialog.
        If validation is ok, it returns a tuple containing min/max values for each axis (None if they are autoscaled)
        If validation failed, it returns False.

        .. note::
            the values of the max/min boxes are already validated thanks to their attached QDoubleValidators
            (except for xMin/xMax in time Mode, but this case is handled by strtime2epoch)
        '''
        xMin = xMax = y1Min = y1Max = y2Min = y2Max = None

        # Validating X axis values
        xMin = self.parent.axisScaleDiv(Qwt5.QwtPlot.xBottom).lowerBound()
        xMax = self.parent.axisScaleDiv(Qwt5.QwtPlot.xBottom).upperBound()
        if self.ui.xDynScaleCheckBox.isChecked():
            if self.parent.getXIsTime():
                rg = abs(self.str2deltatime(
                    str(self.ui.xRangeCB.currentText())))
                ok1 = (rg is not None)
            else:
                try:
                    rg, ok1 = float(self.ui.xRangeCB.currentText()), True
                except:
                    rg, ok1 = 0.0, False
            xMin = xMax - rg
            if not ok1 or (xMin >= xMax):
                Qt.QMessageBox.warning(
                    self, "Invalid parameters for X axis range")
                return False
        elif self.ui.xAutoGroupBox.isChecked():
            if self.parent.getXIsTime():  # time mode
                xMin = self.strtime2epoch(self.ui.xEditMin.text())
                xMax = self.strtime2epoch(self.ui.xEditMax.text())
                ok1 = (xMin is not None)
                ok2 = (xMax is not None)
            else:  # XY mode
                try:
                    xMin, ok1 = float(self.ui.xEditMin.text()), True
                except:
                    xMin, ok1 = 0.0, False
                try:
                    xMax, ok2 = float(self.ui.xEditMax.text()), True
                except:
                    xMax, ok2 = 0.0, False
            if not (ok1 and ok2) or (xMin >= xMax):
                Qt.QMessageBox.warning(self, "Invalid parameters for X axis",
                                       "Min value must be strictly less than max value")
                return False

        # Validating Y1 axis values
        if self.ui.y1AutoGroupBox.isChecked():
            try:
                y1Min, ok1 = float(self.ui.y1EditMin.text()), True
            except:
                y1Min, ok1 = 0.0, False
            try:
                y1Max, ok2 = float(self.ui.y1EditMax.text()), True
            except:
                y1Max, ok2 = 0.0, False
            if not(ok1 and ok2) or (y1Min >= y1Max):
                Qt.QMessageBox.warning(self, "Invalid parameters for Y1 axis",
                                       "Min value must be strictly less than max value")
                return False

        # Validating Y2 axis values
        if self.ui.y2AutoGroupBox.isChecked():
            try:
                y2Min, ok1 = float(self.ui.y2EditMin.text()), True
            except:
                y2Min, ok1 = 0.0, False
            try:
                y2Max, ok2 = float(self.ui.y2EditMax.text()), True
            except:
                y2Max, ok2 = 0.0, False
            if not (ok1 and ok2) or (y2Min >= y2Max):
                Qt.QMessageBox.warning(self, "Invalid parameters for Y2 axis",
                                       "Min value must be strictly less than max value")
                return False

        # if we reached this point, the input is valid
        return (xMin, xMax, y1Min, y1Max, y2Min, y2Max)

    def apply(self):
        """This will apply the values set in the dialog. Note that some of them
        are not necessary to be set, since they're already are set when changing the item selected"""

        # Apply the changes from the curves Appearance widget (they are already
        # validated).
        prop, names = self.curvesAppearanceChooser.onApply()
        self.parent.onCurveAppearanceChanged(prop, names)

        # validate the rest of the inputs
        v = self.validate()
        if not v:
            return
        xMin, xMax, y1Min, y1Max, y2Min, y2Max = v

        self.parent.setAxisScale(Qwt5.QwtPlot.xBottom, xMin, xMax)
        self.parent.setAxisScale(Qwt5.QwtPlot.yLeft, y1Min, y1Max)
        self.parent.setAxisScale(Qwt5.QwtPlot.yRight, y2Min, y2Max)

        self.parent._xMax, self.parent._xMin = xMax, xMin

    def toggledAutoScale(self, toggled):
        """This will catch the group boxes check/uncheck event, and will enable autoscale in case
        the event has been unchecking 'disable autoscale'"""
        # get and check who fired the signal
        groupBox = self.sender()
        if groupBox is None or not isinstance(groupBox, Qt.QGroupBox):
            self.error(
                "TaurusPlotConfig::toggledAutoScale(): event is not recognized")
            return
        # set the axis autoscale in the corresponding axis
        if groupBox.objectName() == "xAutoGroupBox" and not toggled:
            self.parent.setAxisAutoScale(Qwt5.QwtPlot.xBottom)
        elif groupBox.objectName() == "y1AutoGroupBox" and not toggled:
            self.parent.setAxisAutoScale(Qwt5.QwtPlot.yLeft)
        elif groupBox.objectName() == "y2AutoGroupBox" and not toggled:
            self.parent.setAxisAutoScale(Qwt5.QwtPlot.yRight)

    def modeComboChanged(self, itemSelected):
        """This will catch the combo box selection change and will set the corresponding axis scale to
        the value passed as parameter"""
        # get and check who fired the signal
        comboBox = self.sender()
        if comboBox is None or not isinstance(comboBox, Qt.QComboBox):
            self.error(
                "TaurusPlotConfig::modeComboChanged(): event is not recognized")
            return
        else:
                # set the scale for the corresponding axis
            if comboBox.objectName() == "xModeComboBox":
                if not self.parent.getXIsTime():
                    self.parent.setAxisScaleType(
                        Qwt5.QwtPlot.xBottom, itemSelected)
            elif comboBox.objectName() == "y1ModeComboBox":
                self.parent.setAxisScaleType(Qwt5.QwtPlot.yLeft, itemSelected)
            elif comboBox.objectName() == "y2ModeComboBox":
                self.parent.setAxisScaleType(Qwt5.QwtPlot.yRight, itemSelected)
            else:
                self.error(
                    "TaurusPlotConfig::modeComboChanged() invalid axis: " + comboBox.objectName())

    def setXDynScale(self, checked):
        if checked:
            if self.parent.getXIsTime():
                rg = self.deltatime2str(
                    self.parent.getXAxisRange(), fuzzy=True)
            else:
                rg = "%g" % self.parent.getXAxisRange()
            self.ui.xRangeCB.setEditText(rg)
            # disable autoscale for the X axis
            self.ui.xAutoGroupBox.setChecked(True)
        else:
            self._populateXAxisScales()
        self.parent.setXDynScale(checked)

    def peaksComboChanged(self, itemSelected):
        """This will catch the combo box selection change and will set the corresponding axis to
        show peaks"""
        if itemSelected == 0:
            maxPeak = minPeak = True
        elif itemSelected == 1:
            maxPeak = True
            minPeak = False
        elif itemSelected == 2:
            maxPeak = False
            minPeak = True
        else:
            maxPeak = minPeak = False
        self.parent.showMaxPeaks(maxPeak)
        self.parent.showMinPeaks(minPeak)

    def showCalendar(self, target):
        return
        self.qcalendar = Qt.QCalendarWidget()
        self.qcalendar.show()

    def setCurvesYAxis(self, curvesNamesList=None, axis=None):
        """ calls the parent's setCurvesYAxis method but it automatically determines the parameters if not given"""
        if curvesNamesList is None:
            curvesNamesList = self.curvesAppearanceChooser.getSelectedCurveNames()
        if axis is None:
            sender = self.sender()
            if sender is self.curvesAppearanceChooser.assignToY1BT:
                axis = Qwt5.QwtPlot.yLeft
            elif sender is self.curvesAppearanceChooser.assignToY2BT:
                axis = Qwt5.QwtPlot.yRight
            else:
                raise ValueError("Cannot determine axis from %s" % sender)
        # call the parent's setCurvesYAxis()
        self.parent.setCurvesYAxis(curvesNamesList, axis)
        # update the axis scale edits
        self._populateYAxisScales(axis)

    def changeBackgroundColor(self):
        """Launches a dialog for choosing the parent's canvas background color"""
        plot = self.parent
        color = Qt.QColorDialog.getColor(plot.canvasBackground(), self)
        if Qt.QColor.isValid(color):
            plot.setCanvasBackground(color)
            plot.replot()

    def onChangeTitles(self):
        '''Calls The parent's changeCurvesTitlesDialog method, with the selected
        curves list as the parameter
        '''
        curveNamesList = self.curvesAppearanceChooser.getSelectedCurveNames()
        newTitlesDict = self.parent.changeCurvesTitlesDialog(
            curveNamesList=curveNamesList)
        self.curvesAppearanceChooser.updateTitles(newTitlesDict)

    def onCurveTitleEdited(self, name, newTitle):
        '''slot used when a curve title is edited

        :param name: (str) curve name
        :param name: (str) new title
        '''
        newTitlesDict = self.parent.setCurvesTitle(newTitle, [name])
        self.curvesAppearanceChooser.updateTitles(newTitlesDict)
