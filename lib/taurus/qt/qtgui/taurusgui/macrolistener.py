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
###########################################################################

"""
This module provides objects to manage macro-related tasks. Its primary use is
to be used within a TaurusGui for managing panels for:
- setting preferences in the sardana control system for data I/O
- displaying results of macro executions, including creating/removing panels for
  plotting results of scans
- editing macros

.. note:: This module will be moved to sardana.taurus at some point.
"""

 # TODO: move to sardana.taurus

__all__ = ['MacroBroker', 'DynamicPlotManager']
__docformat__ = 'restructuredtext'

import datetime

from taurus.core.util.containers import CaselessList
from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
from sardana.taurus.core.tango.sardana import PlotType
from sardana.taurus.core.tango.sardana.pool import getChannelConfigs


class ChannelFilter(object):

    def __init__(self, chlist):
        self.chlist = tuple(chlist)

    def __call__(self, x):
        return x in self.chlist


class DynamicPlotManager(Qt.QObject, TaurusBaseComponent):
    '''This is a manager of plots related to the execution of macros.
    It dynamically creates/removes plots according to the configuration made by
    an ExperimentConfiguration widget.

    Currently it supports only 1D scan trends (2D scans are only half-baked)

    To use it simply instantiate it and pass it a door name as a model. You may
    want to call :meth:`onExpConfChanged` to update the configuration being
    used.
    '''

    newShortMessage = Qt.pyqtSignal(str)

    def __init__(self, parent=None):
        Qt.QObject.__init__(self, parent)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)

        self.__panels = {}

        self._trends1d = {}
        self._trends2d = {}

    def setModel(self, doorname):
        '''reimplemented from :meth:`TaurusBaseComponent`

        :param doorname: (str) device name corresponding to a Door device.
        '''
        TaurusBaseComponent.setModel(self, doorname)
        # self._onDoorChanged(doorname)
        if not doorname:
            return
        door = self.getModelObj()
        if not isinstance(door, Qt.QObject):
            msg = "Unexpected type (%s) for %s" % (repr(type(door)), doorname)
            Qt.QMessageBox.critical(
                self.parent(), 'Door connection error', msg)
            return

        self._checkJsonRecorder()

        # read the expconf
        expconf = door.getExperimentConfiguration()
        self.onExpConfChanged(expconf)

    def _checkJsonRecorder(self):
        '''Checks if JsonRecorder env var is set and offers to set it'''
        door = self.getModelObj()
        if 'JsonRecorder' not in door.getEnvironment():
            msg = ('JsonRecorder environment variable is not set, but it ' +
                   'is needed for displaying trend plots.\n' +
                   'Enable it globally for %s?') % door.fullname
            result = Qt.QMessageBox.question(self.parent(),
                                             'JsonRecorder not set', msg,
                                             Qt.QMessageBox.Yes | Qt.QMessageBox.No)
            if result == Qt.QMessageBox.Yes:
                door.putEnvironment('JsonRecorder', True)
                self.info('JsonRecorder Enabled for %s' % door.fullname)

    def onExpConfChanged(self, expconf):
        '''
        Slot to be called when experimental configuration changes. It should
        remove the temporary panels and create the new ones needed.

        :param expconf: (dict) An Experiment Description dictionary. See
                        :meth:`sardana.taurus.qt.qtcore.tango.sardana.
                        QDoor.getExperimentDescription`
                        for more details
        '''
        activeMntGrp = expconf['ActiveMntGrp']
        if activeMntGrp is None:
            return
        if activeMntGrp not in expconf['MntGrpConfigs']:
            self.warning(
                "ActiveMntGrp '%s' is not defined" %
                activeMntGrp)
            return
        mgconfig = expconf['MntGrpConfigs'][activeMntGrp]
        channels = dict(getChannelConfigs(mgconfig, sort=False))

        # classify by type of plot:
        trends1d = {}
        trends2d = {}
        plots1d = {}
        images = {}

        for chname, chdata in channels.items():
            ptype = chdata['plot_type']
            if ptype == PlotType.No:
                continue
            elif ptype == PlotType.Spectrum:
                axes = tuple(chdata['plot_axes'])
                # TODO: get default value from the channel.
                ndim = chdata.get('ndim', 0)
                if ndim == 0:  # this is a trend
                    if axes in trends1d:
                        trends1d[axes].append(chname)
                    else:
                        trends1d[axes] = CaselessList([chname])
                elif ndim == 1:  # a 1D plot (e.g. a spectrum)
                    pass  # TODO: implement
                else:
                    self.warning('Cannot create plot for %s', chname)

            elif ptype == PlotType.Image:
                axes = tuple(chdata['plot_axes'])
                # TODO: get default value from the channel.
                ndim = chdata.get('ndim', 1)
                if ndim == 0:  # a mesh-like plot?
                    pass  # TODO implement
                elif ndim == 1:  # a 2D trend
                    if axes in trends2d:
                        trends2d[axes].append(chname)
                    else:
                        trends2d[axes] = CaselessList([chname])
                elif ndim == 2:  # a 2D plot (e.g. an image)
                    pass  # TODO: implement
                else:
                    self.warning('Cannot create plot for %s', chname)

        new1d, removed1d = self._updateTemporaryTrends1D(trends1d)
        self.newShortMessage.emit("Changed panels (%i new, %i removed)" % (len(new1d),
                                                           len(removed1d)))
#        self._updateTemporaryTrends2D(trends2d)

    def _updateTemporaryTrends1D(self, trends1d):
        '''adds necessary trend1D panels and removes no longer needed ones

        :param trends1d: (dict) A dict whose keys are tuples of axes and
                         whose values are list of model names to plot

        :returns: (tuple) two lists new,rm:new contains the names of the new
                  panels and rm contains the names of the removed panels
        '''
        from taurus.qt.qtgui.plot import TaurusTrend
        newpanels = []
        for axes, plotables in trends1d.items():
            if not axes:
                continue
            if axes not in self._trends1d:
                w = TaurusTrend()
                w.setXIsTime(False)
                w.setScanDoor(self.getModelObj().fullname)
                # TODO: use a standard key for <idx> and <mov>
                w.setScansXDataKey(axes[0])
                pname = u'Trend1D - %s' % ":".join(axes)
                panel = self.createPanel(w, pname, registerconfig=False,
                                         permanent=False)
                try:  # if the panel is a dockwidget, raise it
                    panel.raise_()
                except:
                    pass
                self._trends1d[axes] = pname
                newpanels.append(pname)

            widget = self.getPanelWidget(self._trends1d[axes])
            flt = ChannelFilter(plotables)
            widget.onScanPlotablesFilterChanged(flt)

        # remove trends that are no longer configured
        removedpanels = []
        olditems = list(self._trends1d.items())
        for axes, name in olditems:
            if axes not in trends1d:
                removedpanels.append(name)
                self.removePanel(name)
                self._trends1d.pop(axes)

        return newpanels, removedpanels

    def _updateTemporaryTrends2D(self, trends2d):
        '''adds necessary trend2D panels and removes no longer needed ones

        :param trends2d: (dict) A dict whose keys are tuples of axes and
                         whose values are list of model names to plot

        :returns: (tuple) two lists new,rm:new contains the names of the new
                  panels and rm contains the names of the removed panels

        ..note:: Not fully implemented yet
        '''
        try:
            from taurus.qt.qtgui.extra_guiqwt.taurustrend2d import \
                TaurusTrend2DDialog
            from taurus.qt.qtgui.extra_guiqwt.image import TaurusTrend2DScanItem
        except:
            self.info('guiqwt extension cannot be loaded. ' +
                      '2D Trends will not be created')
            raise
            return

        for axes, plotables in trends2d.items():
            for chname in plotables:
                pname = u'Trend2D - %s' % chname
                if pname in self._trends2d:
                    self._trends2d[pname].widget().trendItem.clearTrend()
                else:
                    axis = axes[0]
                    w = TaurusTrend2DDialog(stackMode='event')
                    plot = w.get_plot()
                    t2d = TaurusTrend2DScanItem(chname, axis,
                                                self.getModelObj().fullname)
                    plot.add_item(t2d)
                    self.createPanel(w, pname, registerconfig=False,
                                     permanent=False)
                    self._trends2d[(axes, chname)] = pname

    def createPanel(self, widget, name, **kwargs):
        '''Creates a "panel" from a widget. In this basic implementation this
        means that the widgets is shown as a non-modal top window

        :param widget: (QWidget) widget to be used for the panel
        :param name: (str) name of the panel. Must be unique.

        Note: for backawards compatibility, this implementation accepts
        arbitrary keyword arguments which are just ignored
        '''
        widget.setWindowTitle(name)
        widget.show()
        self.__panels[name] = widget

    def getPanelWidget(self, name):
        '''Returns the widget associated to a panel name

        :param name: (str) name of the panel. KeyError is raised if not found

        :return: (QWidget)
        '''
        return self.__panels[name]

    def removePanel(self, name):
        '''stop managing the given panel

        :param name: (str) name of the panel'''
        widget = self.__panels.pop(name)
        if hasattr(widget, 'setModel'):
            widget.setModel(None)
        widget.setParent(None)
        widget.close()

    def removePanels(self, names=None):
        '''removes panels.

        :param names: (seq<str>) names of the panels to be removed. If None is
                      given (default), all the panels are removed.
        '''
        if names is None:
            names = self._trends1d.values() + self._trends2d.values()
            # TODO: do the same for other temporary panels
        for pname in names:
            self.removePanel(pname)


class MacroBroker(DynamicPlotManager):
    '''A manager of all macro-related panels of a TaurusGui.

    It creates, destroys and manages connections for the following objects:

        - Macro Configuration dialog
        - Experiment Configuration panel
        - Macro Executor panel
        - Sequencer panel
        - Macro description viewer
        - Door output, result and debug panels
        - Macro editor
        - Macro "panic" button (to abort macros)
        - Dynamic plots (see :class:`DynamicPlotManager`)
    '''

    def __init__(self, parent):
        '''Passing the parent object (the main window) is mandatory'''
        DynamicPlotManager.__init__(self, parent)

        self._createPermanentPanels()

        # connect the broker to shared data
        Qt.qApp.SDM.connectReader("doorName", self.setModel)
        Qt.qApp.SDM.connectReader("expConfChanged", self.onExpConfChanged)
        Qt.qApp.SDM.connectWriter("shortMessage", self, 'newShortMessage')

    def setModel(self, doorname):
        ''' Reimplemented from :class:`DynamicPlotManager`.'''
        # disconnect the previous door
        door = self.getModelObj()
        if door is not None:  # disconnect it from *all* shared data providing
            SDM = Qt.qApp.SDM
            try:
                SDM.disconnectWriter("macroStatus", door, "macroStatusUpdated")
            except:
                self.info("Could not disconnect macroStatusUpdated")
            try:
                SDM.disconnectWriter("doorOutputChanged", door, "outputUpdated")
            except:
                self.info("Could not disconnect outputUpdated")
            try:
                SDM.disconnectWriter("doorInfoChanged", door, "infoUpdated")
            except:
                self.info("Could not disconnect infoUpdated")
            try:
                SDM.disconnectWriter("doorWarningChanged", door,
                                     "warningUpdated")
            except:
                self.info("Could not disconnect warningUpdated")
            try:
                SDM.disconnectWriter("doorErrorChanged", door, "errorUpdated")
            except:
                self.info("Could not disconnect errorUpdated")
            try:
                SDM.disconnectWriter("doorDebugChanged", door, "debugUpdated")
            except:
                self.info("Could not disconnect debugUpdated")
            try:
                SDM.disconnectWriter("doorResultChanged", door, "resultUpdated")
            except:
                self.info("Could not disconnect resultUpdated")
            try:
                SDM.disconnectWriter("expConfChanged", door,
                                     "experimentConfigurationChanged")
            except:
                self.info("Could not disconnect experimentConfigurationChanged")
        # set the model
        DynamicPlotManager.setModel(self, doorname)

        # connect the new door
        door = self.getModelObj()
        if door is not None:
            SDM = Qt.qApp.SDM
            SDM.connectWriter("macroStatus", door, "macroStatusUpdated")
            SDM.connectWriter("doorOutputChanged", door, "outputUpdated")
            SDM.connectWriter("doorInfoChanged", door, "infoUpdated")
            SDM.connectWriter("doorWarningChanged", door, "warningUpdated")
            SDM.connectWriter("doorErrorChanged", door, "errorUpdated")
            SDM.connectWriter("doorDebugChanged", door, "debugUpdated")
            SDM.connectWriter("doorResultChanged", door, "resultUpdated")
            SDM.connectWriter("expConfChanged", door,
                              "experimentConfigurationChanged")

    def _createPermanentPanels(self):
        '''creates panels on the main window'''
        from sardana.taurus.qt.qtgui.extra_macroexecutor import \
            TaurusMacroExecutorWidget, TaurusSequencerWidget, \
            TaurusMacroConfigurationDialog, TaurusMacroDescriptionViewer, \
            DoorOutput, DoorDebug, DoorResult

        from sardana.taurus.qt.qtgui.extra_sardana import \
            ExpDescriptionEditor, SardanaEditor

        mainwindow = self.parent()

        # Create macroconfiguration dialog & action
        self.__macroConfigurationDialog = \
            TaurusMacroConfigurationDialog(mainwindow)
        self.macroConfigurationAction = mainwindow.taurusMenu.addAction(
            Qt.QIcon.fromTheme("preferences-system-session"),
            "Macro execution configuration...",
            self.__macroConfigurationDialog.show)

        SDM = Qt.qApp.SDM
        SDM.connectReader("macroserverName",
                          self.__macroConfigurationDialog.selectMacroServer)
        SDM.connectReader("doorName",
                          self.__macroConfigurationDialog.selectDoor)
        SDM.connectWriter("macroserverName", self.__macroConfigurationDialog,
                          'macroserverNameChanged')
        SDM.connectWriter("doorName", self.__macroConfigurationDialog,
                          'doorNameChanged')

        # Create ExpDescriptionEditor dialog
        self.__expDescriptionEditor = ExpDescriptionEditor(plotsButton=False)
        SDM.connectReader("doorName", self.__expDescriptionEditor.setModel)
        mainwindow.createPanel(self.__expDescriptionEditor,
                               'Experiment Config',
                               registerconfig=True,
                               icon=Qt.QIcon.fromTheme('preferences-system'),
                               permanent=True)
        ###############################
        # TODO: These lines can be removed once the door does emit
        # "experimentConfigurationChanged" signals
        SDM.connectWriter("expConfChanged", self.__expDescriptionEditor,
                          "experimentConfigurationChanged")
        ################################

        # put a Macro Executor
        self.__macroExecutor = TaurusMacroExecutorWidget()
        SDM.connectReader("macroserverName", self.__macroExecutor.setModel)
        SDM.connectReader("doorName", self.__macroExecutor.onDoorChanged)
        SDM.connectReader("macroStatus",
                          self.__macroExecutor.onMacroStatusUpdated)
        SDM.connectWriter("macroName", self.__macroExecutor,
                          "macroNameChanged")
        SDM.connectWriter("executionStarted", self.__macroExecutor,
                          "macroStarted")
        SDM.connectWriter("plotablesFilter", self.__macroExecutor,
                          "plotablesFilterChanged")
        SDM.connectWriter("shortMessage", self.__macroExecutor,
                          "shortMessageEmitted")
        mainwindow.createPanel(self.__macroExecutor, 'Macros',
                               registerconfig=True, permanent=True)

        # put a Sequencer
        self.__sequencer = TaurusSequencerWidget()
        SDM.connectReader("macroserverName", self.__sequencer.setModel)
        SDM.connectReader("doorName", self.__sequencer.onDoorChanged)
        SDM.connectReader("macroStatus", self.__sequencer.onMacroStatusUpdated)
        SDM.connectWriter("macroName", self.__sequencer.tree,
                          "macroNameChanged")
        SDM.connectWriter("macroName", self.__sequencer,
                          "macroNameChanged")
        SDM.connectWriter("executionStarted", self.__sequencer,
                          "macroStarted")
        SDM.connectWriter("plotablesFilter", self.__sequencer,
                          "plotablesFilterChanged")
        SDM.connectWriter("shortMessage", self.__sequencer,
                          "shortMessageEmitted")
        mainwindow.createPanel(self.__sequencer, 'Sequences',
                               registerconfig=True, permanent=True)

        # puts a macrodescriptionviewer
        self.__macroDescriptionViewer = TaurusMacroDescriptionViewer()
        SDM.connectReader("macroserverName",
                          self.__macroDescriptionViewer.setModel)
        SDM.connectReader("macroName",
                          self.__macroDescriptionViewer.onMacroNameChanged)
        mainwindow.createPanel(self.__macroDescriptionViewer,
                               'MacroDescription', registerconfig=True,
                               permanent=True)

        # puts a doorOutput
        self.__doorOutput = DoorOutput()
        SDM.connectReader("doorOutputChanged",
                          self.__doorOutput.onDoorOutputChanged)
        SDM.connectReader("doorInfoChanged",
                          self.__doorOutput.onDoorInfoChanged)
        SDM.connectReader("doorWarningChanged",
                          self.__doorOutput.onDoorWarningChanged)
        SDM.connectReader("doorErrorChanged",
                          self.__doorOutput.onDoorErrorChanged)
        mainwindow.createPanel(self.__doorOutput, 'DoorOutput',
                               registerconfig=False, permanent=True)

        # puts doorDebug
        self.__doorDebug = DoorDebug()
        SDM.connectReader("doorDebugChanged",
                          self.__doorDebug.onDoorDebugChanged)
        mainwindow.createPanel(self.__doorDebug, 'DoorDebug',
                               registerconfig=False, permanent=True)

        # puts doorResult
        self.__doorResult = DoorResult(mainwindow)
        SDM.connectReader("doorResultChanged",
                          self.__doorResult.onDoorResultChanged)
        mainwindow.createPanel(self.__doorResult, 'DoorResult',
                               registerconfig=False, permanent=True)

        # puts sardanaEditor
        # self.__sardanaEditor = SardanaEditor()
        # SDM.connectReader("macroserverName", self.__sardanaEditor.setModel)
        # mainwindow.createPanel(self.__sardanaEditor, 'SardanaEditor',
        #                        registerconfig=False, permanent=True)

        # add panic button for aborting the door
        text = "Panic Button: stops the pool (double-click for abort)"
        self.doorAbortAction = mainwindow.jorgsBar.addAction(
            Qt.QIcon("actions:process-stop.svg"),
            text, self.__onDoorAbort)

        # store beginning of times as a datetime
        self.__lastAbortTime = datetime.datetime(1, 1, 1)

        # store doubleclick interval as a timedelta
        td = datetime.timedelta(0, 0, 1000 * Qt.qApp.doubleClickInterval())
        self.__doubleclickInterval = td

    def __onDoorAbort(self):
        '''slot to be called when the abort action is triggered.
        It sends stop command to the pools (or abort if the action
        has been triggered twice in less than self.__doubleclickInterval

        .. note:: An abort command is always preceded by an stop command
        '''
        # decide whether to send stop or abort
        now = datetime.datetime.now()
        if now - self.__lastAbortTime < self.__doubleclickInterval:
            cmd = 'abort'
        else:
            cmd = 'stop'

        door = self.getModelObj()

        # abort the door
        door.command_inout('abort')
        # send stop/abort to all pools
        pools = door.macro_server.getElementsOfType('Pool')
        for pool in pools.values():
            self.info('Sending %s command to %s' % (cmd, pool.getFullName()))
            try:
                pool.getObj().command_inout(cmd)
            except:
                self.info('%s command failed on %s', cmd, pool.getFullName(),
                          exc_info=1)
        self.newShortMessage.emit("%s command sent to all pools" %
                  cmd)
        self.__lastAbortTime = now

    def createPanel(self, widget, name, **kwargs):
        ''' Reimplemented from :class:`DynamicPlotManager` to delegate panel
        management to the parent widget (a TaurusGui)'''
        mainwindow = self.parent()
        return mainwindow.createPanel(widget, name, **kwargs)

    def getPanelWidget(self, name):
        ''' Reimplemented from :class:`DynamicPlotManager` to delegate panel
        management to the parent widget (a TaurusGui)'''
        mainwindow = self.parent()
        return mainwindow.getPanel(name).widget()

    def removePanel(self, name):
        ''' Reimplemented from :class:`DynamicPlotManager` to delegate panel
        management to the parent widget (a TaurusGui)'''
        mainwindow = self.parent()
        mainwindow.removePanel(name)

    def removeTemporaryPanels(self, names=None):
        '''Remove temporary panels managed by this widget'''
        # for now, the only temporary panels are the plots
        DynamicPlotManager.removePanels(self, names=names)


if __name__ == "__main__":
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication()

    b = DynamicPlotManager(None)

    b.setModel('door/cp1/1')

    print '...'
    sys.exit(app.exec_())
