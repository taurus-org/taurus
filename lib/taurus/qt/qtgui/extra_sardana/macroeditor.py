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

__all__ = ["MacroEditor"]

__docformat__ = 'restructuredtext'

import os
import os.path as osp
import tempfile
import shutil
import functools

from PyQt4 import Qt

from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.editor import TaurusBaseEditor
from taurus.qt.qtgui.util import ActionFactory
from taurus.qt.qtgui.dialog import ProtectTaurusMessageBox
from macrotree import MacroTreeWidget, MacroSelectionDialog


class MacroEditor(TaurusBaseEditor, TaurusBaseWidget):
    
    def __init__(self, parent=None, designMode=None):
        name = self.__class__.__name__
        self._base_tmp_dir = None
        self._tmp_dir = None
        self._is_filesystem_prepared = False
        self.call__init__wo_kw(TaurusBaseEditor, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self._macrotree = MacroTreeWidget(self, with_navigation_bar=False, with_filter_widget=False)
        #self._macrotree.setShowToolbar(False)
        self.connect(self._macrotree, Qt.SIGNAL("itemDoubleClicked"), self.macroClicked)
        self.insertWidget(0, self._macrotree)
        self.setAutoTooltip(False)
            
    def setTemporaryDirectory(self, tmp_dir):
        self._base_tmp_dir = tmp_dir
        self._is_filesystem_prepared = False
        
    def getTemporaryDirectory(self):
        return self._base_tmp_dir
    
    def createMenuActions(self):
        af = ActionFactory()
        saveApply = functools.partial(self.saveMacro, apply=True)
        self.new_action  = af.createAction(self, "New macro",
                icon='document-new', tip="Create a new macro",
                triggered=self.newMacro)
        self.open_action = af.createAction(self, "Open macro(s)...",
                icon='document-open', tip="Open a macro(s)",
                triggered=self.openMacro)
        self.save_action = af.createAction(self, "Save macro",
                icon='document-save', tip="Save the current selected macro",
                triggered=self.saveMacro)
        self.save_and_apply_action = af.createAction(self, "Save && apply macro",
                icon='document-save', tip="Save the current selected macro and apply the new code",
                triggered=saveApply)
        self.revert_action = af.createAction(self, "Revert",
                icon='edit-undo', tip="Revert the current selected macro code",
                triggered=self.revertMacro)
        
        io_actions = [self.new_action, self.open_action, self.save_action, self.revert_action]
        actions = [self.new_action, self.open_action, self.save_action, self.save_and_apply_action, self.revert_action]
        return actions, io_actions
    
    def register_editorstack(self, editorstack):
        TaurusBaseEditor.register_editorstack(self, editorstack)
        self.connect(editorstack, Qt.SIGNAL('refresh_save_all_action()'),
                     self.refresh_save_and_apply_action)
    
    def refresh_save_and_apply_action(self):
        self.save_and_apply_action.setEnabled(self.save_action.isEnabled())
    
    def macroClicked(self,item, item_column):
        macro_info = item.itemData()
        self.openMacros([macro_info])
    
    @ProtectTaurusMessageBox(msg="A error occured trying to create a macro")
    def newMacro(self):
        ms = self.getModelObj()
        ms_path = ms.getMacroPathObj()
        directory, ok = Qt.QInputDialog.getItem(self, "New macro module",
            "Select the directory where you want the new macro module to be placed",
            ms_path.macro_path, current = 0, editable=False)
        if not ok:
            return
        directory = str(directory)
        ok = 0
        while not ok:
            mod, ok = Qt.QInputDialog.getText(self, "New macro module",
                "Module name:", Qt.QLineEdit.Normal, "")
            if not ok:
                return
            mod = str(mod)
            m, ext = osp.splitext(mod)
            if len(ext):
                if ext != ".py" :
                    Qt.QMessageBox.critical(self, "Wrong extension",
                        "When given, file extension<b> MUST</b> be <code>.py</code>.")
                    ok = 0
                    continue
            else:
                mod = mod + ".py"
        self._prepare_path(directory)
        filename = osp.join(directory, mod)
        rel_filename = filename[filename.index(osp.sep)+1:] # transform into relative path
        local_filename = osp.join(self._tmp_dir, rel_filename)
        f = file(local_filename, "w")
        f.write("from macro import *\n\n")
        f.close()
        self.editorStack().load(local_filename)
    
    @ProtectTaurusMessageBox(msg="A error occured trying to open a macro")
    def openMacro(self):
        ms = self.getModelObj()
        ms_tree = MacroSelectionDialog(self, model_name=ms.getNormalName())
        ms_tree.exec_()
        if ms_tree.result() != Qt.QDialog.Accepted:
            return
        self.openMacros(ms_tree.getSelectedMacros())
        
    def openMacros(self, macros):
        editorstack = self.editorStack()
        
        last_answer = Qt.QMessageBox.No
        for macro_info in macros:
            fname = macro_info.filename
            fname = fname[fname.index(osp.sep)+1:] # transform into relative path
            local_filename = osp.join(self._tmp_dir, fname)
            
            idx = editorstack.has_filename(local_filename)
            if idx is not None and last_answer not in (Qt.QMessageBox.YesToAll, Qt.QMessageBox.NoToAll):
                last_answer = Qt.QMessageBox.question(self,
                    "Macro file '%s' already opened" % macro_info.module_name,
                    "All changes to <b>%s</b> will be lost."
                    "<br>Do you want to revert file from the server ignoring "
                    "any possible changes you (may) have made?",
                    Qt.QMessageBox.Yes | Qt.QMessageBox.YesToAll | Qt.QMessageBox.No | Qt.QMessageBox.NoToAll,
                    Qt.QMessageBox.No)
            
            if idx is None or last_answer in (Qt.QMessageBox.Yes, Qt.QMessageBox.YesToAll):
                if not self._prepare_path(osp.dirname(macro_info.filename)):
                    Qt.QMessageBox.warning(self,
                        "Error trying to prepare '%s'" % macro_info.module_name,
                        "An error occured trying to prepare '%s'" % macro_info.module_name,
                        Qt.QMessageBox.Ok, Qt.QMessageBox.Ok)
                    continue
                _, code, line = self.getMacroCode(macro_info.module_name, macro_info.name)
                line = int(line)
                self.debug("Creating local file %s...", local_filename)
                fd = file(local_filename, "w")
                fd.write(code)
                fd.close()
                if idx is None:
                    self.debug("Loading local file %s...", local_filename)
                    self.load(local_filename,goto=line)
                else:
                    self.debug("Reloading local file %s...", local_filename)
                    self.reload(idx,goto=line)

    @ProtectTaurusMessageBox(msg="A error occured trying to save macro")
    def saveMacro(self, apply=False):
        editorstack = self.editorStack()
        # Save the currently edited file
        if not editorstack.get_stack_count():
            return
        index = editorstack.get_stack_index()
        res = editorstack.save(index=index)
        file_info = editorstack.data[index]
        if not res:
            return
        local_filename = file_info.filename
        fd = file(local_filename, "r")
        code = fd.read()
        fd.close()
        remote_filename = local_filename[len(self._tmp_dir):]
        self.setMacroCode(remote_filename, code)
        if apply:
            _, module_name = osp.split(local_filename)
            module_name, _ = osp.splitext(module_name)
            self.reloadMacroLib(module_name)
    
    def revertMacro(self):
        self.editorStack().revert()

    def reloadMacroLib(self, module_name):
        pass

    def setMacroCode(self, filename, code):
        ms = self.getModelObj()
        return ms.SetMacroCode((filename, code))

    def getMacroCode(self, module_name, macro_name):
        ms = self.getModelObj()
        return ms.GetMacroCode((module_name, macro_name))
    
    def setModel(self, model_name):
        TaurusBaseWidget.setModel(self, model_name)
        self._macrotree.setModel(model_name)
        self._is_filesystem_prepared = False
        self.prepare_filesystem()
    
    def _prepare_path(self, p):
        if not self.prepare_filesystem():
            return False
        p = p[p.index(osp.sep)+1:] # transform into relative path
        p = osp.join(self._tmp_dir, p)
        if not osp.exists(p):
            os.makedirs(p)
        return True
    
    def prepare_filesystem(self):
        """Prepares a temporary directory to store the macro files locally"""
        if self._is_filesystem_prepared:
            return True
        ms = self.getModelObj()
        if ms is None:
            self.debug("Could not prepare local filesystem to store macros")
            return False
        ms_name = ms.getSimpleName().replace('/','_')
        self._tmp_dir = tempfile.mkdtemp(prefix=ms_name, dir=self._base_tmp_dir)
        self._is_filesystem_prepared = True
        return True
    
    def closeEvent(self, event):
        if self._is_filesystem_prepared:
            shutil.rmtree(self._tmp_dir)
        TaurusBaseEditor.closeEvent(self, event)

def demo(model_name="MS_BL98"):
    test = MacroEditor()
    test.resize(1000, 800)
    test.load(__file__)
    test.setModel(model_name)
    #test.load("__init__.py")
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
        parser.usage = "%prog [options] <macro server name>"
        app = Application(sys.argv, cmd_line_parser=parser, 
                          app_name="Macro editor demo", app_version="1.0",
                          org_domain="Sardana", org_name="Tango community")
        
    args = app.get_command_line_args()

    if len(args) == 0:
        w = demo()
    else:
        w = demo(args[0])
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == "__main__":
    main()