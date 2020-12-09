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

""" """

from __future__ import absolute_import
from future.utils import string_types

from builtins import map
from builtins import range
import textwrap
try:
    from collections.abc import Sequence
except ImportError:  # bck-compat py 2.7
    from collections import Sequence
from future.utils import string_types
from .enums import Alignment


__all__ = ["List"]
__docformat__ = "restructuredtext"


class List(list):

    HeaderSeparator = "-"
    RowSeparator = None

    MaxColumnWidth = -1
    TextAlignment = Alignment.Right | Alignment.Top

    def __init__(self, header, header_separator=HeaderSeparator,
                 row_separator=RowSeparator,
                 max_col_width=MaxColumnWidth,
                 text_alignment=TextAlignment):

        self.col_nb = col_nb = len(header)
        self.cur_col_width = col_nb * [0]

        self.header_separator = header_separator
        self.row_separator = row_separator
        self.max_column_width = max_col_width
        self.text_alignment = text_alignment

        if header is not None:
            self.append(header)

    def setHeaderSeparator(self, header_separator):
        if isinstance(header_separator, string_types):
            header_separator = self.col_nb * [header_separator]
        self.HeaderSeparator = header_separator

    def getHeaderSeparator(self):
        return self.HeaderSeparator

    header_separator = property(getHeaderSeparator, setHeaderSeparator)

    def setRowSeparator(self, row_separator):
        if isinstance(row_separator, string_types):
            row_separator = self.col_nb * [row_separator]
        self.RowSeparator = row_separator

    def getRowSeparator(self):
        return self.RowSeparator

    row_separator = property(getRowSeparator, setRowSeparator)

    def setMaxColumnWidth(self, max_col_width):
        if max_col_width is None:
            max_col_width = -1
        if not isinstance(max_col_width, Sequence):
            max_col_width = self.col_nb * [max_col_width]
        self.MaxColumnWidth = max_col_width

    def getMaxColumnWidth(self):
        return self.MaxColumnWidth

    max_column_width = property(getMaxColumnWidth, setMaxColumnWidth)

    def setTextAlignment(self, text_alignment):
        if not isinstance(text_alignment, Sequence):
            text_alignment = self.col_nb * [text_alignment]
        self.TextAlignment = text_alignment

    def getTextAlignment(self):
        return self.TextAlignment

    text_alignment = property(getTextAlignment, setTextAlignment)

    def _transform_row(self, row):
        return list(map(str, row[:self.col_nb]))

    def __setitem__(self, i, row):
        return list.__setitem__(self, i, self._transform_row(row))

    def append(self, row):
        return list.append(self, self._transform_row(row))

    appendRow = append

    def putRow(self, row, idx):
        self[idx] = row

    def _calc_column_widths(self):
        cur_col_width, max_col_width = self.cur_col_width, self.MaxColumnWidth

        for row_index, row in enumerate(self):
            for column_index, cell in enumerate(row):
                size = len(cell) + 3
                col_width = cur_col_width[column_index]
                max_width = max_col_width[column_index]
                if size > col_width:
                    col_width = size
                if max_width >= 0:
                    col_width = min(max_width, col_width)
                cur_col_width[column_index] = col_width

    def genOutput(self):
        return self.lines()

    def _get_separator_row(self, separator):
        columns = []
        for i, width in enumerate(self.cur_col_width):
            if isinstance(separator[i], string_types):
                column = " " + (width - 1) * separator[i]
            else:
                column = " " + separator[i][:width - 1]
            columns.append(column)
        return "".join(columns)

    def lines(self):
        self._calc_column_widths()
        cur_col_width = self.cur_col_width
        alignment = self.TextAlignment
        ret = []
        wrapper = textwrap.TextWrapper()
        for row_index, row in enumerate(self):
            row_nb = 0
            text_columns = []
            for column_index, cell in enumerate(row):
                align = alignment[column_index]
                width = cur_col_width[column_index]
                wrapper.width = width - 3
                cells = wrapper.wrap(cell)
                for i, c in enumerate(cells):
                    if align & Alignment.Left:
                        cells[i] = " " + c.ljust(width - 1)
                    elif align & Alignment.Right:
                        cells[i] = c.rjust(width)
                    elif align & Alignment.HCenter:
                        cells[i] = c.center(width)
                row_nb = max(len(cells), row_nb)
                text_columns.append(cells)

            text_rows = row_nb * ['']
            for column_index, cells in enumerate(text_columns):
                for i in range(row_nb):
                    if i < len(cells):
                        text_rows[i] = text_rows[i] + cells[i]
                    else:
                        width = cur_col_width[column_index]
                        text_rows[i] = text_rows[i] + width * " "
            ret.extend(text_rows)
            if row_index > 0 and self.row_separator is not None:
                ret.append(self._get_separator_row(self.RowSeparator))

        if self.header_separator is not None:
            ret.insert(1, self._get_separator_row(self.HeaderSeparator))
        return ret

    def str(self):
        return "\n".join(self.lines())

    def __str__(self):
        return self.str()
