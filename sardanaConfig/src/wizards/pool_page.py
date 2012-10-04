import sys, os

from PyQt4 import QtGui, QtCore, Qt

import taurus
import wiz

from taurus.core.utils import Enumeration

PoolSelectionMode = Enumeration('PoolSelectionMode', ('FromSardana', 'FromDatabase'))
    
class SelectPoolBasePage(wiz.SardanaBasePage):
    
    def __init__(self, parent = None, selectionMode=PoolSelectionMode.FromDatabase):
        wiz.SardanaBasePage.__init__(self, parent)
        self.setSelectionMode(selectionMode)
        
        self['pool'] = self._getPool
        
        self.setSubTitle('Please select the Pool instance')
        
        panel = self.getPanelWidget()
        
        layout = QtGui.QFormLayout()
        
        self.poolCB = QtGui.QComboBox(panel)
        self.poolCB.setDuplicatesEnabled(False)
        self.poolCB.setEditable(False)

        layout.addRow("&Pool instance", self.poolCB)

        panel.setLayout(layout)

        self.connect(self.poolCB, 
                     QtCore.SIGNAL('currentIndexChanged(int)'), 
                     QtCore.SIGNAL('completeChanged()'))
    
    def getSelectionMode(self):
        return self._selectionMode
        
    def setSelectionMode(self, selectionMode):
        self._selectionMode = selectionMode
        
    def _getPool(self):
        pool_server = str(self.poolCB.currentText())
        return pool_server

    def pool(self):
        return self.wizard()['pool']
    
    def db(self):
        return self.wizard()['db']
    
    def isComplete(self):
        idx = self.poolCB.currentIndex()
        if idx >= 0:
            self.setStatus('')
            return True
        self.setStatus('No instance selected')
        return False

    def getPoolServerList(self):
        return [ s[s.index('/')+1:] for s in self.db().get_server_list() if s.startswith('Pool/') ]
    
    def _fillCB(self):
        self.poolCB.clear()
        mode = self.getSelectionMode()
        if mode == PoolSelectionMode.FromDatabase:
            self.poolCB.addItems(self.getPoolServerList())
        else:
            #TODO
            pass
            
    def initializePage(self):
        wiz.SardanaBasePage.initializePage(self)
        self._fillCB()

def t1(tg_host=None, sardana=None):

    PoolExamplePages = Enumeration('PoolExamplePages', 
        ('IntroPage', 'TangoPage', 'SardanaPage', 'PoolPage'))

    class PoolExampleIntroPage(wiz.SardanaIntroBasePage):

        def setNextPageId(self, id):
            self._nextPageId = id
        
        def nextId(self):
            return self._nextPageId

    from tango_host_page import SelectTangoHostBasePage

    class SelectTangoHostExamplePage(SelectTangoHostBasePage):

        def setNextPageId(self, id):
            self._nextPageId = id
        
        def nextId(self):
            return self._nextPageId
        
    from sardana_page import SelectSardanaBasePage

    class SelectSardanaExamplePage(SelectSardanaBasePage):

        def setNextPageId(self, id):
            self._nextPageId = id
        
        def nextId(self):
            return self._nextPageId
    
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(wiz.get_resources())
    
    w = wiz.SardanaBaseWizard()

    intro = PoolExampleIntroPage()
    w.setPage(PoolExamplePages.IntroPage, intro)

    curr_page = intro
    if tg_host is None:
        curr_page.setNextPageId(PoolExamplePages.TangoPage)
        tg_host_page = SelectTangoHostExamplePage()
        w.setPage(PoolExamplePages.TangoPage, tg_host_page)
        curr_page = tg_host_page
    else:
        w['db'] = lambda : tau.Database(tg_host)

    if sardana is None:
        curr_page.setNextPageId(PoolExamplePages.SardanaPage)
        sardana_page = SelectSardanaExamplePage()
        w.setPage(PoolExamplePages.SardanaPage, sardana_page)
        curr_page = sardana_page
    else:
        w['sardana'] = lambda : sardana

    curr_page.setNextPageId(PoolExamplePages.PoolPage)
    
    pool_page = SelectPoolBasePage(selectionMode=PoolSelectionMode.FromSardana)

    w.setPage(PoolExamplePages.PoolPage, pool_page)
    
    w.show()
    sys.exit(app.exec_())
    
def main():
    tg_host, sardana = None, None
    if len(sys.argv) >1:
        tg_host = sys.argv[1]
    if  len(sys.argv) >2:
        sardana = sys.argv[2]
    t1(tg_host=tg_host,sardana=sardana)

if __name__ == '__main__':
    main()


