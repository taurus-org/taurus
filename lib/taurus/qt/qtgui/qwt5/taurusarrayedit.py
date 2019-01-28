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
#############################################################################


from __future__ import absolute_import
from taurus.external.qt import Qt, compat
import taurus
import numpy

from taurus.qt.qtgui.container import TaurusWidget
from .arrayedit import ArrayEditor
from functools import partial

class TaurusArrayEditor(TaurusWidget):

    def __init__(self, parent=None, designMode=False):
        TaurusWidget.__init__(self, parent=parent, designMode=designMode)

        self._xAttr = None
        self._yAttr = None

        self._arrayEditor = ArrayEditor()
        self.fromFileBT = Qt.QPushButton('Read From File')
        self.toFileBT = Qt.QPushButton('Write To File')
        self.fromAttrBT = Qt.QPushButton('Read From Device')
        self.toAttrBT = Qt.QPushButton('Write To Device')

        self.fromAttrBT.setEnabled(False)
        self.toAttrBT.setEnabled(False)

        layout = Qt.QGridLayout(self)
        layout.addWidget(self._arrayEditor, 0, 0, 1, 4)
        layout.addWidget(self.fromFileBT, 1, 0)
        layout.addWidget(self.toFileBT, 1, 1)
        layout.addWidget(self.fromAttrBT, 1, 2)
        layout.addWidget(self.toAttrBT, 1, 3)

        self.fromFileBT.clicked.connect(self._onFromFile)
        self.toFileBT.clicked.connect(self.onToFile)
        self.fromAttrBT.clicked.connect(partial(self.onFromAttr, quiet=False))
        self.toAttrBT.clicked.connect(partial(self.onToAttr, quiet=False))

    def arrayEditor(self):
        return self._arrayEditor

    def setModel(self, model):
        '''returns True if a curve could be set from the attribute. Flase otherwise'''
        if not model:
            self._xAttr = self._yAttr = None
            self.fromAttrBT.setEnabled(False)
            return
        attrs = str(model).split("|")
        self._yAttr = taurus.Attribute(attrs[-1])
        if self._yAttr is None or len(attrs) not in (1, 2):
            self.error('Invalid model for %s' % str(self.__class__))
            self.fromAttrBT.setEnabled(False)
            return
        if len(attrs) == 1:
            self._xAttr = None
        else:
            self._xAttr = taurus.Attribute(attrs[0])

        # set the master curve from the attribute(s)
        ok = self.onFromAttr(quiet=True)

        # enable/disable the attribute I/O buttons
        self.fromAttrBT.setEnabled(True)
        enableWrite = (self._xAttr is None or self._xAttr.isWritable()
                       ) and self._yAttr.isWritable()
        self.toAttrBT.setEnabled(True)

        return ok

    def _onFromFile(self):
        """dummy, just to be used as an unambiguous slot"""
        self.onFromFile()

    def onFromFile(self, filename=None, **kwargs):
        '''imports Master curve from a two-column ASCII file.
        The first colum will be interpreted to be the abcissas.
        If filename is not given, a dialog for choosing a file is presented
        kwargs can contain keyword arguments to pass to numpy.loadtxt() when reading each file
        accepted keywords and their default values are:
        {dtype=<type 'float'>, comments='#', delimiter=None, converters=None,
        skiprows=0, usecols=None, unpack=False}
        see help from numpy.loadtxt for more info on the kwargs'''
        if filename is None:
            filename, _ = compat.getOpenFileName(
                self, 'Choose input file', '', 'Ascii file (*)')
        if not filename:
            return False
        filename = str(filename)
        try:
            M = numpy.loadtxt(filename, **kwargs)
            if len(M.shape) != 2:
                raise Exception()
            x = M[:, 0]
            y = M[:, 1]
        except:
            self.error('Invalid input file "%s"' % filename)
            Qt.QMessageBox.warning(
                self, 'Invalid input file', 'Unknown format in selected file.\n Hint: The file must be two-column ASCII')
            return
        self._arrayEditor.setMaster(x, y)

    def onToFile(self):
        '''writes the Corrected curve to an ascii file'''
        if self._arrayEditor.plot1.exportAscii(curves=['Corrected']):
            x, y = self._arrayEditor.getCorrected()
            self._arrayEditor.setMaster(x, y, keepCP=True)

    def onFromAttr(self, quiet=False):
        '''reads the Master curve from the attributes set by model.
        '''
        if self._yAttr is None:
            return False  # @TODO: launch a dialog for choosing the x and y attributes
        try:
            y = numpy.array(self._yAttr.read().rvalue)
            if self._xAttr is None:
                x = numpy.arange(y.size)
            else:
                x = numpy.array(self._xAttr.read().rvalue)
        except Exception as e:
            self.error('Error reading from attribute(s): %s' % (str(e)))
            if not quiet:
                Qt.QMessageBox.warning(
                    self, 'Error Reading Attribute', 'Cannot read master curve')
            return False

        if quiet:
            should_set = True
        else:
            answer = Qt.QMessageBox.question(
                    self, 'Read from attributes?',
                    'Read Master curve from attributes?',
                    Qt.QMessageBox.Yes|Qt.QMessageBox.No
            )
            should_set = (answer == Qt.QMessageBox.Yes == answer)

        if should_set:
            try:
                self._arrayEditor.setMaster(x, y)
            except ValueError:
                self.error('Cannot set master curve from attributes')
                if not quiet:
                    Qt.QMessageBox.warning(self, 'Error',
                            'Cannot set master curve from attributes')
                return False
        return True

    def onToAttr(self, quiet=False):
        '''writes the Corrected curve to the attributes set by the model'''
        if self._yAttr is None:
            return  # @TODO: launch a dialog for choosing the x and y attributes
        x, y = self._arrayEditor.getCorrected()
        try:
            self._yAttr.write(y)
            if self._xAttr is not None:
                self._xAttr.write(x)
            # checking that the write was actually ok (this should be changed
            # when taurus provides a mechanism for this)
            if numpy.any(self._yAttr.read(cache=False).wvalue != y):
                raise IOError('Unexpected Write error: %s' %
                              self._yAttr.getFullName())
            if self._xAttr is not None and numpy.any(self._xAttr.read(cache=False).wvalue != x):
                raise IOError('Unexpected Write error: %s' %
                              self._xAttr.getFullName())
        except Exception as e:
            self.error('Error writing to attribute(s): %s' % (str(e)))
            if not quiet:
                Qt.QMessageBox.warning(
                    self, 'Error Writing attribute', 'Cannot write corrected curve to attribute')
            return
        self._arrayEditor.setMaster(x, y, keepCP=True)
        if not quiet:
            Qt.QMessageBox.information(
                self, 'Success', 'Corrected curve has been written')

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """Returns pertinent information in order to be able to build a valid
        QtDesigner widget plugin

        :return: (dict) a map with pertinent designer information"""
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.qwt5'
        ret['group'] = 'Taurus Input'
        ret['icon'] = 'designer:arrayedit.png'
        ret['container'] = False
        return ret
