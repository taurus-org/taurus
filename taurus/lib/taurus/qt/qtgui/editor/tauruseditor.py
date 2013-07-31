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

"""This module contains a taurus text editor widget."""

__all__ = ["TaurusBaseEditor"]

__docformat__ = 'restructuredtext'

import sys
import os

from taurus.qt import Qt

try:
    import spyderlib
    v = spyderlib.__version__.split('.', 2)[:2]
    v = map(int, v)
    if v < [2,1]:
        raise Exception("TaurusEditor needs spyderlib >= 2.1")
except ImportError: 
    raise Exception("TaurusEditor needs spyderlib >= 2.1")

from spyderlib.utils.qthelpers import create_toolbutton
from spyderlib.widgets.findreplace import FindReplace
from spyderlib.widgets.editortools import OutlineExplorerWidget
from spyderlib.widgets.editor import EditorMainWindow, EditorSplitter
from taurus.qt.qtgui.util import ActionFactory

class TaurusBaseEditor(Qt.QSplitter):
    
    def __init__(self, parent=None):
        Qt.QSplitter.__init__(self, parent)
                
        self.editorstacks = []
        self.editorwindows = []

        self.menu_actions, self.io_actions = self.createMenuActions()

        self.toolbar_list = None
        self.menu_list = None

        self.find_widget = FindReplace(self, enable_replace=True)
        self.outlineexplorer = OutlineExplorerWidget(self, show_fullpath=False,
                                                     show_all_files=False)
        editor_widgets = Qt.QWidget(self)
        editor_layout = Qt.QVBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_widgets.setLayout(editor_layout)
        
        editor_layout.addWidget(EditorSplitter(self, self, self.menu_actions,
                                               first=True))
        editor_layout.addWidget(self.find_widget)
        
        self.setContentsMargins(0, 0, 0, 0)
        self.addWidget(editor_widgets)
        self.addWidget(self.outlineexplorer)
        
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 0)

        self.setup_window([], [])
    
    def editorStack(self):
        return self.editorstacks[0]
    
    def createMenuActions(self):
        return [], []
    
    def closeEvent(self, event):
        for win in self.editorwindows[:]:
            win.close()
        event.accept()

    def load(self, filename, goto=None):
        editorstack = self.editorStack()
        fileinfo = editorstack.load(filename)
        editorstack.analyze_script()
        if goto is not None:
            fileinfo.editor.go_to_line(goto)
    
    def reload(self, idx=None, filename=None, goto=None):
        if idx is None:
            idx = is_file_opened(filename)
        if idx is not None:
            editorstack = self.editorStack()
            editorstack.reload(idx)
            editorstack.analyze_script()
            if goto is not None:
                editorstack.set_current_filename(filename)
                editorstack.data[idx].editor.go_to_line(goto)
    
    def set_current_filename(self, filename):
        self.editorStack().set_current_filename(filename)
    
    def register_editorstack(self, editorstack):
        self.editorstacks.append(editorstack)
        if self.isAncestorOf(editorstack):
            # editorstack is a child of the Editor plugin
            editorstack.set_fullpath_sorting_enabled(True)
            editorstack.set_closable( len(self.editorstacks) > 1 )
            editorstack.set_outlineexplorer(self.outlineexplorer)
            editorstack.set_find_widget(self.find_widget)
            oe_btn = create_toolbutton(self)
            oe_btn.setDefaultAction(self.outlineexplorer.visibility_action)
            editorstack.add_corner_widgets_to_tabbar([5, oe_btn])
        
        editorstack.set_io_actions(*self.io_actions)
        font = Qt.QFont("Monospace")
        font.setPointSize(10)
        editorstack.set_default_font(font, color_scheme='Spyder')
        self.connect(editorstack, Qt.SIGNAL('close_file(int)'),
                     self.close_file_in_all_editorstacks)
        self.connect(editorstack, Qt.SIGNAL("create_new_window()"),
                     self.create_new_window)
        self.connect(editorstack, Qt.SIGNAL('plugin_load(QString)'),
                     self.load)
    
    def unregister_editorstack(self, editorstack):
        self.editorstacks.pop(self.editorstacks.index(editorstack))
        
    def clone_editorstack(self, editorstack):
        editorstack.clone_from(self.editorStack())
        
    def setup_window(self, toolbar_list, menu_list):
        self.toolbar_list = toolbar_list
        self.menu_list = menu_list
        
    def create_new_window(self):
        window = EditorMainWindow(self, self.menu_actions,
                                  self.toolbar_list, self.menu_list,
                                  show_fullpath=False, fullpath_sorting=True,
                                  show_all_files=False, show_comments=True)
        window.resize(self.size())
        window.show()
        self.register_editorwindow(window)
        self.connect(window, Qt.SIGNAL("destroyed()"),
                     lambda win=window: self.unregister_editorwindow(win))
        
    def register_editorwindow(self, window):
        self.editorwindows.append(window)
        
    def unregister_editorwindow(self, window):
        self.editorwindows.pop(self.editorwindows.index(window))
    
    def get_focus_widget(self):
        pass

    def close_file_in_all_editorstacks(self, index):
        sender = self.sender()
        for editorstack in self.editorstacks:
            if editorstack is not sender:
                editorstack.blockSignals(True)
                editorstack.close_file(index)
                editorstack.blockSignals(False)
    
    def register_widget_shortcuts(self, context, widget):
        """Fake!"""
        pass

    def refresh_save_all_action(self):
        pass

from spyderlib.plugins.editor import Editor

class TaurusBaseEditor2(Qt.QMainWindow):

    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent)
        
        self._editor = Editor(self)
        
        self.setCentralWidget(self._editor)

    def register_shortcut(self, qaction_or_qshortcut, context, name,
                          default=None):
        pass

    def show_hide_project_explorer(self):
        pass

def demo():
    test = TaurusBaseEditor()
    test.resize(1000, 800)
    test.load(__file__)
    test.load("__init__.py")
    test.show()
    return test

def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <file names>"
        app = Application(sys.argv, cmd_line_parser=parser, 
                          app_name="Taurus text editor demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")
        
    args = app.get_command_line_args()

    if len(args) == 0:
        w = demo()
    else:
        w = TaurusEditor()
        w.resize(900,800)
        for name in args:
            w.load(name)
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == "__main__":
    main()
    
