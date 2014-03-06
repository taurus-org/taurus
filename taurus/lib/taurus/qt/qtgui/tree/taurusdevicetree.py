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

"""
taurusdevicetree.py: 
"""

__all__ = ["TaurusDevTree","TaurusSearchTree","TaurusDevTreeOptions"] #,"SearchEdit"] #"TaurusTreeNode"]

import time,os,re,traceback
from functools import partial
import PyTango # to change!!

try:import icons_dev_tree
except:icons_dev_tree = None

from taurus.qt import Qt

import taurus.core
from taurus.core.util.colors import DEVICE_STATE_PALETTE,ATTRIBUTE_QUALITY_PALETTE
from taurus.core.util.containers import CaselessDict
from taurus.core.tango.search import * #@TODO: Avoid implicit imports
from taurus.qt.qtcore.util.emitter import SingletonWorker
from taurus.qt.qtcore.mimetypes import *  #@TODO: Avoid implicit imports
from taurus.qt.qtcore.util import properties
from taurus.qt.qtcore.util.properties import djoin
from taurus.qt.qtgui.base import TaurusBaseComponent, TaurusBaseWidget
from taurus.qt.qtgui.container import TaurusWidget

TREE_ITEM_MIME_TYPE = 'application/x-qabstractitemmodeldatalist'

###############################################################################

class TaurusTreeNodeContainer(object):
    """
    Interface that provides Node-focused methods to TaurusDevTree
    This methods should be moved to TaurusDevTreeNode class when it will be able to retrieve currentItem from Tree.
    """
    _icon_map = {} #A dictionary like {device_regexp:pixmap_url}
    
    def __init__(self):
        raise Exception('This class is just an interface, do not instantiate it!')
    
    @classmethod
    def setIconMap(klass,filters):
        """A dictionary like {device_regexp:pixmap_url}"""
        klass._icon_map = filters
        
    @classmethod
    def getIconMap(klass):
        return klass._icon_map
    
    def createItem(self,parent,value,text=None):
        self.debug('createItem(%s,%s)'%(value,text))
        USE_TREE_NODE = False
        if USE_TREE_NODE: item = TaurusTreeNode(parent)
        else: item = Qt.QTreeWidgetItem(parent)
        if text is None: text = value
        item.isAttribute = False
        item.DeviceName = ''
        item.draggable = ''
        item.setText(0,Qt.QApplication.translate('',text, None, Qt.QApplication.UnicodeUTF8))
        self.setNodeParent(item,parent)
        item.adminNode = None
        if not item.parentNode or '/' in text:
            f = item.font(0)
            if not item.parentNode: f.setBold(True)
            if '/' in text: f.setItalic(True)
            item.setFont(0,f)
        item.parentTree = self #hook used to call external methods with item as single argument
        self.item_index[value.strip().split()[0]] = item
        try:
            icon = self.getNodeIcon(item)
            if icon: item.setIcon(0,icon)
        except: pass
        self.item_list.add(item)
        return item

    ###########################################################################
    # Item members methods
    
    def setNodeParent(self,node,parent):
        """ Used to know which parent attributes must be expanded if found """
        node.parentNode = parent if isinstance(parent,Qt.QTreeWidgetItem) else None
        
    def setNodeAdmin(self,node,admin):
        """ Used to assign a controller to its controlled devices in the tree """
        node.adminNode = admin.getNodeText(admin) if isinstance(admin,Qt.QTreeWidgetItem) else None

    def getNodeAdmin(self,node):
        return node.adminNode(node) if isCallable(node.adminNode) else node.adminNode
        
    def getNodeText(self,node=None,full=False):
        """ Get the text of the node as shown in the tree, @full allows to get the first word or the whole text"""
        if node is None: node = self.currentItem()
        if hasattr(node,'text'):
            txt = str(node.text(0)).strip()
            if not full: return txt.split()[0]
            return txt
        else: return ''
    
    def getNodeDeviceName(self,node = None):
        if node is None: node = self.currentItem()
        return str(getattr(node,'DeviceName','')) or self.getNodeText(node)

    def getNodeParentName(self,node=None):
        if node is None: node = self.currentItem()
        return self.getNodeText(node.parentNode)
        
    def getNodePath(self,node=None):
        """ Returns all parent nodes prior to current """
        if node is None: node = self.currentItem()
        p,path,names = node.parentNode,[],[]
        while p is not None:
            path.insert(0,p)
            names.insert(0,self.getNodeDeviceName(p))
            p = p.parentNode
        return path
        
    def getNodeAlias(self,node = None):
        if node is None: node = self.currentItem()        
        alias = getattr(node,'AttributeAlias','')
        return (alias or self.getNodeText(node))

    def getNodeIcon(self,node=None):
        #self.debug('TaurusDevTree.getNodeIcon(node) not implemented, overrided in subclasses')
        
        #self,url = node.parentTree,''
        if node is None: node = self.getNode()
        try:
            name,url = self.getNodeText(node),''
            for k,v in self.getIconMap().items():
                if re.match(k.lower(),name.lower()): url = v
            if not url:
                for k,v in self.getIconMap().items():
                    if k.lower() in name.lower(): url = v
            #if name.count('/')==2:
                #if any(a.startswith(name+'/') for a in getArchivedAttributes()):
                    #url = wdir('image/icons/clock.png')
                #else:
                    #url = wdir('image/equips/icon-%s.gif'%name.split('/')[2].split('-')[0].lower())
            #elif name.count('/')==3:
                #url = filterAttributes(name) or wdir('image/icons/closetab.png')
            #else:
                #url = wdir('image/equips/icon-%s.gif'%name.lower())
        except:
            self.warning(traceback.format_exc())
        if not url or not os.path.isfile(url): return None
        else: return Qt.QIcon(url)
    
    def getNodeDraggable(self,node = None):
        """ This method will return True only if the selected node belongs to a numeric Tango attribute """
        numtypes = [PyTango.DevDouble,PyTango.DevFloat,PyTango.DevLong,PyTango.DevLong64,PyTango.DevULong,PyTango.DevShort,PyTango.DevUShort,PyTango.DevBoolean]
        if node is None: node = self.currentItem()
        try:
            name = self.getNodeText(node).lower()
            drag = name
            if node.isAttribute and getattr(node,'DeviceName','') and '/' not in name: name = node.DeviceName+'/'+name
            if name.count('/')==2: #A Device Name
                drag = name#+'/state' #False
            elif name.count('/')==3: #An Attribute Name
                #dtype = PyTango.AttributeProxy(name).get_config().data_type
                #if dtype in numtypes: self.debug('The attribute %s is a Numeric Attribute'%(name))
                drag = getattr(node,'draggable','') or name
                #else: drag = False
            self.debug('Node(%s,%s,%s): drag: %s'%(name,node.isAttribute,node.DeviceName,drag))
            return drag.split()[0]
        except:
            import traceback
            self.warning(traceback.format_exc())
            return False 
            
    ###########################################################################
    # Context Menu Actions
    
    @staticmethod
    def setDefaultPanelClass(other):
        TaurusTreeNodeContainer._defaultClass = other
    @staticmethod
    def defaultPanelClass():
        if not hasattr(TaurusTreeNodeContainer,'_defaultClass'): 
            from taurus.qt.qtgui.panel import TaurusDevicePanel
            TaurusTreeNodeContainer._defaultClass = TaurusDevicePanel
        obj = TaurusTreeNodeContainer._defaultClass
        return obj
            
    def showPanel(self):
        '''Display widget taurusDevicePanel'''
        device = self.getNodeText()
        nameclass = self.defaultPanelClass()()
        nameclass.setModel(device)
        nameclass.show()
        ##nameclass.setSpectraAtkMode(True)
        #Dialog is used to make new floating panels persistent
        if isinstance(nameclass,TaurusWidget):
            PopupDialog(self,nameclass)

    def showProperties(self):
        '''Display widget TaurusPropTable'''
        import taurus.qt.qtgui.table
        device = self.getNodeText()
        nameclass = taurus.qt.qtgui.table.TaurusPropTable()
        nameclass.setTable(device)
        nameclass.show()
        #Dialog is used to make new floating panels persistent
        PopupDialog(self,nameclass)

    def addToPlot(self):
        """ This method will send a signal with the current selected node """
        items = self.getSelectedNodes()
        for item in items:
            attr = self.getNodeAlias(item)
            self.trace('In addToPlot(%s->%s)'%(item.text(0),attr))
            self.addAttrToPlot(attr)
        return
        
    def addAttrToPlot(self,attr):
        """ This method will send a signal with the given attr name, in a separate method to be called with a pre-filled list  """
        self.emit(Qt.SIGNAL("addAttrSelected(QStringList)"),Qt.QStringList([str(attr)]))

    def removeFromPlot(self):
        """ This method will send a signal with the current selected node """
        items = self.getSelectedNodes()
        for item in items:
            item = self.currentItem()
            attr = getattr(item,'AttributeAlias','') or self.getNodeText(item)
            self.removeAttrFromPlot(attr)
        return
        
    def removeAttrFromPlot(self,attr):
        """ This method will send a signal with the given attr name, in a separate method to be called with a pre-filled list """        
        self.emit(Qt.SIGNAL("removeAttrSelected(QStringList)"),Qt.QStringList([str(attr)]))


###############################################################################
        
class TaurusDevTree(TaurusTreeNodeContainer,Qt.QTreeWidget, TaurusBaseWidget):
    ''' 
    This widget displays a list of servers, devices or instances.
    To set a new Model use either setModel(filters), addModels(list), setFilters(...) or loadTree(filters)
    setModel and loadTree are equivalent; adding a new branch to the tree
    addModels merges the tree with new models
    setFilters clears previous models and adds new one
    '''
    __pyqtSignals__ = (
        "modelChanged(const QString &)",
        "deviceSelected(QString)",
        "addAttrSelected(QStringList)",
        "removeAttrSelected(QStringList)",
        "refreshTree",
        "nodeFound"
        )
    __properties__ = (
        'ModelInConfig',
        'modifiableByUser',
        #'useParentModel',
        'Filters',
        'Source',
        'ShowAlias',
        'ShowColors',
        'ShowNotExported',
        'MaxDevices',
        )
    __slots__ = (
        "setTangoHost",
        #"setModel",
        #"setFilters",
        "addModels",
        "setModelCheck",
        "loadTree", #Applies regexp filters to database
        "setTree",
        "findInTree",
        "setIcons",
        "expandAll",
        "expandNode",
        "collapseNode",
        )
        
    TRACE_ALL = False

    def __init__(self, parent=None, designMode = False):
        name = "TaurusDevTree"
        self._useParentModel = True
        self._localModel = ''
        self.call__init__wo_kw(Qt.QTreeWidget, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

        self.setObjectName(name)
        self._filters = []
        self.__attr_filter = None
        self.__expand =1
        self.collapsing_search = True
        self.index = 0
        self._nameTopItem = ""

        self.excludeFromSearch = [] #This is a list of regular expressions to exclude objects from searches
        self.dictionary = {}
        self.item_index = CaselessDict()
        self.item_list = set() #NOTE: as several nodes may share the same name this list will be different from item_index.values()!!!
        self.setSelectionMode(self.ExtendedSelection)
        
        self.ContextMenu=[]
        self.ExpertMenu=[]
        
        #The SingletonWorker Threads are used for expanding nodes and also for loading a new tree; both objects are the same thread, but read from different queues
        self.Loader = SingletonWorker(parent=self,name='TreeLoader',cursor=True,start=True )
        self.Expander = SingletonWorker(parent=self,name='NodeExpander',method=lambda node,expand:node.setExpanded(expand),cursor=True,start=True )
        
        self.initConfig()
        
        #Signal
        Qt.QObject.connect(self,Qt.SIGNAL("itemClicked(QTreeWidgetItem *,int)"),self.deviceClicked)
        Qt.QObject.connect(self,Qt.SIGNAL("nodeFound"),self,Qt.SLOT("expandNode"))
        
        self.setDragDropMode(Qt.QAbstractItemView.DragDrop)
        self.setModifiableByUser(True)
        self.setModelInConfig(False) #We store Filters instead!
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSupportedMimeTypes([
            TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_ATTR_MIME_TYPE, 
            TAURUS_MODEL_MIME_TYPE, TREE_ITEM_MIME_TYPE, 'text/plain'])
        
        self.setTangoHost(os.environ['TANGO_HOST'])
        self.defineStyle()
            
    def getConfig(self,name): 
        properties.get_property(self,name)
    
    def initConfig(self):
        """
        Initializing the attributes that will be kept persitent as Qt settings.
        e.g. for Filters property, the following attributes are created:
        
            - self.filters
            - self._filters
            - self.setFilters
            - self.getFilters
            - self.resetFilters
            
        """
        properties.set_property_methods(self,'Models','QStringList',default='',
            #setter = self.setFilters,
            setter = self.addModels, #Not trivial!; it avoids QSettings erasing default model
            #set_callback=lambda v,s=self:v and s.loadTree(v,clear=True),
            #reset_callback=lambda s=self:s.setFilters(''),
            qt=False,config=True
            )
        properties.set_property_methods(self,'MaxDevices','int',default=150,qt=False,config=True)
        properties.set_property_methods(self,'ShowAlias','bool',default=False,qt=False,config=True)
        properties.set_property_methods(self,'ShowNotExported','bool',default=True,qt=False,config=True)
        properties.set_property_methods(self,'ShowColors','bool',default=True,qt=False,config=True)
        #properties.set_property_methods(self,'Expand','int',default=0)
        
    @staticmethod
    def setDefaultAttrFilter(other):
        TaurusDevTree._defattrfilter = staticmethod(other)
        
    @staticmethod
    def defaultAttrFilter():
        if not hasattr(TaurusDevTree,'_defattrfilter'): TaurusDevTree._defattrfilter = None
        return TaurusDevTree._defattrfilter
    
    def setAttrFilter(self,other):
        self._attrfilter = other
        
    def getAttrFilter(self):
        if not isCallable(getattr(self,'_attrfilter',None)): self._attrfilter = None
        return self._attrfilter
    
    def matchAttrFilter(self,target):
        def printf(s): print(s)
        if self.getAttrFilter() and isCallable(self._attrfilter): return self._attrfilter(target,p=printf)
        elif TaurusDevTree.defaultAttrFilter() and isCallable(TaurusDevTree._defattrfilter): return TaurusDevTree._defattrfilter(target,p=printf)
        else: return True
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing methods 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def sizeHint(self):
        return Qt.QTreeWidget.sizeHint(self)

    def minimumSizeHint(self):
        return Qt.QTreeWidget.minimumSizeHint(self)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.tree'
        ret['group'] = 'Taurus Views'
        ret['icon'] = ":/designer/listview.png"
        return ret
    
    def defineStyle(self):
        self.setWindowTitle('TaurusDevTree')
        self.setHeaderLabel('Device Browser (right-click on any element to search/show options)')
        self.setGeometry(Qt.QRect(90,60,256,192))
        self.actionFindInTree = Qt.QAction(self)
        self.actionFindInTree.setShortcut(Qt.QKeySequence.Find)
        self.connect(self.actionFindInTree, Qt.SIGNAL("triggered()"), self.findDialog)
        #self.connect(self, Qt.SIGNAL("itemClicked"), self.clickedEvent)
        from taurus.qt.qtgui.table.qdictionary import QDictionaryEditor,QListEditor
        self.ExpertMenu.append(
            ('Edit Model Filters',
            lambda:QListEditor.main(
                self._filters,
                modal=True,
                title='Edit Model Filters',
                callback=lambda d:self.loadTree(d)
                )
            #lambda:self.loadTree(
                #str(Qt.QInputDialog.getText(None,'Set Tree Model','Enter a list of regexp separated by comma:',Qt.QLineEdit.Normal,','.join(str(f) for f in self._filters))[0])
                #or None)
            ))
        self.ExpertMenu.append(
            ('Edit Tree',
            lambda:QDictionaryEditor.main(self.dictionary,modal=True,title='Edit Tree',callback=lambda d:self.setTree(d,clear=True))
            ))
        self.ExpertMenu.append(
            ('Expand All',
            lambda:self.expandAll()
            ))
        self.ExpertMenu.append(
            ('Collapse All',
            lambda: self.collapseNode(ALL=True)
            ))
        self.ExpertMenu.append(
            ('Save Config',
            lambda:self.saveConfigFile()
            ))
        if not getattr(self,'DeviceMenu',None): self.DeviceMenu = {}
        self.DeviceMenu.update({
            'Show Properties':'showProperties',
            'Refresh Tree':'refreshTree',
            })
        if not getattr(self,'AttributeMenu',None): self.AttributeMenu = []
        [self.AttributeMenu.append(a) for a in  [
            ('Add to trends','addToPlot'),
            ('Remove from trends','removeFromPlot'),
            ] if a not in self.AttributeMenu]
        try:
            from PyTangoArchiving.widget.history import show_history
            self.debug('Adding show_history from archiving...')
            self.AttributeMenu.append(('Show History',show_history))
        except: pass
            
    def trace(self,msg):
        if self.TRACE_ALL or self.getLogLevel() in ('DEBUG',40,):
            print 'TaurusDevTree.%s: %s'%(self.getLogLevel(),msg) #@TODO: use the taurus logger instead! ~~cpascual 20121121
        
    def setTangoHost(self,tango_host):
        self.db = taurus.Database(tango_host)
        
    #model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, 
                                #TaurusBaseWidget.setModel, 
                                #TaurusBaseWidget.resetModel)
        
    def getModel(self):
        return self._filters    
    
    def getModelClass(self):
        return list #taurus.core.taurusdatabase.TaurusDatabase
        
    def setModel(self,model):
        TaurusBaseWidget.setModel(self,model)
    
    def setModelCheck(self,model):
        # Called from TaurusBaseWidget.setModel()
        self.trace('setModelCheck(%s)'%str(model)[:80])
        self.loadTree(model)
        
    @Qt.pyqtSignature("addModels(QStringList)")
    def addModels(self, modelNames):
        '''Adds models to the existing ones:
        :param modelNames:  (sequence<str>) the names of the models to be added
        .. seealso:: :meth:`removeModels`
        '''
        self.trace('In addModels(%s)'%str(modelNames)[:80])
        modelNames = split_model_list(modelNames)
        self.setTree(self.getTangoDict(modelNames),clear=False)
        if isSequence(modelNames):
            self._filters = sorted(set(split_model_list(self._filters)+modelNames))
        elif isMap(modelNames):
            if isMap(self._filters): self._filters.update(modelNames)
            else: self._filters = modelNames
        
    ############################################################################
    # Loading/Cleaning the tree

    #@Qt.pyqtSignature("loadTree(QString)")
    #def loadTree(self,filters,clear=False):
        #'''
        #This method show a list of instances and devices depending on the given servers in QTProperty or in another widget, 
        #this method can be used to connect TauDevTree with another widget such as LineEdit.
        #'''
        #self.trace('In loadTree(%s)'%str(filters))
        #if clear: self.setWindowTitle('TaurusDevTree:%s'%str(filters))
        #self.setTree(self.getTangoDict(filters),clear=clear,alias=False)
    
    def loadTree(self,filters):
        try:
            if isString(filters):
                try:
                    assert '{' in filters
                    filters = dict(filters)
                except:
                    filters = split_model_list(filters)
            self.trace('loadTree(%s)'%(filters))
            assert isMap(filters) or isSequence(filters), "Filters have to be map, string or list type!"
            properties.set_property(self,'Filters',filters) #self._filters = filters
            if isSequence(filters):
                self.setWindowTitle('TaurusDevTree:%s'%str(filters))
                dct = self.getTangoDict(filters)
            else: #if isMap(filters):
                self.setWindowTitle('TaurusDevTree:%s'%','.join(filters.keys()))
                def expand_dict(d):
                    return [x for v in d.values() for x in (expand_dict(v) if hasattr(v,'values') else (v,))] 
                targets = [t.upper() for t in get_matching_devices(['*%s*'%f if '*' not in f else f for f in expand_dict(filters)])]
                def get_devs(f):
                    return dict.fromkeys(t for t in targets if matchCl(f,t))
                def expand_filter(f):
                    return dict((k,expand_filter(v) if hasattr(v,'values') else get_devs(v)) for k,v in f.items() if v)
                dct = expand_filter(filters)
            #self.Loader.next([self.setTree,dct,True])
            self.setTree(dct,clear=True)
        except:
            self.warning('TaurusDeviceTree.loadTree(%s):\n%s'%(filters,traceback.format_exc()))
        
    def setTree(self,diction,clear=False):
        """
        Initializes the tree from a dictionary {'Node0.0':{'Node1.0':None,'Node1.1':None}}
        """
        K = len(str(dict(diction)))
        self.trace('In setTree(%d) ...'%K)
        self.debug(diction)
        if diction is None: return
        if clear or self.dictionary: 
            if not clear: diction = djoin(diction,self.dictionary) #Merging new and old models
            self.clear()
        self.dictionary = diction
        if len(diction): 
            self.setNodeTree(self,diction,alias=(self.getShowAlias() or K<self.getMaxDevices()*20))
            #Auto-Expand caused problems when loading filters from QSettings
            if 0<len(self.item_list)<self.getMaxDevices(): self.expandAll(queue=False)
        
    def setNodeTree(self,parent,diction,alias=False):
        """
        It has parent as argument to allow itself to be recursive
        Initializes the node tree from a dictionary {'Node0.0':{'Node1.0':None,'Node1.1':None}}
        """
        self.debug('In setNodeTree(%d,alias=%s) ...'%(len(diction),alias))
        if not hasattr(diction,'keys'): diction = dict.fromkeys(diction)
        for node in sorted(diction.keys()):
            assert int(self.index)<10000000000,'TooManyIterations!'
            self.index = self.index + 1
            dev_alias = alias and str(node).count('/')==2 and get_alias_for_device(node)
            text = '%s (%s)'%(node,dev_alias) if dev_alias else node
            if diction[node] and any(diction[node]):
                item = self.createItem(parent,node,text)
                self.setNodeTree(item,diction[node],alias)
            else:
                item = self.createItem(parent,node,text)
        
    def clear(self):
        while not self.Expander.getQueue().empty(): self.Expander.getQueue().get()
        self.item_index.clear()
        while self.item_list: self.item_list.pop()
        Qt.QTreeWidget.clear(self)
        
    def refreshTree(self):
        self.loadTree(self._filters)
        self.emit(Qt.SIGNAL("refreshTree"))

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    ## @name Methods for building server/devices/attributes tree
    # @{
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getTangoDict(self,filters):
        self.trace('In TaurusDevTree.getTangoDict(%s(%s))'%(type(filters),str(filters)[:80]))
        if filters is None: return
        result = {}
        filters = split_model_list(filters)
        targets = get_matching_devices(filters)
        targets = [t.upper() for t in targets]
        domains = set(t.split('/')[0] for t in targets)
        for d in domains:
            families = set(t.split('/')[1] for t in targets if t.startswith('%s/'%d))
            result[d] = dict((f,dict.fromkeys(t for t in targets if t.startswith('%s/%s/'%(d,f)))) for f in families)
        return result
    
    def addAttrToDev(self,my_device,expert=False,allow_types=None):
        """ This command returns the list of attributes of a given device applying display level and type filters.
        @argin expert If False only PyTango.DispLevel.OPERATOR attributes are displayed
        @argin allow_types Only those types included in the list will be displayed (e.g. may be restricted to numeric types only)
        """
        numeric_types = [PyTango.DevDouble,PyTango.DevFloat,PyTango.DevLong,PyTango.DevLong64,PyTango.DevULong,PyTango.DevShort,PyTango.DevUShort,PyTango.DevBoolean,PyTango.DevState]
        allow_types = allow_types or [PyTango.DevString]+numeric_types
        dct = {}
        self.trace('In addAttrToDev(%s)'%my_device)
        try:
            proxy = PyTango.DeviceProxy(my_device)
            timeout = proxy.get_timeout_millis()
            proxy.set_timeout_millis(50)
            proxy.ping()
            list_attr = proxy.attribute_list_query()
            proxy.set_timeout_millis(timeout)

            for aname,my_attr in sorted([(a.name,a) for a in list_attr]):
                if allow_types and my_attr.data_type not in allow_types: continue
                if not expert and my_attr.disp_level==PyTango.DispLevel.EXPERT: continue
                label = aname==my_attr.label and aname.lower() or "%s (%s)"%(aname.lower(),my_attr.label)
                dct[str(my_device).lower()+'/'+label] = 0
        except PyTango.DevFailed,e:
            self.warning('addAttrToDev(%s): %s'%(my_device,str(e)))
            qmsg = Qt.QMessageBox(Qt.QMessageBox.Critical,'%s Error'%my_device,'%s not available'%my_device,Qt.QMessageBox.Ok,self)
            qmsg.show()
        except Exception,e:
            self.warning('addAttrToDev(%s): %s'%(my_device,str(e)))
            qmsg = Qt.QMessageBox(Qt.QMessageBox.Critical,'%s Error'%my_device,str(e),Qt.QMessageBox.Ok,self)
            qmsg.show()
        return dct
            
    def addAttrToNode(self, node=None, full=False):
        node = node or self.currentItem()
        dev = self.getNodeDeviceName(node)
        self.trace('In addAttrToNode(%s)'%dev)
        attrs = self.addAttrToDev(dev)
        children = [str(node.child(i).text(0)).lower() for i in range(node.childCount())]
        for aname in sorted(attrs):
            tag = aname.rsplit('/')[-1]
            if tag.lower() in children:
                continue
            elif not full and not self.matchAttrFilter(aname):
                continue
            else:
                natt = self.createItem(node,value=aname,text=tag)
                natt.draggable = aname.split()[0].strip()
                natt.isAttribute = True
                natt.DeviceName = dev
                icon = self.getNodeIcon(natt)
                if icon: natt.setIcon(0,icon) 
                alias = getattr(node,'AttributeAlias',{}) #it gets all aliases for this device attributes
                if alias: 
                    self.trace('Got aliases for %s: %s' % (aname,alias))
                    [setattr(natt,'AttributeAlias',v) for k,v in alias.items() if k in aname.lower()]
                else: 
                    natt.AttributeAlias = aname.split()[0].strip()
        node.setExpanded(True)
        return
                        
    ###########################################################################
    # Node getters
    
    def getNode(self,target=None):
        """ Gets currrent node or node by name or by regexp """
        if target is None: 
            return self.currentItem()
        else: 
            nodes = self.getMatchingNodes(target,1)
            if not nodes:
                return None
            else:
                return nodes[0]
        return
        
    def getNodeByName(self,key):
        return self.item_index[key]
    
    def getNodeList(self):
        return self.item_index.keys()

    def getMatchingNodes(self,regexp,limit=0, all=False, exclude=None):
        """ It returns all nodes matching the given expression. """
        result,regexp = [],str(regexp).lower()
        exclude = exclude or []        
        self.trace('In TauDevTree.getMatchingNodes(%s,%s,%s,%s)'%(regexp,limit,all,exclude))
        if not all:
            node = self.item_index.get(regexp,None)
            if node is not None:
                return [node]
        regexp = re.compile(extend_regexp(regexp))
        for k,node in self.item_index.iteritems():
            nname = self.getNodeText(node,full=True).lower()
            if (regexp.match(k) or regexp.match(nname)) and \
                (not exclude or not any(re.match(x.lower(),y) for x in exclude for y in (k.lower(),nname))):
                result.append(node)
                if not all and len(result)==1: break
                if limit and len(result)>=limit: break
        return result
        
    def getSelectedNodes(self):
        return self.selectedItems()
    
    def getAllNodes(self):
        """ Returns a list with all node objects. """
        def get_child_nodes(dct,node,fun=None):
            if fun: fun(node)
            dct.update([(str(node.text(0)),node)])
            for j in range(node.childCount()):
                get_child_nodes(dct,node.child(j))
            return dct
        dct = {}
        for i in range(self.topLevelItemCount()):
            get_child_nodes(dct,self.topLevelItem(i))
        return dct 

    def unpackChildren(self):
        """ removes all nodes from the tree and returns them in a list, used for resorting """
        allChildren = []
        nodes = self.getAllNodes().values()
    
        for node in nodes:
            allChildren.extend(node.takeChildren())
        while self.topLevelItemCount(): 
            allChildren.append(self.takeTopLevelItem(0))
        return allChildren    
    
    ## @}
    ########################################################################################################################
            
    ###########################################################################
    # Expand/Collapse/Search nodes
    
    def collapseNode(self,ALL=False,filters='',fun=None):
        """ Collapses the whole tree or from a given node.
        @argin ALL tells whether to collapse from current item or the whole tree
        @argin filters Allows to set a list of nodes to not be filtered
        
        """
        filters = str(filters).lower()
        found = ''
        self.debug( 'In TaurusTree.collapseAll(%s)'%filters)
        todelete = []
        def expand_child_nodes(node):
            result = int(bool(filters))
            if fun: fun(node)
            if not node: return ''
            for j in range(node.childCount()):
                child = node.child(j)
                result = expand_child_nodes(child)
                if filters and re.search(filters,str(child.text(0)).lower()):
                    self.debug( 'In TaurusTree.collapseAll(%s): %s matches!'%(filters,str(child.text(0)).lower()))
                    result = True
                elif not result:
                    child.setExpanded(False)
                aname = '/'.join(['[0-9a-zA-Z\-\_]+']*4) #When collapsing all attribute lists are cleaned up
                if re.match(aname,str(child.text(0))):
                    todelete.append((node,child))
            if not result: node.setExpanded(False)
            return result
        if ALL:
            for i in range(self.topLevelItemCount()):
                found = expand_child_nodes(self.topLevelItem(i)) or found
        else: found = expand_child_nodes(self.currentItem()) or found
        for node,child in todelete: #Pruning attribute nodes
            node.removeChild(child)
            del child
        return found

    ###########################################################################
    # New expand/search methods
            
    #@Qt.pyqtSignature("expandNode")
    def expandNode(self,node=None,expand=True):
        """ Needed to do threaded expansion of the tree """
        if node is None: node = self.getNode()
        if isinstance(node,(basestring,Qt.QString)): name,node = str(node),self.getNode(node)
        else: name = self.getNodeText(node)
        node.setExpanded(expand)
        return expand
        
    def expandAll(self,queue=True):
        self.findInTree('*',select=False,queue=queue)
        
    def findDialog(self):
        self.findInTree(str(Qt.QInputDialog.getText(self,'Search ...','Write a part of the name',Qt.QLineEdit.Normal)[0]))
        
    @Qt.pyqtSignature("findInTree(const QString &)")
    def findInTree(self,regexp,collapseAll=None,exclude=None,select=True,queue=True):
        self.trace( 'In TauTree.findInTree(%s)'%regexp)
        if collapseAll is None: collapseAll = self.collapsing_search
        regexp = str(regexp).lower().strip()
        exclude = (lambda x: x if hasattr(x,'__iter__') else [x])(exclude or self.excludeFromSearch or [])
        if not regexp: return
        try:
            t0 = time.time()
            nodes = self.getMatchingNodes(regexp,all=True,exclude=exclude)
            if len(nodes)>150:
                v = Qt.QMessageBox.warning(None,'Device Tree Search',
                    'Your search matches too many devices (%d) and may slow down the application.\nDo you want to continue?'%len(nodes),
                    Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel)
                if v == Qt.QMessageBox.Cancel:
                    self.debug('Search cancelled by user.')
                    return
            if nodes:
                #It's good to have first node matched to be selected fast
                if select: 
                    nodes[0].setSelected(True)
                    self.setCurrentItem(nodes[0])
                    self.deviceSelected(self.getNodeDeviceName(nodes[0])) #Searches must not trigger events!
                    self.debug('The selected node is %s'%self.getNodeText(nodes[0]))
                #Then proceed to expand/close the rest of nodes
                parents = set(parent for node in nodes for parent in self.getNodePath(node) if parent)
                for item in self.item_list:
                    matched,expanded = item in parents,item.isExpanded()
                    if (matched and not expanded):
                        if queue: self.Expander.getQueue().put((item,True))
                        else: item.setExpanded(True)
                    elif (not matched and expanded and self.collapsing_search):
                        if queue: self.Expander.getQueue().put((item,False))
                        else: item.setExpanded(False)
                if select:
                    self.scrollTo(self.indexFromItem(nodes[0]),Qt.QAbstractItemView.PositionAtTop)#Center)
                self.debug('\tfindInTree(%s): %d nodes found in %f s' %(regexp,len(nodes),time.time()-t0))
            else:
                if collapseAll: 
                    if queue: [self.Expander.getQueue().put((item,False)) for item in self.item_list if item.isExpanded()]
                    else: [item.setExpanded(False) for item in self.item_list if item.isExpanded()]
                self.debug( 'findInTree(%s): Node not found'%(regexp))
            if queue: self.Expander.next()
        except: 
            self.warning( 'findInTree(%s): failed'%(regexp))
            self.error(traceback.format_exc())
            
    def sortCustom(self,order):
        assert order and len(order), 'sortCustom(order) must not be empty'
        allChildren = {}
        while self.topLevelItemCount(): 
            it = self.takeTopLevelItem(0)
            allChildren[str(it.text(0))]=it

        sorter = lambda k,ks=[re.compile(c) for c in order]: str((i for i,r in enumerate(ks) if r.match(k.lower())).next())+str(k)
        for c,it in sorted(allChildren.items(),key=lambda k:sorter(k[0])):
            self.debug( 'tree.sortCustom(%s): %s inserted at %d' % (order,it.text(0),self.topLevelItemCount()))
            self.insertTopLevelItem(self.topLevelItemCount(),it)
        return

    ###########################################################################
    # Update node colors
    
    #@Qt.pyqtSignature("setIcons")
    def setIcons(self,dct={},root_name=None,regexps=True):
        '''
        This method change the icons depending of the status of the devices
        Dict is a dictionary with name of device and colors such as {name_device:color,name_device2:color2}
        An alternative may be an icon name!
        '''
        #secs = time.time()
        #ID = int(100*random.random())
        state2color = lambda state: Qt.QColor(DEVICE_STATE_PALETTE.number(state))
        #quality2color = lambda attr: Qt.QColor(ATTRIBUTE_QUALITY_PALETTE.number(quality))

        def update_node(node,key,dct):
            if hasattr(node,'CustomForeground'):
                node.setForeground(0,Qt.QBrush(Qt.QColor(node.CustomForeground)))
            if hasattr(node,'CustomBackground'):
                node.setBackground(0,Qt.QBrush(Qt.QColor(node.CustomBackground)))            
            elif hasattr(node,'StateBackground'):
                node.setBackground(0,Qt.QBrush(state2color(dct[key])))
            if hasattr(node,'CustomIcon'):
                node.setIcon(0,Qt.QIcon(node.CustomIcon))
            else:
                #key = str(node.text(0)).split(' ')[0]
                if key.count('/')==2:
                    self.setStateIcon(node,dct and dct[key] or '')
            return

        if not isinstance(dct,dict): 
            dct = dict.fromkeys(dct,'')    
        nodes = self.getAllNodes()
        for name,node in nodes.iteritems():
            name = str(name).split()[0]
            if node.isHidden(): continue
            if regexps:
                matches = [v for k,v in dct.items() if re.match(k.lower(),name.lower())]
                if matches: 
                    update_node(node,name,{name:matches[0]})
            elif name in dct or not dct:
                update_node(node,name,dct or {name:''})
        return

    def setStateIcon(self,child,color):
        if icons_dev_tree is None: 
            self.debug('In setStateIcon(...): Icons for states not available!')
            return
        if color=="#00ff00" or color in 'ON,OPEN,EXTRACT':
            icon = Qt.QIcon(":/ICON_GREEN")
            child.setIcon(0,icon)
        elif color=="#ff0000" or color in 'OFF,FAULT':
            icon = Qt.QIcon(":/ICON_RED")
            child.setIcon(0,icon)
        elif color=="#ff8c00" or color in 'ALARM':
            icon = Qt.QIcon(":/ICON_ORANGE")
            child.setIcon(0,icon)
        elif color=="#ffffff" or color in 'CLOSE,INSERT':
            icon = Qt.QIcon(":/ICON_WHITE")
            child.setIcon(0,icon)
        elif color=="#80a0ff" or color in 'MOVING,RUNNING':
            icon = Qt.QIcon(":/ICON_BLUE")
            child.setIcon(0,icon)
        elif color=="#ffff00" or color in 'STANDBY':
            icon = Qt.QIcon(":/ICON_YELLOW")
            child.setIcon(0,icon)
        elif color=="#cccc7a" or color in 'INIT':
            icon = Qt.QIcon(":/ICON_BRAWN")
            child.setIcon(0,icon)
        elif color=="#ff00ff" or color in 'DISABLE':
            icon = Qt.QIcon(":/ICON_PINK")
            child.setIcon(0,icon)
        elif color=="#808080f" or color in 'UNKNOWN':
            icon = Qt.QIcon(":/ICON_GREY")
            child.setIcon(0,icon)
        else:
            icon = Qt.QIcon(":/ICON_WHITE")
            child.setIcon(0,icon)        
        
    ############################################################################
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Event methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def deviceClicked(self,item,column):
        self.trace("In TaurusDevTree.deviceClicked(%s)"%item.text(column))
        self.deviceSelected(self.getNodeDeviceName())
        
    def deviceSelected(self,device_name=''):
        '''QSIGNAL: this method is used to emit deviceSelected(QString) signal'''
        self.trace("In TaurusDevTree.deviceSelected(%s)"%device_name)
        try:
            #item = self.currentItem()
            device_name = device_name or self.getNodeDeviceName()#item.text(0)
            if str(device_name).count('/')!=2: return
            #Signal
            self.trace('TaurusTree emit deviceSelected(%s) signal ...'%device_name)
            self.emit(Qt.SIGNAL("deviceSelected(QString)"), Qt.QString(device_name))
        except:
            self.error(traceback.format_exc())
            pass
            
    def getModelMimeData(self):
        '''Returns a MimeData object containing the model data. The default implementation 
        fills the `TAURUS_MODEL_MIME_TYPE`. If the widget's Model class is
        Attribute or Device, it also fills `TAURUS_ATTR_MIME_TYPE` or
        `TAURUS_DEV_MIME_TYPE`, respectively
        '''
        mimeData = Qt.QMimeData()
        node = self.currentItem() 
        draggable = self.getNodeDraggable(node)
        if draggable:
            slashes = draggable.count('/')-draggable.count(':')
            #mimeData.setData('application/x-qabstractitemmodeldatalist',draggable)
            if slashes==3: mimeData.setData(TAURUS_ATTR_MIME_TYPE, draggable)
            elif slashes==2: mimeData.setData(TAURUS_DEV_MIME_TYPE, draggable)
            else: mimeData.setData(TAURUS_MODEL_MIME_TYPE, draggable)
        return mimeData
            
    def checkHeaderClicked(self,position):
        if self.itemAt(position) is self.headerItem():
            node = self.headerItem()
            self.showNodeContextMenu(node,event)
            #node.ContextMenu = ['Search ...']            
        
    def mouseMoveEvent(self, event):
        '''
        copied from TaurusBaseWidget to provide drag events
        It had to be rewritten as QTreeWidget does not allow drag events
        '''
        self.debug('In TaurusDevTree.mouseMoveEvent')
        if not self._dragEnabled or not event.buttons() & Qt.Qt.LeftButton:
            return self.getQtClass().mouseMoveEvent(self, event)
        if (event.pos() - self.dragStartPosition).manhattanLength()  < Qt.QApplication.startDragDistance():
            return self.getQtClass().mouseMoveEvent(self, event)
        #The mouseMoveEvent of QTreeWidget do not allow drag, commented
        ret = None #self.getQtClass().mouseMoveEvent(self, event) #call the superclass
        event.accept() #we make sure we accept after having called the superclass so that it is not propagated (many default implementations of mouseMoveEvent call event.ignore())
        drag = Qt.QDrag(self)
        drag.setMimeData(self.getModelMimeData())
        drag.exec_(Qt.Qt.CopyAction, Qt.Qt.CopyAction)
        return ret
    
    def mimeTypes(self):
        return self.getSupportedMimeTypes()
        
    def dropEvent(self, event):
        '''reimplemented to support dropping of modelnames in forms'''
        self.debug('dropEvent(%s): %s,%s'%(event,event.mimeData(),split_model_list(event.mimeData().formats())))
        if event.source() is self:
            self.info('Internal drag/drop not allowed')
            return
        if any(s in event.mimeData().formats() for s in self.getSupportedMimeTypes()):
            #mtype = self.handleMimeData(event.mimeData(),self.addModels)#lambda m:self.addModels('^%s$'%m))
            event.acceptProposedAction()
        else:
            self.warning('Invalid model in dropped data')
        
    ########################################################################################################################3      
    ## @name Context Menu Actions
    # @{
        
    def contextMenuEvent(self,event):
        ''' 
        This function is called when right clicking on TaurusDevTree area. 
        '''
        node = self.currentItem() 
        self.showNodeContextMenu(node,event)
        return
        
    def showNodeContextMenu(self,node,event):
        """
        A pop up menu will be shown with the available options. 
        Menus are managed using two tuple lists for each node: node.ContextMenu and node.ExpertMenu
        """
        obj = self.getNodeDraggable(node)
        position = event.globalPos()
        self.debug('showNodeContextMenu(%s)'%obj)
        if self.itemAt(position) is self.headerItem():
            node = self.headerItem()
            #node.ContextMenu = ['Search ...']
        if node is None:
            node = self
        else:
            if not hasattr(node,'ContextMenu'):
                node.ContextMenu=[]
            if not 'Search ...' in [k for k,a in node.ContextMenu]: ##Creating default menu
                # DEVICE NODE CONTEXT MENU
                if obj.count('/')==2:
                    
                    node.ContextMenu.append(("Open Panel", self.showPanel))
                    node.ContextMenu.append(("Show Attributes",self.addAttrToNode))
                    if self.getNodeAdmin(node):
                        node.ContextMenu.append(("Go to %s"%self.getNodeAdmin(node),\
                            lambda p=self.getNodeAdmin(node): p and self.findInTree(p)
                            ))
                    if not hasattr(node,'ExpertMenu'): setattr(node,'ExpertMenu',self.ExpertMenu)#[])
                    if not 'Show Properties' in [k for k,a in node.ExpertMenu]:
                        node.ExpertMenu.append(("Show Properties", self.showProperties))
                        def test_device():
                            device = str(self.getNodeDeviceName())
                            if device:
                                comm = 'tg_devtest %s &'%device
                                os.system(comm)
                            else: self.debug('TaurusDevTree.TestDevice: Selected Device is None!')
                        node.ExpertMenu.append(("Test Device", test_device))
                        node.ExpertMenu.append(("Show ALL Attributes", lambda s=self:s.addAttrToNode(full=True)))
                    node.ContextMenu.append(('',None))
                    
                # ATTRIBUTE NODE CONTEXT MENU
                elif obj.count('/')==3:
                    for k,v in self.AttributeMenu:
                        self.debug('Adding action %s'%k)
                        if type(v) is str and hasattr(self,v):
                            node.ContextMenu.append((k, getattr(self,v)))
                        else:
                            node.ContextMenu.append((k, lambda s=self.getNodeAlias(node): v(s)))
                    #node.ContextMenu.append(("add to Trends", self.addToPlot))
                    #node.ContextMenu.append(("remove from Trends", self.removeFromPlot))
                    node.ContextMenu.append(('',None))    
                elif not hasattr(node,'ExpertMenu'): 
                    setattr(node,'ExpertMenu',self.ExpertMenu)#[])
                #node.ContextMenu.append(("Expand Node", self.expandNode))
                #node.ContextMenu.append(("Collapse Node", self.collapseNode))
                if node.isExpanded() and node.childCount()<10 and all(self.getNodeText(node.child(j)).count('/')==2 for j in range(node.childCount())):
                    node.ContextMenu.append(("Show Attributes", lambda n=node,s=self: [s.addAttrToNode(n.child(j)) for j in range(n.childCount())]))
                node.ContextMenu.append(("Search ...",\
                    lambda: self.findInTree(str(Qt.QInputDialog.getText(self,'Search ...','Write a part of the name',Qt.QLineEdit.Normal)[0]))
                    ))
        #configDialogAction = menu.addAction("Refresh Tree")
        #self.connect(configDialogAction, Qt.SIGNAL("triggered()"), self.refreshTree)
        menu = Qt.QMenu(self)
        
        if hasattr(node,'ContextMenu'):
            last_was_separator = True
            for t in (type(node.ContextMenu) is dict and node.ContextMenu.items() or node.ContextMenu):
                try:
                    k,action = t
                    if k:
                        configDialogAction = menu.addAction(k)
                        if action: self.connect(configDialogAction, Qt.SIGNAL("triggered()"), action)
                        else: configDialogAction.setEnabled(False)
                        last_was_separator = False
                    elif not last_was_separator: 
                        menu.addSeparator()
                        last_was_separator = True
                except Exception,e: 
                    self.warning('Unable to add Menu Action: %s:%s'%(t,e))
        
        if hasattr(node,'ExpertMenu'):
            menu.addSeparator()
            expert = menu.addMenu('Expert')
            #expert.addSeparator()
            last_was_separator = True
            for t in (type(node.ContextMenu) is dict and node.ExpertMenu.items() or node.ExpertMenu):
                try:
                    k,action = t
                    if k:
                        configDialogAction = expert.addAction(k)
                        if action: self.connect(configDialogAction, Qt.SIGNAL("triggered()"), action)
                        else: configDialogAction.setEnabled(False)
                        last_was_separator = False
                    elif not last_was_separator: 
                        expert.addSeparator()
                        last_was_separator = True
                except Exception,e: 
                    self.warning('Unable to add Expert Action: %s:%s'%(t,e))            
        #menu.addSeparator()
        menu.exec_(event.globalPos())
        del menu


class PopupDialog(Qt.QDialog):
    """ 
    This class create the dialog 
    Dialog is used to make new floating panels persistent
    """
    def __init__(self, parent = None,target = None):
        Qt.QDialog.__init__(self, parent)
        if target: self.initComponents(target)
        
    def initComponents(self,newWidget,show=True):
        widgetLayout = Qt.QVBoxLayout(self)
        widgetLayout.setContentsMargins(10,10,10,10)
        widgetLayout.addWidget(newWidget)
        self.setWindowTitle(newWidget.windowTitle())
        self.setModal(False)
        self.setVisible(True)
        if show: self.exec_()
        
#####################################################################################
            
class TaurusTreeNode(Qt.QTreeWidgetItem, TaurusBaseComponent):
    """
    Unused; one day should replace TaurusTreeNodeContainer and all methods moved here.
    Base class for all Taurus Tree Node Items
    """
    
    #---------------------------------------------------------------------------
    # Write your own code here to define the signals generated by this widget
    #
    __pyqtSignals__ = ("modelChanged(const QString &)",)    
    #__pyqtSignals__ = ("refreshIcon",)
    
    def __init__(self, name = None, parent = None):
        name = name or self.__class__.__name__
        self.call__init__wo_kw(Qt.QTreeWidgetItem, parent)        
        self.call__init__(TaurusBaseComponent, name, parent)
        #self.defineStyle()
    
    #def defineStyle(self):
        #""" Defines the initial style for the widget """
        ##-----------------------------------------------------------------------
        ## Write your own code here to set the initial style of your widget
        ##
        #self.updateStyle()        
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory methods to be implemented in any subclass of TaurusComponent
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getParentTaurusComponent(self):
        """ Returns a parent Taurus component or None if no parent TaurusBaseComponent 
            is found."""
        p = self.parentItem()
        while p and not isinstance(p, TaurusTreeNode):
            p = self.parentItem()
        return p

    def updateStyle(self):
        """ Method called when the component detects an event that triggers a change
            in the style."""
        
        #if self.scene():
        #    self.scene().updateSceneItem(self)
            
        #-----------------------------------------------------------------------
        # Write your own code here to update your widget style
        
        # send a repaint in the end
        #self.repaint()
        #if self._parent: self._parent.repaint()
        
        state2color = lambda state: Qt.QColor(DEVICE_STATE_PALETTE.number(state))
        quality2color = lambda attr: Qt.QColor(ATTRIBUTE_QUALITY_PALETTE.number(attr))
        v = self.getModelValueObj()
        if isinstance(v,PyTango.DevState):
            node.setBackground(0,Qt.QBrush(state2color(v))) #@TODO: node is undefined. Check code
        if hasattr(v,'quality'):
            self.setForeground(0,Qt.QBrush(quality2color(v.quality)))

    def isReadOnly(self):
        return True

    def __str__(self):
        return self.log_name + "(" + self.modelName + ")"

    def getModelClass(self):
        return taurus.core.taurusdevice.TaurusDevice
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseComponent over writing
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    #def attach(self):
        #"""Attaches the widget to the model"""
        #if self.isAttached():
            #return True
        ##-----------------------------------------------------------------------
        ## Write your own code here before attaching widget to attribute connect 
        ## the proper signal so that the first event is correctly received by the
        ## widget
        ##
        ## Typical code is:
        ##self.connect(self, Qt.SIGNAL('valueChangedDueToEvent(QString)'), 
        ##             self.setTextValue)
        #ret = TaurusBaseWidget.attach(self)
        ## by default enable/disable widget according to attach state
        #self.setEnabled(ret)
        #return ret

    #def detach(self):
        #"""Detaches the widget from the model"""
        #TaurusBaseWidget.detach(self)

        ##-----------------------------------------------------------------------
        ## Write your own code here after detaching the widget from the model 
        ##
        ## Typical code is:
        ##self.emit(Qt.SIGNAL('valueChangedDueToEvent(QString)'), 
        ##          Qt.QString(value_str))
        ##self.disconnect(self, Qt.SIGNAL('valueChangedDueToEvent(QString)'),
        ##                self.setTextValue)
        ## by default disable widget when dettached
        #self.setEnabled(False)

    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, 
                                TaurusBaseWidget.setModel, 
                                TaurusBaseWidget.resetModel)
                                
    useParentModel = Qt.pyqtProperty("bool",
                                         TaurusBaseWidget.getUseParentModel, 
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)

    #---------------------------------------------------------------------------
    # Write your own code here for your own widget properties
    
class TaurusDevTreeOptions(Qt.QWidget):
    """ This class provides a search(QString) signal to be connected to TaurusDevTree.findInTree slot """
    __pyqtSignals__ = (
      "search(QString)",
      "loadTree(QString)",
      "hideUnexported",
      "hideUnarchived",
      )
    
    def __init__(self,parent=None,icon=None):
        Qt.QWidget.__init__(self,parent)
        
        self.setLayout(Qt.QHBoxLayout())
        try:
            self._pixmap = Qt.QPixmap(icon or 'image/icons/search.png')
            self._label = Qt.QLabel(self)
            self._label.setPixmap(self._pixmap)
            self.layout().addWidget(self._label)    
        except:
            pass
        
        self._edit = Qt.QLineEdit()
        self._button = Qt.QPushButton()
        self._button.setText('Search')
        self.connect(self._edit,Qt.SIGNAL('returnPressed()'),self._button.animateClick)
        self.connect(self._button,Qt.SIGNAL('clicked()'),self._emitSearch)
        self.layout().addWidget(self._edit)
        self.layout().addWidget(self._button)

    def connectWithTree(self,tree):
        Qt.QObject.connect(self,Qt.SIGNAL("search(QString)"),tree.findInTree)
    
    def _emitSearch(self):
        text = self._edit.text()
        if text: 
            self.emit(Qt.SIGNAL("search(QString)"), text)
        return

SearchEdit = TaurusDevTreeOptions
    
#####################################################################################
    
class ServerBrowser(TaurusDevTree):
    """ This class is used only when browsing by Server/Instance instead of Domain/Family/Member scheme """
    
    def getDeviceDict(self,filters):
        '''
        This method build a dictionary of instances and devices depending on the given servers,devices or instances in QTProperty or in another widget
        --- filters is a string with names of devices/servers such as "LT/VC/ALL,LT02/VC/IP-01" or "modbus,pyplc"
        --- filters is a list of devices such as ["LT/VC/ALL","LT02/VC/IP-01"]
        '''
        self.trace('In TaurusDevTree.buildDictFromFilters(%s)'%filters)
        self._filters = filters
        if type(filters)==type("") or isinstance(filters,Qt.QString):#@TODO:QString and QStringList should not be used (They disappear in API2)
            filters = str(filters).split(',')
        elif isinstance(filters,Qt.QStringList): #@TODO:QString and QStringList should not be used (They disappear in API2)
            filters = list(filters)
        elif type(filters)!=type([]):
            self.debug("'filters' has to be a string or the list type!")
        vals = {}
        if not filters: return vals
        if filters[0].count('/')==0:
            self.debug('In TaurusDevTree.buildDictFromFilters(%s): Getting Servers'%filters)
            targets,addMe = self.db.get_server_name_list(),self.addInstToServ #Searching servers
        elif filters[0].count('/')==1:
            self.debug('In TaurusDevTree.buildDictFromFilters(%s): Getting Instances'%filters)
            targets,addMe = self.db.get_server_list(),self.addDevToInst #Searching instances
        elif filters[0].count('/')==2:
            self.debug('In TaurusDevTree.buildDictFromFilters(%s): Getting Devices'%filters)
            targets,addMe = self.db.get_device_exported("*"),lambda s: {s:{}} #self.addAttrToDev #Searching devices
        else:
            raise Exception('UnknownFilter!: %s'%filters[0])
        
        for t in targets:
            for f in filters:
                f = str(f)
                exp = f.replace('*','.*').lower() if '*' in f and '.*' not in f else f.lower()
                if re.match(exp,t.lower()):
                    self.debug('Adding node %s'%t)
                    vals[t] = addMe(t) 
        self.trace('Out of TaurusDevTree.getDeviceDict(%s)'%filters)
        return vals

    def addInstToServ(self,my_server):
        dict = {}
        list_inst = self.get_instances_for_server(my_server)
        lower_list_inst = [s.lower() for s in list_inst]
        for my_inst in lower_list_inst:
            if self._expand:
                dict[my_inst] = self.addDevtoInst(my_inst)
            else:
                dict[my_inst] = 0
        return dict

    def addDevtoInst(self,my_inst,expand_attrs = False):
        d = {}
        list_dev = self.get_devices_for_instance(my_inst)
        lower_list_dev = [s.lower() for s in list_dev]
        for my_dev in lower_list_dev:
            if self._expand:
                d[my_dev] = self.addAttrToDev(my_dev) if expand_attrs else {my_dev:{}}
            else:
                d[my_dev] = 0
        return d
            
    def addFamilyToDomain(self,prev,expand_attrs):
        d = {}
        #children = self.get_devices_for_instance(my_inst)
        lower_list_dev = [s.lower() for s in list_dev] #@TODO: list_dev is undefined. Check code
        for my_dev in lower_list_dev:
            if self._expand:
                d[my_dev] = self.addAttrToDev(my_dev) if expand_attrs else {my_dev:{}}
            else:
                d[my_dev] = 0
        return d
            

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Methods  for database commands
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def get_instances_for_server(self, server_name):
        #executable_name = class_name
        instances = self.db.get_instance_name_list(server_name)
        return [server_name+'/'+instance for instance in instances]

    def get_devices_for_instance(self, instance_name):
        devslist = self.db.get_device_class_list(instance_name)
        return [dev for dev in devslist if '/' in dev and not dev.startswith('dserver')]            
            
            
    ##@}
                    
#####################################################################################

class TaurusSearchTree(TaurusWidget):
    """
    This Class is a mere wrapper providing a TaurusDevTree connected with an options panel and some optional checkboxes.
    """
    __pyqtSignals__ = list(getattr(TaurusWidget,'__pyqtSignals__',[]))+[
        "search(QString)",
        "modelChanged(const QString &)",
        "deviceSelected(QString)",
        "addAttrSelected(QStringList)",
        "removeAttrSelected(QStringList)",
        "refreshTree",
        "nodeFound"
        ]
    __slots__ = (
        "setTangoHost",
        #"setModel",
        "addModels",
        "setModelCheck",
        "setTree",
        "findInTree",
        "expandAll",
        "loadTree",
        )        
    
    @staticmethod
    def method_forwarder(*args,**kwargs):
        m,o = kwargs['method'],kwargs['object']
        #print 'Calling %s.%s'%(o,m)
        getattr(o.__class__,m)(o,*args)

    def defineStyle(self):
        #print('In TaurusSearchTree.defineStyle()')
        self.setWindowTitle('TaurusDevTree')
        self.setLayout(Qt.QVBoxLayout())
        self.edit = TaurusDevTreeOptions(self)
        self.tree = TaurusDevTree(self)
        self.layout().addWidget(self.edit)
        self.layout().addWidget(self.tree)
        self.registerConfigDelegate(self.tree)
        #Slot forwarding ...
        for k in TaurusDevTree.__dict__.keys():
            #if k in ['__init__','defineStyle']: continue
            if k not in self.__slots__: continue
            try: setattr(self,k,partial(self.method_forwarder,method=k,object=self.tree))
            except Exception,e: self.warning('Unable to add slot %s: %s'%(k,e))
        #Event forwarding ...
        for signal in TaurusDevTree.__pyqtSignals__:
            #Qt.QObject.connect(self,Qt.SIGNAL("search(QString)"),tree.findInTree)
            #self.emit(Qt.SIGNAL("search(QString)"), text)
            Qt.QObject.connect(self.tree,Qt.SIGNAL(signal),lambda args,f=self,s=signal:f.emit(Qt.SIGNAL(s),args))
        self.edit.connectWithTree(self)
        return
        

#####################################################################################

def taurusDevTreeMain():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    
    if False:
        app = Qt.QApplication([])
        args = sys.argv[1:]
        #args = app.get_command_line_args()
        #app = TaurusApplication(sys.argv)
        if not args: args = ['database']
    else:
        taurus.setLogLevel(taurus.Debug)
        parser = argparse.get_taurus_parser()
        parser.set_usage("%prog [options] devname [attrs]")
        parser.set_description("Taurus Application inspired in Jive and Atk Panel")
        parser.add_option("--config", "--config-file", dest="config_file", default=None,
                  help="use the given config file for initialization")
        app = TaurusApplication(cmd_line_parser=parser,app_name="TaurusDevicePanel",
                                app_version=taurus.Release.version)
        args = app.get_command_line_args()
        options = app.get_command_line_options()
        
    form = TaurusSearchTree()
    #try:
        #if options.tango_host is None:
            #options.tango_host = taurus.Database().getNormalName()
        #form.setTangoHost(options.tango_host)
    #except: pass
    
    def trace(m): print(m)
    [setattr(form.tree,f,trace) for f in ('info','warning','error','trace')]
    
    form.setLogLevel(taurus.Debug)
    form.tree.setLogLevel(taurus.Debug)
    #set a model list from the command line or launch the chooser  
    if options.config_file is not None: 
        form.tree.loadConfigFile(options.config_file)
    if len(args)>0:
        models=args
        form.setModel(models)
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    taurusDevTreeMain()