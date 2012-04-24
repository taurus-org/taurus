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
taurusgrid.py: module containing the Taurus Widget: TaurusGrid 
original idea and development by gcuni
integrated with taurus and regular expressions by srubio
alba, 2009
"""

__all__ = ["TaurusGrid"]

__docformat__ = 'restructuredtext'

import re
import operator
import traceback
from functools import partial

from taurus.qt import QtGui, QtCore

import taurus
from taurus.core import TaurusManager
from taurus.core.util import Logger
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.panel import TaurusValue
from taurus.qt.qtgui.display import TaurusValueLabel,TaurusStateLabel
from taurus.qt.qtgui.input import TaurusValueLineEdit

metachars = re.compile('([.][*])|([.][^*])|([$^+\-?{}\[\]|()])')

def re_search_low(regexp,target): return re.search(regexp.lower(),target.lower())
def re_match_low(regexp,target): return re.match(regexp.lower(),target.lower())

def get_all_models(expressions,limit=1000):
    '''
    All devices matching expressions must be obtained.
    For each device only the good attributes are read.
    '''
    print( 'In TaurusGrid.get_all_models(%s:"%s") ...' % (type(expressions),expressions))
    if isinstance(expressions,str):
        if any(re.match(s,expressions) for s in ('\{.*\}','\(.*\)','\[.*\]')):
            #self.debug( 'evaluating expressions ....')
            expressions = list(eval(expressions))
        else:
            #self.debug( 'expressions as string separated by commas ...')
            expressions = expressions.split(',')
            
    elif any(isinstance(expressions,klass) for klass in (QtCore.QStringList,list,tuple,dict)):
        #self.debug( 'expressions converted from list ...')
        expressions = list(str(e) for e in expressions)
        
    #self.debug( 'In TaurusGrid.get_all_models(%s:"%s") ...' % (type(expressions),expressions))
    taurus_db = taurus.core.TaurusManager().getFactory()().getDatabase()
    if 'SimulationDatabase' in str(type(taurus_db)):
        #self.info( 'Using a simulated database ...')
        models = expressions
    else:
        all_devs = taurus_db.get_device_exported('*')
        models = []
        for exp in expressions:
            #self.info( 'evaluating exp = "%s"' % exp)
            exp = str(exp)
            devs = []
            targets = []
            if exp.count('/')==3: device,attribute = exp.rsplit('/',1)
            else: device,attribute = exp,'State'
            
            if any(c in device for c in '.*[]()+?'):
                if '*' in device and '.*' not in device: device = device.replace('*','.*')
                devs = [s for s in all_devs if re_match_low(device,s)]
            else:
                devs = [device]
                
            #self.info( 'TaurusGrid.get_all_models(): devices matched by %s / %s are %d:' % (device,attribute,len(devs)))
            #self.debug( '%s' % (devs))
            for dev in devs:
                if any(c in attribute for c in '.*[]()+?'):
                    if '*' in attribute and '.*' not in attribute: attribute = attribute.replace('*','.*')
                    #taurus_dp = taurus.core.TaurusManager().getFactory()().getDevice( 'test/sim/sergi')
                    try:
                        #taurus_dp = taurus.core.TaurusDevice(dev)
                        taurus_dp = taurus.core.TaurusManager().getFactory()().getDevice(dev)
                        #self.debug( "taurus_dp = %s"%taurus_dp.getFullName())
                        attrs = [att.name for att in taurus_dp.attribute_list_query() if re_match_low(attribute,att.name)]
                        targets.extend(dev+'/'+att for att in attrs)
                    except Exception,e: 
                        #self.warning( 'ERROR! TaurusGrid.get_all_models(): Unable to get attributes for device %s: %s' % (dev,str(e)))
                        pass
                else: targets.append(dev+'/'+attribute)
            #print 'TaurusGrid.get_all_models(): targets added by %s are: %s' % (exp,targets)
            models.extend(targets)
    models = models[:limit]
    print( 'Out of TaurusGrid.get_all_models(...)')
    return models   
                    
def get_readwrite_models(expressions,limit=1000):
    '''
    All devices matching expressions must be obtained.
    For each device only the good attributes are read.
    '''
    #self.debug( 'In TaurusGrid.get_all_models(%s:"%s") ...' % (type(expressions),expressions))
    if isinstance(expressions,str):
        if any(re.match(s,expressions) for s in ('\{.*\}','\(.*\)','\[.*\]')):
            #self.debug( 'evaluating expressions ....')
            expressions = list(eval(expressions))
        else:
            #self.debug( 'expressions as string separated by commas ...')
            expressions = expressions.split(',')
            
    elif any(isinstance(expressions,klass) for klass in (QtCore.QStringList,list,tuple,dict)):
        expressions = list(str(e) for e in expressions)
        
    taurus_db = taurus.core.TaurusManager().getFactory()().getDatabase()
    if 'SimulationDatabase' in str(type(taurus_db)):
      models = expressions
    else:
      all_devs = taurus_db.get_device_exported('*')
      models = []
      for exp in expressions:
          exp = str(exp)
          devs = []
          targets = []
          if exp.count('/')==3: device,attribute = exp.rsplit('/',1)
          else: device,attribute = exp,'State'
          
          if any(c in device for c in '.*[]()+?'):
              if '*' in device and '.*' not in device: device = device.replace('*','.*')
              devs = [s for s in all_devs if re_match_low(device,s)]
          else:
              devs = [device]
              
          for dev in devs:
              if any(c in attribute for c in '.*[]()+?'):
                  if '*' in attribute and '.*' not in attribute: attribute = attribute.replace('*','.*')
                  #taurus_dp = taurus.core.TaurusManager().getFactory()().getDevice( 'test/sim/sergi')
                  try: 
                      taurus_dp = taurus.core.TaurusManager().getFactory()().getDevice(dev)
                      attrs = [att.name for att in taurus_dp.attribute_list_query() if re_match_low(attribute,att.name) and att.isReadOnly()]
                      targets.extend(dev+'/'+att for att in attrs)
#                      for att in attrs:
#                          if taurus.core.TaurusManager().getFactory()().getAttribute(dev+'/'+att).isReadOnly:
#                              continue
#                          targets.extend(dev+'/'+att)
                  except Exception,e: 
                    pass
              else: targets.append(dev+'/'+attribute)
          models.extend(targets)
    models = models[:limit]
    return models

def modelSetter(args):
    print '#'*80
    obj,model = args[0],args[1]
    print 'In modelSetter(%s,%s)' % (str(obj),str(model))
    obj.setModel(model)
    print 'Out of modelSetter(%s,%s)' % (str(obj),str(model))


class TaurusGrid(QtGui.QFrame, TaurusBaseWidget):
    """ TaurusGrid is a Taurus widget designed to represent a set of attributes distributed in columns and rows.
    The Model will be a list with attributes or device names (for devices the State attribute will be shown).
    Each setModel(*) execution will be able to modify the attribute list.
    An example of execution:<pre>
    /usr/bin/python taurusgrid.py "model=lt.*/VC.*/.*/((C*)|(P*)|(I*))" cols=IP,CCG,PNV rows=LT01,LT02
    </pre>
    @author originally developed by gcuni, extended by srubio and sblanch
    @todo Future releases should allow a list of filters as argument
    @todo names/widgets should be accessible as a caselessdict dictionary (e.g. for adding custom context menus)
    @todo refactoring to have methods that add/remove new widgets one by one, not only the whole dictionary
    @todo _TAGS property should allow to change row/columns meaning and also add new Custom tags based on regexp
    """
    
    #---------------------------------------------------------------------------
    # Write your own code here to define the signals generated by this widget
    #
    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    _TAGS = ['DOMAIN','FAMILY','HOST','LEVEL','CLASS','ATTRIBUTE','DEVICE']
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        
        self.call__init__wo_kw(QtGui.QFrame, parent)
        #self.call__init__(TaurusBaseWidget, name, parent, designMode=designMode)
        if isinstance(parent,TaurusBaseWidget): #It was needed to avoid exceptions in TaurusDesigner!
            self.call__init__(TaurusBaseWidget, name, parent, designMode=designMode)
        else:
            self.call__init__(TaurusBaseWidget, name, designMode=designMode)

        self.title = ''
        self.showLabels = True
        self.filter = ''
        self._modelNames = []
        self.row_labels = []
        self.column_labels = []
        self.defineStyle()
        self._others = False
        self._widgets_list = []
        self.hideLabels=False
        self.modelsQueue = Queue.Queue()
        self.modelsThread = TaurusEmitterThread(parent=self,queue=self.modelsQueue,method=modelSetter )
        
    def save(self,filename):
        import pickle
        d = {'model':self.filter,'row_labels':self.row_labels,'column_labels':self.column_labels}
        f = open(filename,'w')
        pickle.dump(d,f)
        f.close()
        
    def load(self,filename):
        import pickle
        f = open(filename)
        d = pickle.load(f)
        f.close()
        self.setRowLabels(d['row_labels'])
        self.setColumnLabels(d['column_labels'])        
        self.setModel(d['model'])
        return self._modelNames 
    
    def defineStyle(self):
        """ Defines the initial style for the widget """
        #-----------------------------------------------------------------------
        # Write your own code here to set the initial style of your widget
        #
        self.setLayout(QtGui.QGridLayout())
        #self.layout().setContentsMargins(0,0,0,0) 
        self.updateStyle()
        
    def sizeHint(self):
        return QtGui.QFrame.sizeHint(self)

    def minimumSizeHint(self):
        return QtGui.QFrame.minimumSizeHint(self)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        #-----------------------------------------------------------------------
        # [MANDATORY]
        # Replace your own code here
        # ex.: return taurus.core.Attribute
        raise RuntimeError("Forgot to overwrite %s.getModelClass" % str(self)) 
        return list
    
    def attach(self):
        """Attaches the widget to the model"""
        
        if self.isAttached():
            return True
        
        #-----------------------------------------------------------------------
        # Write your own code here before attaching widget to attribute connect 
        # the proper signal so that the first event is correctly received by the
        # widget
        #
        # Typical code is:
        #self.connect(self, QtCore.SIGNAL('valueChangedDueToEvent(QString)'), 
        #             self.setTextValue)
        
        
        ret = TaurusBaseWidget.attach(self)
        
        # by default enable/disable widget according to attach state
        self.setEnabled(ret)
        return ret

    def detach(self):
        """Detaches the widget from the model"""
        
        TaurusBaseWidget.detach(self)

        #-----------------------------------------------------------------------
        # Write your own code here after detaching the widget from the model 
        #
        # Typical code is:
        #self.emit(QtCore.SIGNAL('valueChangedDueToEvent(QString)'), 
        #          QtCore.QString(value_str))
        #self.disconnect(self, QtCore.SIGNAL('valueChangedDueToEvent(QString)'),
        #                self.setTextValue)
        
        # by default disable widget when dettached
        self.setEnabled(False)
    
    #---------------------------------------------------------------------------
    # [MANDATORY]
    # Uncomment the following method if your superclass does not provide with a 
    # isReadOnly() method or if you need to change its behavior
    
    #def isReadOnly(self):
    #    return True
    
    def updateStyle(self):
        #-----------------------------------------------------------------------
        # Write your own code here to update your widget style
        self.debug('@'*80)
        self.debug('In TaurusGrid.updateStyle() ....... It seems never called!!!!')
        self.debug('@'*80)
        
        value = self.getShowText() or ''
        if self._setText: self._setText(value) ##It must be included
        #update tooltip
        self.setToolTip(self.getFormatedToolTip()) ##It must be included
                
        # send a repaint in the end
        if hasattr(self,'title_widget'):
            if self.title: self.title_widget.show()
            else: self.title_widget.hide()
        #if hasattr(self,'table'):
            #self.table.resizeColumnsToContents()
            #self.table.resizeRowsToContents()            
            
        if hasattr(self,'modelsThread') and not self.modelsThread.isRunning(): 
            self.debug('<'*80)
            self.modelsThread.start()#self.modelsThread.IdlePriority)
            
        self.update()
        
    #---------------------------------------------------------------------------
    # Write your own code here for your own widget properties
    
    @QtCore.pyqtSignature("setModel(QStringList)")
    def setModel(self,model,devsInRows=False):
        '''The model can be initialized as a list of devices or hosts or ...'''
        #self.setModelCheck(model) ##It must be included
        #differenciate if the model is a RegExp
        model = isinstance(model,(str,QtCore.QString)) and [model] or list(model)
        self.debug('#'*80)
        self.debug('In TaurusGrid.setModel(%s)'%model)
        self.filter = model
        if any('*' in m for m in model):
            model = get_all_models(model)
            self.debug('model was a RegExp, done the query and converted to an attr list')

        if not self._modelNames == []:#clean to start from scratch
            self._modelNames = []
            for widget in self._widgets_list:
                del widget

        #here we always have the reals model list, even if it comes from a regexp
        self._modelNames = model
        self.debug('In setModel(%s): modelNames are %s'%(model,self._modelNames))
        if devsInRows:
            self.setRowLabels(','.join(set(d.rsplit('/',1)[0] for d in self._modelNames)))
        self.create_widgets_table(self._modelNames)
        self.debug('Out of TaurusGrid.setModel(%s)'%model)
        self.updateStyle()
    
    def getModel(self):
        return self._modelNames
    
    def resetModel(self):
        self._modelNames = []
        self.updateFromList(self._modelNames)
        return
    
    @QtCore.pyqtSignature("setTitle(QString)")    
    def setTitle(self,title):
        self.title = str(title)
        if hasattr(self,'title_widget'):
            if title: 
                self.title_widget.setText(self.title)
                self.title_widget.show()
            else: self.title_widget.hide()
    
    def parse_labels(self,text):
        if any(text.startswith(c[0]) and text.endswith(c[1]) for c in [('{','}'),('(',')'),('[',']')]):
            try:
                labels = eval(text)
                return labels
            except Exception,e:
                self.warning('ERROR! Unable to parse labels property: %s'%str(e))
                return []
        else:
            exprs = text.split(',')
            labels = [(':' in e and tuple(e.split(':',1)) or (e,e)) for e in exprs]
            return labels
        
    @QtCore.pyqtSignature("setRowLabels(QStringList)")
    def setRowLabels(self,rows):
        '''The model can be initialized as a list of devices or hosts or ...'''
        #self.setModelCheck(model) ##It must be included
        self.row_labels = self.parse_labels(str(rows))
        try:
            self.rows = [r[0] for r in self.row_labels]
            for i in range(len(self.rows)):
                section = self.rows[i]
                self.table.setVerticalHeaderItem(i,QtGui.QTableWidgetItem(section))
        except Exception,e:
            self.debug("setRowLabels(): Exception! %s"%e)
        #self.create_widgets_table(self._columnsNames)
        
    def getRowLabels(self):
        return ','.join(':'.join(c) for c in self.row_labels)
    
    def resetRowLabels(self):
        self.row_labels = []
        return       
    
    @QtCore.pyqtSignature("setColumnLabels(QStringList)")
    def setColumnLabels(self,columns):
        '''The model can be initialized as a list of devices or hosts or ...'''
        #self.setModelCheck(model) ##It must be included
        self.column_labels = self.parse_labels(str(columns))
        try:
            self.columns = [c[0] for c in self.column_labels]
            for i in range(len(self.columns)):
                equipment = self.columns[i]
                self.table.setHorizontalHeaderItem(i,QtGui.QTableWidgetItem(equipment))
        except Exception,e:
            self.debug("setColumnLabels(): Exception! %s"%e)
        #self.create_widgets_table(self._columnsNames)
        
    def getColumnLabels(self):
        return ','.join(':'.join(c) for c in self.column_labels)
    
    def resetColumnLabels(self):
        self.column_labels = []
        return        

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = QtCore.pyqtProperty("QStringList", getModel, 
                                setModel, 
                                resetModel)
                                
    rowlabels = QtCore.pyqtProperty("QString", getRowLabels, 
                                setRowLabels, 
                                resetRowLabels)

    columnlabels = QtCore.pyqtProperty("QString", getColumnLabels, 
                                setColumnLabels, 
                                resetColumnLabels)
                                
    useParentModel = QtCore.pyqtProperty("bool",
                                         TaurusBaseWidget.getUseParentModel, 
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)

    #---------------------------------------------------------------------------
    # Write your own code here for your own widget properties
              
    def create_widgets_dict(self,models):
        from collections import defaultdict
        values = defaultdict(lambda: defaultdict(list)) #recursive dictionary with 2 levels
        #domains = list(set(m.split('/')[0].upper()))
        #families = list(set(m.split('/')[1].upper()))
        
        if not self.row_labels: #Domains used by default
            self.row_labels = sorted(list(set(m.split('/')[0].upper() for m in models if m.count('/')>=2)))
            self.row_labels = zip(self.row_labels,self.row_labels)
        if not self.column_labels: #Families used by default
            self.column_labels = sorted(list(set(m.split('/')[1].upper() for m in models if m.count('/')>=2)))
            self.column_labels = zip(self.column_labels,self.column_labels)
            
        #for m in models:
            #if m.count('/')<2:
                #self.warning('Wrong model cannot be added: %s'%m)
            #else:
                #domain,family = m.upper().split('/')[:2]
                #values[domain][family].append(m)
                
        row_not_found, col_not_found = False, False                
                
        for m in models:
            row,column = 'Others','Others'
            for label,rexp in self.row_labels:
                if '*' in rexp and '.*' not in rexp: rexp = rexp.replace('*','.*')
                if re_search_low(rexp,m):
                    row = label
                    break
            for label,rexp in self.column_labels:
                if '*' in rexp and '.*' not in rexp: rexp = rexp.replace('*','.*')
                if re_search_low(rexp,m):
                    column = label
                    break
            if 'Others' == row: row_not_found = True
            if 'Others' == column: col_not_found = True
            self.debug('Model %s added to row %s , column %s' % (m,row,column))
            values[row][column].append(m)
        if row_not_found: self.row_labels.append(('Others','.*'))
        if col_not_found: self.column_labels.append(('Others','.*'))
            
        return values
            
    def create_frame_with_gridlayout(self):
        """ Just a 'macro' to create the layouts that seem to fit better. """
        frame = QtGui.QFrame()
        frame.setLayout(QtGui.QGridLayout())
        frame.layout().setContentsMargins(2,2,2,2)
        frame.layout().setSpacing(0)
        frame.layout().setSpacing(0)
        return frame
            
    def create_widgets_table(self,models):
        
        ##Added a title to the panel
        self.title_widget = QtGui.QLabel()
        self.layout().addWidget(self.title_widget,0,0)
        self.setTitle(self.title)
        
        dct = self.create_widgets_dict(models)
        ##Assignments modified to keep the order of labels as inserted in properties
        self.rows = [r[0] for r in self.row_labels]#dct.keys()
        self.columns = [c[0] for c in self.column_labels]#list(set(reduce(operator.add,v.keys()) for v in dct.values()))
        
        values = []
        for row in self.rows:
            line = []
            for col in self.columns:
                #line.append(dct[row][col] if col in dct[row] else [])
                if col in dct[row]: line.append(dct[row][col])
                else: line.append([])
            values.append(line)
            
        ## Here is where the table is created!
        self.table = self.build_table(values)
           
        # SET COLUMN HEADERS (self.columns)
        for i in range(len(self.columns)):
            equipment = self.columns[i]
            self.table.setHorizontalHeaderItem(i,QtGui.QTableWidgetItem(equipment))
            # SOMEDAY THIS WILL BE ICONS
    
        # SET ROW HEADERS (self.rows)
        for i in range(len(self.rows)):
            section = self.rows[i]
            self.table.setVerticalHeaderItem(i,QtGui.QTableWidgetItem(section))
        
#        table.setAutoScroll(True)
#        resize_mode = QtGui.QHeaderView.Stretch
#        table.horizontalHeader().setResizeMode(resize_mode)
        #table.verticalHeader().setResizeMode(resize_mode)
        
#        for row in range(len(self.rows)):
#            table.setRowHeight(row,5+25*sum(len(dct[self.rows[row]][col]) for col in self.columns))
        #for col in range(len(self.columns)):
        #    table.setColumnWidth(col,300)        
        
        use_scroll = False # It didn't work ... it doesn't allow the table widget to resize
        if use_scroll:
            scrollable = QtGui.QScrollArea(self)
            scrollable.setWidget(self.table)
            self.layout().addWidget(scrollable,1,0)
        else: self.layout().addWidget(self.table,1,0)
        
        #-------------------------------------------------------------------------------------
        # SECTION CHECKBOXES
        self.checkboxes_frame = self.create_frame_with_gridlayout()
        
        self.rows_frame = self.create_frame_with_gridlayout()
        self.rows_frame.setFrameStyle(QtGui.QFrame.Box)
        self.checkboxes_frame.layout().addWidget(self.rows_frame,0,0)
        
        self.columns_frame = self.create_frame_with_gridlayout()
        self.columns_frame.setFrameStyle(QtGui.QFrame.Box)
        self.checkboxes_frame.layout().addWidget(self.columns_frame,0,1)
        
        layout_row = 0
        layout_col = 0
        # For all rows, create rows of three checkboxes in order to
        # show or hide the corresponding rows in the table
        for i in range(len(self.rows)):
            section = self.rows[i]
            checkbox = QtGui.QCheckBox(section)
            if checkbox.text() == 'Others':
                checkbox.setChecked(False)
                if not self._others: checkbox.hide()
            else:
                checkbox.setChecked(True)
            self.rows_frame.layout().addWidget(checkbox,layout_row,layout_col)
            layout_col += 1
            if layout_col == 3:
                layout_col = 0
                layout_row += 1
            QtCore.QObject.connect(checkbox,QtCore.SIGNAL('toggled(bool)'),self.show_hide_rows)
        self.show_hide_rows()
        
        layout_row = 0
        layout_col = 0
        # For all self.columns, create rows of three checkboxes in order to
        # show or hide the corresponding columns in the table
        for i in range(len(self.columns)):
            column = self.columns[i]
            checkbox = QtGui.QCheckBox(column)
            if checkbox.text() == 'Others':
                checkbox.setChecked(False)
                if not self._others: checkbox.hide()
            else:
                checkbox.setChecked(True)
            self.columns_frame.layout().addWidget(checkbox,layout_row,layout_col)
            layout_col += 1
            if layout_col == 3:
                layout_col = 0
                layout_row += 1
            QtCore.QObject.connect(checkbox,QtCore.SIGNAL('toggled(bool)'),self.show_hide_columns)
        self.show_hide_columns()
        
        self.layout().addWidget(self.checkboxes_frame,2,0)
        #self.resize(800,600)

    def show_hide_rows(self):
        """
        This needs refactoring to be together with the show_hide_columns method
        """
        for checkbox in self.rows_frame.children():
            if isinstance(checkbox,QtGui.QCheckBox):
                table_row = self.rows.index(checkbox.text())
                if checkbox.isChecked():
                    self.table.showRow(table_row)
                else:
                    self.table.hideRow(table_row)

    def show_hide_columns(self):
        """
        This needs refactoring to be together with the show_hide_rows method
        """
        for checkbox in self.columns_frame.children():
            if isinstance(checkbox,QtGui.QCheckBox):
                table_col = self.columns.index(checkbox.text())
                if checkbox.isChecked():
                    self.table.showColumn(table_col)
                else:
                    self.table.hideColumn(table_col)

    def showOthers(self,boolean):
        self._others = boolean
        if hasattr(self,'rows_frame'):
            for checkbox in self.rows_frame.children():
                if isinstance(checkbox,QtGui.QCheckBox) and checkbox.text() == 'Others':
                    if self._others: checkbox.show()
                    else: checkbox.hide()
        if hasattr(self,'columns_frame'):
            for checkbox in self.columns_frame.children():
                if isinstance(checkbox,QtGui.QCheckBox) and checkbox.text() == 'Others':
                    if self._others: checkbox.show()
                    else: checkbox.hide()

    #FIXME: when they are called before setModel they fails because 
    # frames are not yet created, and it doesn't has memoty about this.
    def showRowFrame(self,boolean):
        if boolean == True:
            self.rows_frame.show()
        else:
            self.rows_frame.hide()
    def showColumnFrame(self,boolean):
        if boolean == True:
            self.columns_frame.show()
        else:
            self.columns_frame.hide()

    def build_table(self,values):
        """
        This is a builder. For all the elements in widgets matrix,
        just set the corresponding cells of the QTableWidget.
        """
        self.debug('In TaurusGrid.build_table(%s)'%values)
        widgets_matrix = self.build_widgets(values,self.showLabels)
        rows = len(widgets_matrix)
        cols = len(widgets_matrix[0])
        
        table = QtGui.QTableWidget()
        table.setItemDelegate(Delegate(table))
        
        table.setRowCount(rows)
        table.setColumnCount(cols)
        for row in range(len(widgets_matrix)):
            for col in range(len(widgets_matrix[row])):
                table.setCellWidget(row,col,widgets_matrix[row][col])
        
        #table.resizeColumnsToContents()
        #table.resizeRowsToContents()
        table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        #table.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        #table.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        table.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        
        return table

    def build_widgets(self,values,show_labels=False,width=240,height=20,value_width=120):
        widgets_matrix = []
        for row in values:
            widgets_row = []
            for cell in row:
                cell_frame = self.create_frame_with_gridlayout()
                count = 0
                for synoptic in cell:
                    self.debug("processing synoptic %s"%synoptic)
                    name = model = synoptic

                    self.debug('Creating TaurusValue with model =  %s'%model)
                    synoptic_value = TaurusValue(cell_frame)    
                    #synoptic_value.setModel(model)
                    self.modelsQueue.put((synoptic_value,model))
                            
                    if self.hideLabels:
                        synoptic_value.setLabelWidgetClass(None)
                    else: 
                        synoptic_value.setLabelConfig('label') ## DO NOT DELETE THIS LINE!!!      
                    cell_frame.layout().addWidget(synoptic_value,count,0)
                    self._widgets_list.append(synoptic_value)
                    count += 1
                widgets_row.append(cell_frame)
            widgets_matrix.append(widgets_row)
        return widgets_matrix
    
    def getItemByModel(self, model, index=0):
        #a particular model can be many times, index means which one of them
        for widget in self._widgets_list:
            #@todo taurus model comparision?
            if widget.getModel().lower() == model.lower():
                if index <= 0:
                    return widget
                else:
                    index -= 1

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.table'
        ret['group'] = 'Taurus Views'
        ret['icon'] = ":/designer/grid.png"
        return ret

import Queue,traceback
class TaurusEmitterThread(QtCore.QThread):
    """
    This object get items from a python Queue and performs a thread safe operation on them.
    It is useful to delay signals in a background thread.
    :param parent: a Qt/Taurus object
    :param queue: if None parent.getQueue() is used, if not then the queue passed as argument is used
    :param target: the method to be executed using each queue item as argument
    """
    def __init__(self, parent=None,queue=None,method=None):
        """Parent most not be None and must be a TaurusGraphicsScene!"""
        #if not isinstance(parent, TaurusGraphicsScene):
            #raise RuntimeError("Illegal parent for TaurusGraphicsUpdateThread")
        QtCore.QThread.__init__(self, parent)
        self.log = Logger('TaurusEmitterThread')
        self.queue = queue
        self.todo = Queue.Queue()
        self.method = method
        self.emitter = QtCore.QObject(QtGui.QApplication.instance())
        self._done = 0
        QtCore.QObject.connect(self.emitter, QtCore.SIGNAL("doSomething"), self._doSomething)
        QtCore.QObject.connect(self.emitter, QtCore.SIGNAL("somethingDone"), self._next)
        self.emitter.moveToThread(QtGui.QApplication.instance().thread())        
        
    def getQueue(self):
        if self.queue: return self.queue
        elif hasattr(self.parent(),'getQueue'): self.parent().getQueue()
        else: return None

    def getDone(self):
        """ Returns % of done tasks in 0-1 range """
        return self._done/(self._done+self.getQueue().qsize()) if self._done else 0.

    def _doSomething(self,args):
        print '#'*80
        self.log.debug('At TaurusEmitterThread._doSomething(%s)'%str(args))
        if self.method: 
            try:
                self.method(args)
            except:
                self.log.error('At TaurusEmitterThread._doSomething(): %s' % traceback.format_exc())
        self.emitter.emit(QtCore.SIGNAL("somethingDone"))
        self._done += 1
        return
        
    def _next(self):
        queue = self.getQueue()
        self.log.debug('At TaurusEmitterThread._next(), %d items remaining.' % queue.qsize())
        if not queue.empty():
            try:
                item = queue.get(False) #A blocking get here would hang the GUIs!!!
                self.todo.put(item)
            except Queue.Empty,e:
                pass
        return
        
    def run(self):
        print '#'*80
        self.log.debug('At TaurusEmitterThread.run()')
        self._next()
        while True:
            item = self.todo.get(True)
            if type(item) in taurus.core.util.types.StringTypes:
                if item == "exit":
                    break
                else:
                    continue
            self.emitter.emit(QtCore.SIGNAL("doSomething"), item)
            #End of while
        self.log.info('Out of TaurusEmitterThread.run()')
        #End of Thread                    
    
class Delegate(QtGui.QItemDelegate):
    
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self,parent)
        
    def sizeHint(self, option, index):
        table = self.parent()
        widget = table.cellWidget(index.row(),index.column())
        size = widget.sizeHint()
        return size

def sysargs_to_dict(defaults=[]):
    import sys
    i,result = 0,{}
    for a in sys.argv[1:]:
        if '=' in a:
            bar = a.split('=')
            if bar[1] in ['True','False']:#convert string to boolean
                bar[1] = eval(bar[1])
            result[bar[0]] = bar[1]
        else:
            result[defaults[i]] = a
            i+=1
    return result
        
        
if __name__ == '__main__':
    import sys   
    if len(sys.argv)<2: 
        print "The format of the call is something like:"
        print '\t/usr/bin/python taurusgrid.py grid.pickle.file'
        print '\t/usr/bin/python taurusgrid.py "model=lt.*/VC.*/.*/((C*)|(P*)|(I*))" cols=IP,CCG,PNV rows=LT01,LT02 others=False rowframe=True colframe=False'
        exit()
        
    app = QtGui.QApplication(sys.argv[0:1])
    gui = TaurusGrid()

    try: #first try if argument is a file to be opened
      filename = sys.argv[1]
      open(filename,'r')
      gui.load(filename)
    except:
      args = sysargs_to_dict(['model','rows','cols','others','rowframe','colframe'])
      print "args = %s"%args
      if args.get('rows'): gui.setRowLabels(args['rows'])
      if args.get('cols'): gui.setColumnLabels(args['cols'])
      if args.get('model'): gui.setModel(args['model'])
      gui.showRowFrame('rowframe' in args and args['rowframe'] and True)
      gui.showColumnFrame('colframe' in args and args['colframe'] and True)
      gui.showOthers('others' in args and args['others'] or True)

    print "current TaurusGrid model= %s"%(gui.getModel())
    gui.show()
    sys.exit(app.exec_())        
        

