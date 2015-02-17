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
This module provides a button for executing macros
"""

__all__ = ['MacroButton']

import functools
import uuid

import PyTango

import taurus
from taurus.core import TaurusEventType, TaurusDevice
from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.button import TaurusCommandButton
from taurus.qt.qtgui.dialog import ProtectTaurusMessageBox
from taurus.core.util.colors import DEVICE_STATE_PALETTE
from taurus.qt.qtgui.util.ui import UILoadable


class DoorStateListener(Qt.QObject):
    '''A listener of Change and periodic events from a Door State attribute.
    It converts the received Tango events and emits a Qt signal
    '''

    __pyqtSignals__ = ["doorStateChanged"]

    def eventReceived(self, evt_src, evt_type, evt_value):
        if evt_type not in (TaurusEventType.Change, TaurusEventType.Periodic):
            return
        door_state = evt_value.value
        self.emit(Qt.SIGNAL('doorStateChanged'), door_state)

        
@UILoadable(with_ui='ui')
class MacroButton(TaurusWidget):
    ''' A button to execute/pause/stop macros. The model must be a valid door.
        
    .. todo:: Not implemented but will be needed: set an icon
 
    .. todo:: It may be useful to have all the streams from qdoor available 
             somehow (right-click?)
    '''

    __pyqtSignals__ = ['statusUpdated', 'resultUpdated']

    def __init__(self, parent=None, designMode=False):
        TaurusWidget.__init__(self, parent, designMode)
        self.loadUi()
        self.door = None
        self.door_state_listener = None
        self.macro_name = ''
        self.macro_args = []
        self.macro_id = None
        self.running_macro = None

        self.ui.progress.setValue(0)

        self.ui.button.setCheckable(True)
        self.connect(self.ui.button, Qt.SIGNAL('clicked()'), 
                     self._onButtonClicked)

    def toggleProgress(self, visible):
        '''deprecated'''
        self.warning('toggleProgress is deprecated. Use showProgress')
        self.showProgress(visible)
        
    def showProgress(self, visible):
        '''Set whether the progress bar is shown
        
        :param visible: (bool) If True, the progress bar is shown. Otherwise it 
                        is hidden'''
        self.ui.progress.setVisible(visible)

    def setModel(self, model):
        '''
        reimplemented from :class:`TaurusWidget`. A door device name is 
        expected as the model
        '''
        TaurusWidget.setModel(self, model)
        if self.door is not None:
            self.disconnect(self.door, Qt.SIGNAL('macroStatusUpdated'), self._statusUpdated)
            self.disconnect(self.door, Qt.SIGNAL('resultUpdated'), self._resultUpdated)

            # disable management of Door Tango States
            self.door.getAttribute('State').removeListener(self.door_state_listener)
            self.disconnect(self.door_state_listener, Qt.SIGNAL('doorStateChanged'), self._doorStateChanged)
            self.door_state_listener = None

        try: self.door = taurus.Device(model)
        except: return

        self.connect(self.door, Qt.SIGNAL('macroStatusUpdated'), self._statusUpdated)
        self.connect(self.door, Qt.SIGNAL('resultUpdated'), self._resultUpdated)

        # Manage Door Tango States
        self.door_state_listener = DoorStateListener()
        self.connect(self.door_state_listener, Qt.SIGNAL('doorStateChanged'), self._doorStateChanged)
        self.door.getAttribute('State').addListener(self.door_state_listener)

    def _doorStateChanged(self, state):
        '''slot called on door state changes'''
        color = '#' + DEVICE_STATE_PALETTE.hex(state)
        stylesheet = 'QFrame{border: 4px solid %s;}' % color
        self.ui.frame.setStyleSheet(stylesheet)

        # In case state is not ON, and macro not triggered by the button, disable it
        door_available = True
        if state not in [PyTango.DevState.ON, PyTango.DevState.ALARM] and not self.ui.button.isChecked():
            door_available = False

        self.ui.button.setEnabled(door_available)
        self.ui.progress.setEnabled(door_available)


    def _statusUpdated(self, *args):
        '''slot called on status changes'''
        # SHOULD SEE THE DOCUMENTATION ABOUT THE ARGS AND ALSO THE STATUS STATE MACHINE
        # ARGS FORMAT IS (GUESSING WITH PRINT STATEMENTS)
        # e.g. ((<sardana.taurus.core.tango.sardana.macro.Macro object at 0x7f29300bc210>, [{u'step': 100.0, u'state': u'stop', u'range': [0.0, 100.0], u'id': u'b226f5e8-c807-11e0-8abe-001d0969db5b'}]),)
        # ( (MacroObj, [status_dict, .?.]), .?.)

        # QUESTIONS: THIS MACRO OBJECT HAS ALOS STEP, RANGE, ...
        # AND ALSO THE STATUS DICT... WHICH SHOULD I USE?

        first_tuple = args[0]
        self.running_macro = first_tuple[0]

        status_dict = first_tuple[1][0]
        # KEYS RECEIVED FROM A 'SCAN' MACRO AND A 'TWICE' MACRO: IS IT GENERAL ?!?!?!
        macro_id = status_dict['id']
        # if macro id is unknown ignoring this signal
        if macro_id is None:
            return
        # check if we have launch this macro, otherwise ignore the signal
        if macro_id != str(self.macro_id):
            return
        state = status_dict['state']
        step = status_dict['step']
        step_range = status_dict['range']

        # Update progress bar
        self.ui.progress.setMinimum(step_range[0])
        self.ui.progress.setMaximum(step_range[1])
        self.ui.progress.setValue(step)

        if state in ['stop', 'abort', 'finish', 'alarm']:
            self.ui.button.setChecked(False)

        self.emit(Qt.SIGNAL('statusUpdated'), status_dict)

    def _resultUpdated(self, *args):
        '''slot called on result changes'''
        # ARGS APPEAR TO BE EMPTY... SHOULD THEY CONTAIN THE RESULT ?!?!?!
        # I have to rely on the 'macro object' received in the last status update
        if self.running_macro is None:
            return
        result = self.running_macro.getResult()
        self.emit(Qt.SIGNAL('resultUpdated'), result)

    def setText(self, text):
        '''set the button text
        
        :param text: (str) text for the button
        '''
        self.setButtonText(text)

    def setButtonText(self, text):        
        '''same as :meth:`setText`
        '''
        # SHOULD ALSO BE POSSIBLE TO SET AN ICON
        self.ui.button.setText(text)

    def setMacroName(self, name):
        '''set the name of the macro to be executed
        
        :param name: (str) text for the button
        '''
        self.macro_name = str(name)

    def updateMacroArgument(self, index, value):
        '''change a given argument
        
        :param index: (int) positional index for this argument
        :param value: (str) value for this argument
        '''
        #make sure that the macro_args is at least as long as index
        while len(self.macro_args) < index + 1:
            self.macro_args.append('')
        #update the given argument
        self.macro_args[index] = str(value)
    
    def updateMacroArgumentFromSignal(self, index, obj, signal):
        '''deprecated'''
        msg = 'updateMacroArgumentFromSignal is deprecated. connectArgEditors'
        self.warning(msg)
        self.connect(obj, signal, 
                     functools.partial(self.updateMacroArgument, index))
    
    def connectArgEditors(self, signals):
        '''Associate signals to argument changes. 
        
        :param signals: (seq<tuple>) An ordered sequence of (`obj`, `sig`) 
                        tuples , where `obj` is a parameter editor object and 
                        `sig` is a signature for a signal emitted by `obj` which
                        provides the value of a parameter as its argument.
                        Each (`obj`, `sig`) tuple is associated to parameter
                        corresponding to its position in the `signals` sequence.
                        '''
        
        for i,(obj,sig) in enumerate(signals):
            self.connect(obj, Qt.SIGNAL(sig), 
                         functools.partial(self.updateMacroArgument, i))

    def _onButtonClicked(self):
        if self.ui.button.isChecked():
            self.runMacro()
        else:
            self.abort()

    @ProtectTaurusMessageBox(msg='Error while executing the macro.')
    def runMacro(self):
        '''execute the macro with the current arguments'''
        if self.door is None:
            return

        # Thanks to gjover for the hint... :-D
        #macro_cmd = self.macro_name + ' ' + ' '.join(self.macro_args)
        self.macro_id = uuid.uuid1()
        macro_cmd_xml = '<macro name="%s" id="%s">\n' % \
                        (self.macro_name, self.macro_id)
        for arg in self.macro_args:
            macro_cmd_xml += '<param value="%s"/>\n' % arg
        macro_cmd_xml += '</macro>'
        try:
            #self.door.runMacro(macro_cmd)
            self.door.runMacro(macro_cmd_xml)
        except Exception, e:
            self.ui.button.setChecked(False)
            raise e

    def abort(self):
        '''abort the macro.'''
        if self.door is None:
            return
        self.door.PauseMacro()
        # Since this could be done by error (impatient users clicking more than once)
        # we provide a warning message that does not make the process too slow
        # It may also be useful and 'ABORT' at TaurusApplication level (macros+motions+acquisitions)
        title = 'Aborting macro'
        message = 'The following macro is still running:\n\n'
        message += '%s %s\n\n' % (self.macro_name, ' '.join(self.macro_args))
        message += 'Are you sure you want to abort?\n'
        buttons = Qt.QMessageBox.Ok | Qt.QMessageBox.Cancel
        ans = Qt.QMessageBox.warning(self, title, message, buttons, Qt.QMessageBox.Ok)
        if ans == Qt.QMessageBox.Ok:
            self.door.abort(synch=True)
        else:
            self.ui.button.setChecked(True)
            self.door.ResumeMacro()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''reimplemented from :class:`TaurusWidget`'''
        return {'container': False,
                'group': 'Taurus Sardana',
                'module': 'taurus.qt.qtgui.extra_macroexecutor',
                'icon': ':/designer/pushbutton.png'}


class MacroButtonAbortDoor(Qt.QPushButton, TaurusBaseWidget):
    '''Deprecated class. Instead use TaurusCommandButton.
    A button for aborting macros on a door
    '''
    #todo: why not inheriting from (TaurusBaseComponent, Qt.QPushButton)?
    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QPushButton, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self.warning('Deprecation warning: use TaurusCommandButton class ' +\
                     'instead of MacroButtonAbortDoor')

        self.setText('Abort')
        self.setToolTip('Abort Macro')
        self.connect(self, Qt.SIGNAL('clicked()'), self.abort)

    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return TaurusDevice

    @ProtectTaurusMessageBox(msg='An error occurred trying to abort the macro.')
    def abort(self):
        '''stops macros'''
        door = self.getModelObj()
        if door is not None:
            door.stopMacro()


if __name__ == '__main__':
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util.argparse import get_taurus_parser
    from sardana.macroserver.macros.test import SarDemoEnv

    parser = get_taurus_parser()
    parser.set_usage("python macrobutton.py [door_name]")
    parser.set_description("Macro button for macro execution")

    app = TaurusApplication(app_name="macrobutton",
                            app_version=taurus.Release.version)

    args = app.get_command_line_args()

    if len(args) < 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    door_name = args[0]

    w = Qt.QWidget()
    w.setLayout(Qt.QGridLayout())

    col = 0
    w.layout().addWidget(Qt.QLabel('macro name'), 0, col)
    macro_name = Qt.QLineEdit()
    w.layout().addWidget(macro_name, 1, col)

    _argEditors = []
    for a in range(5):
        col += 1
        w.layout().addWidget(Qt.QLabel('arg%d' % a), 0, col)
        argEdit = Qt.QLineEdit()
        w.layout().addWidget(argEdit, 1, col)
        _argEditors.append(argEdit)


    from sardana.taurus.qt.qtcore.tango.sardana.macroserver import registerExtensions
    registerExtensions()
    mb = MacroButton()

    mb.setModel(door_name)

    w.layout().addWidget(mb, 2, 0, 2, 7)

    w.layout().addWidget(Qt.QLabel('Result:'), 4, 0)

    result_label = Qt.QLabel()
    w.layout().addWidget(result_label, 4, 1, 1, 5)

    show_progress = Qt.QCheckBox('Progress')
    show_progress.setChecked(True)
    w.layout().addWidget(show_progress, 5, 0)

    mb_abort = TaurusCommandButton(command = 'StopMacro',
                                   icon=':/actions/media_playback_stop.svg')
    mb_abort.setModel(door_name)

    w.layout().addWidget(mb_abort, 5, 1)

    # Change macro name
    Qt.QObject.connect(macro_name, Qt.SIGNAL('textChanged(QString)'), mb.setMacroName)
    Qt.QObject.connect(macro_name, Qt.SIGNAL('textChanged(QString)'), mb.setButtonText)
    
    # connect the argument editors
    signals = [(e, 'textChanged(QString)') for e in _argEditors]
    mb.connectArgEditors(signals)

    def update_result(result):
        result_label.setText(str(result))

    def toggle_progress(showProgress):
        visible = show_progress.isChecked()
        mb.toggleProgress(visible)

    # Toggle progressbar
    Qt.QObject.connect(show_progress, Qt.SIGNAL('stateChanged(int)'), toggle_progress)
    # Update possible macro result
    Qt.QObject.connect(mb, Qt.SIGNAL('resultUpdated'), update_result)

    # Obtain a demo motor
    try:
        demo_motor_name = SarDemoEnv(door_name).getMotors()[0]
    except Exception, e:
        from taurus.core.util.log import warning, debug
        warning('It was unable to obtain a demo motor')
        debug('Details: %s' % e.message)
        demo_motor_name = ''

    # Since everything is now connected, the parameters will be updated
    macro_name.setText('ascan')
    macro_params = [demo_motor_name, '0', '1', '5', '.1']
    for e,v in zip(_argEditors, macro_params):
        e.setText(v)

    w.show()
    sys.exit(app.exec_())
