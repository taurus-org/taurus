import sys, os

from PyQt4 import QtGui, QtCore, Qt

import taurus
import wiz

def get_default_tango_host():
    tg = os.environ.get('TANGO_HOST','')
    if not tg or tg.count(':') != 1: return '',''
    return tg.split(':')

class SelectTangoHostBasePage(wiz.SardanaBasePage):
    
    def __init__(self, parent = None):
        wiz.SardanaBasePage.__init__(self, parent)
        
        self.setSubTitle('Please select the Tango Host')
        
        panel = self.getPanelWidget()
        layout = QtGui.QFormLayout()
        self.hostEdit = QtGui.QLineEdit()
        self.portEdit = QtGui.QLineEdit()

        layout.addRow("&Host", self.hostEdit)
        layout.addRow("&Port", self.portEdit)

        host, port = get_default_tango_host()
        
        self.hostEdit.setText(host)
        self.portEdit.setText(port)
        
        panel.setLayout(layout)

        self['db'] = self._getDatabase
        
        self.connect(self.hostEdit, 
                     QtCore.SIGNAL('textEdited(const QString &)'), 
                     QtCore.SIGNAL('completeChanged()'))
        self.connect(self.portEdit, 
                     QtCore.SIGNAL('textEdited(const QString &)'), 
                     QtCore.SIGNAL('completeChanged()'))
                         
    def _getDatabase(self):
        host = str(self.hostEdit.text()).lower()
        port = str(self.portEdit.text())
        return taurus.Database("%s:%s" % (host, port))

    def db(self):
        return self.wizard()['db']
        
    def isComplete(self):
        try:
            db = self.db()
            if not db is None:
                self.setStatus('')
                return True
        except Exception, e:
            pass
        self.setStatus('Invalid database')
        return False
        
def t1():
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(wiz.get_resources())
    w = wiz.SardanaBaseWizard()
    intro = wiz.SardanaIntroBasePage()
    tg_host_page = SelectTangoHostBasePage()
    w.addPage(intro)
    w.addPage(tg_host_page)
    w.show()
    sys.exit(app.exec_())

def main():
    t1()

if __name__ == '__main__':
    main()


