#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
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

"""The macro submodule."""

__all__ = ["MacroInfo", "Macro", "MacroNode", "ParamFactory",
           "MacroRunException"]

__docformat__ = 'restructuredtext'

import os
import tempfile
import types
import operator
import copy
import threading
import PyTango

from lxml import etree

from taurus.core.util.user import USER_NAME
from taurus.core.util.codecs import CodecFactory

class MacroRunException(Exception):
    pass

class MacroInfo(object):
    """Contains all information about a macro: name, documentation, parameters, 
    result, etc"""
    
    def __init__(self, from_json_str=None, from_json=None):
        json_obj = from_json
        if from_json_str is not None:
            json_obj = self._fromJSON(from_json_str)
        
        if json_obj:
            self.__dict__.update(json_obj)
            self._buildDoc()
    
    def _fromJSON(self, json_str):
        json_codec = CodecFactory().getCodec('json')
        format, data = json_codec.decode(('json', json_str))
        return data
    
    def _buildDoc(self):
        if self.hasParams():
            self._parameter_line = self._buildParameterLine(self.parameters)
            self._parameter_description = self._buildParameterDescription(self.parameters)
        if self.hasResult():
            self._result_line = self._buildResultLine(self.result)
            self._result_description = self._buildResultDescription(self.result)
            
        doc = 'Syntax:\n\t%s %s' % (self.name, self.getParamStr())
        if self.hasResult():
            doc += ' -> ' + self.getResultStr()
        doc += '\n\n'
        doc += self.description
        if self.hasParams():
            doc += '\n\nParameters:\n\t'
            doc += '\n\t'.join(self.getParamDescr())
        if self.hasResult():
            doc += '\n\nResult:\n\t'
            doc += '\n\t'.join(self.getResultDescr())
        self.doc = doc

    def _hasParamComplex(self, parameters=None):
        if parameters is None:
            parameters = self.parameters
        
        for p in parameters:
            if self._isParamComplex(p):
                return True
        return False
    
    def _isParamComplex(self, p):
        return not self._isParamAtomic(p)
    
    def _isParamAtomic(self, p):
        return type(p['type']) in types.StringTypes
    
    def _buildParameterLine(self, parameters):
        l = []
        for p in parameters:
            t = p['type']
            if type(t) in types.StringTypes:
                #Simple parameter
                l.append('<%s>' % p['name'])
            else:
                l.append('[ %s ]' % self._buildParameterLine(t))
        return ' '.join(l)
    
    _buildResultLine = _buildParameterLine
    
    def _buildParameterDescription(self, parameters):
        l = []
        for p in parameters:
            t = p['type']
            if type(t) in types.StringTypes:
                #Simple parameter
                l.append('{name} : ({type}) {description}'.format(**p))
            else:
                l.extend(self._buildParameterDescription(t))
        return l
    
    _buildResultDescription = _buildParameterDescription

    def hasParams(self):
        """Determines if the macro has parameters
        
        :return: (bool) True if the macro has parameters or False otherwise
        """
        return hasattr(self ,'parameters')
    
    def getParamList(self):
        """Returs the list of parameters
        
        :return: (sequence) a list of parameters
        """
        if not self.hasParams():
            return []
        return self.parameters
            
    def getParam(self,idx=0):
        """Gets the parameter for the given index
        
        :param idx: (int) the index (default is 0)
        
        :return: (object) the parameter or None if the macro does not have the 
                 desired parameter
        """
        if not self.hasParams():
            return
        return self.parameters[idx]

    def getPossibleParams(self, idx, parameters=None):
        """Gets the possible parameters for the given index
        
        :param idx: (int) parameter index
        :param parameters: (sequence) sequence of parameter information (default 
                           is None which means use the macro parameters
        :return: (sequence) list of possible parameters
        """
        if parameters is None:
            parameters = self.parameters
        
        res = []
        n = len(parameters)
        if idx >= n:
            if self._hasParamComplex(parameters):
                p = copy.copy(parameters)
                p.reverse()
                res.extend(self.getPossibleParams(0, p))
            return res
        
        res = []
        for i,p in enumerate(parameters):
            atomic = self._isParamAtomic(p)
            if i < idx:
                if atomic: continue
                else:
                    res.extend(self.getPossibleParams(idx-i, p['type']))
            elif i == idx:
                if atomic:
                    res.append(p)
                else: 
                    res.extend(self.getPossibleParams(0, p['type']))
            else:
                break
        return res

    def getParamStr(self):
        """Returns the string line representing the macro parameters.
           For example, if a macro has a motor parameter followed by a list of
           numbers it will return:
           '<motor> [ <number> ]'

        :return: (str) a string representing the macro parameter line
        """
        if not self.hasParams():
            return ''
        return self._parameter_line

    def getParamDescr(self):
        """Returns the list of strings, each one documenting each macro parameter
        
        :return: (sequence<str>) list of parameter lines
        """
        if not self.hasParams():
            return []
        return self._parameter_description

    def hasResult(self):
        """Determines if the macro has a result
        
        :return: (bool) True if the macro has a result or False otherwise
        """
        return hasattr(self ,'result')

    def getResultList(self):
        """Returns the list of results
        
        :return: (sequence) a list of results
        """
        if not self.hasResult():
            return []
        return self.result
    
    def getResult(self,idx=0):
        """Gets the result for the given index
        
        :param idx: (int) the index (default is 0)
        
        :return: (object) the result or None if the macro does not have the 
                 desired result
        """
        return self.result[idx]

    def getResultStr(self):
        """Returns the string line representing the macro results.
           For example, if a macro returns a number, this method it will return:
           '<number>'

        :return: (str) a string representing the macro result line
        """
        if not self.hasResult():
            return ''
        return self._result_line
    
    def getResultDescr(self):
        """Returns the list of strings, each one documenting each macro result
        
        :return: (sequence<str>) list of result lines
        """
        if not self.hasResult():
            return []
        return self._result_description

    def formatResult(self, res):
        if not self.hasResult():
            if res is None:
                return None
            raise Exception('Macro %s does not return any result' % self.name)
        result_info = self.getResult()
        rtype = result_info['type']
        if rtype == 'File':
            fd, filename = tempfile.mkstemp(prefix='spock_',text=True)
            os.write(fd, res[1])
            os.close(fd)
            # put the local filename in the result
            res.insert(0,filename)
            return res
        if len(res) > 0:
            if rtype == 'Float':
                return float(res[0])
            elif rtype == 'Integer':
                return int(res[0])
            elif rtype == 'Boolean':
                return res[0].lower() == 'true'
            elif rtype in ('String', 'User', 'Filename'):
                return res[0]
            else:
                raise Exception('Unknown return type for macro %s' % self.name)
        else:
            return None

    def __str__(self):
        return self.name

class Macro(object):

    Ready    = PyTango.DevState.ON
    Init     = PyTango.DevState.INIT
    Running  = PyTango.DevState.RUNNING
    Pause    = PyTango.DevState.STANDBY
    Fault    = PyTango.DevState.FAULT
    Finished = PyTango.DevState.ON
    Abort    = PyTango.DevState.ALARM

    def __init__(self, door, name, id, xml_obj):
        self.door = door
        self.name = name
        self.xml_node = xml_obj
        self.id = id
        self.range = None
        self.step = None
        self.result = None
    
    def getID(self):
        return self.id
    
    def getRange(self):
        return self.range
    
    def getStep(self):
        return self.step
    
    def getInfo(self):
        return self.door.macro_server.getMacroInfoObj(self.name)

    def setResult(self, res):
        self.result = self.getInfo().formatResult(res)

    def getResult(self):
        return self.result
    

class BaseNode(object):
    """Base class defining basic interface for all type of nodes used to represent,
    relationship between sequence, macros and parameters."""
    
    def __init__(self, parent=None):
#        if parent:
#            parent = weakref.ref(parent)
        self._parent = parent
    
    def parent(self):
        return self._parent
    
    def setParent(self, parent):
#        if parent:
#            parent = weakref.ref(parent)
        self._parent = parent
    
    def value(self):
        return ""
    
    def isAllowedMoveUp(self):
        return False
    
    def isAllowedMoveDown(self):
        return False
    
    def isAllowedDelete(self):
        return False
    
class BranchNode(BaseNode):
    """Class used to represent all types of elements which contain
    a list of other elements (children)"""

    def __init__(self, parent=None):
        BaseNode.__init__(self, parent)
        self._children = []
        
    def __len__(self):
        return len(self.children())
        
    def children(self):
        return self._children
    
    def child(self, idx):
        try:
            children = self.children()
            return children[idx]
        except:
            return None
    
    def rowOfChild(self, child):
        try:
            return self.children().index(child)
        except ValueError:
            return -1
        
    def insertChild(self, child, row=-1):
        child.setParent(self)
        if row == -1: row = len(self)
        self.children().insert(row, child)
        return row
        
    def removeChild(self, child):
        self.children().remove(child)
        
    def upChild(self, child):
        i = self.children().index(child)
        if i == 0: return
        self.removeChild(child)
        self.children().insert(child, i - 1)
        
    def downChild(self, child):
        i = self.children().index(child)
        if i == len(self)-1: return
        self.removeChild(child)
        self.children().insert(i + 1,child)
        
    def toRun(self):
        values = []
        alert = ""
        for child in self.children():
            val, ale = child.toRun()
            values += val
            alert += ale            
        return values, alert
                
class ParamNode(BaseNode):
    """Base class for param elements: single parameters and param repeats.
    It groups a common interface of them."""
    
    def __init__(self, parent=None, param=None):
        BaseNode.__init__(self, parent)
        if param is None:
            self.setName(None)
            self.setDescription(None)
            self.setMin(None)
            self.setMax(None)
        else:
            self.setName(str(param.get('name')))
            self.setDescription(str(param.get('description')))
            self.setMin(str(param.get('min')))
            self.setMax(str(param.get('max')))
        
            
    def name(self):
        return self._name
    
    def setName(self, name):
        self._name = name
    
    def description(self):
        return self._description
    
    def setDescription(self, description):
        self._description = description
        
    def min(self):
        return self._min
    
    def setMin(self, min):
        if min == 'None':
            min = None
        elif min:
            min = float(min)
        self._min = min
        
    def max(self):
        return self._max
    
    def setMax(self, max):
        if max == 'None':
            max = None
        elif max:
            max = float(max)
        self._max = max  
        
        
class SingleParamNode(ParamNode):
    """Single parameter class."""
    def __init__(self, parent=None, param=None):
        ParamNode.__init__(self, parent, param)
        if param is None: return
        self.setType(str(param.get('type')))
        self.setDefValue(str(param.get('default_value', '')))
        if self.type() == "User":
            self.setDefValue(str(USER_NAME))
        self.setValue(self.defValue())
        
    def __len__(self):
        return 0
           
    def value(self):
        return self._value
    
    def setValue(self, value):
        self._value = value
        
    def defValue(self):
        return self._defValue
    
    def setDefValue(self, defValue):
        self._defValue = defValue
        
    def type(self):
        return self._type
    
    def setType(self, type):
        self._type = type
        
    def toXml(self):
        paramElement = etree.Element("param", name = self.name(), 
                                              value = self.value())  
        return paramElement    
    
    def fromXml(self, xmlElement):
        self.setName(xmlElement.get("name"))
        self.setValue(xmlElement.get("value"))
        
    def isMotorParam(self):
        return self.type() == globals.PARAM_MOTOR
    
    def allMotors(self):
        if self.isMotorParam() and self.value() != 'None':
            return [self.value()]
        else:
            return[]
            
    def toRun(self):
        val = self.value()
        if val is None or val == "None" or val == "": 
            alert = "Parameter <b>" + self.name() + "</b> is missing.<br>"
            return ([val], alert)
        return ([val], "")
                        
class RepeatParamNode(ParamNode, BranchNode):
    """Repeat parameter class."""

    def __init__(self, parent=None, param=None):
        ParamNode.__init__(self, parent, param)
        BranchNode.__init__(self, parent)
        if param is None:
            return
        self.setParamsInfo(copy.deepcopy(param.get('type')))
        
    def arrangeIndexes(self):
        for i, child in enumerate(self.children()):
            child.setIndex(i+1)
        
    def paramsInfo(self):
        return self._paramsInfo
    
    def setParamsInfo(self, paramsInfo):
        self._paramsInfo = paramsInfo
        
    def newRepeat(self):
        repeatNode = RepeatNode(self)
        for repeatParam in self.paramsInfo():
            repeatNode.addParam(repeatParam)
        return repeatNode
        
    def addRepeat(self):
        repeat = RepeatNode(self)
        self.insertChild(repeat)
        for repeatParam in self.paramsInfo():
            repeat.addParam(repeatParam)
        
    def isReachedMin(self):
        if self.min() is None: 
            return False
        return len(self) <= self.min()
    
    def isBelowMin(self):
        if self.min() is None: 
            return False
        return len(self) < self.min()
    
    def isReachedMax(self):
        if self.max() is None:
            return False
        return len(self) == self.max() 
        
    def isAboveMax(self):
        if self.max() is None:
            return False
        return len(self) > self.max() 

    def insertChild(self, child, row=-1):
        #this line was removed on purpose
        #in case of importing sequences from plain text, it is possible that user introduced more repetitions than allowed
        #in this case later validation will inform him about exceeding a limit
        #if self.isReachedMax(): return
        return BranchNode.insertChild(self, child, row) 
        
    def removeChild(self, child):
        if self.isReachedMin(): return
        child.setParent(None)
        begin = self.children().index(child) + 1
        for i in range(begin,len(self)):
            self.child(i).setIndex(self.child(i).index() - 1)
        BranchNode.removeChild(self, child)
        
    def upChild(self, child):
        i = self.children().index(child)
        if i == 0: return
        child.setIndex(child.index() - 1)
        self.child(i - 1).setIndex(self.child(i - 1).index() + 1)
        BranchNode.removeChild(self, child)
        self.insertChild(child, i - 1) 
        
    def downChild(self, child):
        i = self.children().index(child)
        if i == len(self) - 1: return
        child.setIndex(child.index() + 1)
        self.child(i + 1).setIndex(self.child(i + 1).index() - 1)
        BranchNode.removeChild(self, child)
        self.insertChild(child, i + 1)
    
    def toRun(self):
        values = []
        alert = ""
        if self.isBelowMin():
            alert += "Parameter <b>" + self.name() + "</b> has not enough repeats<br>"
        for child in self.children():
            val,ale = child.toRun()
            values += val
            alert += ale
        return (values, alert)
    
    def toXml(self):
        paramElement =  etree.Element("paramrepeat", name = self.name())
        for child in self.children():
            paramElement.append(child.toXml())
        return paramElement
    
    def fromXml(self, xmlElement):
        self.setName(xmlElement.get("name"))
        for repeatElement in xmlElement.getiterator("repeat"):
            repeat = RepeatNode(self)
            repeat.fromXml(repeatElement)
            self.insertChild(repeat)
    
    def allMotors(self):
        motors = []
        for child in self.children():
            motors += child.allMotors()
        return motors
    
#    def isAllowedMoveUp(self):
#        return self is not self.parent().child(0)
#    
#    def isAllowedMoveDown(self):
#        return self is not self.parent().child(len(self.parent()) - 1)   
        
    
class RepeatNode(BranchNode):
    """Class for repetition elements (group of params which were repeated in macro)"""
    
    def __init__(self, parent=None):
        BranchNode.__init__(self, parent)
        if parent is None: return
        self.setIndex(len(self.parent()) + 1)
         
    def index(self):
        return self._index
    
    def setIndex(self, index):
        self._index = index
          
    def name(self):
        return "#%d" %self.index()
    
    def addParam(self, param):
        type = param.get('type', None)
        if isinstance(type, list):
            paramRepeat = RepeatParamNode(self, param)
            self.insertChild(paramRepeat)
            paramRepeat.addRepeat()
        else:
            self.insertChild(SingleParamNode(self, param))
    
    def toXml(self):
        repeatElement = etree.Element("repeat", nr = str(self.index()))
        for child in self.children():
            repeatElement.append(child.toXml())
        return repeatElement

    def fromXml(self, xmlElement):
        self.setIndex(int(xmlElement.get("nr")))
        for paramElement in xmlElement:
            if paramElement.tag == "param":
                param = SingleParamNode(self)
            elif paramElement.tag == "paramrepeat":
                param = RepeatParamNode(self)
            param.fromXml(paramElement)
            self.insertChild(param)
            
    def allMotors(self):
        motors = []
        for child in self.children():
            motors += child.allMotors()
        return motors
    
    def isAllowedDel(self):
        pass
    
    def isAllowedMoveUp(self):
        return self is not self.parent().child(0)
    
    def isAllowedMoveDown(self):
        return self is not self.parent().child(len(self.parent()) - 1)   
        
class MacroNode(BranchNode):
    """Class to represent macro element."""
    count = 0
    
    def __init__(self, parent=None, name=None):
        BranchNode.__init__(self, parent)
        self.setId(None)
        self.setName(name)
        self.setPause(False)
        self.setProgress(0)
        self.setRange((0,100))
        self.setParams([])
        self.setHooks([])
        self.setHookPlaces([])
        self.setAllowedHookPlaces([])
        
    def id(self):
        """
        Getter of macro's id property
        
        :return: (int)
        
        .. seealso: :meth:`MacroNode.setId`, assignId
        """
        
        return self._id
    
    def setId(self, id):
        """
        Setter of macro's id property
        
        :param id: (int) new macro's id
        
        See Also: id, assignId
        """
        
        self._id = id
        
    def assignId(self):
        """
        If macro didn't have an assigned id it assigns it
        and return macro's id.
        
        :return: (int)
        
        See Also: id, setId
        """
        id = self.id()
        if id is not None: return id
        MacroNode.count += 1
        self.setId(MacroNode.count)
        return MacroNode.count
            
    def name(self):
        return self._name
    
    def setName(self, name):
        self._name = name
        
    def isPause(self):
        return self._pause
    
    def setPause(self, pause):
        self._pause = pause
        
    def range(self):
        return self._range
    
    def setRange(self, range):
        self._range = range 
        
    def progress(self):
        return self._progress

    def setProgress(self, progress):
        self._progress = progress
        
    def isAllowedHooks(self):
        return bool(self._allowedHookPlaces)

    def allowedHookPlaces(self):
        return self._allowedHookPlaces
        
    def setAllowedHookPlaces(self, allowedHookPlaces):
        self._allowedHookPlaces = allowedHookPlaces
        
    def hookPlaces(self):
        return self._hookPlaces
    
    def setHookPlaces(self, hookPlaces):
        self._hookPlaces = hookPlaces
        
    def addHookPlace(self, hookPlace):
        self._hookPlaces.append(hookPlace)
    
    def removeHookPlace(self, hookPlace):
        self._hookPlaces.remove(hookPlace)
        
    def hasParams(self):
        return self._hasParams
    
    def setHasParams(self, hasParams):
        self._hasParams = hasParams
      
#################################   
    def params(self):
        return self._params
    
    def setParams(self, params):
        self._params = params
        
    def addParam(self, param):
        param.setParent(self)
        self._params.append(param)
    
    def popParam(self, index=None):
        if index == None:
            return self._params.pop()
        else:
            return self._params.pop(index)
        
    def hooks(self):
        return self._hooks
    
    def setHooks(self, hooks):
        self._hooks = hooks
        
    def addHook(self, hook):
        hook.setParent(self)
        self._hooks.append(hook)    
        
    def removeHook(self, hook):
        self._hooks.remove(hook)
        
    def rowOfHook(self, hook):
        try:
            return self.hooks().index(hook)
        except ValueError:
            return -1
  
##################################  
    def children(self):
        return self.params() + self.hooks()
    
    def insertChild(self, child, row=-1):
        child.setParent(self)
        if isinstance(child, MacroNode):
            if row == -1: row = len(self._hooks)
            else: row = row - len(self._params) 
            self._hooks.insert(row, child)
        elif isinstance(child, ParamNode):
            if row == -1: row = len(self._params)
            self._params.insert(row, child)
        return self.rowOfChild(child)
            
    def removeChild(self, child):
        if isinstance(child, MacroNode):
            self._hooks.remove(child)
        elif isinstance(child, ParamNode):
            self._params.insert(child)
        
    def toRun(self):
        values = []
        alert = ""
        for child in self.children():
            if isinstance(child, ParamNode):
                val, ale = child.toRun()
                values += val
                alert += ale            
        return values, alert
    
    def toSpockCommand(self):
        values, alerts = self.toRun()
        return "%s %s" % (self.name(), str.join(' ',values)) 


    def value(self):
        values, alerts = self.toRun()
        if len(values) == 0:
            return ''
        elif len(values) == 1:
            return '[%s]' %values[0]
        else:
            valueString = '' 
            for value in values:
                valueString += (value + ', ') 
            return '[%s]' %valueString[:-2]
    
#    def allMotors(self):
#        motors = []
#        for macro in self.allMacros():
#            motors += macro.ownMotors()
#        return motors
#    
#    def ownMotors(self):
#        motors = []
#        for macro in self.hooks():
#            motors += macro.allMotors()
#        return motors
    
    def allMacros(self):
        macros = self.allDescendants()
        macros.append(self)
        return macros
    
    def allDescendants(self):
        descendantsMacros = []
        ownMacros = []
        for child in self.children():
            if isinstance(child, MacroNode):
                ownMacros.append(child)
                descendantsMacros += child.allDescendants()
        return descendantsMacros + ownMacros
    
#    def descendantFromId(self, id):
#        descendant = None
#        for child in self.children():
#            if isinstance(child, MacroNode) and child.id() == id:
#                descendant = child
#                break
#        else:
#            for child in self.children():
#                descendant = child.descendantById(id)
#        return descendant
            
    def isAllowedMoveLeft(self):
        """This method checks if is is allowed to move macro to grandparent's hook list.
        It is enough to check that grandparent exist, cause all parents must allow hooks"""
        return self.parent().parent() is not None 
    
    def moveLeft(self):
        """This method moves macro to grandparent's hook list 
        and place it right after its ex-parent,
        it also returns newRow"""
        oldParent = self.parent()
        newParent = oldParent.parent()
        newRow = newParent.hooks().index(oldParent) + 1
        oldParent.removeHook(self)
        self.setParent(newParent)
        newParent.insertHook(newRow, self)
        return newRow
        
    def isAllowedMoveRight(self):
        """This method is used to check if it is allowed to move macro
        to it's first following sibling's hook list."""
        parent = self.parent()
        try:     
            return parent.child(parent.rowOfChild(self) + 1).isAllowedHooks()
        except:
            return False
    
    def moveRight(self):
        """This method is used to move selected macro (pased via index)
        to it's first following sibling's hook list. In tree representation it basically move macro to the right"""
        parent = self.parent()
        for idx, hook in enumerate(parent.hooks()):
            if hook is self:
                newParent = parent.hook(idx + 1)
                parent.removeHook(self)
                self.setParent(newParent)
                newParent.insertHook(0,self)
                return 0
        
    def isAllowedMoveUp(self):
        parent = self.parent()
        if isinstance(parent, SequenceNode):
            return self is not self.parent().child(0)
        elif isinstance(parent, MacroNode): 
            return self is not self.parent()._hooks[0]
        else: 
            return False
    
    def moveUp(self):
        """This method moves hook up and returns newRow"""
        parent = self.parent()
        myOldRow = parent.rowOfHook(self)
        parent.removeHook(self)
        parent.insertHook(myOldRow - 1, self)
        return myOldRow - 1 
    
    def isAllowedMoveDown(self):
        parent = self.parent()
        return parent.rowOfChild(self) < len(parent) - 1
    
    def moveDown(self):
        """This method moves hook up and returns newRow"""
        parent = self.parent()
        myOldRow = parent.rowOfHook(self)
        parent.removeHook(self)
        parent.insertHook(myOldRow + 1, self)
        return myOldRow + 1
    
    def toXml(self, withId=True):
        """
        Converts MacroNode obj to etree.Element obj.
        
        :param withId: (bool) if we want to export also macro id (default: True)
        
        See Also: fromXml 
        """
        
        macroElement = etree.Element("macro", name = self.name())
        if withId: macroElement.set("id", str(self.id()))
        for hookPlace in self.hookPlaces():
            hookElement = etree.SubElement(macroElement, "hookPlace")
            hookElement.text = hookPlace    
        for child in self.children():
            if isinstance(child, MacroNode):
                xmlElement = child.toXml(withId)
            else:
                xmlElement = child.toXml()
            macroElement.append(xmlElement)
        return macroElement
    
    def fromXml(self, xmlElement):
        """
        Fills properties of MacroNode obj from etree.Element obj passed as a parameter
        
        :param xmlElement: (etree.Element)
        
        See Also: toXml
        """
        
        self.setName(xmlElement.get("name"))
        hookPlaces = []
        for element in xmlElement:
            if element.tag == "param":
                param = SingleParamNode(self)
                param.fromXml(element)
                self.addParam(param)
            elif element.tag == "paramrepeat":
                param = RepeatParamNode(self)
                param.fromXml(element)
                self.addParam(param)
            elif element.tag == "macro":
                macro = MacroNode(self)
                macro.fromXml(element)
                self.addHook(macro)
            elif element.tag == "hookPlace":
                hookPlaces.append(element.text)
        self.setHookPlaces(hookPlaces)
    
    def fromPlainText(self, plainText):
        words = plainText.split()
        length = len(words)
        if length == 0:
            return
        self.setName(words[0])
        for index in range(1,length):
            param = SingleParamNode(self)
            param.setValue(words[index])
            self.addParam(param)
        
    
class SequenceNode(BranchNode):
    """Class to represent sequence element."""
        
    def __init__(self, parent=None):
        BranchNode.__init__(self, parent)
        
    def allMacros(self):
        macros = []
        for macro in self.children():
            macros += macro.allDescendants()
        macros += self.children()
        return macros
    
    def upMacro(self, macro):
        BranchNode.upChild(self, macro)
        
    def downMacro(self, macro):
        BranchNode.downChild(self, macro)
            
    def toXml(self, withId=True):
        sequenceElement = etree.Element("sequence")
        for child in self.children():
            sequenceElement.append(child.toXml(withId))
        return sequenceElement
    
    def fromXml(self, sequenceElement):
        for childElement in sequenceElement.iterchildren("macro"):
            macro = MacroNode(self)
            macro.fromXml(childElement)
            self.insertChild(macro)

    def fromPlainText(self, plainText):
        plainMacros = plainText.split('\n')
        for plainMacro in plainMacros:
            #ignoring empty lines
            if len(plainMacro) == 0:
                continue
            macro = MacroNode(self)
            macro.fromPlainText(plainMacro)
            self.insertChild(macro)
            
#    def descendantFromId(self, id):
#        descendant = None
#        for child in self.children():
#            if isinstance(child, MacroNode) and child.id() == id:
#                descendant = child
#                break
#        else:
#            for child in self.children():
#                descendant = child.descendantById(id)
#        return descendant
                    
        
        
            
def ParamFactory(paramInfo):
    """Factory method returning param element, depends of the paramInfo argument."""

    if isinstance(paramInfo.get('type'),list):
        param = RepeatParamNode(param=paramInfo)
        if param.min() > 0:
            param.addRepeat()
    else:
        param = SingleParamNode(param=paramInfo)
    return param
    
