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
from __future__ import division
from builtins import map
from builtins import range
from builtins import object
from past.utils import old_div
from functools import reduce

__all__ = ["Table"]

__docformat__ = "restructuredtext"


class Table(object):

    DefTermWidth = 80

    PrettyOpts = {'col_sep': ' |', 'col_head_sep': '-', 'border': '='}

    def __init__(self, elem_list, elem_fmt=None, term_width=None,
                 row_head_str=None, row_head_fmt='%-*s', row_head_width=None,
                 col_head_str=None, col_head_fmt='%*s',  col_head_width=None,
                 col_sep=' ', row_sep=' ', col_head_sep=None, border=None):

        self.nr_col = len(elem_list)
        self.nr_row = len(elem_list[0])
        self.elem_list = elem_list

        if elem_fmt is None:
            elem_fmt = self.nr_row * ['%*s']
        if len(elem_fmt) == 1:
            elem_fmt *= self.nr_row
        self.elem_fmt = elem_fmt

        self.term_width = term_width or Table.DefTermWidth
        self.col_sep = col_sep
        self.row_sep = row_sep
        self.col_head_sep = col_head_sep
        self.border = border

        max_len_fn = lambda x: reduce(max, list(map(len, x)))

        self.row_head_str = row_head_str
        self.row_head_fmt = row_head_fmt
        if row_head_str is not None and len(row_head_str) != self.nr_row:
            msg = 'RowHeadStr nr (%d) and RowNr (%d) mistmatch' % \
                  (len(row_head_str), self.nr_row)
            raise ValueError(msg)
        if row_head_width is None:
            if row_head_str is not None:
                row_head_width = max_len_fn(row_head_str)
            else:
                row_head_width = 0
        self.row_head_width = row_head_width

        self.col_head_str = col_head_str
        self.col_head_fmt = col_head_fmt
        if col_head_str is not None and len(col_head_str) != self.nr_col:
            msg = 'ColHeadStr nr (%d) and ColNr (%d) mistmatch' % (
                  len(col_head_str), self.nr_col)
            raise ValueError(msg)
        if col_head_width is None:
            if col_head_str is not None:
                col_head_width = reduce(max, list(map(max_len_fn, col_head_str)))
            else:
                col_head_width = 10
        self.col_head_width = col_head_width
        if col_head_str is not None:
            self.col_head_lines = len(col_head_str[0])
        else:
            self.col_head_lines = 0

    def updateElem(self, elem_list):
        new_col, new_row = len(elem_list), len(elem_list[0])
        if new_col != self.nr_col or new_row != self.nr_row:
            raise 'Invalid new elem list size %dx%d, was %dx%d' % \
                  (new_col, new_row, self.nr_col, self.nr_row)
        self.elem_list = elem_list

    def genOutput(self, term_width=None):
        if term_width is None:
            term_width = self.term_width

        rhw, chw = self.row_head_width, self.col_head_width
        chl = self.col_head_lines
        lcs = len(self.col_sep)
        width = term_width - chw   # At least one disp column!
        if rhw > 0:
            width -= rhw + lcs
        disp_cols = old_div(width, (chw + lcs)) + 1
        tot_width = chw + (disp_cols - 1) * (chw + lcs)
        tot_rows = chl + self.nr_row
        if rhw > 0:
            tot_width += rhw + lcs

        output = []

        if self.row_head_str is not None:
            row_head = []
            fmt = self.row_head_fmt
            for head in [''] * chl + self.row_head_str:
                head = fmt % (rhw, head)
                row_head.append(head + self.col_sep)
        else:
            row_head = [''] * tot_rows

        for i in range(0, self.nr_col, disp_cols):
            if i > 0:
                nr_sep = old_div(tot_width, len(self.row_sep))
                output.append(self.row_sep * nr_sep)

            row_end = min(i + disp_cols, self.nr_col)
            line = list(row_head)
            for j in range(i, row_end):
                elem = self.elem_list[j]
                if chl:
                    col_head = self.col_head_str[j]
                    if j > i:
                        for k in range(tot_rows):
                            line[k] += self.col_sep
                    fmt = self.col_head_fmt
                    for k in range(chl):
                        line[k] += fmt % (chw, col_head[k])

                for k in range(self.nr_row):
                    fmt = self.elem_fmt[k]
                    line[chl + k] += fmt % (chw, elem[k])

            max_width = reduce(max, list(map(len, line)))
            if self.border is not None:
                nr_border = old_div(max_width, len(self.border))
                output.append(self.border * nr_border)
            for l in line[:chl]:
                output.append(l)
            if self.col_head_sep is not None:
                nr_sep = old_div(max_width, len(self.col_head_sep))
                output.append(self.col_head_sep * nr_sep)
            for l in line[chl:]:
                output.append(l)
            if self.border is not None:
                output.append(self.border * nr_border)

        return output
