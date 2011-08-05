import os, sys
from PyQt4 import QtGui, QtCore, Qt

import wiz

from tango_host_page import SelectTangoHostBasePage
from sardana_page import SelectSardanaBasePage
from pool_page import SelectPoolBasePage



def main():
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(wiz.get_resources())
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
