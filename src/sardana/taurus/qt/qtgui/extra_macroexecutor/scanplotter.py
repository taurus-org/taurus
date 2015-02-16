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

"""
scanplotter.py: 
    module containing the widget: scanplotter,
    to be used in the Taurus app "scanner.py"
"""

import taurus.core

from taurus.external.qt import QtGui, Qwt5
#from taurus.qt.Qt import *

from taurus.core.util import dictFromSequence
from taurus.core.util.containers import CaselessDict
from taurus.core.util import eventfilters
from taurus.qt.qtgui.plot import TaurusTrend


class ScanPlotter(TaurusTrend):

    def __init__(self, parent=None, designMode=False):

        TaurusTrend.__init__(self, parent, designMode)
        self.setUseParentModel(False)
        self._plotables = CaselessDict()
        self._movingMotors = []
        self._macroNames = []
        self._doorName = None

        self.setMinimumSize(300, 200)
        self.setXIsTime(True)
        self.setAxisScale(Qwt5.QwtPlot.xBottom, 0, 60)
        self.setXDynScale(True)

    def onSequenceCleared(self):
        self._movingMotors = []
        self._macroNames = []
        self.populatePlotables()

    def onMacrosAdded(self, macroNames, motors):
        for macro in macroNames:
            self._macroNames.append(macro)
        self._movingMotors += motors
        self.populatePlotables()

    def onMacroEdited(self, oldMotors, newMotors):
        for motor in oldMotors:
            self._movingMotors.remove(motor)
        self._movingMotors += newMotors
        self.populatePlotables()

    def onMacrosDeleted(self, macroNames, motors):
        for macro in macroNames:
            self._macroNames.remove(macro)
        for motor in motors:
            self._movingMotors.remove(motor)
        self.populatePlotables()

    def onMacroStarted(self, macroName, motors):
        self._macroNames = [macroName]
        self._movingMotors = motors
        self.populatePlotables()

    def onMotorChanged(self, oldMotor, newMotor):
        if oldMotor in self._movingMotors:
            self._movingMotors.remove(oldMotor)
        self._movingMotors.append(newMotor)
        self.populatePlotables()

    def onMacroChanged(self, macroNode):
        if macroNode is None:
            self._macroNames = []
            self._movingMotors = []
#            return
        else:
            self._macroNames = [macroNode.name()]
            self._movingMotors = macroNode.allMotors()
        self.populatePlotables()

    def onDoorChanged(self, doorName):
        self._doorName = doorName
        self._movingMotors = []
        self.populatePlotables()

    def getPlotables(self, macronames=None, doorname=None, movingmotors=None):
        """returns a list of plotables for this scan given macro (channels and moving motors)"""
        plotables = []
        if macronames is None: macronames = list(set(self._macroNames))
        if doorname is None: doorname = self._doorName
        if movingmotors is None: movingmotors = list(set(self._movingMotors))
        if doorname is None or not len(macronames):
            return plotables
        door = taurus.Device(doorname)


        for macroname in macronames:
            env = dictFromSequence(door.getMacroEnv([macroname]))
            mntgrp_name = env.get("ActiveMntGrp")
            if mntgrp_name is None:
                continue
            mntgrp = taurus.Device(mntgrp_name)
            channels = mntgrp.getAttribute('Channels').read()
            channelsList = channels.value
            timer_name = mntgrp.getAttribute('Timer').read().value.lower()
            plotables += [('%s/%s_value' % (mntgrp_name, ch)).lower() for ch in channelsList if ch.lower() != timer_name]

        for m in movingmotors:
            if not (m is None or m == "" or m == "None"):
                plotables += ["%s/position" % m]
        return plotables

    def populatePlotables(self, plotables=None):
        ##@TODO: The name in the legend should be more descriptive: i.e. "dev/attr" instead of "attr" (this probably has to be changed for taurusplot in general  )
        if plotables is None: plotables = self.getPlotables()
        self.setModel(plotables)
        self.curves_lock.acquire()
        try:
            for name in self.getTrendSetNames():
                ts = self.getTrendSet(name)
                ts.fireEvent(None, taurus.core.taurusbasetypes.TaurusEventType.Change, None)
        finally:
            self.curves_lock.release()
        self.setEventFilters([eventfilters.ONLY_VALID], plotables)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = ScanPlotter()
    if len(sys.argv) < 4: raise ValueError('Syntax: ' + sys.argv[0] + ' macroname doorname plotable [anotherplotable...]')
    form._macroName = sys.argv[1]
    form._doorName = sys.argv[2]
    form.populatePlotables(sys.argv[3:])
    form.show()
    sys.exit(app.exec_())
