#############################################################################
##
## This file is part of Taurus
##
## http://taurus-scada.org
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

__all__ = ["PintValidator"]

from taurus.external.qt import Qt
from taurus.external.pint import (Quantity, DimensionalityError, UR)

class PintValidator(Qt.QValidator):
    """A QValidator for pint Quantities"""
    _top = None
    _bottom = None
    _unit = UR.parse_units('')
    _implicit = True

    @property
    def top(self):
        """
        :return: (Quantity or None) maximum acceptable or None if it should not
                 be enforced
        """
        return self._top

    def setTop(self, top):
        """
        Set maximum limit
        :param top: (Quantity or None) maximum acceptable value
        """
        self._top = Quantity(top)

    @property
    def unit(self):
        """
        :return: (str or None) base units or None if it should not
                 be enforced
        """
        return self._unit

    def setUnit(self, unit):
        """
        Set base unit
        :param unit: (str or None) str unit representation.
        """
        self._unit = unit

    @property
    def bottom(self):
        """
        :return: (Quantity or None) minimum acceptable or None if it should not
                 be enforced
        """
        return self._bottom

    def setBottom(self, bottom):
        """
        Set minimum limit
        :param bottom: (Quantity or None) minimum acceptable value
        """
        self._bottom = Quantity(bottom)

    def _validate(self, input, pos):
        """Reimplemented from :class:`QValidator` to validate if the input
        string is a representation of a quantity within the set bottom and top
        limits
        """
        try:
            q = Quantity(input)
        except:
            return Qt.QValidator.Intermediate, input, pos
        if q.dimensionless and self._implicit:
            q = Quantity(q.magnitude, self._unit)
        if self._unit.dimensionality != q.dimensionality:
            return Qt.QValidator.Intermediate, input, pos
        try:
            if self.bottom is not None and q < self.bottom:
                return Qt.QValidator.Intermediate, input, pos
            if self.top is not None and q > self.top:
                return Qt.QValidator.Intermediate, input, pos
        except DimensionalityError:
            return Qt.QValidator.Intermediate, input, pos
        return Qt.QValidator.Acceptable, input, pos

    def _validate_oldQt(self, input, pos):
        """Old Qt (v4.4.) -compatible implementation of validate"""
        state, _, pos =  self._validate(input, pos)
        return state, pos

    # select the appropriate implementation of validate. See:
    # https://www.mail-archive.com/pyqt@riverbankcomputing.com/msg26344.html
    validate = Qt.PYQT_QSTRING_API_1 and _validate_oldQt or _validate