import copy
import exception

class WrongParam(exception.MacroServerException): 
    pass

class MissingParam(WrongParam): 
    pass

class UnknownParamObj(WrongParam): 
    pass

class WrongParamType(WrongParam):
    pass

class TypeNames:
    """Class that holds the list of registered macro parameter types"""
    
    def __init__(self):
        self._type_names = {}
    
    def addType(self, name):
        """Register a new macro parameter type"""
        setattr(self, name, name)
        self._type_names[name] = name
    
    def removeType(self, name):
        """remove a macro parameter type"""
        delattr(self, name)
        try:
            del self._type_names[name]
        except ValueError,e:
            pass
        
    def __str__(self):
        return str(self._type_names.keys())
    

# This instance of TypeNames is intended to provide access to types to the 
# Macros in a "Type.Motor" fashion
Type = TypeNames()


import taurus.core.util
from taurus.core.tango.sardana.pool import BaseElement

class ParamType(taurus.core.util.Logger):
    
    All             = 'All'
    
    # Capabilities
    ItemList        = 'ItemList'
    ItemListEvents  = 'ItemListEvents'
    
    capabilities    = []
    
    def __init__(self, name):
        self._name = name
        taurus.core.util.Logger.__init__(self, '%sType' % name)
    
    def getName(self):
        return self._name

    def getObj(self, str_repr):
        return self.type_class(str_repr)
        
    @classmethod
    def hasCapability(cls, cap):
        return cap in cls.capabilities


class ParamRepeat:
    # opts: min, max
    def __init__(self, *param_def, **opts):
        self.param_def = param_def
        self.opts = {'min': 1, 'max': None}
        self.opts.update(opts)
        self._obj = list(param_def)
        self._obj.append(self.opts)

    def items(self):
        return self.opts.items()
    
    def __getattr__(self, name):
        return self.opts[name]
    
    def obj(self):
        return self._obj
    
import weakref
import manager

class PoolObjParamType(ParamType, taurus.core.util.ListEventGenerator):
    
    capabilities = [ParamType.ItemList, ParamType.ItemListEvents]
    
    def __init__(self, name):
        ParamType.__init__(self, name)
        taurus.core.util.ListEventGenerator.__init__(self, self._name)

        # dict<Pool, list<str>> 
        # key   : Pool object 
        # value : list of object names
        self._pool_dict = taurus.core.util.CaselessDict()
        
        mg = manager.MacroServerManager()
        
        mg.getPoolListObj().subscribeEvent(self.poolsChanged)
        
    def poolsChanged(self, data, pool_data):
        all_pools, old_pools, new_pools = pool_data
        mg = manager.MacroServerManager()
        
        for pool_name in old_pools:
            pool_obj = mg.getPoolObj(pool_name)
            list_obj = pool_obj.getListObj(self._name)
            # if the pool has this list (it may not have because it is an old 
            # software version of the Pool, for example)
            if list_obj:
                list_obj.unsubscribeEvent(self.listChanged, (pool_name, list_obj))
            self._pool_dict.pop(pool_name, None)
        
        for pool_name in new_pools:
            self._pool_dict[pool_name] = taurus.core.util.CaselessDict()
            pool_obj = mg.getPoolObj(pool_name)
            list_obj = pool_obj.getListObj(self._name)
            # if the pool has this list (it may not have because it is an old 
            # software version of the Pool, for example)
            if list_obj:
                list_obj.subscribeEvent(self.listChanged, (pool_name, list_obj))
    
    def listChanged(self, info, list_data):
        pool_name, list_obj = info
        new_elems = taurus.core.util.CaselessDict()
        list_data = list_data or []
        self.trace("listChanged(%s, %s)" % (pool_name, list_data))
        for elem_name in list_data:
            new_elem_obj = list_obj.getObj(elem_name)
            new_elems[new_elem_obj.getName()] = new_elem_obj
        self._pool_dict[pool_name] = new_elems
        self._fireElementsChanged()
    
    def _fireElementsChanged(self):
        objs = self.getObjList(cache=True)
        objs_str = map(BaseElement.str, objs)
        self.fireEvent(objs_str)

    def getObj(self, name, pool=ParamType.All, cache=False):
        obj_dict = self.getObjDict(pool=pool, cache=cache)
        return obj_dict.get(name, None)

    def getObjDict(self, pool=ParamType.All, cache=False):
        if not (self.hasCapability(ParamType.ItemListEvents) or cache):
            # TODO refresh the object list
            pass
        
        if pool == ParamType.All:
            objs = taurus.core.util.CaselessDict()
            for pool_objs in self._pool_dict.values():
                objs.update(pool_objs)
            return objs
        else:
            return self._pool_dict.get(pool,[])

    def getObjListStr(self, pool=ParamType.All, cache=False):
        obj_dict = self.getObjDict(pool=pool, cache=cache)
        return obj_dict.keys()

    def getObjList(self, pool=ParamType.All, cache=False):
        obj_dict = self.getObjDict(pool=pool, cache=cache)
        return obj_dict.values()


class AttrParamType(ParamType):
    pass


AbstractParamTypes = (ParamType, PoolObjParamType, AttrParamType)


class ParamDecoder:

    def __init__(self, macro_class, param_str_list):
        self.macro_class = macro_class
        self.param_str_list = param_str_list
        self.param_list = None
        self.decode()

    def decode(self):
        dec_token, obj_list = self.decodeNormal(self.param_str_list[1:],
                                                self.macro_class.param_def)
        self.param_list = obj_list

    def decodeNormal(self, str_list, def_list):
        str_len = len(str_list)
        par_len = len(def_list)
        obj_list = []
        str_idx = 0
        for i, par_def in enumerate(def_list):
            name, type_class, def_val, desc = par_def
            if str_idx == str_len:
                if def_val is None:
                    if not isinstance(type_class, ParamRepeat):
                        raise MissingParam, "'%s' not specified" % name
                    elif isinstance(type_class, ParamRepeat):
                        min = par_def[1].opts['min']
                        if min > 0:
                            raise WrongParam, "'%s' demands at least %d values" % (name, min)
                new_obj_list = []
                if not def_val is None:
                    new_obj_list.append(def_val)
            else:
                if isinstance(type_class, ParamRepeat):
                    data = self.decodeRepeat(str_list[str_idx:], par_def)
                    dec_token, new_obj_list = data
                else:
                    mg = manager.MacroServerManager()
                    type_name = type_class
                    type_class = mg.getTypeClass(type_name)
                    par_type = mg.getTypeObj(type_name)
                    par_str = str_list[str_idx]
                    try:
                        val = par_type.getObj(par_str)
                    except ValueError, e:
                        raise WrongParamType, e.message
                    if val is None:
                        msg = 'Could not create %s param "%s" from "%s"' % \
                              (par_type.getName(), name, par_str)
                        raise WrongParam, msg
                    dec_token = 1
                    new_obj_list = [val]
                str_idx += dec_token
            obj_list += new_obj_list
        return str_idx, obj_list

    def decodeRepeat(self, str_list, par_def):
        name, rep_data, def_val, desc = par_def
        min_rep = rep_data.min
        max_rep = rep_data.max
        dec_token = 0
        obj_list = []
        rep_nr = 0
        while dec_token < len(str_list):
            if max_rep is not None and rep_nr == max_rep:
                break
            new_token, new_obj_list = self.decodeNormal(str_list[dec_token:],
                                                        rep_data.param_def)
            dec_token += new_token
            if len(new_obj_list) == 1:
                new_obj_list = new_obj_list[0]
            obj_list.append(new_obj_list)
            rep_nr += 1
        if rep_nr < min_rep:
            msg = 'Found %d repetitions of param %s, min is %d' % \
                  (rep_nr, name, min_rep)
            raise RuntimeError, msg
        return dec_token, obj_list
        
    def getParamList(self):
        return self.param_list

    def __getattr__(self, name):
        return getattr(self.param_list, name)