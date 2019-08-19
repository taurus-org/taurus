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
###########################################################################


"""
qdoublelist.py: Provides a generic dialog containing two list which can move
items from one to the other
"""

from __future__ import print_function

from builtins import str
from builtins import range

from taurus.external.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable


__all__ = ["QDoubleListDlg"]

__docformat__ = 'restructuredtext'


@UILoadable(with_ui='ui')
class QDoubleListDlg(Qt.QDialog):
    '''Generic dialog providing two lists. Items can be moved from one to the other
    '''
    #@todo: drag&drop is disabled because Qt<4.6 does not have QList.setDefaultDragAndDropMode()

    def __init__(self, parent=None, designMode=False, winTitle='', mainLabel='',
                 label1='', label2='', list1=None, list2=None):

        if list1 is None:
            list1 = []
        if list2 is None:
            list2 = []

        super(QDoubleListDlg, self).__init__(parent)
        self.loadUi()

        if winTitle:
            self.setWindowTitle(winTitle)
        self.ui.mainLabel.setText(mainLabel)
        self.ui.group1.setTitle(label1)
        self.ui.group2.setTitle(label2)

        self.setList1(list1)
        self.setList2(list2)

        self.ui.to1BT.clicked.connect(self.onTo1)
        self.ui.to2BT.clicked.connect(self.onTo2)

    def _moveItem(self, fromlist, tolist):
        selected = fromlist.selectedItems()
        for item in selected:
            fromlist.takeItem(fromlist.row(item))
            tolist.addItem(item)

    def setList1(self, list1):
        '''sets the items to be present in the first list

        :param list2: (seq<str>) a sequence of strings
        '''
        self.ui.list1.clear()
        self.ui.list1.addItems(list1)

    def setList2(self, list2):
        '''sets the items to be present in the second list

        :param list2: (seq<str>) a sequence of strings
        '''
        self.ui.list2.clear()
        self.ui.list2.addItems(list2)

    def onTo1(self, *args):
        '''slot to be called when the "To1" button is pressed'''
        self._moveItem(self.ui.list2, self.ui.list1)

    def onTo2(self, *args):
        '''slot to be called when the "To2" button is pressed'''
        self._moveItem(self.ui.list1, self.ui.list2)

    def getAll1(self):
        '''returns a copy the items in the first list

        :return: (list<str>)
        '''
        return [str(self.ui.list1.item(row).text()) for row in range(self.ui.list1.count())]

    def getAll2(self):
        '''returns a copy the items in the second list

        :return: (list<str>)
        '''
        return [str(self.ui.list2.item(row).text()) for row in range(self.ui.list2.count())]

    # note, for the moment we do not make it available in designer because it does not
    # behave well as a widget (only as a dialog) (e.g., it closes if ESC is pressed
#    @classmethod
#    def getQtDesignerPluginInfo(cls):
#        return {
#            'module' : 'taurus.qt.qtgui.panel',
#            'group' : 'Taurus Input',
#            #'icon' : "designer:ledred.png",
#            'container' : False,
#        }
#------------------------------------------------------------------------------


def main():
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)

    dlg = QDoubleListDlg(winTitle='foo', mainLabel='bla, bla', label1='1', label2='2',
                         list1=['11', '22'], list2=['123', '33'])
    result = dlg.exec_()

    print("Result", result)
    print("list1", dlg.getAll1())
    print("list2", dlg.getAll2())


if __name__ == "__main__":
    import sys
    main()
