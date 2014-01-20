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
delegate.py: 
"""

from taurus.qt import Qt
from taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.parameditors import AttrListComboBoxParam, SpinBoxParam, \
    DoubleSpinBoxParam, LineEditParam, FileDialogParam

from taurus.qt.qtgui.extra_macroexecutor import globals
from taurus.core.tango.sardana import macro  

class SequenceEditorDelegate(Qt.QItemDelegate):
    
    def __init__(self, parent=None):
        Qt.QItemDelegate.__init__(self, parent)
        
    def paint(self, painter, option, index):
        if index.column() == 2:
            macroNode = index.model().nodeFromIndex(index)
            opts = Qt.QStyleOptionProgressBarV2()
            opts.rect = option.rect
            range = macroNode.range()
            opts.minimum = range[0]
            opts.maximum = range[1]
            opts.textVisible = True
            percent = macroNode.progress()
            opts.progress = percent
#            opts.text = Qt.QString('Unavailable' if percent == 0 else '%d%%'%percent)
            opts.text = Qt.QString('%d%%'%percent)
#            opts.text = Qt.QString(percent)
            Qt.QApplication.style().drawControl(Qt.QStyle.CE_ProgressBar, opts, painter)
        else:
            Qt.QItemDelegate.paint(self, painter, option, index)

    
    def createEditor(self, parent, option, index):
        if index.column() == 3:
            return Qt.QCheckBox(parent)
        else:
            return Qt.QItemDelegate.createEditor(self, parent, option, index)
    
    def setEditorData(self, editor, index):
        node = index.model().mapToSource(index).internalPointer()
        if index.column() == 3: #and isinstance(node, MacroNode):
            editor.setChecked(node.isPause())
        else:
            Qt.QItemDelegate.setEditorData(self, editor, index)
            
    def setModelData(self, editor, model, index):
        if index.column() == 3:
            model.setData(index, Qt.QVariant(editor.isChecked()))
            
class MacroParametersProxyDelegate(Qt.QItemDelegate):
        
    def __init__(self, parent=None):
        Qt.QItemDelegate.__init__(self, parent)
    
    def createEditor(self, parent, option, index):
        if index.column() == 1: 
            node = index.model().nodeFromIndex(index)
            if isinstance(node, macro.SingleParamNode):
                paramType = node.type()
                if paramType in globals.EDITOR_COMBOBOX_PARAMS:
                    comboBox = AttrListComboBoxParam(parent, node)
                    comboBox.setUseParentModel(True)
                    return comboBox
                elif paramType in globals.EDITOR_SPINBOX_PARAMS:
                    return SpinBoxParam(parent, node)
                elif paramType in globals.EDITOR_DOUBLESPINBOX_PARAMS:
                    return DoubleSpinBoxParam(parent, node)
                elif paramType in globals.EDITOR_LINEEDIT_PARAMS:
                    return LineEditParam(parent, node)
                elif paramType in globals.EDITOR_FILEDIALOG_PARAMS:
                    return FileDialogParam(parent, node)
        return Qt.QItemDelegate.createEditor(self, parent, option, index)
    
    def setEditorData(self, editor, index):
        if index.column() == 1:
            text = Qt.from_qvariant(index.model().data(index, Qt.Qt.DisplayRole), str)
            if text == "None" or text == "":
                pass
            else:
                node = index.model().mapToSource(index).internalPointer()
                paramType = node.type()
                if paramType in globals.EDITOR_COMBOBOX_PARAMS :
                    i = editor.findText(text)
                    if i == -1: 
                        i = 0
                    else: 
                        editor.previous = text
                    editor.setCurrentIndex(i)  
                elif paramType in globals.EDITOR_SPINBOX_PARAMS:
                    editor.setValue(int(text))
                elif paramType in globals.EDITOR_DOUBLESPINBOX_PARAMS:
                    editor.setValue(float(text))
                elif paramType in globals.EDITOR_LINEEDIT_PARAMS:
                    editor.setText(text)
                elif paramType in globals.EDITOR_FILEDIALOG_PARAMS:
                    editor.filePath.setText(text)
        else:
            Qt.QItemDelegate.setEditorData(self, editor, index)
            
    def setModelData(self, editor, model, index):
        if index.column() == 1:
            model.setData(index, Qt.QVariant(editor.getValue()))
            
    def sizeHint(self, option, index):
        if index.column() == 0:
            fm = option.fontMetrics
            text = Qt.from_qvariant(index.model().data(index,Qt.Qt.DisplayRole), str)
            document = Qt.QTextDocument()
            document.setDefaultFont(option.font)
            document.setHtml(text)
            size = Qt.QSize(document.idealWidth() + 5, fm.height())
        elif index.column() == 1:
            editor = self.createEditor(self.parent(), option, index)
            if editor is None:
                size = Qt.QItemDelegate.sizeHint(self, option, index)
            else:
                size = editor.sizeHint()
                editor.hide()
                editor.setParent(None)
#                editor.destroy()
        else: 
            size = Qt.QItemDelegate.sizeHint(self, option, index)
        return size

                
