from taurus.qt import Qt
from taurus.qt.qtgui.resource import getThemeIcon

class MyGUI(Qt.QMainWindow):
    
    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent)
        toolbar = self.addToolBar("Tools")
        open_icon = getThemeIcon("document-open")
        toolbar.addAction(open_icon, "Open HDF5", self.open_file)
        
    def open_file(self):
        fileName = Qt.QFileDialog.getOpenFileName(self, "Open HDF5", "/home/homer",
                                                  "HDF5 Files (*.h5)")
        # do something

if __name__ == "__main__":
    import sys
    app = Qt.QApplication(sys.argv)
    gui = MyGUI()
    gui.show()
    sys.exit(app.exec_())