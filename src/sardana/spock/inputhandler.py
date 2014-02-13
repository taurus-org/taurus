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

"""Spock submodule. It contains an input handler"""

__all__ = ['SpockInputHandler', 'InputHandler']

__docformat__ = 'restructuredtext'

import sys
from multiprocessing import Process, Pipe

import genutils

from taurus.core.taurusmanager import TaurusManager
from taurus.core.util import Singleton
from taurus.core.tango.sardana.macroserver import BaseInputHandler
from taurus.qt import Qt
from taurus.qt.qtgui.dialog import TaurusMessageBox, TaurusInputDialog


class SpockInputHandler(BaseInputHandler):

    def __init__(self):
        # don't call super __init__ on purpose
        self._input = genutils.spock_input

    def input(self, input_data=None):
        if input_data is None:
            input_data = {}
        prompt = input_data.get('prompt')
        ret = dict(input=None, cancel=False)
        try:
            if prompt is None:
                ret['input'] = self._input()
            else:
                ret['input'] = self._input(prompt)
        except:
            ret['cancel'] = True
        return ret

    def input_timeout(self, input_data):
        print "SpockInputHandler input timeout"


class MessageHandler(Qt.QObject):

    def __init__(self, conn, parent=None):
        Qt.QObject.__init__(self, parent)
        self._conn = conn
        self._dialog = None
        self.connect(self, Qt.SIGNAL("messageArrived"), self.on_message)
        
    def handle_message(self, input_data):
        self.emit(Qt.SIGNAL("messageArrived"), input_data)
    
    def on_message(self, input_data):
        msg_type = input_data['type']
        if msg_type == 'input':
            if 'macro_name' in input_data and 'title' not in input_data:
                input_data['title'] = input_data['macro_name']
            self._dialog = dialog = TaurusInputDialog(input_data=input_data)
            dialog.activateWindow()
            dialog.exec_()
            ok = dialog.result()
            value = dialog.value()
            ret = dict(input=None, cancel=False)
            if ok:
                ret['input'] = value
            else:
                ret['cancel'] = True
            self._conn.send(ret)
        elif msg_type == 'timeout':
            dialog = self._dialog
            if dialog:
                dialog.close()


class InputHandler(Singleton, BaseInputHandler):
    
    def __init__(self):
        # don't call super __init__ on purpose
        pass
            
    def init(self, *args, **kwargs):
        self._conn, child_conn = Pipe()
        self._proc = proc = Process(target=self.safe_run,
            name="SpockInputHandler", args=(child_conn,))
        proc.daemon = True
        proc.start()
    
    def input(self, input_data=None):
        # parent process
        data_type = input_data.get('data_type', 'String')
        if isinstance(data_type, (str, unicode)):
            ms = genutils.get_macro_server()
            interfaces = ms.getInterfaces()
            if data_type in interfaces:
                input_data['data_type'] = [ elem.name for elem in interfaces[data_type].values() ]
        self._conn.send(input_data)
        ret = self._conn.recv()
        return ret

    def input_timeout(self, input_data):
        # parent process
        self._conn.send(input_data)
        
    def safe_run(self, conn):
        # child process
        try:
            return self.run(conn)
        except Exception, e:
            msgbox = TaurusMessageBox(*sys.exc_info())
            conn.send((e, False))
            msgbox.exec_()
    
    def run(self, conn):
        # child process
        self._conn = conn
        app = Qt.QApplication.instance()
        if app is None:
            app = Qt.QApplication([])
        app.setQuitOnLastWindowClosed(False)
        self._msg_handler = MessageHandler(conn)
        TaurusManager().addJob(self.run_forever, None)
        app.exec_()
        conn.close()
        print "Quit input handler"
                
    def run_forever(self):
        # child process
        message, conn = True, self._conn
        while message:
            message = conn.recv()
            if not message:
                continue
            self._msg_handler.handle_message(message)
        app = Qt.QApplication.instance()
        if app:
            app.quit()

