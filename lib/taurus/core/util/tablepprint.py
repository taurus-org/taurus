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

"""Adapted from http://code.activestate.com/recipes/267662/"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import str
from builtins import range
from functools import reduce
import operator
import re
import math

__docformat__ = "restructuredtext"


def indent(rows, hasHeader=False, headerChar='-', delim=' | ', justify='left',
           separateRows=False, prefix='', postfix='', wrapfunc=lambda x: x):
    """Indents a table by column.
    :param rows: A sequence of sequences of items, one sequence per row.
    :param hasHeader: True if the first row consists of the columns' names.
    :param headerChar: Character to be used for the row separator line
    (if hasHeader==True or separateRows==True).
    :param delim: The column delimiter.
    :param justify: Determines how are data justified in their column.
    Valid values are 'left','right' and 'center'.
    :param separateRows: True if rows are to be separated by a line of
    'headerChar's.
    :param prefix: A string prepended to each printed row.
    :param postfix: A string appended to each printed row.
    :param wrapfunc: A function f(text) for wrapping text;
    each element in the table is first wrapped by this function.
    :return: a list of strings. One for each row of the table
    """
    # closure for breaking logical rows to physical, using wrapfunc
    def rowWrapper(row):
        newRows = [wrapfunc(item).split('\n') for item in row]
        return [[substr or '' for substr in item] for item in list(*newRows)]

    # break each logical row into one or more physical ones
    logicalRows = [rowWrapper(row) for row in rows]
    # columns of physical rows

    columns = list(*reduce(operator.add, logicalRows))

    # get the maximum of each column by the string length of its items
    maxWidths = [max([len(str(item)) for item in column])
                 for column in columns]
    if separateRows or hasHeader:
        rowSeparator = headerChar * (len(prefix) + len(postfix) + sum(maxWidths) +
                                     len(delim) * (len(maxWidths) - 1))
    else:
        rowSeparator = "<ERR>"

    # select the appropriate justify method
    justify = {'center': str.center, 'right': str.rjust,
               'left': str.ljust}[justify.lower()]

    output = []
    if separateRows:
        output.append(rowSeparator)
    for physicalRows in logicalRows:
        for row in physicalRows:
            line = prefix
            line += delim.join([justify(str(item), width)
                                for (item, width) in zip(row, maxWidths)])
            line += postfix
            output.append(line)
        if separateRows or hasHeader:
            output.append(rowSeparator)
            hasHeader = False
    return output

# written by Mike Brown
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061


def wrap_onspace(text, width):
    """A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\\\\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line[line.rfind('\n') + 1:])
                          + len(word.split('\n', 1)[0]
                                ) >= width)],
                   word),
                  text.split(' ')
                  )


def wrap_onspace_strict(text, width):
    """Similar to wrap_onspace, but enforces the width constraint:
       words longer than width are split."""
    wordRegex = re.compile(r'\S{' + str(width) + r',}')
    return wrap_onspace(wordRegex.sub(lambda m: wrap_always(m.group(), width), text), width)


def wrap_always(text, width):
    """A simple word-wrap function that wraps text on exactly width characters.
       It doesn't split the text in words."""
    return '\n'.join([text[width * i:width * (i + 1)]
                      for i in range(int(math.ceil(1. * len(text) / width)))])

if __name__ == '__main__':
    labels = ('First Name', 'Last Name', 'Age', 'Position')
    data = \
        '''John,Smith,24,Software Engineer
       Mary,Brohowski,23,Sales Manager
       Aristidis,Papageorgopoulos,28,Senior Reseacher'''
    rows = [row.strip().split(',') for row in data.splitlines()]

    print('Without wrapping function\n')
    for l in indent([labels] + rows, hasHeader=True):
        print(l)

    # test indent with different wrapping functions
    width = 10
    for wrapper in (wrap_always, wrap_onspace, wrap_onspace_strict):
        print('Wrapping function: %s(x,width=%d)\n' % (wrapper.__name__, width))
        o = indent([labels] + rows, headerChar='=', hasHeader=True, separateRows=False,
                   prefix='|', postfix='|', delim=' ',
                   wrapfunc=lambda x: wrapper(x, width))
        for l in o:
            print(l)

    # output:
    #
    # Without wrapping function
    #
    # First Name | Last Name        | Age | Position
    #-------------------------------------------------------
    # John       | Smith            | 24  | Software Engineer
    # Mary       | Brohowski        | 23  | Sales Manager
    # Aristidis  | Papageorgopoulos | 28  | Senior Reseacher
    #
    # Wrapping function: wrap_always(x,width=10)
    #
    #----------------------------------------------
    #| First Name | Last Name  | Age | Position   |
    #----------------------------------------------
    #| John       | Smith      | 24  | Software E |
    #|            |            |     | ngineer    |
    #----------------------------------------------
    #| Mary       | Brohowski  | 23  | Sales Mana |
    #|            |            |     | ger        |
    #----------------------------------------------
    #| Aristidis  | Papageorgo | 28  | Senior Res |
    #|            | poulos     |     | eacher     |
    #----------------------------------------------
    #
    # Wrapping function: wrap_onspace(x,width=10)
    #
    #---------------------------------------------------
    #| First Name | Last Name        | Age | Position  |
    #---------------------------------------------------
    #| John       | Smith            | 24  | Software  |
    #|            |                  |     | Engineer  |
    #---------------------------------------------------
    #| Mary       | Brohowski        | 23  | Sales     |
    #|            |                  |     | Manager   |
    #---------------------------------------------------
    #| Aristidis  | Papageorgopoulos | 28  | Senior    |
    #|            |                  |     | Reseacher |
    #---------------------------------------------------
    #
    # Wrapping function: wrap_onspace_strict(x,width=10)
    #
    #---------------------------------------------
    #| First Name | Last Name  | Age | Position  |
    #---------------------------------------------
    #| John       | Smith      | 24  | Software  |
    #|            |            |     | Engineer  |
    #---------------------------------------------
    #| Mary       | Brohowski  | 23  | Sales     |
    #|            |            |     | Manager   |
    #---------------------------------------------
    #| Aristidis  | Papageorgo | 28  | Senior    |
    #|            | poulos     |     | Reseacher |
    #---------------------------------------------
