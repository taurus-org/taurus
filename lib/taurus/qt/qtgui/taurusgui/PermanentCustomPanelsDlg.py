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
###########################################################################


"""
PermanentCustomPanelDlg.py: 
"""

from taurus.qt import Qt
from ui.ui_PermanentCustomPanelsDlg import Ui_PermanentCustomPanelsDlg

class PermanentCustomPanelsDlg(Qt.QDialog):
    '''Dialog to define which Custom panels should be permanently stored in the configuration
    '''
    #@todo: drag&drop is disabled because Qt<4.6 does not have QList.setDefaultDragAndDropMode() 
    def __init__(self, parent=None, designMode=False, temporaryList=None, permanentList=None):
        super(PermanentCustomPanelsDlg,self).__init__(parent)
        
        self.ui = Ui_PermanentCustomPanelsDlg()
        self.ui.setupUi(self)
        
        self.setPermanentPanels(permanentList)
        self.setTemporaryPanels(temporaryList)
        
        self.connect(self.ui.toTemporaryBT, Qt.SIGNAL('clicked(bool)'), self.onToTemp)
        self.connect(self.ui.toPermanentBT, Qt.SIGNAL('clicked(bool)'), self.onToPerm)
        
    
    def setPermanentPanels(self, permanentList):
        self.ui.permanentPanelsList.clear()
        self.ui.permanentPanelsList.addItems(permanentList)
        
    def setTemporaryPanels(self, tempList):
        self.ui.temporaryPanelsList.clear()
        self.ui.temporaryPanelsList.addItems(tempList)
    
    def _moveItem(self, fromlist, tolist):
        selected = fromlist.selectedItems()
        for item in selected:
            fromlist.takeItem(fromlist.row(item))
            tolist.addItem(item)
        
    def onToTemp(self, *args):
        self._moveItem(self.ui.permanentPanelsList, self.ui.temporaryPanelsList)

    def onToPerm(self, *args):
        self._moveItem(self.ui.temporaryPanelsList, self.ui.permanentPanelsList)
        
    def getTemporaryPanels(self):
        return [unicode(self.ui.temporaryPanelsList.item(row).text()) for row in xrange(self.ui.temporaryPanelsList.count())]
    
    def getPermanentPanels(self):
        return [unicode(self.ui.permanentPanelsList.item(row).text()) for row in xrange(self.ui.permanentPanelsList.count())]


#------------------------------------------------------------------------------ 

def main():
    app = Qt.QApplication(sys.argv)
    
    
    form = PermanentCustomPanelsDlg(temporaryList=['11','22'], permanentList=['123','33'])
    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    import sys
    main()    
        
        