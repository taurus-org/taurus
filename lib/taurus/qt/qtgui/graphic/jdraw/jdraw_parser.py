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

"""This module parses jdraw files"""

from __future__ import absolute_import

import os
import re

from ply import lex
from ply import yacc

from taurus.core.util.log import Logger


__all__ = ["new_parser", "parse"]

tokens = ('NUMBER', 'SYMBOL', 'LBRACKET', 'RBRACKET', 'TWOP', 'COMMA',
          'JDFILE', 'GLOBAL', 'JDLINE', 'JDRECTANGLE', 'JDROUNDRECTANGLE',
          'JDGROUP', 'JDELLIPSE', 'JDBAR', 'JDSWINGOBJECT', 'JDLABEL', 'JDPOLYLINE',
          'JDIMAGE', 'JDAXIS', 'JDSLIDER', 'JDSPLINE', 'TEXT',
          'true', 'false',
          )

t_LBRACKET = r'\{'
t_RBRACKET = r'\}'
t_TWOP = r'\:'
t_COMMA = r'\,'

t_TEXT = r'\"[^"]*\"'

reserved = {
    'JDFile': 'JDFILE',
    'Global': 'GLOBAL',
    'JDLine': 'JDLINE',
    'JDRectangle': 'JDRECTANGLE',
    'JDRoundRectangle': 'JDROUNDRECTANGLE',
    'JDGroup': 'JDGROUP',
    'JDEllipse': 'JDELLIPSE',
    'JDBar': 'JDBAR',
    'JDSwingObject': 'JDSWINGOBJECT',
    'JDLabel': 'JDLABEL',
    'JDPolyline': 'JDPOLYLINE',
    'JDImage': 'JDIMAGE',
    'JDAxis': 'JDAXIS',
    'JDSlider': 'JDSLIDER',
    'JDSpline': 'JDSPLINE',
    'true': 'true',
    'false': 'false',

}


def t_SYMBOL(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'SYMBOL')    # Check for reserved words
    return t


def t_NUMBER(t):
    r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
    try:
        t.value = float(t.value)
    except:
        t.lexer.log.info("[%d]: Number %s is not valid!" % (t.lineno, t.value))
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    t.lexer.log.info("[%d]: Illegal character '%s'" %
                     (t.lexer.lineno, t.value[0]))
    t.lexer.skip(1)


def p_error(p):
    p.lexer.log.error("[%d]: Syntax error in input [%s]" %
                      (p.lexer.lineno, (str(p))))

#-------------------------------------------------------------------------
# Yacc Starting symbol
#-------------------------------------------------------------------------


def p_jdfile(p):
    ''' jdfile :  JDFILE SYMBOL LBRACKET global element_list RBRACKET '''
    factory = p.parser.factory
    p[0] = factory.getSceneObj(p[5])

    if p[0] is None:
        p.parser.log.info("[%d]: Unable to create Scene" % p.lexer.lineno)


def p_jdfile_empty(p):
    ''' jdfile : JDFILE LBRACKET global RBRACKET '''
    factory = p.parser.factory
    p[0] = factory.getSceneObj([])

    if p[0] is None:
        p.parser.log.info("[%d]: Unable to create Scene" % p.lexer.lineno)


def p_global(p):
    ''' global : GLOBAL LBRACKET RBRACKET
               | GLOBAL LBRACKET parameter_list RBRACKET'''
    if len(p) == 4:
        p[0] = {}
    else:
        p[0] = p[3]


def p_element_list(p):
    '''element_list : element_list element '''
    if not p[2] is None:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]


def p_element(p):
    '''element_list : element '''
    p[0] = [p[1]]


def p_single_element(p):
    '''element : obj LBRACKET RBRACKET
               | obj LBRACKET parameter_list RBRACKET'''

    #elems = None
    if len(p) == 4:
        p[3] = {}

    # determine the model name
    org = name = p[3].get('name')

    # change name: if item has no name it should take the name of its nearest-named-parent
    # as no-name it is also considered any element with a name like a reserved
    # keyword or plain value
    keywords = ['JDGroup'] + [n.replace('JD', '') for n in reserved]
    if not name or name in keywords or re.match('[0-9]+$', name):
        #if re.match('[0-9]+$',name):  p[3]['mapvalue'] = name
        p[3]['name'] = name = ""
        # print '\t name is empty, checking stack: %s' % [str(s) for s in
        # reversed(p.parser.modelStack)]
        for model in reversed(p.parser.modelStack):
            if model and model not in keywords and not re.match('[0-9]+$', model):
                # print 'Setting Model %s to %s' % (model,p[1])
                p[3]['name'] = name = model
                break
    # print 'parser: %s => %s [%s]' % (org,name,p.parser.modelStack)
    extension = p[3].get("extensions")
    if p.parser.modelStack2:
        if extension is None:
            p[3]["extensions"] = p.parser.modelStack2[0]
        elif len(p.parser.modelStack2) == 2:
            extension.update(p.parser.modelStack2[0])
            p[3]["extensions"] = extension

    # create the corresponding element
    factory = p.parser.factory
    #p.parser.log.debug('ret = factory.getObj(%s,%s)'% (str(p[1]),str(p[3])))
    ret = factory.getObj(p[1], p[3])

    if ret is None:
        p.parser.log.info("[%d]: Unable to create obj '%s'" %
                          (p.lexer.lineno, p[1]))

    # clear the model stack
    # if name:
    p.parser.modelStack.pop()
    if extension:
        p.parser.modelStack2.pop()

    #extension = p[3].get("extensions")
    p[0] = ret


def p_obj(p):
    '''obj : JDLINE
           | JDRECTANGLE
           | JDROUNDRECTANGLE
           | JDGROUP
           | JDELLIPSE
           | JDBAR
           | JDSWINGOBJECT
           | JDLABEL
           | JDPOLYLINE
           | JDIMAGE
           | JDAXIS
           | JDSLIDER
           | JDSPLINE'''
    p[0] = p[1]


def p_parameter_list(p):
    '''parameter_list : parameter_list parameter'''
    p[0] = p[1]
    p[0].update(p[2])


def p_parameter(p):
    '''parameter_list : parameter'''
    p[0] = p[1]


def p_single_parameter(p):
    '''parameter : SYMBOL TWOP param_value'''
    # modelStacks added in this method control how extensions/models/names are
    # propagated within JDGroup items
    if p[1] == 'name':
        p.parser.modelStack.append(p[3])
    if p[1] == 'extensions':
        p.parser.modelStack2.append(p[3])
    p[0] = {p[1]: p[3]}


def p_complex_parameter(p):
    '''parameter : SYMBOL TWOP LBRACKET RBRACKET
                 | SYMBOL TWOP LBRACKET parameter_list RBRACKET
                 | SYMBOL TWOP LBRACKET element_list RBRACKET'''
    if len(p) == 5:
        p[4] = []
    p[0] = {p[1]: p[4]}
    if p[1] == 'extensions':
        p.parser.modelStack2.append(p[4])


def p_param_value_number_list(p):
    '''param_value : value_list '''
    if len(p[1]) == 1:
        p[0] = p[1][0]
    else:
        p[0] = p[1]


def p_value_list(p):
    ''' value_list : value_list COMMA value '''
    p[0] = p[1] + [p[3]]


def p_value_list_value(p):
    ''' value_list : value '''
    p[0] = [p[1]]


def p_value_number(p):
    '''value : NUMBER'''
    p[0] = p[1]


def p_value_text(p):
    '''value : TEXT'''
    p[0] = p[1].strip('"')


def p_value_bool(p):
    '''value : true
             | false'''
    p[0] = p[1] == 'true'


def new_parser(optimize=None, debug=0, outputdir=None):
    log = Logger('JDraw Parser')

    if optimize is None:
        from taurus import tauruscustomsettings
        optimize = getattr(tauruscustomsettings, 'PLY_OPTIMIZE', 1)
    if outputdir is None:
        # use '.taurus' dir in the user "home" dir
        outputdir = os.path.join(os.path.expanduser('~'), '.taurus')
        # create the output dir if it didn't exist
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

    debuglog = None
    if debug:
        debuglog = log

    common_kwargs = dict(optimize=optimize, outputdir=outputdir,
                         debug=debug, debuglog=debuglog, errorlog=log)

    # lex/yacc v<3.0 do not accept  debuglog or errorlog keyword args
    if int(lex.__version__.split('.')[0]) < 3:
        common_kwargs.pop('debuglog')
        common_kwargs.pop('errorlog')

    jdraw_lextab = 'jdraw_lextab'
    jdraw_yacctab = 'jdraw_yacctab'

    # Lexer
    l = lex.lex(lextab=jdraw_lextab, **common_kwargs)

    # Yacc
    try:
        p = yacc.yacc(tabmodule=jdraw_yacctab, debugfile=None, write_tables=1,
                      **common_kwargs)
    except Exception as e:
        msg = ('Error creating jdraw parser.\n' +
               'HINT: Try removing jdraw_lextab.* and jdraw_yacctab.* from %s' %
               outputdir)
        raise RuntimeError(msg)

    return l, p


def parse(filename=None, factory=None):

    if filename is None or factory is None:
        return

    _, p = new_parser()

    p.factory = factory
    p.modelStack = []
    p.modelStack2 = []

    res = None
    try:
        filename = os.path.realpath(filename)
        f = open(filename)
        res = yacc.parse(f.read())
    except:
        log = Logger('JDraw Parser')
        log.warning("Failed to parse %s" % filename)
        log.debug("Details:", exc_info=1)
    return res


if __name__ == "__main__":
    new_parser()
