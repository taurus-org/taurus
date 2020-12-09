#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""
"""

__all__ = ["QObjectRepresentation", "get_qobject_tree", "get_qobject_tree_str",
           "TreeQObjectModel", "TreeQObjectWidget"]

__docformat__ = 'restructuredtext'

import weakref

from taurus.external.qt import Qt

from taurus.core.util.enumeration import Enumeration

QObjectRepresentation = Enumeration('QObjectRepresentation',
                                    ('ClassName', 'ObjectName', 'FullName'))


def _build_qobjects_as_dict(qobject, container):

    container[qobject] = childs = {}
    for child in qobject.children():
        if isinstance(child, Qt.QWidget):
            _build_qobjects_as_dict(child, childs)


def get_qobject_tree_as_dict(qobject=None):

    if qobject is None:
        app = Qt.QApplication.instance()
        qobjects = app.topLevelWidgets()
    else:
        qobjects = [qobject]

    tree = {}
    for qobject in qobjects:
        _build_qobjects_as_dict(qobject, tree)

    return tree


def _build_qobjects_as_list(qobject, container):

    children = qobject.children()
    node = qobject, []
    container.append(node)
    for child in children:
        if isinstance(child, Qt.QWidget):
            _build_qobjects_as_list(child, node[1])


def get_qobject_tree_as_list(qobject=None):

    if qobject is None:
        app = Qt.QApplication.instance()
        qobjects = app.topLevelWidgets()
    else:
        qobjects = [qobject]

    tree = []
    for qobject in qobjects:
        _build_qobjects_as_list(qobject, tree)

    return tree

get_qobject_tree = get_qobject_tree_as_list


def _get_qobject_str(qobject, representation):
    if representation == QObjectRepresentation.ClassName:
        return qobject.__class__.__name__
    elif representation == QObjectRepresentation.ObjectName:
        return str(qobject.objectName())
    elif representation == QObjectRepresentation.FullName:
        return '{0}("{1}")'.format(qobject.__class__.__name__, str(qobject.objectName()))
    return str(qobject)


def _build_qobject_str(node, str_tree, representation=QObjectRepresentation.ClassName):

    qobject, children = node
    str_node = _get_qobject_str(qobject, representation)
    str_children = []
    str_tree.append((str_node, str_children))
    for child in children:
        _build_qobject_str(child, str_children, representation=representation)


def get_qobject_tree_str(qobject=None, representation=QObjectRepresentation.ClassName):

    tree, str_tree = get_qobject_tree(qobject=qobject), []
    for e in tree:
        _build_qobject_str(e, str_tree, representation=representation)
    return str_tree


from taurus.qt.qtgui.tree.qtree import QBaseTreeWidget
from taurus.qt.qtcore.model import TaurusBaseModel, TaurusBaseTreeItem

QR = QObjectRepresentation


class TreeQObjecttItem(TaurusBaseTreeItem):

    def __init__(self, model, data, parent=None):
        TaurusBaseTreeItem.__init__(self, model, data, parent=parent)
        if data is not None:
            self.qobject = weakref.ref(data)
            dat = _get_qobject_str(data, QR.ClassName), \
                _get_qobject_str(data, QR.ObjectName)
            self.setData(0, dat)


class TreeQObjectModel(TaurusBaseModel):

    ColumnNames = "Class", "Object name"
    ColumnRoles = (QR.ClassName,), QR.ObjectName

    def __init__(self, parent=None, data=None):
        TaurusBaseModel.__init__(self, parent=parent, data=data)

#    def createNewRootItem(self):
#        return TreeQObjecttItem(self, self.ColumnNames)

    def role(self, column, depth=0):
        if column == 0:
            return self.ColumnRoles[column][0]
        return self.ColumnRoles[column]

    def roleIcon(self, taurus_role):
        return Qt.QIcon()

    def roleSize(self, taurus_role):
        return Qt.QSize(300, 70)

    def roleToolTip(self, role):
        return "widget information"

    @staticmethod
    def _build_qobject_item(model, parent, node):
        qobject, children = node
        item = TreeQObjecttItem(model, qobject, parent)
        parent.appendChild(item)
        for child in children:
            TreeQObjectModel._build_qobject_item(model, item, child)

    def setupModelData(self, data):
        if data is None:
            return
        rootItem = self._rootItem
        for node in data:
            TreeQObjectModel._build_qobject_item(self, rootItem, node)


class TreeQObjectWidget(QBaseTreeWidget):

    KnownPerspectives = {
        "Default": {
            "label": "Default perspecive",
            "tooltip": "QObject tree view",
            "icon": "",
            "model": [TreeQObjectModel],
        },
    }

    DftPerspective = "Default"

    def __init__(self, parent=None, designMode=False, with_navigation_bar=True,
                 with_filter_widget=True, perspective=None, proxy=None,
                 qobject_root=None):
        QBaseTreeWidget.__init__(self, parent, designMode=designMode,
                                 with_navigation_bar=with_navigation_bar,
                                 with_filter_widget=with_filter_widget,
                                 perspective=perspective, proxy=proxy)
        qmodel = self.getQModel()
        qmodel.setDataSource(get_qobject_tree(qobject=qobject_root))


def build_gui():
    mw = Qt.QMainWindow()
    mw.setObjectName("main window")
    w = Qt.QWidget()
    w.setObjectName("central widget")
    mw.setCentralWidget(w)
    l = Qt.QVBoxLayout()
    w.setLayout(l)
    l1 = Qt.QLabel("H1")
    l1.setObjectName("label 1")
    l.addWidget(l1)
    l2 = Qt.QLabel("H2")
    l2.setObjectName("label 2")
    l.addWidget(l2)
    mw.show()
    return mw


def main():
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(cmd_line_parser=None)

    w = build_gui()
    tree = TreeQObjectWidget(qobject_root=w)
    tree.show()
    #import pprint
    # pprint.pprint(get_qobject_tree_str())
    w.dumpObjectTree()
    app.exec_()

if __name__ == "__main__":
    main()
