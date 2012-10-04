import sys, os

from PyQt4 import QtGui, QtCore, Qt

import taurus
import wiz

from taurus.core.utils import Enumeration
    
class SelectSardanaBasePage(wiz.SardanaBasePage):
    
    def __init__(self, parent = None):
        wiz.SardanaBasePage.__init__(self, parent)
        
        self['sardana'] = self._getSardana
        
        self.setSubTitle('Please select the Sardana instance')
        
        panel = self.getPanelWidget()
        
        layout = QtGui.QFormLayout()
        
        self.sardanaCB = QtGui.QComboBox(panel)
        self.sardanaCB.setDuplicatesEnabled(False)
        self.sardanaCB.setEditable(False)

        layout.addRow("&Sardana instance", self.sardanaCB)

        panel.setLayout(layout)

        self.connect(self.sardanaCB, 
                     QtCore.SIGNAL('currentIndexChanged(int)'), 
                     QtCore.SIGNAL('completeChanged()'))
        
    def _getSardana(self):
        sardana = str(self.sardanaCB.currentText())
        return sardana

    def sardana(self):
        return self.wizard()['sardana']
    
    def db(self):
        return self.wizard()['db']
    
    def isComplete(self):
        idx = self.sardanaCB.currentIndex()
        if idx >= 0:
            self.setStatus('')
            return True
        self.setStatus('No instance selected')
        return False
    
    def _fillCB(self):
        self.sardanaCB.clear()
        db = self.db()
        services = db.get_service_list('Sardana.*')
        service_instances = []
        for service in services:
            service_instances.append(service.split('/', 1)[1])
        self.sardanaCB.addItems(service_instances)
            
    def initializePage(self):
        wiz.SardanaBasePage.initializePage(self)
        self._fillCB()

def t1(tg_host=None):

    SardanaExamplePages = Enumeration('SardanaExamplePages', ('IntroPage', 'TangoPage', 'SardanaPage'))

    class SardanaExampleIntroPage(wiz.SardanaIntroBasePage):

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
        
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(wiz.get_resources())
    
    w = wiz.SardanaBaseWizard()

    intro = SardanaExampleIntroPage()
    w.setPage(SardanaExamplePages.IntroPage, intro)
    
    curr_page = intro
    if tg_host is None:
        curr_page.setNextPageId(SardanaExamplePages.TangoPage)
        from tango_host_page import SelectTangoHostBasePage
        tg_host_page = SelectTangoHostBasePage()
        w.setPage(SardanaExamplePages.TangoPage, tg_host_page)
        curr_page = tg_host_page
    else:
        w['db'] = lambda : taurus.Database(tg_host)

    curr_page.setNextPageId(SardanaExamplePages.SardanaPage)
    sardana_page = SelectSardanaBasePage()
    w.setPage(SardanaExamplePages.SardanaPage, sardana_page)
    
    w.show()
    sys.exit(app.exec_())
    
def main():
    import taurus
    taurus.setLogLevel(taurus.Warning)
    tg_host=None
    if len(sys.argv) >1:
        tg_host = sys.argv[1]
    t1(tg_host=tg_host)

if __name__ == '__main__':
    main()


