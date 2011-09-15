#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
macrobutton.py: 
"""
__all__=['MacroButton']

import PyTango

from taurus.qt import Qt

import taurus
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.dialog import ProtectTaurusMessageBox
from taurus.core.util import DEVICE_STATE_PALETTE

from ui_macrobutton import Ui_MacroButton

class DoorStateListener(Qt.QObject):

    __pyqtSignals__ = ["doorStateChanged"]

    def eventReceived(self, evt_src, evt_type, evt_value):
        if evt_type not in (taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic):
            return
        door_state = evt_value.value
        self.emit(Qt.SIGNAL('doorStateChanged'), door_state)
        

class MacroButton(TaurusWidget):
    ''' This class is intended to be used as a button to execute macros.
    The model must be a valid door.
    NOTE: Not implemented but will be needed: set an icon
    NOTE: It may be useful to have a slot update_macro_param that any qwidget signal may be
          connected to. The only condition might be that the sender widget should have an
          attribute 'widget.macro_param_index' in order to determine where the value has
          to be added.
    NOTE: It may be useful to have all the streams from qdoor available somehow (right-click?)
    
    '''

    __pyqtSignals__ = ['statusUpdated', 'resultUpdated']
    
    def __init__(self, parent=None, designMode=False):
        TaurusWidget.__init__(self, parent, designMode)
        self.door = None
        self.door_state_listener = None
        self.macro_name = ''
        self.macro_args = []
        self.running_macro = None

        self.ui = Ui_MacroButton()
        self.ui.setupUi(self)
        self.ui.progress.setValue(0)

        self.ui.button.setCheckable(True)
        self.connect(self.ui.button, Qt.SIGNAL('clicked()'), self.button_clicked)

    def toggleProgress(self, visible):
        self.ui.progress.setVisible(visible)

    def setModel(self, model):
        if self.door is not None:
            self.disconnect(self.door, Qt.SIGNAL('macroStatusUpdated'), self.statusUpdated)
            self.disconnect(self.door, Qt.SIGNAL('resultUpdated'), self.resultUpdated)
            self.door.getAttribute('State').removeListener(self.door_state_listener)

        try: self.door = taurus.Device(model)
        except: return

        self.connect(self.door, Qt.SIGNAL('macroStatusUpdated'), self.statusUpdated)
        self.connect(self.door, Qt.SIGNAL('resultUpdated'), self.resultUpdated)

        # Manage Door Tango States
        self.door_state_listener = DoorStateListener()
        self.connect(self.door_state_listener, Qt.SIGNAL('doorStateChanged'), self.doorStateChanged)
        self.door.getAttribute('State').addListener(self.door_state_listener)

    def doorStateChanged(self, state):
        color = '#'+DEVICE_STATE_PALETTE.hex(state)
        stylesheet = 'QFrame{border: 4px solid %s;}' % color
        self.ui.frame.setStyleSheet(stylesheet)

        # In case state is not ON, and macro not triggered by the button, disable it
        door_available = True
        if state != PyTango.DevState.ON and not self.ui.button.isChecked():
            door_available = False
            self.ui.progress.setValue(0)
            
        self.ui.button.setEnabled(door_available)
        self.ui.progress.setEnabled(door_available)
            

    def statusUpdated(self, *args):
        # SHOULD SEE THE DOCUMENTATION ABOUT THE ARGS AND ALSO THE STATUS STATE MACHINE
        # ARGS FORMAT IS (GUESSING WITH PRINT STATEMENTS)
        # e.g. ((<taurus.core.tango.sardana.macro.Macro object at 0x7f29300bc210>, [{u'step': 100.0, u'state': u'stop', u'range': [0.0, 100.0], u'id': u'b226f5e8-c807-11e0-8abe-001d0969db5b'}]),)
        # ( (MacroObj, [status_dict, .?.]), .?.)

        # QUESTIONS: THIS MACRO OBJECT HAS ALOS STEP, RANGE, ...
        # AND ALSO THE STATUS DICT... WHICH SHOULD I USE?
        
        first_tuple = args[0]
        self.running_macro = first_tuple[0]

        status_dict = first_tuple[1][0]
        # KEYS RECEIVED FROM A 'SCAN' MACRO AND A 'TWICE' MACRO: IS IT GENERAL ?!?!?!
        state = status_dict['state']
        step = status_dict['step']
        step_range = status_dict['range']
        macro_id = status_dict['id']

        # Update progress bar
        self.ui.progress.setMinimum(step_range[0])
        self.ui.progress.setMaximum(step_range[1])
        self.ui.progress.setValue(step)

        if state in ['stop', 'abort']:
            self.ui.button.setChecked(False)
        
        self.emit(Qt.SIGNAL('statusUpdated'), status_dict)

    def resultUpdated(self, *args):
        # ARGS APPEAR TO BE EMPTY... SHOULD THEY CONTAIN THE RESULT ?!?!?!
        # I have to rely on the 'macro object' received in the last status update
        if self.running_macro is None:
            return
        result = self.running_macro.getResult()
        
        self.emit(Qt.SIGNAL('resultUpdated'), result)

    def setButtonText(self, text):
        # SHOULD ALSO BE POSSIBLE TO SET AN ICON
        self.ui.button.setText(text)

    def setMacroName(self, macro_name):
        self.macro_name = macro_name

    def setMacroArgs(self, args):
        self.macro_args = args

    def button_clicked(self):
        if self.ui.button.isChecked():
            self.runMacro()
        else:
            self.abort()

    @ProtectTaurusMessageBox(msg='An error occurred trying to execute the macro.')
    def runMacro(self):
        if self.door is None:
            return

        macro_cmd = self.macro_name + ' ' + ' '.join(self.macro_args)
        try:
            self.door.runMacro(macro_cmd)
        except Exception,e:
            self.ui.button.setChecked(False)
            raise e

    def abort(self):
        if self.door is None:
            return
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

if __name__ == '__main__':
    import sys
    app = Qt.QApplication(sys.argv)

    form = Qt.QWidget()
    form.setLayout(Qt.QVBoxLayout())

    macro_cmd = Qt.QLineEdit()
    form.layout().addWidget(macro_cmd)

    from taurus.qt.qtcore.tango.sardana.macroserver import registerExtensions
    registerExtensions()
    mb = MacroButton()
    mb.setModel('door/gcuni/1')

    form.layout().addWidget(mb)

    result_label = Qt.QLabel()
    form.layout().addWidget(result_label)

    show_progress = Qt.QCheckBox('Progress')
    show_progress.setChecked(True)
    form.layout().addWidget(show_progress)

    def update_macro(text):
        splitted = map(str,text.split(' '))
        macro_name = splitted[0]
        macro_args = splitted[1:]

        mb.setMacroName(macro_name)
        mb.setMacroArgs(macro_args)

        mb.setButtonText(macro_name)

    def update_result(result):
        result_label.setText(str(result))

    def toggle_progress(showProgress):
        visible = show_progress.isChecked()
        mb.toggleProgress(visible)

    Qt.QObject.connect(macro_cmd, Qt.SIGNAL('textChanged(QString)'), update_macro)
    Qt.QObject.connect(mb, Qt.SIGNAL('resultUpdated'), update_result)
    Qt.QObject.connect(show_progress, Qt.SIGNAL('stateChanged(int)'), toggle_progress)

    macro_cmd.setText('ascan gc_dmot1 0 1 10 0.1')
    form.show()
    sys.exit(app.exec_())
