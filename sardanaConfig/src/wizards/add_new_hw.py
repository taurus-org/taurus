import os, sys
from PyQt4 import QtGui, QtCore, Qt

import wiz



def main():
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(wiz.get_resources())
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
