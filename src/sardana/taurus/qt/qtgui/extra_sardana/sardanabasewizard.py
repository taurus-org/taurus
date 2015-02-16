#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module contains sardana base wizard classes."""

__all__ = ["SardanaBaseWizard"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt


class SardanaBasePage(Qt.QWizardPage):

    def __init__(self, parent=None):
        Qt.QWizardPage.__init__(self, parent)
        self._item_funcs = {}

    def __setitem__(self, name, value):
        self._item_funcs[name] = value

    def __getitem__(self, name):
        return self._item_funcs[name]

    def getPanelWidget(self):
        return self._panel


class SardanaBaseWizard(Qt.QWizard):

    def __init__(self, parent=None):
        Qt.QWizard.__init__(self, parent)
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
                except Exception, e:
                    pass
        return self._item_funcs[name]()
        return None

    def addPage(self, page):
        id = Qt.QWizard.addPage(self, page)
        self._pages[id] = page

    def setPage(self, id, page):
        Qt.QWizard.setPage(self, id, page)
        self._pages[id] = page

    def getPages(self):
        return self._pages

