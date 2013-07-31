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
model.py: 
"""

from taurus.qt import Qt
from lxml import etree
from taurus.core.tango.sardana import macro

class MacroSequenceTreeModel(Qt.QAbstractItemModel):
    
    def __init__(self, parent=None):
        Qt.QAbstractItemModel.__init__(self, parent)
        self.columns = 4
        self.setRoot(macro.SequenceNode())
        self.headers = ["Macro","Parameters", "Progress", "Pause"]
        
    def root(self):
        return self._root
    
    def setRoot(self, root):
        self._root = root
        self.reset()
        
    def clearSequence(self):
        self.setRoot(macro.SequenceNode())
        
    def isEmpty(self):
        return len(self.root()) == 0  
        
    def flags(self, index):
        column = index.column()
        node = self.nodeFromIndex(index)
        flags = Qt.Qt.ItemIsEnabled
        
        if column == 0:
            flags |= Qt.Qt.ItemIsSelectable
            
        elif column == 1:
            if isinstance(node, macro.SingleParamNode) and \
                not node.type() == "User":
                flags |= Qt.Qt.ItemIsEditable
            else:
                flags |= Qt.Qt.ItemIsSelectable  
                
        elif column == 2:
            flags |= Qt.Qt.ItemIsSelectable
            
        elif index.column() == 3:
            flags |= (Qt.Qt.ItemIsSelectable | Qt.Qt.ItemIsEditable)
            
        if isinstance(node, macro.MacroNode):
            flags |= Qt.Qt.ItemIsDragEnabled
            if node.isAllowedHooks():
                flags |= Qt.Qt.ItemIsDropEnabled 
        return flags
    
    def _insertRow(self, parentIndex, node=None, row=-1):
        parentNode = self.nodeFromIndex(parentIndex)
        
        if row == -1: row = len(parentNode)
        
        if isinstance(parentNode, macro.RepeatParamNode):
            if node == None: node = parentNode.newRepeat()
        
        self.beginInsertRows(parentIndex, row, row)
        row = parentNode.insertChild(node, row)
        self.endInsertRows()
        
        return self.index(row, 0, parentIndex)
        
    def _removeRow(self, index):
        """This method is used remove macro (pased via index)"""
        node = self.nodeFromIndex(index)
        parentIndex = index.parent()
        parentNode = self.nodeFromIndex(parentIndex)
        row = parentNode.rowOfChild(node)
        self.beginRemoveRows(parentIndex, row, row)
        parentNode.removeChild(node)
        self.endRemoveRows()

    def _upRow(self, index):
        node = self.nodeFromIndex(index)
        parentIndex = index.parent()
        parentNode = self.nodeFromIndex(parentIndex)
        row = parentNode.rowOfChild(node)
        self._removeRow(index)
        newIndex = self._insertRow(parentIndex, node, row - 1)
        if isinstance(parentNode, macro.RepeatParamNode): 
            parentNode.arrangeIndexes()
        return newIndex
    
    def _downRow(self, index):
        node = self.nodeFromIndex(index)
        parentIndex = index.parent()
        parentNode = self.nodeFromIndex(parentIndex)
        row = parentNode.rowOfChild(node)
        self._removeRow(index)
        newIndex = self._insertRow(parentIndex, node, row + 1)
        if isinstance(parentNode, macro.RepeatParamNode): 
            parentNode.arrangeIndexes()
        return newIndex
    
    def _leftRow(self, index):
        """This method is used to move selected macro (pased via index)
        to it's grandparent's hook list. In tree representation it basically move macro to the left"""
        node = self.nodeFromIndex(index)
        parentIndex = index.parent()
        grandParentIndex = parentIndex.parent()
        self._removeRow(index)
        return self._insertRow(grandParentIndex, node)
    
    def _rightRow(self, index):
        """This method is used to move selected macro (pased via index)
        to it's grandparent's hook list. In tree representation it basically move macro to the left"""
        node = self.nodeFromIndex(index)
        parentIndex = index.parent()
        row = index.row()
        self._removeRow(index)
        newParentIndex = self.index(row, 0, parentIndex) 
        return self._insertRow(newParentIndex, node)
    
    def rowCount(self, parent):
        branchNode = self.nodeFromIndex(parent)
        return len(branchNode)
    
    def columnCount(self, parent):
        return self.columns
    
    def data(self, index, role):
        if role == Qt.Qt.DisplayRole:
            node = self.nodeFromIndex(index)  
            if index.column() == 0: 
                return Qt.QVariant(node.name())
            elif index.column() == 1: 
                return Qt.QVariant(node.value())
            elif index.column() == 2:
                if isinstance(node, macro.MacroNode):
                    return Qt.QVariant(node.progress())
        elif role == Qt.Qt.DecorationRole:
            node = self.nodeFromIndex(index)
            if index.column() == 3:
                if isinstance(node, macro.MacroNode):
                    if node.isPause():
                        return Qt.QVariant(Qt.QIcon(":/actions/media-playback-pause.svg"))
        return Qt.QVariant()    
            
    def setData (self, index, value, role=Qt.Qt.EditRole):
        node = self.nodeFromIndex(index)
        if index.column() == 1:
            if isinstance(node, macro.SingleParamNode):
                node.setValue(Qt.from_qvariant(value, str))
                self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
                while True:
                    index = index.parent()
                    node = self.nodeFromIndex(index)
                    if isinstance(node, macro.MacroNode):
                        self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index.sibling(index.row(), self.columnCount(index)))
                        break
        elif index.column() == 2:
            progress = Qt.from_qvariant(value, float)
            node.setProgress(progress)
            self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        elif index.column() == 3:  
            node.setPause(Qt.from_qvariant(value, bool))
            self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        return True

    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Qt.Horizontal and role == Qt.Qt.DisplayRole:
            return Qt.QVariant(self.headers[section])
        return Qt.QVariant()
    
    def index(self, row, column, parent):
        assert self.root() is not None
        branchNode = self.nodeFromIndex(parent)
        assert branchNode is not None
        return self.createIndex(row, column, branchNode.child(row))
    
    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return Qt.QModelIndex()
        parent = node.parent()
        if parent is None:
            return Qt.QModelIndex()
        grandparent = parent.parent()
        if grandparent is None:
            return Qt.QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)
    
    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root()        
        
    def toXmlString(self, pretty=False, withId=True):
        xmlSequence = self.root().toXml(withId=withId)
        xmlTree = etree.ElementTree(xmlSequence)
        xmlString = etree.tostring(xmlTree, pretty_print=pretty) 
        return xmlString
    
    def fromXmlString(self, xmlString):
        xmlElement = etree.fromstring(xmlString)
        newRoot = macro.SequenceNode(None)
        newRoot.fromXml(xmlElement)
        self.setRoot(newRoot)
        self.reset()
        return newRoot
    
    def fromPlainText(self, text):
        newRoot = macro.SequenceNode(None)
        newRoot.fromPlainText(text)
        self.setRoot(newRoot)
        self.reset()
        return newRoot
    
    def assignIds(self):
        """
        Assigns ids for all macros present in the sequence. If certain macro
        already had an id, it stays without change. A list of all ids is returned
        
        :return: (list)
        """
        parentNode = self.root()
        return self.__assignIds(parentNode)
    
    def __assignIds(self, parentNode):
        ids = []
        for childNode in parentNode.children():
            if isinstance(childNode, macro.MacroNode): 
                id = childNode.assignId()
                ids.append(id)
                ids.extend(self.__assignIds(childNode))
        return ids
    
    def firstMacroId(self):
        return self.root().child(0).id()
    
    def lastMacroId(self):
        root = self.root()
        return root.child(len(root.children())-1).id()
        
    def createIdIndexDictionary(self):
        parentIndex = Qt.QModelIndex()
        parentNode = self.root()
        return self.__createIdIndexDictionary(parentIndex, parentNode)
        
    def __createIdIndexDictionary(self, parentIndex, parentNode):
        d = {}
        for row, child in enumerate(parentNode.children()):
            if isinstance(child, macro.MacroNode):
                index = self.index(row, 0, parentIndex)
                d[child.id()] = index
                d.update(self.__createIdIndexDictionary(index, child))
        return d
        
#    def supportedDropActions(self):
#        return Qt.Qt.CopyAction | Qt.Qt.MoveAction
        
#    def mimeTypes(self):
#        types = Qt.QStringList()
#        types.append("text/xml")
#        return types
    
#    def mimeData(self, indexes):
#        mimeData = Qt.QMimeData()
#        encodedData = Qt.QByteArray()
#        stream = Qt.QDataStream(encodedData, Qt.QIODevice.WriteOnly)
#        doc = xml.dom.minidom.Document()
#        for i,index in enumerate(indexes):
#            if i % 2:
#                continue
#            text = self.nodeFromIndex(index).toXml(doc).toxml()
#            stream.writeString(text)
#            
#        mimeData.setData("text/xml", encodedData)
#        return mimeData
#    
#    def dropMimeData(self, data, action, row, column, parent):
#        if action == Qt.Qt.IgnoreAction:
#            return True
#        if not data.hasFormat("text/xml"):
#            return False
#        
#        encodedData = data.data("text/xml")
#        stream = Qt.QDataStream(encodedData, Qt.QIODevice.ReadOnly)
#        newItems = Qt.QStringList()
#        rows = 0
#        
#        while(not stream.atEnd()):
#            text = stream.readString()
#            newItems.append(text)
#            rows += 1
#            
#        sequence = self.nodeFromIndex(parent)
#        
#        for text in newItems:
#            macroNode = macro.MacroNode()
#            macroNode.fromDoc(xml.dom.minidom.parseString(text))
#            self.insertMacro(sequence, macroNode, row, False)
#            macros = [macro.name() for macro in macroNode.allMacros()]
#            if action == Qt.Qt.CopyAction:
#                self.emit(Qt.SIGNAL("macrosAdded"), macros, macroNode.allMotors())
#            self.emit(Qt.SIGNAL("dataChanged"))
#        return True
    
    
class MacroSequenceProxyModel(Qt.QSortFilterProxyModel):
    
    def __init__(self, parent=None):
        Qt.QSortFilterProxyModel.__init__(self, parent)
        self.setDynamicSortFilter(True)
        self.headers = ["Macro","Parameters", "Progress", "Pause"]
        self.columns = 4
                    
    def __getattr__(self, name):
        return getattr(self.sourceModel(), name)
    
    def nodeFromIndex(self, index):
        sourceIndex = self.mapToSource(index)
        node = self.sourceModel().nodeFromIndex(sourceIndex)
        return node
    
    def createIdIndexDictionary(self):
        d = self.sourceModel().createIdIndexDictionary()
        for id, sourceIndex in d.iteritems():
            proxyIndex = self.mapFromSource(sourceIndex)
            d[id] = Qt.QPersistentModelIndex(proxyIndex)
        return d
        
    def filterAcceptsRow(self, row, parentIndex):
        child = self.sourceModel().index(row, 0, parentIndex)
        node = self.sourceModel().nodeFromIndex(child)
        return isinstance(node, macro.MacroNode)
     
class MacroParametersProxyModel(Qt.QSortFilterProxyModel):
    
    def __init__(self, parent=None):
        Qt.QSortFilterProxyModel.__init__(self, parent)
        self.columns = 2
        self.headers = ["Parameter", "Value", "", "", "", ""]
        self._macroIndex = None
        
    def __getattr__(self, name):
        return getattr(self.sourceModel(), name)
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Qt.Horizontal and role == Qt.Qt.DisplayRole:
            return Qt.QVariant(self.headers[section])
        return Qt.QVariant()
    
    def nodeFromIndex(self, index):
        sourceIndex = self.mapToSource(index)
        node = self.sourceModel().nodeFromIndex(sourceIndex)
        return node
        
    def setMacroIndex(self, macroIndex):
        self._macroIndex = macroIndex
        
    def macroIndex(self):
        return self._macroIndex
    
    def columnCount(self, parent):
        return self.columns
        
    def filterAcceptsRow(self, row, parentIndex):
        if self.macroIndex() == None:
            return False
        if self.macroIndex() == parentIndex:
            child = self.sourceModel().index(row, 0, parentIndex)
            node = self.sourceModel().nodeFromIndex(child) 
            if not isinstance(node, macro.ParamNode):
                return False 
        return True
    
            
    
