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

"""This is an experimental property parser"""

from __future__ import print_function
from builtins import str

import os
import ply.lex as lex
import ply.yacc as yacc
from .containers import CaselessDict
from .log import Logger

reserved = CaselessDict({
    'true': 'true',
    'false': 'false',
    'yes': 'yes',
    'no': 'no'
})

tokens = ['EQUALS',
          'KEY',
          'STRING',
          'NUMBER',
          'COMMA',
          'LLST', 'RLST',
          #'LBRACKET', 'RBRACKET',
          ] + list(reserved.values())

t_EQUALS = r'\='
t_LLST = r'\['
t_RLST = r'\]'
t_COMMA = r'\,'
#t_LBRACKET = r'\{'
#t_RBRACKET = r'\}'


def t_NUMBER(t):
    r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
    try:
        if t.value.count('.') == 0:
            try:
                t.value = int(t.value)
            except:
                t.value = float(t.value)
        else:
            t.value = float(t.value)
    except:
        print("[%d]: Number %s is not valid!" % (t.lineno, t.value))
        t.value = 0
    return t

# The following backslash sequences have their usual special meaning: \",
# \\, \n, and \t.


def t_STRING(t):
    r'\"([^\\"]|(\\.))*\"'
    escaped = 0
    str = t.value[1:-1]
    new_str = ""
    for i in range(0, len(str)):
        c = str[i]
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = 0
        else:
            if c == "\\":
                escaped = 1
            else:
                new_str += c
    t.value = new_str
    return t


def t_KEY(t):
    r'[a-zA-Z0-9/_\.\/]+'
    t.type = reserved.get(t.value, 'KEY')    # Check for reserved words
    return t


# Ignored characters
t_ignore = ' \t'

t_ignore_COMMENT = r'\#.*'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("[%d]: Illegal character '%s'" % (t.lexer.lineno, t.value[0]))
    t.lexer.skip(1)


def p_error(p):
    print("[%d]: Syntax error in input [%s]" % (p.lineno, (str(p))))

#-------------------------------------------------------------------------
# Yacc Starting symbol
#-------------------------------------------------------------------------


def p_property_file(p):
    '''property_file : statement_list
                     |'''
    if len(p) == 1:
        p[0] = {}
    else:
        p[0] = p[1]


def p_statement_list(p):
    '''statement_list : statement_list statement'''
    p[1].update(p[2])
    p[0] = p[1]


def p_statement(p):
    '''statement_list : statement'''
    p[0] = p[1]


def p_statement_assign(p):
    '''statement : KEY EQUALS value'''
    p[0] = {p[1]: p[3]}


def p_value(p):
    '''value : atomic
             | list'''
    p[0] = p[1]


def p_value_atomic(p):
    '''atomic : KEY
              | STRING
              | NUMBER
              | boolean'''
    p[0] = p[1]


def p_value_boolean(p):
    '''boolean : true
               | false
               | yes
               | no'''
    v = p[1].lower()
    p[0] = v in ('true', 'yes')


def p_value_list(p):
    '''list : LLST value_list RLST'''
    p[0] = p[2]


def p_value_list_elems1(p):
    '''value_list : value_list COMMA value'''
    p[0] = p[1] + [p[3]]


def p_value_list_elems2(p):
    '''value_list : value'''
    p[0] = [p[1]]


class PropertyParser(Logger):

    def __init__(self, parent=None):
        name = self.__class__.__name__
        self.call__init__(Logger, name, parent)
        self._last_filename = None

    def parse_file(self, f, logger=None, debug=0, optimize=1):
        self._last_filename = os.path.abspath(f.name)

        kw = {
            'debuglog': logger or self,
            'errorlog': logger or self,
            'debug': debug,
            'optimize': optimize,
        }

        kw_lex = kw.copy()
        kw_lex.update({'lextab': 'property_lextab'})
        kw_yacc = kw.copy()
        kw_yacc.update({'tabmodule': 'property_yacctab'})
        lexer = lex.lex(**kw_lex)
        parser = yacc.yacc(**kw_yacc)

        if debug:
            debug = self
        return parser.parse(f.read(), debug=debug, lexer=lexer)

    def parse(self, filename, logger=None, debug=0, optimize=1):
        filename = os.path.realpath(filename)
        f, res = None, None
        try:
            f = open(filename)
            res = self.parse_file(
                f, logger=logger, debug=debug, optimize=optimize)
            f.close()
        except IOError as e:
            if f:
                f.close()
            raise
        return res

    def getLastFilename(self):
        return self._last_filename

if __name__ == '__main__':
    import sys
    pp = PropertyParser()
    res = pp.parse(sys.argv[1])
    print(res)
