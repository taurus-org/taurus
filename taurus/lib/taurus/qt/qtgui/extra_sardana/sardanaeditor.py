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

__all__ = ["SardanaEditor"]

__docformat__ = 'restructuredtext'

import os
import os.path as osp
import tempfile
import shutil
import functools

from taurus.qt import Qt

from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.editor import TaurusBaseEditor
from taurus.qt.qtgui.util import ActionFactory
from taurus.qt.qtgui.dialog import ProtectTaurusMessageBox
from macrotree import MacroSelectionDialog
from elementtree import SardanaElementTreeWidget

from taurus.qt.qtcore.tango.sardana.model import SardanaBaseProxyModel, \
    SardanaElementTypeModel, SardanaTypeTreeItem, SardanaRootTreeItem

from sardanabasewizard import SardanaBaseWizard, SardanaBasePage

_MACRO_LIB_TEMPLATE = """#!/usr/bin/env python
{copyright}
# don't forget to place every new macro here!
__all__ = []

__docformat__ = 'restructuredtext'

{non_sardana_imports}
from sardana.macroserver.macro import macro, Macro, Type
{sardana_imports}
# Place your code here!

"""

_MACRO_CLASS_TEMPLATE = """

class {macro_name}(Macro):
    \"\"\"{macro_name} description.\"\"\"

    # uncomment the following lines as necessary. Otherwise you may delete them
    #param_def = []
    #result_def = []
    #hints = {}
    #env = (,)
    
    # uncomment the following lines if need prepare. Otherwise you may delete them
    #def prepare(self):
    #    pass
        
    def run(self):
        pass

"""

_MACRO_FUNCTION_TEMPLATE = """

@macro()
def {macro_name}(self):
    self.output("Running {macro_name}...")

"""

class NewElementWizard(SardanaBaseWizard):
    pass


class ChooseElementTypePage(SardanaBasePage):
    
    def __init__(self, parent = None):
        SardanaBasePage.__init__(self, parent)
    
        self.setTitle('Please select type of element you wish to create')
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)


class SardanaLibProxyModel(SardanaBaseProxyModel):
    
    ALLOWED_TYPES =  'MacroLibrary', #'ControllerLibrary',
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, 0, sourceParent)
        treeItem = idx.internalPointer()
        
        if isinstance(treeItem, SardanaRootTreeItem):
            return True
        if isinstance(treeItem, SardanaTypeTreeItem):
            return treeItem.itemData() in self.ALLOWED_TYPES
        return True


class SardanaLibTreeWidget(SardanaElementTreeWidget):
    
    KnownPerspectives = { "Type" : {
                          "label" : "By lib",
                          "icon" : ":/python-package.png",
                          "tooltip" : "View elements by library",
                          "model" : [SardanaLibProxyModel, SardanaElementTypeModel],
                        },
    }
    DftPerspective = "Type"
    

class SardanaEditor(TaurusBaseEditor, TaurusBaseWidget):

    def __init__(self, parent=None, designMode=None):
        name = self.__class__.__name__
        self._base_tmp_dir = None
        self._tmp_dir = None
        self._is_filesystem_prepared = False
        self.call__init__wo_kw(TaurusBaseEditor, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self._elementTree = elementTree = \
            SardanaLibTreeWidget(self, with_navigation_bar=False,
                                 with_filter_widget=False,)
        elementTree.treeView().setColumnHidden(1, True)
        self.connect(self._elementTree, Qt.SIGNAL("itemDoubleClicked"),
                     self.on_element_clicked)
        self.insertWidget(0, self._elementTree)
        self.setAutoTooltip(False)
            
    def setTemporaryDirectory(self, tmp_dir):
        self._base_tmp_dir = tmp_dir
        self._is_filesystem_prepared = False
        
    def getTemporaryDirectory(self):
        return self._base_tmp_dir
    
    def createMenuActions(self):
        af = ActionFactory()
        on_save = functools.partial(self.on_save, apply=False)
        on_save_apply = functools.partial(self.on_save, apply=True)
        
        self.new_action = af.createAction(self, "New...",
                icon='document-new', tip="Create a new macro or controller class",
                triggered=self.on_new, shortcut=Qt.QKeySequence.New)
        self.open_action = af.createAction(self, "Open...",
                icon='document-open', tip="Open macro(s) or controller(s)",
                triggered=self.on_open, shortcut=Qt.QKeySequence.Open)
        self.save_action = af.createAction(self, "Save",
                icon='document-save', tip="Save the current selected item",
                triggered=on_save)
        self.save_and_apply_action = af.createAction(self, "Save && apply",
                triggered=on_save_apply, icon='document-save',
                tip="Save the current selected item and apply the new code",
                shortcut=Qt.QKeySequence.Save)
        self.revert_action = af.createAction(self, "Revert",
                icon='edit-undo', tip="Revert the current selected item code",
                triggered=self.on_revert)
        
        io_actions = [self.new_action, self.open_action, self.save_action,
                      self.revert_action]
        actions = [self.new_action, self.open_action, self.save_action,
                   self.save_and_apply_action, self.revert_action]
        return actions, io_actions
    
    def register_editorstack(self, editorstack):
        TaurusBaseEditor.register_editorstack(self, editorstack)
        self.connect(editorstack, Qt.SIGNAL('refresh_save_all_action()'),
                     self.refresh_save_and_apply_action)
    
    def refresh_save_and_apply_action(self):
        self.save_and_apply_action.setEnabled(self.save_action.isEnabled())
    
    def on_element_clicked(self, item, item_column):
        item_data = item.itemData()
        interfaces = item_data.interfaces
        if 'MacroCode' in interfaces:
            self.open_macros([item_data])
        elif 'MacroLibrary' in interfaces:
            self.open_macro_libraries([item_data])
            
    @ProtectTaurusMessageBox(title="A error occured trying to create a class")
    def on_new(self):
        
        elem_types = "Macro function", "Macro class", "Macro library", \
            "Motor controller class", "Counter/Timer controller class", \
            "Pseudo motor controller class"
        
        msg = "Please select type of element you wish to create"
        elem_type, ok = Qt.QInputDialog.getItem(self, "New", msg, elem_types,
                                                current=0, editable=False)
        if not ok:
            return
        
        idx = elem_types.index(elem_type)
        if idx == 0:
            return self.new_macro_function()
        elif idx == 1:
            return self.new_macro_class()
        elif idx == 2:
            return self.new_macro_library()
        raise NotImplementedError("Sorry! Not implemented yet.")
    
    def new_macro(self, template):
        macro_server = self.getModelObj()
        
        msg = "Please select the library where you want to place the new macro"
        
        macro_libraries = macro_server.getElementsOfType("MacroLibrary")
        macro_lib_names = macro_libraries.keys()
        macro_lib_names.sort()
        macro_lib_name, ok = Qt.QInputDialog.getItem(self, "Macro library", msg,
            macro_lib_names, current = 0, editable=False)
        if not ok:
            return
        macro_lib_name = str(macro_lib_name)
        macro_lib = macro_libraries[macro_lib_name]
        
        fname, path = macro_lib.file_path, macro_lib.path
        fname = fname[fname.index(osp.sep)+1:] # transform into relative path
        local_filename = osp.join(self._tmp_dir, fname)
        
        msg = "Please give new macro name"
        
        macros = macro_lib.elements
        valid = False
        while not valid:
            macro_name, ok = Qt.QInputDialog.getText(self, "Macro name", msg)
            if not ok:
                return
            if macro_name in macros:
                res = Qt.QMessageBox.information(self, "Macro already exists",
                    "A macro named '%s' already exists in '%s'.\n"
                    "Please give a different macro name"
                    % (macro_name, macro_lib_name),
                    Qt.QMessageBox.Ok | Qt.QMessageBox.Cancel, Qt.QMessageBox.Ok)
                if res == Qt.QMessageBox.Cancel:
                    return
                continue
            valid = True

        pars = dict(macro_name=macro_name)
        code = template.format(**pars)
        
        editorstack = self.editorStack()
        idx = editorstack.has_filename(local_filename)
        if idx is None:
            if not self._prepare_path(path):
                raise Exception("Error trying to prepare path for %s", path)
            self.debug("Creating local file %s...", local_filename)
            fname, lib_code, line = macro_server.GetMacroCode((macro_lib_name,))
            fd = file(local_filename, "w")
            fd.write(lib_code)
            fd.close()
            self.debug("Loading local file %s...", local_filename)
            self.load(local_filename, goto=None)
        else:
            pass
        editorstack.set_current_filename(local_filename)
        editor = editorstack.get_current_editor()
        editor.set_cursor_position(editor.get_position("eof"))
        editor.append(code)
        return macro_lib, macro_name

    def new_macro_class(self):
        macro_info = self.new_macro(_MACRO_CLASS_TEMPLATE)
        if macro_info is None:
            return
        macro_lib, macro_name = macro_info
    
    def new_macro_function(self):
        macro_info = self.new_macro(_MACRO_FUNCTION_TEMPLATE)
        if macro_info is None:
            return
        macro_lib, macro_name = macro_info
        
    def new_macro_library(self):
        ms = self.getModelObj()
        ms_path = ms.getMacroPathObj()
        directory, ok = Qt.QInputDialog.getItem(self, "New macro module",
            "Select the directory where you want the new macro module to " \
            "be placed",
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
        
        #TODO: ask for additional imports
        #TODO: check if door environment has copyright variable
        
        pars = dict(copyright="", non_sardana_imports = "",
                    sardana_imports = "")
        code = _MACRO_LIB_TEMPLATE.format(**pars)
        f.write(code)
        f.close()
        self.editorStack().load(local_filename)
    
    @ProtectTaurusMessageBox(title="An error occured trying to open a macro class")
    def on_open(self):
        ms = self.getModelObj()
        ms_tree = MacroSelectionDialog(self, model_name=ms.getNormalName())
        ms_tree.exec_()
        if ms_tree.result() != Qt.QDialog.Accepted:
            return
        self.open_macros(ms_tree.getSelectedMacros())
    
    @ProtectTaurusMessageBox(title="An error occured trying to open macro(s)")
    def open_macros(self, macros):
        editorstack = self.editorStack()

        all_any = Qt.QMessageBox.YesToAll, Qt.QMessageBox.NoToAll
        yes_any = Qt.QMessageBox.Yes, Qt.QMessageBox.YesToAll
        no_any = Qt.QMessageBox.No, Qt.QMessageBox.NoToAll
        
        last_answer = Qt.QMessageBox.No
        for macro_info in macros:
            name, fname = macro_info.name, macro_info.file_path
            module = macro_info.module
            fname = fname[fname.index(osp.sep)+1:] # transform into relative path
            local_filename = osp.join(self._tmp_dir, fname)
            
            idx = editorstack.has_filename(local_filename)
            if idx is not None and last_answer not in all_any:
                last_answer = Qt.QMessageBox.question(self,
                    "Macro file '{0}' already opened".format(module),
                    "All changes to <b>{0}</b> will be lost."
                    "<br>Do you want to revert file from the server ignoring "
                    "any possible changes you (may) have made?".format(module),
                    Qt.QMessageBox.Yes | Qt.QMessageBox.YesToAll | \
                    Qt.QMessageBox.No  | Qt.QMessageBox.NoToAll,
                    Qt.QMessageBox.No)
            
            if idx is None or last_answer in yes_any:
                if not self._prepare_path(macro_info.path):
                    Qt.QMessageBox.warning(self,
                        "Error trying to prepare '{0}'".format(module),
                        "An error occured trying to prepare '{0}'".format(module),
                        Qt.QMessageBox.Ok, Qt.QMessageBox.Ok)
                    continue
                _, code, line = self.get_macro_code(module, name)
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
                    self.reload(idx, filename=local_filename, goto=line)
            elif last_answer in no_any:
                self.set_current_filename(local_filename)
    
    @ProtectTaurusMessageBox(title="An error occured trying to open macro(s)")
    def open_macro_libraries(self, macro_libraries):
        editorstack = self.editorStack()

        all_any = Qt.QMessageBox.YesToAll, Qt.QMessageBox.NoToAll
        yes_any = Qt.QMessageBox.Yes, Qt.QMessageBox.YesToAll
        no_any = Qt.QMessageBox.No, Qt.QMessageBox.NoToAll
        
        last_answer = Qt.QMessageBox.No
        for macro_library in macro_libraries:
            name, fname = macro_library.name, macro_library.file_path
            module = macro_library.module
            fname = fname[fname.index(osp.sep)+1:] # transform into relative path
            local_filename = osp.join(self._tmp_dir, fname)
            
            idx = editorstack.has_filename(local_filename)
            if idx is not None and last_answer not in all_any:
                last_answer = Qt.QMessageBox.question(self,
                    "Macro file '{0}' already opened".format(module),
                    "All changes to <b>{0}</b> will be lost."
                    "<br>Do you want to revert file from the server ignoring "
                    "any possible changes you (may) have made?".format(module),
                    Qt.QMessageBox.Yes | Qt.QMessageBox.YesToAll | \
                    Qt.QMessageBox.No  | Qt.QMessageBox.NoToAll,
                    Qt.QMessageBox.No)
            
            if idx is None or last_answer in yes_any:
                if not self._prepare_path(macro_library.path):
                    Qt.QMessageBox.warning(self,
                        "Error trying to prepare '{0}'".format(module),
                        "An error occured trying to prepare '{0}'".format(module),
                        Qt.QMessageBox.Ok, Qt.QMessageBox.Ok)
                    continue
                _, code, line = self.get_macro_code(module)
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
                    self.reload(idx, filename=local_filename, goto=line)
            elif last_answer in no_any:
                self.set_current_filename(local_filename)
    
    @ProtectTaurusMessageBox(msg="A error occured trying to save")
    def on_save(self, apply=True):
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
        self.set_macro_code(remote_filename, code, apply)
    
    def on_revert(self):
        self.editorStack().revert()
    
    def reload_macro_lib(self, module_name):
        pass
    
    def set_macro_code(self, filename, code, apply=True):
        ms = self.getModelObj()
        if apply:
            apply = "true"
        else:
            apply = "false"
        return ms.SetMacroCode((filename, code, apply))

    def get_macro_code(self, module_name, macro_name=None):
        ms = self.getModelObj()
        pars = [ module_name ]
        if macro_name is not None:
            pars.append(macro_name)
        return ms.GetMacroCode(pars)
    
    def setModel(self, model_name):
        TaurusBaseWidget.setModel(self, model_name)
        self._elementTree.setModel(model_name)
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
            self.warning("Could not prepare local filesystem to store macros")
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
    test = SardanaEditor()
    test.resize(1000, 800)
    #test.load(__file__)
    test.setModel(model_name)
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
        parser.error("must give a macroserver device name")
    else:
        w = demo(args[0])
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == "__main__":
    main()
