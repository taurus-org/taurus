import os, sys
from PyQt4 import QtGui, QtCore, Qt

class SardanaBasePage(QtGui.QWizardPage):
    
    def __init__(self, parent = None):
        QtGui.QWizardPage.__init__(self, parent)
        self._item_funcs = {}
        
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/logo.jpg"))
    
        layout = QtGui.QVBoxLayout()
        
        self._panel = QtGui.QWidget()
        
        self._status_label = QtGui.QLabel()
        self._status_label.setAutoFillBackground(True)
        palette = self._status_label.palette()
        gradient = QtGui.QLinearGradient(0, 0, 0, 15)
        gradient.setColorAt(0.0, Qt.QColor.fromRgb( 60, 150, 255))
        gradient.setColorAt(0.5, Qt.QColor.fromRgb(  0,  85, 227))
        gradient.setColorAt(1.0, Qt.QColor.fromRgb( 60, 150, 255))
        gradient.setSpread(QtGui.QGradient.RepeatSpread)
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(gradient))
        palette.setBrush(QtGui.QPalette.WindowText, Qt.Qt.white)
        
        layout.addWidget(self._panel)
        layout.addStretch()
        layout.addWidget(self._status_label)
        self.setLayout(layout)

    def __setitem__(self, name, value):
        self._item_funcs[name] = value

    def __getitem__(self, name):
        return self._item_funcs[name]
        
    def setStatus(self, text):
        self._status_label.setText(text)

    def getPanelWidget(self):
        return self._panel


class SardanaIntroBasePage(QtGui.QWizardPage):
    
    def __init__(self, parent = None):
        QtGui.QWizardPage.__init__(self, parent)
    
        self.setTitle('Introduction')
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap(":/watermark.jpg"))
        
        label = QtGui.QLabel(self.getIntroText())
        label.setWordWrap(True)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        
    def getIntroText(self):
        return """This wizard will guide you through the Sardana configuration"""

class SardanaBaseWizard(QtGui.QWizard):

    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self._item_funcs = {}
        self._pages = {}

    def __setitem__(self, name, value):
        self._item_funcs[name] = value
        
    def __getitem__(self, name):
        for id in self.getPages():
            p = self.page(id)
            if isinstance(p, SardanaBasePage):
                try:
                    return p[name]()
                except Exception,e:
                    pass
        return self._item_funcs[name]()
        return None
        
    def addPage(self, page):
        id = QtGui.QWizard.addPage(self, page)
        self._pages[id] = page

    def setPage(self, id, page):
        QtGui.QWizard.setPage(self, id, page)
        self._pages[id] = page
        
    def getPages(self):
        return self._pages

def get_resources():
    res_fname = os.path.abspath(__file__)
    res_fname = os.path.splitext(res_fname)[0] + '.rcc'
    return res_fname

def t1():
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(get_resources())
    w = QtGui.QWizard()
    intro = SardanaBaseIntroPage()
    base1 = SardanaBasePage()
    base1.setTitle('Empty title')
    base1.setSubTitle('Empty sub-title')
    base1.setStatus("The status bar")
    w.addPage(intro)
    w.addPage(base1)
    w.show()
    sys.exit(app.exec_())

def main():
    t1()

if __name__ == "__main__":
    main()
