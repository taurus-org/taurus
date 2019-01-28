# -*- coding: utf-8 -*-

##############################################################################
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
##############################################################################

"""
This module provides a simple HTML help browser.
"""

__all__ = ["HelpPanel"]

from taurus.external.qt import Qt
from taurus.external.qt import QtHelp


class _HelpBrowser(Qt.QTextBrowser):

    def __init__(self, help_engine=None, parent=None):
        Qt.QTextBrowser.__init__(self, parent)
        self.__help_engine = None
        if help_engine:
            self.setHelpEngine(help_engine)

    def setHelpEngine(self, help_engine):
        self.__help_engine = help_engine
        content_widget = help_engine.contentWidget()
        index_widget = help_engine.indexWidget()
        content_widget.linkActivated.connect(self.setSource)
        index_widget.linkActivated.connect(self.setSource)

    def loadResource(self, type, url):
        if url.scheme() == "qthelp":
            if self.__help_engine:
                return self.__help_engine.fileData(url)
        return Qt.QTextBrowser.loadResource(self, type, url)


class HelpPanel(Qt.QWidget):
    """
    Simple widget to display application help system. Usage::

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.help import HelpPanel

        app = Qt.QApplication([])
        help_panel = HelpPanel()

        help_panel.setCollectionFile("help_file.qhc")
        help_panel.show()
        app.exec_()
    """

    def __init__(self, collection_file=None, parent=None):
        Qt.QWidget.__init__(self, parent)
        layout = Qt.QVBoxLayout(self)
        self.setLayout(layout)
        self.__help_engine = None
        if collection_file:
            self.setCollectionFile(collection_file)

    def __clear(self):
        layout = self.layout()
        while layout.count():
            layout.takeAt(0)
        self.__help_engine = None

    @Qt.Slot(str)
    def setCollectionFile(self, collection_file):
        """
        Displays the help from the specified collection file

        :param collection_file: the collection file name (.qhc)
        :type collection_file: str
        """

        self.__clear()
        if not collection_file:
            return
        help_engine = QtHelp.QHelpEngine(collection_file, self)
        if not help_engine.setupData():
            raise Exception("Help engine not available")
        layout = self.layout()
        self.__tab = tab = Qt.QTabWidget()
        self.__help_engine = help_engine
        content_widget = help_engine.contentWidget()
        index_widget = help_engine.indexWidget()
        tab.addTab(content_widget, "Contents")
        tab.addTab(index_widget, "Index")
        self.__help_browser = _HelpBrowser(help_engine, self)
        splitter = Qt.QSplitter(Qt.Qt.Horizontal)
        splitter.insertWidget(0, tab)
        splitter.insertWidget(1, self.__help_browser)
        layout.addWidget(splitter)

    def getCollectionFile(self):
        """
        Returns the name of the current collection file or empty
        string if no collection file is active

        :return: the name of the current collection file
        :rtype: str
        """
        if self.__help_engine:
            return self.__help_engine.collectionFile()
        return ""

    def resetCollectionFile(self):
        """
        Resets the collection file
        """
        self.setCollectionFile("")

    #: This property holds the current collection file name
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`HelpPanel.getCollectionFile`
    #:     * :meth:`HelpPanel.setCollectionFile`
    #:     * :meth:`HelpPanel.resetCollectionFile`
    #:
    collectionFile = Qt.Property("QString", getCollectionFile,
                                 setCollectionFile,
                                 resetCollectionFile)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {'group': 'Taurus Help',
                'icon': Qt.QIcon.fromTheme("help"),
                'module': 'taurus.qt.qtgui.help',
                'container': False}


def main():
    import sys
    app = Qt.QApplication([])
    help_panel = HelpPanel()
    if len(sys.argv) > 1:
        help_panel.setCollectionFile(sys.argv[1])
    help_panel.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
