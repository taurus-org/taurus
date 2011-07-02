import inspect
import os
import operator
import types
import parameter

MACRO_TEMPLATE = """class @macro_name@(Macro):
    \"\"\"@macro_name@ description.\"\"\"

    # uncomment the following lines as necessary. Otherwise you may delete them
    #param_def = []
    #result_def = []
    #hints = {}
    #env = (,)
    
    # uncomment the following lines if need prepare. Otherwise you may delete them
    #def prepare(self):
    #    pass
        
    def run(self):
        pass

"""

class MacroLib:
    """Object representing a python module containning macro classes.
       Public members:
           f_path - complete (absolute) path and filename
           f_name - filename (including file extension)
           path - complete (absolute) path
           name - module name (without file extension)
           macro_list - list<MacroClass>
    """
    
    def __init__(self,f_path):
        self.f_path = f_path
        self.path, self.f_name = os.path.split(f_path)
        self.name, ext = os.path.splitext(self.f_name)
        self.macro_list = []
    
    def __cmp__(self, o):
        return cmp(self.name, o.name)

    def __str__(self):
        return self.getModuleName()
    
    def addMacro(self,macro_data):
        self.macro_list.append(macro_data)
        
    def getMacro(self,macro_name):
        for m in self.macro_list:
            if m.name == macro_name:
                return m
        return None

    def hasMacro(self,macro_name):
        return not self.getMacro(macro_name) is None
    
    def getModuleName(self):
        return self.name
    
    def getFileName(self):
        if self.f_path.endswith('.pyc'):
            return self.f_path[:-1]
        return self.f_path
        

import json

class MacroClassJSONEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if not isinstance(obj, MacroClass):
            return json.JSONEncoder.default(self, ret)
        klass = obj.getMacroClass()
        ret = { 'name' : obj.getName(),
          'module_name' : obj.getModuleName(),
          'filename' : obj.getFileName(),
          'description' : obj.getDescription(),
          'hints' : obj.klass.hints }
        param, result = obj.getParamObj(), obj.getResultObj()
        if param: ret['parameters'] = param
        if result: ret['result'] = result
        return ret
        

class MacroClass:
    """Object representing a python macro class. 
       Public members:
           name - class name
           klass - python class object
           lib - MacroLib object representing the module where the macro is.
    """
    
    NoDoc = '<Undocumented macro>'
    
    def __init__(self, lib, klass, name=None):
        self.klass = klass
        self.name = name or klass.__name__
        self.lib = lib

    def __cmp__(self, o):
        if o is None: return cmp(self.getName(), None)
        return cmp(self.getName(), o.getName())

    def __str__(self):
        return self.getName()

    def _toJSON(self, obj):
        klass = obj.getMacroClass()
        ret = { 'name' : obj.getName(),
          'module' : obj.getModuleName(),
          'filename' : obj.getFileName(),
          'description' : obj.getDescription(),
          'hints' : obj.klass.hints }
        param, result = obj.getParamObj(), obj.getResultObj()
        if param: ret['parameters'] = param
        if result: ret['result'] = result
        return ret

    def getJSON(self):
        import taurus.core.util
        json_codec = taurus.core.util.CodecFactory().getCodec('json')
        format, data = json_codec.encode(('', self), cls=MacroClassJSONEncoder)
        return data

    def getMacroLib(self):
        return self.lib
    
    def getMacroClass(self):
        return self.klass

    def getName(self):
        return self.name

    def getFullName(self):
        return '%s.%s' % (self.getModuleName(), self.getName())

    def getModuleName(self):
        return self.getMacroLib().getModuleName()

    def getFileName(self):
        return self.getMacroLib().getFileName()
    
    def getDescription(self):
        return self.getMacroClass().__doc__ or MacroClass.NoDoc

    def getBriefDescription(self, max_chars=60):
        d = self.getMacroClass().__doc__ or MacroClass.NoDoc
        d = d.replace('\n',' ')
        if len(d) > max_chars: d = d[:max_chars-5] + '[...]'
        return d

    def getMacroCode(self):
        """Returns a tuple (sourcelines, firstline) corresponding to the 
        definition of the macro class. sourcelines is a list of source code 
        lines. firstline is the line number of the first source code line.
        """
        return inspect.getsourcelines(self.getMacroClass())

    def getInfo(self):
        klass = self.getMacroClass()
        info = [self.getFullName(), self.getDescription(), str(klass.hints)]
        info += self.getParamInfo()
        info += self.getResultInfo()
        return info
    
    def getParamObj(self):
        return self._getParamObj(self.klass.param_def)

    def getResultObj(self):
        return self._getParamObj(self.klass.result_def)

    def _getParamObj(self, param_def):
        ret = []
        for p in param_def:
            t = p[1]
            ret_p = {'min': 1, 'max': None}
            # take care of old ParamRepeat
            if isinstance(t, parameter.ParamRepeat):
                t = t.obj()
                
            if operator.isSequenceType(t) and not type(t) in types.StringTypes:
                if operator.isMappingType(t[-1]):
                    ret_p.update(t[-1])
                    t = self._getParamObj(t[:-1])
                else:
                    t = self._getParamObj(t)
                
            ret_p['name'] = p[0]
            ret_p['type'] = t
            ret_p['default_value'] = p[2]
            ret_p['description'] = p[3]
            ret.append(ret_p)
        return ret

    def getParamInfo(self, param_def=None):
        param_def = param_def or self.klass.param_def
        
        info = [str(len(param_def))]
        for name, type_class, def_val, desc in param_def:
            repeat = isinstance(type_class, parameter.ParamRepeat)
            info.append(name)
            type_name = (repeat and 'ParamRepeat') or type_class
            info.append(type_name)
            info.append(desc)
            if repeat:
                rep = type_class
                opts = sep = ''
                for opt, val in rep.items():
                    opts += '%s%s=%s' % (sep, opt, val)
                    sep = ', '
                info.append(opts)
                info += self.getParamInfo(rep.param_def)
            else:
                info.append(str(def_val))
        return info

    def getResultInfo(self, result_def=None):
        result_def = result_def or self.klass.result_def
        
        info = [str(len(result_def))]
        for name, type_class, def_val, desc in result_def:
            repeat = isinstance(type_class, parameter.ParamRepeat)
            info.append(name)
            type_name = (repeat and 'ParamRepeat') or type_class
            info.append(type_name)
            info.append(desc)
            if repeat:
                rep = type_class
                opts = sep = ''
                for opt, val in rep.items():
                    opts += '%s%s=%s' % (sep, opt, val)
                    sep = ', '
                info.append(opts)
                info += self.getParamInfo(rep.param_def)
            else:
                info.append(str(def_val))
        return info