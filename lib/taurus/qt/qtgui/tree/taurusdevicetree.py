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

__all__ = ["TaurusDevTree"]

import random,time,os,re,traceback
import PyTango # to change!!
import subprocess

try:import icons_dev_tree
except:icons_dev_tree = None

from taurus.qt import Qt, QtCore, QtGui
from PyQt4 import Qwt5

import taurus.core
from taurus.core.util import DEVICE_STATE_PALETTE,ATTRIBUTE_QUALITY_PALETTE
from taurus.qt.qtgui.base import TaurusBaseComponent, TaurusBaseWidget


class TaurusDevTree(QtGui.QTreeWidget, TaurusBaseWidget):
    ''' This widget display the list of servers, devices or instances. '''
    __pyqtSignals__ = ("modelChanged(const QString &)","deviceSelected(QString)",\
            "addAttrSelected(QStringList)","removeAttrSelected(QStringList)","refreshTree",)

    def __init__(self, parent=None, designMode = False):
        name = "TaurusDevTree"
        self._useParentModel = True
        self._localModel = ''
        self.call__init__wo_kw(QtGui.QTreeWidget, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        ##self.call__init__(TaurusBaseWidget, name, parent, designMode=designMode)
        #if isinstance(parent,TaurusBaseWidget): #It was needed to avoid exceptions in TaurusDesigner!
            #print 'in DbWidget->TaurusBaseWidget __init__(parent)'
            #self.call__init__(TaurusBaseWidget, name, parent, designMode=designMode)
        #else:
            #print 'in DbWidget->TaurusBaseWidget __init__()'
          ##self.call__init__(TaurusBaseWidget, name, designMode=designMode)
          #self.call__init__(TaurusBaseWidget, name, designMode=designMode)

        self.setObjectName(name)
        #self.setModelCheck('controls01:10000')
        self.defineStyle()
        self.__filters = ""
        self.__expand =1
        self.index = 0
        self._nameTopItem = ""
        self._filters = None
        
        self.DeviceMenu = {
            'Show Panel':'showPanel',
            'Show AtkPanel':'showAtkPanel',
            'Show Properties':'showProperties',
            'Refresh Tree':'refreshTree',
            }
        
        self.AttributeMenu = [
            ('Add to trends','addToPlot'),
            ('Remove from trends','removeFromPlot'),
            #'Refresh Tree':'refreshTree',
            ]        
        
        #Signal
        QtCore.QObject.connect(self,QtCore.SIGNAL("itemClicked (QTreeWidgetItem *,int)"),self.deviceClicked)
        #QtCore.QObject.connect(self,QtCore.SIGNAL("itemSelectionChanged()"),self.deviceSelected) #Redudant
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # My methods 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def deviceClicked(self,item,column):
        self.info("In TaurusDevTree.deviceClicked(%s)"%item.text(column))
        self.deviceSelected(self.getNodeDeviceName())
        
    def deviceSelected(self,device_name=''):
        '''QSIGNAL: this method is used to emit deviceSelected(QString) signal'''
        self.info("In TaurusDevTree.deviceSelected(%s)"%device_name)
        try:
            #item = self.currentItem()
            device_name = device_name or self.getNodeDeviceName()#item.text(0)
            if str(device_name).count('/')!=2: return
            #Signal
            self.trace('TaurusTree emit deviceSelected(%s) signal ...'%device_name)
            self.emit(QtCore.SIGNAL("deviceSelected(QString)"), QtCore.QString(device_name))
        except:
            self.error(traceback.format_exc())
            pass
        
    ########################################################################################################################3
        
    ## @name Context Menu Actions
    # @{
        
    def getNodeText(self,node=None):
        if node is None: node = self.currentItem()
        return str(node.text(0)).strip().split(' ')[0]
    
    def getNodeDeviceName(self,node = None):
        if node is None: node = self.currentItem()
        return str(getattr(node,'DeviceName','')) or self.getNodeText(node)
        
    def getNodeAlias(self,node = None):
        if node is None: node = self.currentItem()        
        alias = getattr(node,'AttributeAlias','')
        return (alias or self.getNodeText(node))

    def contextMenuEvent(self,event):
        ''' 
        This function is called when right clicking on TaurusDevTree area. 
        A pop up menu will be shown with the available options. 
        Menus are managed using two tuple lists for each node: node.ContextMenu and node.ExpertMenu
        '''
        node = self.currentItem() 
        obj = self.getNodeDeviceName(node)        
        
        if not hasattr(node,'ContextMenu'): node.ContextMenu=[]
            
        if not 'Search ...' in [k for k,a in node.ContextMenu]: ##Creating default menu
            if obj.count('/')==2:
                #Menu for devices
                node.ContextMenu.append(("Show Panel", self.showAtkPanel))
                node.ContextMenu.append(("Show Attributes",self.addAttrToNode))
                node.ContextMenu.append(("Go to %s Controller"%getattr(node,'DefaultParent',"Parent"),\
                    lambda: self.findInTree(getattr(self.currentItem(),'DefaultParent',''))
                    ))
                
                if not hasattr(node,'ExpertMenu'): setattr(node,'ExpertMenu',[])
                if not 'Show Properties' in [k for k,a in node.ExpertMenu]:
                    node.ExpertMenu.append(("Show Properties", self.showProperties))
                    def test_device():
                        device = str(self.getNodeDeviceName())
                        if device:
                            comm = 'tg_devtest %s &'%device
                            #subprocess.Popen(['atkpanelALBA',device]) #It works!!!
                            #subprocess.Popen(['tg_devtest',device]) #But this fails!?!
                            os.system(comm)
                        else: self.debug('TaurusDevTree.TestDevice: Selected Device is None!')
                    node.ExpertMenu.append(("Test Device", test_device))
                node.ContextMenu.append(('',None))
                
            elif obj.count('/')==3:
                #Menu for attributes
                for k,v in self.AttributeMenu:
                    self.info('Adding action %s'%k)
                    if type(v) is str and hasattr(self,v):
                        node.ContextMenu.append((k, getattr(self,v)))
                    else:
                        node.ContextMenu.append((k, lambda s=self.getNodeAlias(node): v(s)))
                #node.ContextMenu.append(("add to Trends", self.addToPlot))
                #node.ContextMenu.append(("remove from Trends", self.removeFromPlot))
                node.ContextMenu.append(('',None))    
            
            node.ContextMenu.append(("Expand Node", self.expandAll))
            node.ContextMenu.append(("Collapse Node", self.collapseAll))
            node.ContextMenu.append(("Collapse All", lambda: self.collapseAll(ALL=True)))
            node.ContextMenu.append(("Search ...",\
                lambda: self.findInTree(str(QtGui.QInputDialog.getText(self,'Search ...','Write a part of the name',QtGui.QLineEdit.Normal)[0]))
                ))
        #configDialogAction = menu.addAction("Refresh Tree")
        #self.connect(configDialogAction, QtCore.SIGNAL("triggered()"), self.refreshTree)
        menu = Qt.QMenu(self)
        
        if hasattr(node,'ContextMenu'):
            last_was_separator = True
            for t in (type(node.ContextMenu) is dict and node.ContextMenu.items() or node.ContextMenu):
                try:
                    k,action = t
                    if k:
                        configDialogAction = menu.addAction(k)
                        if action: self.connect(configDialogAction, QtCore.SIGNAL("triggered()"), action)
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
                        if action: self.connect(configDialogAction, QtCore.SIGNAL("triggered()"), action)
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
        
    def showPanel(self):
        '''Display widget taurusDevicePanel'''
        device = self.getNodeText()
        try:
            from taurusDevicePanel import taurusDevicePanel
        except:
            from taurusPanel.taurusDevicePanel import taurusDevicePanel
        nameclass = taurusDevicePanel()
        nameclass.setModel(device)
        nameclass.setSpectraAtkMode(True)
        #nameclass.show()
        obj = newDialog(self)
        obj.initComponents(nameclass)
        obj.setModal(False)
        obj.setVisible(True)
        obj.exec_()

    def showAtkPanel(self):
        '''Open AtkPanel'''
        device = self.getNodeText()
        #tg_host = os.environ.get('TANGO_HOST')
        #javalib = '/homelocal/sicilia/lib/java'
        #classpath = '%s/atkpanel.jar:%s/ATKCore.jar:%s/ATKWidget.jar:%s/TangORB.jar'%(javalib,javalib,javalib,javalib)
        #command = ['/usr/bin/java','-classpath', classpath, '-DTANGO_HOST=%s' % tg_host,'atkpanel.MainPanel',device]
        #subprocess.Popen(command)
        
        ##srubio@cells.es: Modified to use the improved and sorted version of ATKPanel
        subprocess.Popen(['atkpanelALBA',device])

    def showProperties(self):
        '''Display widget TaurusPropTable'''
        import taurus.qt.qtgui.table
        device = self.getNodeText()
        nameclass = taurus.qt.qtgui.table.TaurusPropTable()
        nameclass.setTable(device)
        obj = newDialog(self)
        obj.initComponents(nameclass)
        obj.setModal(False)
        obj.setVisible(True)
        obj.exec_()

    def addToPlot(self):
        item = self.currentItem()
        attr = self.getNodeAlias(item)
        self.info('In addToPlot(%s->%s)'%(item.text(0),attr))
        #item2 = item.parent()
        #dev = item2.text(0).split(' ')[0]
        #devattr = str(dev) + "/" + str(attr)
        self.emit(QtCore.SIGNAL("addAttrSelected(QStringList)"),QtCore.QStringList([str(attr)]))

    def removeFromPlot(self):
        item = self.currentItem()
        attr = getattr(item,'AttributeAlias','') or self.getNodeText(item)
        #item2 = item.parent()
        #dev = item2.text(0).split(' ')[0]
        #devattr = str(dev) + "/" + str(attr)
        self.emit(QtCore.SIGNAL("removeAttrSelected(QStringList)"),QtCore.QStringList([str(attr)]))

    def refreshTree(self):
        self.setTree(self._filters)
        self.emit(QtCore.SIGNAL("refreshTree"))

    ## @}
    ########################################################################################################################
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    ## @name Methods for building server/devices/attributes tree
    # @{
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def buildDictFromFilters(self,filters):	
        '''
        This method build a dictionary of instances and devices depending on the given servers,devices or instances in QTProperty or in another widget
        --- filters is a string with names of devices/servers such as "LT/VC/ALL,LT02/VC/IP-01" or "modbus,pyplc"
        --- filters is a list of devices such as ["LT/VC/ALL","LT02/VC/IP-01"]
        '''
        self.info('In TaurusDevTree.buildDictFromFilters(%s)'%filters)
        self._filters = filters
        self.db = self.getModelObj()
        if type(filters)==type("") or isinstance(filters,QtCore.QString):
            filters = str(filters).split(',')
        elif isinstance(filters,QtCore.QStringList):
            filters = list(filters)
        elif type(filters)!=type([]):
            self.info("'filters' has to be a string or the list type!")
        vals = {}
        if not filters: return vals
        if filters[0].count('/')==0:
            self.info('In TaurusDevTree.buildDictFromFilters(%s): Getting Servers'%filters)
            targets,addMe = self.db.get_server_name_list(),self.addInstToServ #Searching servers
        elif filters[0].count('/')==1:
            self.info('In TaurusDevTree.buildDictFromFilters(%s): Getting Instances'%filters)
            targets,addMe = self.db.get_server_list(),self.addDevToInst #Searching instances
        elif filters[0].count('/')==2:
            self.info('In TaurusDevTree.buildDictFromFilters(%s): Getting Devices'%filters)
            targets,addMe = self.db.get_device_exported("*"),lambda s: {s:{}} #self.addAttrToDev #Searching devices
        else:
            raise Exception('UnknownFilter!: %s'%filters[0])
        
        for t in targets:
            for f in filters:
                f = str(f)
                exp = f.replace('*','.*').lower() if '*' in f and '.*' not in f else f.lower()
                if re.match(exp,t.lower()):
                    self.info('Adding node %s'%t)
                    vals[t] = addMe(t) 
        self.info('Out of TaurusDevTree.buildDictFromFilters(%s)'%filters)
        return vals

    def checkifexist(self,name,list_):
        lower_list = [s.lower() for s in list_]
        name = str(name).lower()
        b = 0
        if name in lower_list:
            b = 1
        return b   

    def addInstToServ(self,my_server):
        dict = {}
        list_inst = self.get_instances_for_server(my_server)
        lower_list_inst = [s.lower() for s in list_inst]
        for my_inst in lower_list_inst:
            if self.__expand:
                dict[my_inst] = self.addDevtoInst(my_inst)
            else:
                dict[my_inst] = 0
        return dict

    def addDevtoInst(self,my_inst,expand_attrs = False):
        dict = {}
        list_dev = self.get_devices_for_instance(my_inst)
        lower_list_dev = [s.lower() for s in list_dev]
        for my_dev in lower_list_dev:
            if self.__expand:
                dict[my_dev] = self.addAttrToDev(my_dev) if expand_attrs else {my_dev:{}}
            else:
                dict[my_dev] = 0
        return dict
            
    def addFamilyToDomain(self,prev,expand_attrs):
        dict = {}
        children = self.get_devices_for_instance(my_inst)
        lower_list_dev = [s.lower() for s in list_dev]
        for my_dev in lower_list_dev:
            if self.__expand:
                dict[my_dev] = self.addAttrToDev(my_dev) if expand_attrs else {my_dev:{}}
            else:
                dict[my_dev] = 0
        return dict

    def addAttrToDev(self,my_device,expert=False,allow_types=[PyTango.DevDouble,PyTango.DevFloat,PyTango.DevLong,PyTango.DevLong64,PyTango.DevULong,PyTango.DevShort,PyTango.DevUShort,PyTango.DevBoolean]):
        """ This command returns the list of attributes of a given device applying display level and type filters.
        @argin expert If False only PyTango.DispLevel.OPERATOR attributes are displayed
        @argin allow_types Only those types included in the list will be displayed (numeric types only by default)
        """
        #self.list_attr = self.db.get_device_attribute_list(my_device,'*')   #BUG    
        self.info('In addAttrToDev(%s)'%my_device)
        try:
            proxy = PyTango.DeviceProxy(my_device)
            timeout = proxy.get_timeout_millis()
            try:
                proxy.set_timeout_millis(50)
                proxy.ping()
                list_attr = proxy.attribute_list_query()
                proxy.set_timeout_millis(timeout)
            except: 
                self.error(traceback.format_exc())
                list_attr = []
            dict = {}
            for aname,my_attr in sorted([(a.name,a) for a in list_attr]):
                if my_attr.data_type not in allow_types: continue
                if not expert and my_attr.disp_level==PyTango.DispLevel.EXPERT: continue
                label = aname==my_attr.label and aname.lower() or "%s (%s)"%(aname.lower(),my_attr.label)
                dict[str(my_device).lower()+'/'+label] = 0
        except PyTango.DevFailed,e:
            self.warning('addAttrToDev(%s): %s'%(my_device,str(e)))
        except Exception,e:
            self.warning('addAttrToDev(%s): %s'%(my_device,str(e)))
        return dict
            
    def addAttrToNode(self):
        node = self.currentItem()
        dev = self.getNodeDeviceName(node)
        self.info('In addAttrToNode(%s)'%dev)
        attrs = self.addAttrToDev(dev)
        children = [str(node.child(i).text(0)).lower() for i in range(node.childCount())]
        for aname in sorted(attrs):
            if aname.lower() not in children:
                natt = self.createItem(node,aname)
                natt.IsAttribute = True
                alias = getattr(node,'AttributeAlias',{}) #it gets all aliases for this device attributes
                self.info('Got aliases for %s: %s' % (aname,alias))
                [setattr(natt,'AttributeAlias',v) for k,v in alias.items() if k in aname.lower()]
        node.setExpanded(True)
        return
            
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
    ############################################################################################################################3

    @QtCore.pyqtSignature("setTree(QString)")
    def setTree(self,filters):
        '''
        This method show a list of instances and devices depending on the given servers in QTProperty or in another widget, 
        this method can be used to connect TaurusDevTree with another widget such as LineEdit.
        '''
        self.clear()
        self.drawTree(self,self.buildDictFromFilters(filters))

    def drawTree(self,item,diction):
        for node in sorted(diction.keys()):
            assert int(self.index)<10000000000,'TooManyIterations!'
            self.index = self.index + 1
            if diction[node]<>0:
                item1 = self.createItem(item,node)
                item1.DefaultParent = hasattr(item,'text') and str(item.text(0)).split()[0] or ''
                self.drawTree(item1,diction[node])
            else:
                item2 = self.createItem(item,node)

    def createItem(self,obj,value):
        USE_TREE_NODE = False
        if USE_TREE_NODE: item = TaurusTreeNode(obj)
        else: item = QtGui.QTreeWidgetItem(obj)
        item.setText(0,QtGui.QApplication.translate('',value, None, QtGui.QApplication.UnicodeUTF8))
        return item
    
    def getAllNodes(self):
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
        
    def expandAll(self,ALL=False,filters='',fun=None):
        #for node in self.getAllNodes().values():
            #if not any((node.isDisabled(),node.isExpanded())):
                #node.setExpanded(True)
        filters = str(filters).lower()
        self.debug( 'In TaurusTree.expandAll(%s)'%filters)
        def expand_child_nodes(node):
            if fun: fun(node)
            result = not filters
            propagate = not filters
            for j in range(node.childCount()): #Searches on each branch of tree
                result = not filters
                child = node.child(j)
                if all([re.search(f,str(child.text(0)).lower()) for f in filters.split()]): #A matching node found 
                #if re.search(str(filters).replace(' ','.*')):
                    self.debug('In TaurusTree.expandAll(%s): %s matches!'%(filters,str(child.text(0)).lower()))
                    child.setExpanded(True)
                    result = child.text(0)
                    
                children = expand_child_nodes(child)
                if children: self.debug( 'In TaurusTree.expandAll(%s): %s contains %s!'%(filters,child.text(0),children))
                if (children or result) and not propagate: 
                    node.setExpanded(True)
                    propagate = children or result
            
            if propagate: self.debug( 'expand_child_nodes(%s): Passing %s to the top branch' % (node.text(0),propagate))
            return propagate #Propagate is True if there's a match in any of children nodes (result is reset for every branch, propagate for every top)
            
        found = []            
        if ALL:
            for i in range(self.topLevelItemCount()):
                res = expand_child_nodes(self.topLevelItem(i))
                if res: found.append(str(res))
        else: 
            res = expand_child_nodes(self.currentItem())
            if res: found.append(str(res))
        return found
    
    def collapseAll(self,ALL=False,filters='',fun=None):
        """ Collapses the whole tree or from a given node.
        @argin ALL tells whether to collapse from current item or the whole tree
        @argin filters Allows to set a list of nodes to not be filtered
        
        """
        #for node in self.getAllNodes().values():
            #if any((node.isDisabled(), node.isExpanded())):
                #node.setExpanded(False)
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
            
    def findInNode(self,node,regexp):
        regexp = regexp.lower()
        for child in [node.child(i) for i in range(node.childCount())]:
            if re.search(regexp,str(child.text(0)).lower()): return str(child.text(0))
            next = findInNode(self,child,regexp)
            if next: return next
        return ''
            
    @QtCore.pyqtSignature("findInTree(const QString &)")
    def findInTree(self,regexp,collapseAll=True):
        self.findInTreeOld(regexp,collapseAll)
                
    def findInTreeOld(self,regexp,collapseAll=True):
        self.debug( 'In TaurusTree.findInTree(%s)'%regexp)
        current = self.currentItem() or self.topLevelItem(0)
        #print 'The node %s seems already visible ... collapsing tree'%str(n.text(0))
        if not regexp: return
        elif str(regexp).lower() == str(current.text(0)).lower():
            self.debug('Node already selected')
            return
        self.collapseAll(ALL=collapseAll)
        result = self.expandAll(ALL=True,filters=regexp)
        self.debug( 'expandAll(%s) returned %s: %s' % (regexp,type(result),result))
        if not result: 
            self.warning( 'findInTree(): Node %s not found!?!?! %s'%(regexp,result))
        elif len(result) == 1:
            try:
                self.debug( 'findInTree(): Node %s selected'%result[0])
                node = self.findItems('.*'+str(result[0]).replace(' ','.*')+'.*',Qt.Qt.MatchRegExp|Qt.Qt.MatchRecursive)[0]#self.getAllNodes()[result]
                node.setSelected(True)
                self.setCurrentItem(node)
                self.deviceSelected(result[0]) #Searches must not trigger events!
            except: 
                self.warning( 'findInTree(%s): Node %s not found!?'%(regexp,result[0]))
                self.error(traceback.format_exc())
        else:
            self.info('findInTree(%s): %d nodes found, displayed but not selected: %s'%(regexp,len(result),result))
            
    def findInTreeNew(self,regexp,collapseAll=True):
        """ This method has been rejected as it doesn't collapsed well the nodes """
        if '.*' not in regexp:
            if '*' in regexp:regexp = regexp.replace('*','.*')
            target = '.*'+str(regexp).replace(' ','.*')+'.*'
            #target = '(%s)|(%s)|(%s)' % (target,target.lower(),target.upper())
        self.debug( 'In TaurusTree.findInTree(%s)'%target)
        try:
            self.info('TaurusDevTree.findInTree(%s): searching in level %d'%(regexp)) 
            items = (self.findItems(target,Qt.Qt.MatchRegExp|Qt.Qt.MatchRecursive))
            if not items:
                QtGui.QMessageBox.warning(None,'Search', 'Nothing found matching %s'%target, QtGui.QMessageBox.Ok)
            else:
                if collapseAll:
                    for i in range(self.topLevelItemCount()):
                        self.collapseItem(self.topLevelItem(i))                
                for it in items:
                    self.expandItem(it)
                node = items[0]                
                node.setSelected(True)
                self.setCurrentItem(node)
        except: 
            self.warning( 'findInTree(): Node %s not found, Exception:'%(target))
            self.traceback()            
            
    def sortCustom(self,order):
        allChildren = {}
        while self.topLevelItemCount(): 
            it = self.takeTopLevelItem(0)
            allChildren[str(it.text(0))]=it
        for rexp in order:
            for c in sorted(allChildren):
                if not re.match(rexp,c): continue
                it = allChildren.pop(c)
                self.debug( 'tree.sortCustom(%s): %s inserted at %d' % (order,it.text(0),self.topLevelItemCount()))
                self.insertTopLevelItem(self.topLevelItemCount(),it)
        
        for k,v in sorted(allChildren.items()): self.insertTopLevelItem(self.topLevelItemCount(),v)
        return

    #@QtCore.pyqtSignature("setIcons")
    def setIcons(self,dct={},root_name=None,regexps=True):
        '''
        This method change the icons depending of the status of the devices
        Dict is a dictionary with name of device and colors such as {name_device:color,name_device2:color2}
        An alternative may be an icon name!
        '''
        #QtGui.QBrush(QtGui.QColor(143,165,203))
        #Qt.QBrush(Qt.Qt.yellow)
        secs = time.time()
        ID = int(100*random.random())
        #self.clear()
        #self.addIcons(root_name,dict)
        state2color = lambda state: QtGui.QColor(DEVICE_STATE_PALETTE.number(state))
        quality2color = lambda attr: QtGui.QColor(ATTRIBUTE_QUALITY_PALETTE.number(quality))

        def update_node(node,key,dct):
            if hasattr(node,'CustomForeground'):
                node.setForeground(0,QtGui.QBrush(QtGui.QColor(node.CustomForeground)))
            if hasattr(node,'CustomBackground'):
                node.setBackground(0,QtGui.QBrush(QtGui.QColor(node.CustomBackground)))            
            elif hasattr(node,'StateBackground'):
                node.setBackground(0,QtGui.QBrush(state2color(dct[key])))
            if hasattr(node,'CustomIcon'):
                node.setIcon(0,QtGui.QIcon(node.CustomIcon))
            else:
                #key = str(node.text(0)).split(' ')[0]
                if key.count('/')==2:
                    self.setStateIcon(node,dct and dct[key] or '')
            return
        
        nodes = self.getAllNodes()
        if not isinstance(dct,dict): 
            dct = dict.fromkeys(dct,'')    

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
            icon = QtGui.QIcon(":/ICON_GREEN")
            child.setIcon(0,icon)
        elif color=="#ff0000" or color in 'OFF,FAULT':
            icon = QtGui.QIcon(":/ICON_RED")
            child.setIcon(0,icon)
        elif color=="#ff8c00" or color in 'ALARM':
            icon = QtGui.QIcon(":/ICON_ORANGE")
            child.setIcon(0,icon)
        elif color=="#ffffff" or color in 'CLOSE,INSERT':
            icon = QtGui.QIcon(":/ICON_WHITE")
            child.setIcon(0,icon)
        elif color=="#80a0ff" or color in 'MOVING,RUNNING':
            icon = QtGui.QIcon(":/ICON_BLUE")
            child.setIcon(0,icon)
        elif color=="#ffff00" or color in 'STANDBY':
            icon = QtGui.QIcon(":/ICON_YELLOW")
            child.setIcon(0,icon)
        elif color=="#cccc7a" or color in 'INIT':
            icon = QtGui.QIcon(":/ICON_BRAWN")
            child.setIcon(0,icon)
        elif color=="#ff00ff" or color in 'DISABLE':
            icon = QtGui.QIcon(":/ICON_PINK")
            child.setIcon(0,icon)
        elif color=="#808080f" or color in 'UNKNOWN':
            icon = QtGui.QIcon(":/ICON_GREY")
            child.setIcon(0,icon)
        else:
            icon = QtGui.QIcon(":/ICON_WHITE")
            child.setIcon(0,icon)        
        

    #@QtCore.pyqtSignature("addIcons")
    def addIcons(self,root_name,dict):
        '''
        This method updates all the icons in the tree using a dictionary.
        But in fact it creates the tree from scratch !?!?!?!
        '''
        filters = dict.keys()
        dicttest = self.buildDictFromFilters(filters)
        topItem = QtGui.QTreeWidgetItem(self)
        self.setTopItemName(root_name)
        #if self._nameTopItem == "":
        #self.drawTree(self,dicttest)
        #else:
        self.drawTree(topItem,dicttest)
        for index in range(topItem.childCount()):
            child = topItem.child(index)
            self.setStateIcon(child)
            
            #list1 =  ["LT/VC/ALL","LT02/VC/IP-01"]
            #self.setIcons2(list1)

    #def setIcons2(self,mylist):
        #'''
        #This method change the icons depending of the status of the devices
        #---- list  is a list of  names of device ["LT/VC/ALL","LT02/VC/IP-01"]
        #'''
        #print "\n\n\n SETICON2 ----------------------------------------------"
        #self.clear()

        #dicttest = self.buildDictFromFilters(mylist)
        #topItem = QtGui.QTreeWidgetItem(self)
        #self.setTopItemName("Testing")

        #self.drawTree(topItem,dicttest)
        #for index in range(topItem.childCount()):
            #child = topItem.child(index)
            #key = str(child.text(0))

            #model = str(mylist[index])
            #model = model+'/state'
            #print "     model = ", model
            #model = "LT02/VC/IP-01/state"
            #myClass.setModel(self,model)

            #v = self.getModelValueObj()
            ##if not value:
            ##    return self.getNoneValue()
            ##self._currText = "ALARM"
            #print "v = ",str(v)
            #bg_brush, fg_brush = QT_DEVICE_STATE_PALETTE.qbrush(self._currText)
            #print bg_brush.color().name(),"  ",fg_brush.color().name(),"\n\n"
            #color = bg_brush.color().name()
            #if color =="#00ff00":#ON,OPEN,EXTRACT
                #icon = QtGui.QIcon(":/ICON_GREEN")
                #child.setIcon(0,icon)
            #elif color =="#ff0000":#OFF,FAULT
                #icon = QtGui.QIcon(":/ICON_RED")
                #child.setIcon(0,icon)
            #elif color =="#ff8c00":#ALARM
                #icon = QtGui.QIcon(":/ICON_ORANGE")
                #child.setIcon(0,icon)
            #elif color =="#ffffff":#CLOSE,INSERT
                #icon = QtGui.QIcon(":/ICON_WHITE")
                #child.setIcon(0,icon)
            #elif color =="#80a0ff":#MOVING,RUNNING
                #icon = QtGui.QIcon(":/ICON_BLUE")
                #child.setIcon(0,icon)
            #elif color =="#ffff00":#STANDBY
                #icon = QtGui.QIcon(":/ICON_YELLOW")
                #child.setIcon(0,icon)
            #elif color =="#cccc7a":#INIT
                #icon = QtGui.QIcon(":/ICON_BRAWN")
                #child.setIcon(0,icon)
            #elif color =="#ff00ff":#DISABLE
                #icon = QtGui.QIcon(":/ICON_PINK")
                #child.setIcon(0,icon)
            #elif color =="#808080f":#UNKNOWN
                #icon = QtGui.QIcon(":/ICON_GREY")
                #child.setIcon(0,icon)
            #else:
                #icon = QtGui.QIcon(":/ICON_WHITE")
                #child.setIcon(0,icon)


    def setTopItemName(self,name):
        self._nameTopItem = name
        topItem = self.topLevelItem(0)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setItalic(True)
        topItem.setFont(0,font)
        topItem.setText(0,name)
        topItem.setExpanded(True)
        if icons_dev_tree is None:
            self.debug('In setTopItemName(...): Icons for states not available!')
        else:
            icon = QtGui.QIcon(":/ICON_FILENEW")
            topItem.setIcon(0,icon)

    def defineStyle(self):
        self.setGeometry(QtCore.QRect(90,60,256,192))

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Methods  for QTProperty "filters" and "expand"
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setFilters(self,filters):
        self.__filters = str(filters)
        self.setTree(self.__filters)

    def getFilters(self):
        return self.__filters

    def resetFilters(self):
        self.__servers=""
        self.setTree(self.__filters)

    def setExpand(self,expand):
        self.__expand = expand

    def getExpand(self):
        return self.__expand

    def resetExpand(self):
        self.__expand = 0

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing methods 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def sizeHint(self):
        return QtGui.QTreeWidget.sizeHint(self)

    def minimumSizeHint(self):
        return QtGui.QTreeWidget.minimumSizeHint(self)

    def getModelClass(self):
        return taurus.core.TaurusDatabase

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.tree'
        ret['group'] = 'Taurus Views'
        ret['icon'] = ":/designer/listview.png"
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setModel(self, m):
        if isinstance(m, Qt.QAbstractItemModel):
            return Qt.QTreeWidget.setModel(self, m)
        return TaurusBaseWidget.setModel(self, m)


    model = QtCore.pyqtProperty("QString", TaurusBaseWidget.getModel, 
                                TaurusBaseWidget.setModel, 
                                TaurusBaseWidget.resetModel)

    filters = QtCore.pyqtProperty("QString", getFilters, setFilters, resetFilters)

    expand = QtCore.pyqtProperty("int", getExpand, setExpand, resetExpand)

    useParentModel = QtCore.pyqtProperty("bool", 
                                         TaurusBaseWidget.getUseParentModel, 
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)


class newDialog(QtGui.QDialog):
    """ This class create the dialog """
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        
    def initComponents(self,newWidget):
        widgetLayout = QtGui.QVBoxLayout(self)
        widgetLayout.setContentsMargins(10,10,10,10)
        widgetLayout.addWidget(newWidget)
        
#####################################################################################
#####################################################################################                    
        
#class TaurusDevTreeItem(QtGui.QTreeWidgetItem, TaurusBaseWidget):
    #def __init__(self, parent=None, designMode = False):
        #try:
            #name = "TaurusDevTree"

            #self.call__init__wo_kw(QtGui.QTreeWidgetItem, parent)
            #self.call__init__(TaurusBaseWidget, name, designMode=designMode)
            
            #self.setObjectName(name)
            ##self.setModelCheck('controls01:10000')
            #self.defineStyle()
            #self.__filters = ""
            #self.__expand =1
            #self.index = 0
            #self._nameTopItem = ""
            #self._filters = None
            ##Signal
            ##QtCore.QObject.connect(self,QtCore.SIGNAL("itemSelectionChanged()"),self.deviceClicked)
        #except Exception,e:
            #self.info('Exception in TaurusDevTreeItem.__init__():' , str(e))
            #self.traceback()                
    #pass
            
class TaurusTreeNode(QtGui.QTreeWidgetItem, TaurusBaseComponent):
    """Base class for all Taurus Tree Node Items"""
    
    #---------------------------------------------------------------------------
    # Write your own code here to define the signals generated by this widget
    #
    __pyqtSignals__ = ("modelChanged(const QString &)",)    
    #__pyqtSignals__ = ("refreshIcon",)
    
    def __init__(self, name = None, parent = None):
        name = name or self.__class__.__name__
        self.call__init__wo_kw(QtGui.QTreeWidgetItem, parent)        
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
        
        state2color = lambda state: QtGui.QColor(DEVICE_STATE_PALETTE.number(state))
        quality2color = lambda attr: QtGui.QColor(ATTRIBUTE_QUALITY_PALETTE.number(attr))
        v = self.getModelValueObj()
        if isinstance(v,PyTango.DevState):
            node.setBackground(0,QtGui.QBrush(state2color(v)))
        if hasattr(v,'quality'):
            self.setForeground(0,QtGui.QBrush(quality2color(v.quality)))

    def isReadOnly(self):
        return True

    def __str__(self):
        return self.log_name + "(" + self.modelName + ")"

    def getModelClass(self):
        return taurus.core.TaurusDevice
    
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
        ##self.connect(self, QtCore.SIGNAL('valueChangedDueToEvent(QString)'), 
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
        ##self.emit(QtCore.SIGNAL('valueChangedDueToEvent(QString)'), 
        ##          QtCore.QString(value_str))
        ##self.disconnect(self, QtCore.SIGNAL('valueChangedDueToEvent(QString)'),
        ##                self.setTextValue)
        ## by default disable widget when dettached
        #self.setEnabled(False)

    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = QtCore.pyqtProperty("QString", TaurusBaseWidget.getModel, 
                                TaurusBaseWidget.setModel, 
                                TaurusBaseWidget.resetModel)
                                
    useParentModel = QtCore.pyqtProperty("bool",
                                         TaurusBaseWidget.getUseParentModel, 
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)

    #---------------------------------------------------------------------------
    # Write your own code here for your own widget properties
    
class SearchEdit(Qt.QWidget):
  """ This class provides a search(QString) signal to be connected to TaurusDevTree.findInTree slot """
  
  __pyqtSignals__ = ("search(QString)",)
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

  def _emitSearch(self):
    text = self._edit.text()
    if text: 
      self.emit(Qt.SIGNAL("search(QString)"), text)
    return
                    
#####################################################################################
#####################################################################################                    

if __name__ == "__main__":
    import sys
    app = Qt.QApplication(sys.argv)
    
    args=sys.argv[1:]
    if not args: args = ['Starter']
    form = TaurusDevTree()
    form.setModel(os.getenv('TANGO_HOST'))
    form.setTree(args)
    form.show()
    sys.exit(app.exec_())
