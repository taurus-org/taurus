#!/usr/bin/env python

#############################################################################
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
###########################################################################

"""This package provides a dialog for graphically choosing a Taurus class"""
from __future__ import print_function
from future.builtins import str

from taurus.external.qt import Qt


__all__ = ["GraphicalChoiceDlg", "GraphicalChoiceWidget"]

__docformat__ = 'restructuredtext'


class GraphicalChoiceDlg(Qt.QDialog):
    '''
    A generic dialog for choosing among a set of choices which are presented as
    an array of, each with a given pixmap.

    The :meth:`getChoice` static method is provided for convenience so that the
    dialog can be invoked wit a single line::

        chosen,ok = GraphicalChoiceDlg.getChoice(parent, title, msg, choices, pixmaps, size, defpixmap, horizontalScrollBarPolicy, verticalScrollBarPolicy)
    '''

    def __init__(self, parent=None, designMode=False, choices=None, pixmaps=None, iconSize=128, defaultPixmap=None, horizontalScrollBarPolicy=Qt.Qt.ScrollBarAsNeeded, verticalScrollBarPolicy=Qt.Qt.ScrollBarAsNeeded):
        Qt.QDialog.__init__(self, parent)
        self._chosen = None
        self.setLayout(Qt.QVBoxLayout())
        self.label = Qt.QLabel('Click on your choice:')
        self.layout().addWidget(self.label)
        self._iconsArea = GraphicalChoiceWidget(parent=parent, designMode=designMode, choices=choices,
                                                pixmaps=pixmaps, iconSize=iconSize, defaultPixmap=defaultPixmap,
                                                horizontalScrollBarPolicy=horizontalScrollBarPolicy,
                                                verticalScrollBarPolicy=verticalScrollBarPolicy)
        self.layout().addWidget(self._iconsArea)
        self._iconsArea.choiceMade.connect(self.onChoiceMade)

    def setHorizontalScrollBarPolicy(self, policy):
        '''sets horizontal scrollbar policy of scrollArea'''
        return self._iconsArea.setHorizontalScrollBarPolicy(policy)

    def setVerticalScrollBarPolicy(self, policy):
        '''sets vertical scrollbar policy of scrollArea'''
        return self._iconsArea.setVerticalScrollBarPolicy(policy)

    def setMessage(self, msg):
        '''sets the text which is shown to the user in the dialog'''
        self.label.setText(msg)

    def onChoiceMade(self, chosen):
        '''slot called when the user chooses an option'''
        self.accept()

    def getChosen(self):
        '''
        returns the choice
        :return: (str)
        '''
        return self._iconsArea.getChosen()

    @staticmethod
    def getChoice(parent=None, title='', msg='', choices=None, pixmaps=None, iconSize=128, defaultPixmap=None, horizontalScrollBarPolicy=Qt.Qt.ScrollBarAsNeeded, verticalScrollBarPolicy=Qt.Qt.ScrollBarAsNeeded):
        '''
        Static method which launches a GraphicalChoiceDlg with the given options
        and returns the result

        :param parent: (QWidget) The parent of the dialog (it will be centered on it)
        :param title: (str) the text which is displayed in the title bar of the dialog
        :param msg: (str) the text which is shown to the user in the dialog,
                    above the choices.
        :param choices: (list<list>) a list of lists of strings to be used as
                        choices names. The (possibly sparse) 2D array defined by
                        the nested lists will be used to present the choices in
                        a grid. The choice names will be used as keys for pixmaps
        :param pixmaps: (dict<str,QPixmap>) dictionary mapping the choices text to
                        corresponding pixmap. If no valid pixmap is provided for
                        a given choice, the defaultPixmap will be used
        :param iconSize: (int) size of the icons to be displayed (128px by default)
        :param defaultPixmap: (QPixmap) Default Pixmap to use if none passed for a
                              given choice. No Pixmap will be used if None passed.
        :param horizontalScrollBarPolicy: (enum Qt.ScrollBarPolicy) defines the mode of the horizontal scroll bar.
                                          The default mode is ScrollBarAsNeeded.
        :param verticalScrollBarPolicy: (enum Qt.ScrollBarPolicy) defines the mode of the vertical scroll bar.
                                        The default mode is ScrollBarAsNeeded
        :return: (tuple<str,bool>) A tuple containing choice,ok. choice is the name of
                 the chosen option. ok is true if the user pressed OK and false
                 if the user pressed Cancel.
        '''
        dlg = GraphicalChoiceDlg(parent=parent, choices=choices, pixmaps=pixmaps, iconSize=iconSize,
                                 defaultPixmap=defaultPixmap, horizontalScrollBarPolicy=horizontalScrollBarPolicy,
                                 verticalScrollBarPolicy=verticalScrollBarPolicy)
        dlg.setWindowTitle(title)
        dlg.setMessage(msg)
        dlg.exec_()
        return dlg.getChosen(), (dlg.result() == dlg.Accepted)


class GraphicalChoiceWidget(Qt.QScrollArea):
    '''A widget that presents a 2D grid of buttons'''

    choiceMade = Qt.pyqtSignal('QString')

    def __init__(self, parent=None, designMode=False, choices=None, pixmaps=None, iconSize=128,
                 defaultPixmap=None, horizontalScrollBarPolicy=Qt.Qt.ScrollBarAsNeeded,
                 verticalScrollBarPolicy=Qt.Qt.ScrollBarAsNeeded):
        Qt.QScrollArea.__init__(self, parent)

        self._chosen = None
        self._iconSize = iconSize
        if defaultPixmap is None:
            defaultPixmap = Qt.QPixmap()
        self._defaultPixmap = defaultPixmap

        self.setFrameShape(Qt.QFrame.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(horizontalScrollBarPolicy)
        self.setVerticalScrollBarPolicy(verticalScrollBarPolicy)

        w = Qt.QWidget()
        self.gridLayout = Qt.QGridLayout()
        w.setLayout(self.gridLayout)
        self.setWidget(w)

        if choices is not None:
            self.setChoices(choices, pixmaps)
        elif designMode:
            from taurus.qt.qtgui.icon import getCachedPixmap
            pm = getCachedPixmap('logos:taurus.png')
            self.setChoices([['choice1', 'choice2'], ['choice3', 'choice4']],
                            dict(choice1=pm, choice2=pm, choice3=pm,
                                 choice4=pm))

    def setChoices(self, choices, pixmaps=None):
        '''
        sets the available options

        :param choices: (list<list>) a list of lists of strings to be used as
                        choices names. The (possibly sparse) 2D array defined by
                        the nested lists will be used to present the choices in
                        a grid. The choice names will be used as keys for pixmaps
        :param pixmaps: (dict<str,QPixmap>) dictionary mapping the choices text to
                        corresponding pixmap. If no valid pixmap is provided for
                        a given choice, a default pixmap will be used
        '''
        if pixmaps is None:
            pixmaps = {}
        for i, rowlist in enumerate(choices):
            for j, choice in enumerate(rowlist):
                self.setChoice(i, j, str(choice),
                               pixmap=pixmaps.get(choice, None))

    def setChoice(self, row, col, text, pixmap=None, tooltip=None):
        '''
        sets the option for a given row,column coordinate in the grid

        :param row: (int) row in the grid for this option
        :param col: (int) column in the grid for this option
        :param text: (str) name for this option
        :param pixmap: (QPixmap or None) If no valid pixmap is provided for
                        a given choice, the default one will be used
        :param tooltip: (str) tooltip for this option (if None given, the `text` is used)
        '''
        if not pixmap or pixmap is None or pixmap.isNull():
            pixmap = self._defaultPixmap
        if tooltip is None:
            tooltip = text
        button = Qt.QToolButton()
        button.setText(text)
        button.setIcon(Qt.QIcon(pixmap))
        button.setIconSize(Qt.QSize(self._iconSize, self._iconSize))
        button.setToolTip(tooltip)
        button.clicked.connect(self.onClick)
        self.gridLayout.addWidget(button, row, col, Qt.Qt.AlignCenter)
        # -------------------------------------------------------
        # Work around for https://bugs.kde.org/show_bug.cgi?id=345023
        # TODO: make better solution for this
        button._id = text  # <-- ugly monkey-patch!
        # -------------------------------------------------------

    def onClick(self):
        '''slot called when a button is clicked'''
        # -------------------------------------------------------
        # Work around for https://bugs.kde.org/show_bug.cgi?id=345023
        # TODO: make better solution for this
        # self._chosen = str(self.sender().text())  # <-- fails due to added "&"
        self._chosen = self.sender()._id  # <-- this was monkey-patched
        # -------------------------------------------------------
        self.choiceMade.emit(self._chosen)

    def getChosen(self):
        '''
        returns the choice
        :return: (str)
        '''
        return self._chosen

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """Returns pertinent information in order to be able to build a valid
        QtDesigner widget plugin

        The dictionary returned by this method should contain *at least* the
        following keys and values:
        - 'module' : a string representing the full python module name (ex.: 'taurus.qt.qtgui.base')
        - 'icon' : a string representing valid resource icon (ex.: 'designer:combobox.png')
        - 'container' : a bool telling if this widget is a container widget or not.

        This default implementation returns the following dictionary::

            { 'group'     : 'Taurus Widgets',
              'icon'      : 'logos:taurus.png',
              'container' : False }

        :return: (dict) a map with pertinent designer information"""
        return {
            'module': 'taurus.qt.qtgui.input',
            'group': 'Taurus Input',
            'icon': 'logos:taurus.png',
            'container': False}


#------------------------------------------------------------------------------

def testWidget():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    w = GraphicalChoiceWidget(None, True)
    w.show()
    sys.exit(app.exec_())


def main():
    import sys
    from taurus.qt.qtgui.icon import getCachedPixmap
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)

    pixmaps = {}
    choices = [['TaurusForm', 'TaurusTrend'], ['TaurusPlot', 'Qub']]
    for row in choices:
        for k in row:
            pixmaps[k] = getCachedPixmap('snapshot:%s.png' % k)

    print(GraphicalChoiceDlg.getChoice(parent=None, title='Panel chooser', msg='Choose the type of Panel:', choices=choices, pixmaps=pixmaps))

    sys.exit()


if __name__ == "__main__":
    main()
    # testWidget()
