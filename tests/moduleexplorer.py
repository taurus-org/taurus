#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
###########################################################################

''' Returns info about a module'''

import sys, os, inspect, glob, re

class ModuleExplorer(object):
    
    def __init__(self, exclude_patterns=(), verbose=True):
        '''
        :param exclude_patterns: (seq<str>) sequence of strings containing regexp
                                 patterns. Each candidate to be explored will be 
                                 matched against these patterns and will be excluded
                                 if it matches any of them.
        :param verbose: (bool) If True (default) status messages will be printed to stdout
        '''
        self.exclude_patterns = [re.compile(p) for p in exclude_patterns]
        self.verbose = verbose
    
    def _matchesAnyPattern(self, name, paterns):
        for p in paterns:
            if re.match(p,name) is not None:
                if self.verbose: print 'excluding "%s"'%name
                return True
        return False
    
    def _getlocalmembernames(self, module, predicate=None):
        ret =[]
        modulepath, tail = os.path.split(inspect.getabsfile(module))
        for n,v in inspect.getmembers(module, predicate):
            if inspect.isbuiltin(v): 
                continue #ignore builtin functions
            try: 
                memberpath, tail = os.path.split(inspect.getabsfile(v))
            except TypeError: 
                continue #ignore builtin modules
            if memberpath == modulepath: 
                ret.append(n)
        return ret
    
    def _getSubmodulesFromPath(self, modulepath):
        g = glob.glob(os.path.join(modulepath,'*','__init__.py'))
        ret = [re.findall(r".+\/(.*)\/__init__.py", s)[0] for s in g]
        return ret
    
    def _isclass_with_init(self, obj):
        return inspect.isclass(obj) and hasattr(obj,'__init__')
    
    def _isenumeration(self, obj):
#        return isinstance(obj, taurus.core.util)
        return False #@todo
            
    def exploreModule(self, modulename):
        '''Recursive function that gathers info on a module and all its submodules.
        
        :param modulename: the name of the module to explore
        
        :return: (dict<str,object>) a dictionary containing submodulenames, 
                 localclassnames, localfunctionnames, localenumerationnames,
                 externalmembernames, submodules, warnings
        '''
        if self.verbose: print "Exploring %s..."%modulename  
        warnings = []
        try:
          module = __import__(modulename, fromlist = [''])
        except Exception,e:
          msg = 'exploreModule: WARNING: Cannot import %s. Reason: %s'%(modulename,repr(e))
          warnings.append(msg)
          if self.verbose: print msg
          return dict(modulename = modulename,
                    basemodulename = modulename.split('.')[-1],
                    modulepath = None,
                    submodulenames = [], 
                    localclassnames = [], 
                    localfunctionnames = [],
                    localenumerationnames = [],
                    externalmembernames = [],
                    submodules = {},
                    warnings = warnings)
        modulepath, tail = os.path.split(inspect.getabsfile(module))
        
        submodulenames = sorted(self._getSubmodulesFromPath(modulepath))
        localclassnames =  sorted(self._getlocalmembernames(module, self._isclass_with_init)) 
        localfunctionnames = sorted(self._getlocalmembernames(module, inspect.isfunction))
        localenumerationnames = sorted([])#@todo
        externalmembernames = sorted([]) #@todo
#        localmembers = list(submodules) + localfunctionnames + localclassnames + localenumerationnames
#        externalmembers = [n for n,v in inspect.getmembers(object) if (n not in localmembers and not n.startswith('_'))]
        
        #filter out excluded members
        submodulenames = [n for n in submodulenames if not self._matchesAnyPattern(os.path.join(modulename,n), self.exclude_patterns)]
        localclassnames = [n for n in localclassnames if not self._matchesAnyPattern(os.path.join(modulename,n), self.exclude_patterns)]
        localfunctionnames = [n for n in localfunctionnames if not self._matchesAnyPattern(os.path.join(modulename,n), self.exclude_patterns)]
        localenumerationnames = [n for n in localenumerationnames if not self._matchesAnyPattern(os.path.join(modulename,n), self.exclude_patterns)]
        externalmembernames = [n for n in externalmembernames if not self._matchesAnyPattern(os.path.join(modulename,n), self.exclude_patterns)]
        
        #recurse
        submodules = {}
        for n in submodulenames:
            sm_name = '.'.join((modulename, n))
            submodules[n] = self.exploreModule(sm_name)
        
        return dict(modulename = modulename,
                    basemodulename = modulename.split('.')[-1],
                    modulepath = modulepath,
                    submodulenames = submodulenames, 
                    localclassnames = localclassnames, 
                    localfunctionnames = localfunctionnames,
                    localenumerationnames = localenumerationnames,
                    externalmembernames = externalmembernames,
                    submodules = submodules,
                    warnings = warnings)
        
    @staticmethod
    def getAll(info, key):
        '''
        append all values for a given key in a nested "moduleinfo" dictionary
        
        :param info: (dict) a moduleinfo dictionary like the one returned by :meth:`exploreModule`
        :param key: (str) a key of a moduleinfo dictionary
        
        :return: (list<tuple>) a list that concatenates tuples where the first element is  the (sub)module name
                 and the second element is the value for the given key. 
                 If for a certain submodule, the value is empty, it is not included in the list at all.
        '''
        mname = info['modulename']
        try:
            ret = [(mname,el) for el in info[key]]
        except KeyError:
            return []
        for sminfo in info['submodules'].itervalues():
            ret += ModuleExplorer.getAll(sminfo,key)
        return ret
        
    @staticmethod
    def explore(modulename, exclude_patterns=(), verbose=True):
        '''convenience to explore a module
        
        :param modulename: the name of the module to explore
        :param exclude_patterns: (seq<str>) sequence of strings containing regexp
                                 patterns. Each candidate to be explored will be 
                                 matched against these patterns and will be excluded
                                 if it matches any of them.
        :param verbose: (bool) If True (default) status messages will be printed to stdout
        
        :return: (dict<str,object>, allwarnings) a tuple whose first member is a dictionary
                 containing submodulenames, localclassnames, localfunctionnames, localenumerationnames,
                 externalmembernames, submodules, warnings. The second member of the tuple is a list
                 containing all the warnings accummulated.
        '''
        explorer = ModuleExplorer(exclude_patterns=exclude_patterns, verbose=verbose)
        minfo = explorer.exploreModule(modulename)
        return minfo, ModuleExplorer.getAll(minfo, 'warnings')


        
def main(modulename='taurus', exclude_patterns = ('.*/ui',)):
    moduleinfo, allw = ModuleExplorer.explore(modulename, exclude_patterns=exclude_patterns, verbose=True)
    print '\n\n'+'*'*50
    print "Exploration finished with %i warnings:"%(len(allw))
    for m,w in allw: print w
    print '*'*50+'\n'
    print 
    assert len(allw) == 0
 
    
if __name__ == "__main__":
    main() 