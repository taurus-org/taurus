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
#############################################################################

"""
This module provides an icon catalog widget
"""

from __future__ import print_function

from builtins import str

import os
import click
import hashlib
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.input import GraphicalChoiceWidget
from taurus.qt.qtgui.icon import REGISTERED_PREFIXES, getCachedPixmap
from taurus.external.qt import Qt


class QIconCatalogPage(GraphicalChoiceWidget):
    """A widget that shows all icons available under a given searchPath prefix
    """

    def __init__(self, prefix, iconSize=24, columns=10):
        choices, pixmaps = self.__build_catalog(prefix, columns=columns)
        GraphicalChoiceWidget.__init__(self, choices=choices, pixmaps=pixmaps,
                                       iconSize=iconSize, defaultPixmap=None)

        spacer = Qt.QSpacerItem(0, 0, Qt.QSizePolicy.Expanding,
                                Qt.QSizePolicy.Expanding)

        self.gridLayout.addItem(spacer, self.gridLayout.rowCount(),
                                self.gridLayout.columnCount())

    def __build_catalog(self, prefix, columns=10):
        """explores paths registered under the given prefix and selects unique
        pixmaps (performs an md5 check to discard duplicated icon files)
        """
        pixmaps_hashed = {}
        hashes = {}

        for path in Qt.QDir.searchPaths(prefix):
            if not os.path.exists(path):
                print(" %s not found. Skipping.!" % path)
                continue

            for fname in os.listdir(path):
                abs_fname = os.path.join(path, fname)
                if not os.path.isfile(abs_fname):
                    continue
                md5 = self.__md5(abs_fname)
                choice = '%s:%s' % (prefix, fname)

                if md5 in hashes:
                    hashes[md5] += '\n%s\t(%s)' % (choice, abs_fname)
                else:
                    hashes[md5] = '%s\t(%s)' % (choice, abs_fname)
                    pixmap = getCachedPixmap(choice)
                    if not pixmap.isNull():
                        pixmaps_hashed[md5] = pixmap
        pixmaps = {}
        choices = []
        row = []
        for md5, choice in hashes.items():
            try:
                pixmaps[choice] = pixmaps_hashed[md5]
            except KeyError:
                continue
            row.append(choice)
            if len(row) > columns:
                choices.append(row)
                row = []
        if len(row) > 0:
            choices.append(row)

        return choices, pixmaps

    def __md5(self, fname):
        """
        Extracts md5 sum of a file

        :param fname: (str) path to file
        :return: md5 hash
        """
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def onClick(self):
        """Reimplemented :class:`GraphicalChoiceWidget`
        """
        # From all alternatives, extract the one with the shortest name
        # -------------------------------------------------------
        # Work around for https://bugs.kde.org/show_bug.cgi?id=345023
        # TODO: make better solution for this
        # self._chosen = str(self.sender().text())
        # it fails due to added "&"
        chosen = self.sender()._id  # <-- this was monkey-patched
        # -------------------------------------------------------

        alts = chosen.splitlines()
        alts = sorted(alts, key=lambda s: len(s.split()[0]))
        name, absname = alts[0].split()

        # Store chosen name and emit signal using name
        self._chosen = name
        self.choiceMade.emit(name)

        # show a message dialob with more info on the selected icon
        dlg = Qt.QMessageBox()
        dlg.setWindowTitle(name)
        text = 'You can access the selected icon as:\n%s\n\n' % name
        text += 'Or, by absolute name:\n%s\n\n' % absname
        if len(alts) > 1:
            text += 'Other alternative names:\n\n' + '\n\n'.join(alts[1:])
        dlg.setText(text)
        dlg.setIconPixmap(getCachedPixmap(name, size=128))
        dlg.exec_()


class QIconCatalog(Qt.QTabWidget):
    """
    A widget that shows a tab for each registered search path prefix.
    In each tab, all icons available for the corresponding prefix are displayed.
    Clicking on an icon provides info on how to use it from a taurus
    application.
    """

    iconSelected = Qt.pyqtSignal('QString')

    def __init__(self, parent=None):
        Qt.QTabWidget.__init__(self)
        nprefix = len(REGISTERED_PREFIXES)
        progress = Qt.QProgressDialog('Building icon catalog...', None,
                                      0, nprefix, self)

        progress.setWindowModality(Qt.Qt.WindowModal)

        for i, prefix in enumerate(sorted(REGISTERED_PREFIXES)):
            progress.setValue(i)
            page = QIconCatalogPage(prefix)
            page.choiceMade.connect(self.iconSelected)

            self.addTab(page, prefix)
        progress.setValue(nprefix)


@click.command('icons')
def icons_cmd():
    """Show the Taurus icon catalog"""
    import sys
    app = TaurusApplication(cmd_line_parser=None)
    w = QIconCatalog()
    w.setWindowTitle('Taurus Icon Catalog')
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    icons_cmd()
