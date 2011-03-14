#!/usr/bin/env python
# Copyright (c) 2008 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *
import sys, os
import bisect
import codecs
import taurus.qt.qtgui.resource
import PyQt4.QtGui
from PyQt4.QtCore import (QAbstractItemModel, QModelIndex, QString,
        QVariant, Qt, SIGNAL)

KEY, NODE = range(2)


class BranchNode(object):

    def __init__(self, name, parent=None):
        super(BranchNode, self).__init__()
        self.name = name
        self.parent = parent
        self.children = []

    def orderKey(self):
        return self.name.lower()

    def toString(self):
        return self.name

    def __len__(self):
        return len(self.children)

    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row][NODE]
        
    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i
        return -1

#     with sorting
#    def childWithKey(self, key):
#        if not self.children:
#            return None
#        # Causes a -3 deprecation warning. Solution will be to
#        # reimplement bisect_left and provide a key function.
#        i = bisect.bisect_left(self.children, (key, None))
#        if i < 0 or i >= len(self.children):
#            return None
#        if self.children[i][KEY] == key:
#            return self.children[i][NODE]
#        return None

    # without sorting
    def childWithKey(self, key):
        if not self.children:
            return None
        for i in range(len(self.children)):
            if self.children[i][KEY] == key:
                return self.children[i][NODE]
        return None

    def insertChild(self, child):
        child.parent = self
        # sorted
        #bisect.insort(self.children, (child.orderKey(), child))
        # unsorted
        self.children.append((child.orderKey(), child))

    def hasLeaves(self):
        if not self.children:
            return False
        return isinstance(self.children[0], LeafNode)


class LeafNode(object):

    def __init__(self, name, data, parent=None):
        super(LeafNode, self).__init__()
        self.parent = parent
        self.name = name
        self.data = data

    def orderKey(self):
        return "\t"+self.name.lower()
    
    def getName(self):
        return self.name

    def asRecord(self):
        return self.getName()
    
    def asData(self):        
        return self.data
    

class SimpleTreeModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super(SimpleTreeModel, self).__init__(parent)
        self.columns = 1
        self.root = BranchNode("")
        self.headers = ["Type"]
        
    def setHeaders(self, headers):
        self.headers = headers
        
    def getHeaders(self):
        return self.headers
        
    def addNodes(self, fields, callReset=True):
        root = self.root
        branch = None
        for i in range(len(fields)):
            key = fields[i].lower()
            branch = root.childWithKey(key)
            if branch is not None:
                root = branch
            else:
                branch = BranchNode(fields[i])
                root.insertChild(branch)
                root = branch
        if callReset:
            self.reset()   
        self.headers = ["Type"]
            
    def addRecord(self, fields, data, callReset=True):
        root = self.root
        branch = None
        for i in range(len(fields)-1):
            key = fields[i].lower()
            branch = root.childWithKey(key)
            if branch is not None:
                root = branch
            else:
                branch = BranchNode(fields[i])
                root.insertChild(branch)
                root = branch
        assert branch is not None
        item = fields[len(fields)-1]
        branch.insertChild(LeafNode(item, data, branch))
        if callReset:
            self.reset()   
        self.headers = ["Type"]

    def asRecord(self, index):
        leaf = self.nodeFromIndex(index)
        if leaf is not None and isinstance(leaf, LeafNode):
            return leaf.asRecord()
        return "None"

    def asData(self, index):
        leaf = self.nodeFromIndex(index)
        if leaf is not None and isinstance(leaf, LeafNode):
            return leaf.asData()
        else:
            return None

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, LeafNode):
            return 0
        return len(node)

    def columnCount(self, parent):
        return self.columns

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop|Qt.AlignLeft))
        
        if role == Qt.DecorationRole:
            node = self.nodeFromIndex(index)
            assert node is not None
            if isinstance(node, LeafNode):
                return QVariant(node.asData().get_icon())
            else:
                return QVariant()
        
        if role != Qt.DisplayRole:
            return QVariant()
        
        node = self.nodeFromIndex(index)
        assert node is not None
        
        if isinstance(node, BranchNode):
            if index.column() == 0:
                return QVariant(node.toString())
            else:
                return QVariant(QString(""))

        if isinstance(node, LeafNode):
            return QVariant(QString(node.getName()))

    def headerData(self, section, orientation, role):
        if (orientation == Qt.Horizontal and
            role == Qt.DisplayRole):
            #assert 0 <= section <= len(self.headers)
            return QVariant(self.headers[section])
        return QVariant()


    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))

    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)


    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root
        
        #return (index.internalPointer()
        #        if index.isValid() else self.root)######################
        
        
