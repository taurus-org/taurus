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
from taurus.core.util.colors import DEVICE_STATE_PALETTE

import functools

from ui_macrobutton import Ui_MacroButton

class DoorStateListener(Qt.QObject):

    __pyqtSignals__ = ["doorStateChanged"]

    def eventReceived(self, evt_src, evt_type, evt_value):
        if evt_type not in (taurus.core.taurusbasetypes.TaurusEventType.Change, taurus.core.taurusbasetypes.TaurusEventType.Periodic):
            return
        door_state = evt_value.value
        self.emit(Qt.SIGNAL('doorStateChanged'), door_state)
        

class MacroButton(TaurusWidget):
    ''' This class is intended to be used as a button to execute macros.
    The model must be a valid door.
    
    ..note:: Not implemented but will be needed: set an icon

    ..note::
        
        It may be useful to have a slot update_macro_param that any qwidget signal may be
        connected to. The only condition might be that the sender widget should have an
        attribute 'widget.macro_param_index' in order to determine where the value has
        to be added.
 
    ..note::
        
        It may be useful to have all the streams from qdoor available somehow
        (right-click?)
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
        TaurusWidget.setModel(self, model)
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
        if state not in [PyTango.DevState.ON, PyTango.DevState.ALARM] and not self.ui.button.isChecked():
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

        if state in ['stop', 'abort', 'finish', 'alarm']:
            self.ui.button.setChecked(False)
        
        self.emit(Qt.SIGNAL('statusUpdated'), status_dict)

    def resultUpdated(self, *args):
        # ARGS APPEAR TO BE EMPTY... SHOULD THEY CONTAIN THE RESULT ?!?!?!
        # I have to rely on the 'macro object' received in the last status update
        if self.running_macro is None:
            return
        result = self.running_macro.getResult()
        self.emit(Qt.SIGNAL('resultUpdated'), result)

    def setText(self, text):
        self.setButtonText(text)

    def setButtonText(self, text):
        # SHOULD ALSO BE POSSIBLE TO SET AN ICON
        self.ui.button.setText(text)

    def setMacroName(self, macro_name):
        self.macro_name = str(macro_name)

    def updateMacroArgument(self, index, value):
        while len(self.macro_args) < index + 1:
            self.macro_args.append('')
            
        self.macro_args[index] = str(value)

    def updateMacroArgumentFromSignal(self, index, obj, signal):
        self.connect(obj, signal, functools.partial(self.updateMacroArgument,index))

    def button_clicked(self):
        if self.ui.button.isChecked():
            self.runMacro()
        else:
            self.abort()

    @ProtectTaurusMessageBox(msg='An error occurred trying to execute the macro.')
    def runMacro(self):
        if self.door is None:
            return

        # Thanks to gjover for the hint... :-D
        #macro_cmd = self.macro_name + ' ' + ' '.join(self.macro_args)
        macro_cmd_xml = '<macro name="%s">\n' % self.macro_name
        for arg in self.macro_args:
            macro_cmd_xml += '<param value="%s"/>\n' % arg
        macro_cmd_xml += '</macro>'
        try:
            #self.door.runMacro(macro_cmd)
            self.door.runMacro(macro_cmd_xml)
        except Exception,e:
            self.ui.button.setChecked(False)
            raise e

    def abort(self):
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
        return {'container': False, 
                'group': 'Taurus Sardana', 
                'module': 'taurus.qt.qtgui.extra_macroexecutor', 
                'icon': ':/designer/pushbutton.png'}



class MacroButtonAbortDoor(TaurusWidget):
    def __init__(self, parent=None, designMode=False):
        TaurusWidget.__init__(self, parent, designMode)
        self.setLayout(Qt.QGridLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)

        self.btn_abort = Qt.QPushButton('Abort')
        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.btn_abort.setSizePolicy(sizePolicy)
        
        self.door = None
        self.btn_abort.setToolTip('Abort Macro')

        self.layout().addWidget(self.btn_abort, 0, 0)
        self.connect(self.btn_abort, Qt.SIGNAL('clicked()'), self.abort)

    def setModel(self, model):
        TaurusWidget.setModel(self, model)
        try: self.door = taurus.Device(model)
        except: self.door = None

    @ProtectTaurusMessageBox(msg='An error occurred trying to abort the macro.')
    def abort(self):
        if self.door is not None:
            self.door.stopMacro()



if __name__ == '__main__':
    import sys
    app = Qt.QApplication(sys.argv)

    w = Qt.QWidget()
    w.setLayout(Qt.QGridLayout())

    col = 0
    clear_button = Qt.QPushButton('clear')
    w.layout().addWidget(clear_button, 0, col, 2, 1)
    
    col += 1
    w.layout().addWidget(Qt.QLabel('macro name'), 0, col)
    macro_name = Qt.QLineEdit()
    w.layout().addWidget(macro_name, 1, col)

    col += 1
    w.layout().addWidget(Qt.QLabel('arg0'), 0, col)
    arg0 = Qt.QLineEdit()
    w.layout().addWidget(arg0, 1, col)

    col += 1
    w.layout().addWidget(Qt.QLabel('arg1'), 0, col)
    arg1 = Qt.QLineEdit()
    w.layout().addWidget(arg1, 1, col)

    col += 1
    w.layout().addWidget(Qt.QLabel('arg2'), 0, col)
    arg2 = Qt.QLineEdit()
    w.layout().addWidget(arg2, 1, col)

    col += 1
    w.layout().addWidget(Qt.QLabel('arg3'), 0, col)
    arg3 = Qt.QLineEdit()
    w.layout().addWidget(arg3, 1, col)

    col += 1
    w.layout().addWidget(Qt.QLabel('arg4'), 0, col)
    arg4 = Qt.QLineEdit()
    w.layout().addWidget(arg4, 1, col)

    from taurus.qt.qtcore.tango.sardana.macroserver import registerExtensions
    registerExtensions()
    mb = MacroButton()
    mb.setModel('door/gc/1')

    w.layout().addWidget(mb, 2, 0, 2, 7)

    w.layout().addWidget(Qt.QLabel('Result:'), 4, 0)

    result_label = Qt.QLabel()
    w.layout().addWidget(result_label, 4, 1, 1, 5)

    show_progress = Qt.QCheckBox('Progress')
    show_progress.setChecked(True)
    w.layout().addWidget(show_progress, 5, 0)

    mb_abort = MacroButtonAbortDoor()
    mb_abort.setModel('door/gc/1')
    w.layout().addWidget(mb_abort, 5, 1)

    # Change macro name
    Qt.QObject.connect(macro_name, Qt.SIGNAL('textChanged(QString)'), mb.setMacroName)
    Qt.QObject.connect(macro_name, Qt.SIGNAL('textChanged(QString)'), mb.setButtonText)

    # Change Nth macro argument
    mb.updateMacroArgumentFromSignal(0, arg0, Qt.SIGNAL('textChanged(QString)'))
    mb.updateMacroArgumentFromSignal(1, arg1, Qt.SIGNAL('textChanged(QString)'))
    mb.updateMacroArgumentFromSignal(2, arg2, Qt.SIGNAL('textChanged(QString)'))
    mb.updateMacroArgumentFromSignal(3, arg3, Qt.SIGNAL('textChanged(QString)'))
    mb.updateMacroArgumentFromSignal(4, arg4, Qt.SIGNAL('textChanged(QString)'))


    def update_result(result):
        result_label.setText(str(result))
    
    def toggle_progress(showProgress):
        visible = show_progress.isChecked()
        mb.toggleProgress(visible)

    def clear_params():
        for line_edit in [macro_name, arg0, arg1, arg2, arg3, arg4]:
            line_edit.setText('')

    # Toggle progressbar
    Qt.QObject.connect(show_progress, Qt.SIGNAL('stateChanged(int)'), toggle_progress)
    # Update possible macro result
    Qt.QObject.connect(mb, Qt.SIGNAL('resultUpdated'), update_result)
    # Clear parameters
    Qt.QObject.connect(clear_button, Qt.SIGNAL('clicked()'), clear_params)
    
    # Since everything is now connected, the parameters will be updated
    macro_name.setText('ascan')
    arg0.setText('gcdmot1')
    arg1.setText('1')
    arg2.setText('10')
    arg3.setText('5')
    arg4.setText('0.1')

    w.show()
    sys.exit(app.exec_())
