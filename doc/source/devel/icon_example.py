from taurus.external.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication


class MyGUI(Qt.QMainWindow):

    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent)
        toolbar = self.addToolBar("Tools")

        # get icon from theme
        icon1 = Qt.QIcon.fromTheme("document-open")

        # get icon using prefix + filename
        icon2 = Qt.QIcon("actions:exit.svg")

        toolbar.addAction(icon1, "Open HDF5", self.open_file)
        toolbar.addAction(icon2, "Exit", self.close)


    def open_file(self):
        pass   # do something

if __name__ == "__main__":
    import sys
    app = TaurusApplication(cmd_line_parser=None)
    gui = MyGUI()
    gui.show()
    sys.exit(app.exec_())
