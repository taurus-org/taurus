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
curveprops: Model and view for curve properties
"""
__all__=['CurveConf','CurvesTableModel','ExtendedSelectionModel','CurvePropertiesView']
#raise NotImplementedError('Under Construction!')

import copy, re

from taurus.qt import Qt, Qwt5
import taurus
import taurus.core
from taurus.qt.qtgui.resource import getThemeIcon
from ui.ui_CurvePropertiesView import Ui_CurvePropertiesView
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE

from curvesAppearanceChooserDlg import NamedLineStyles, ReverseNamedLineStyles, \
                                       NamedCurveStyles, ReverseNamedCurveStyles, \
                                       NamedSymbolStyles, ReverseNamedSymbolStyles, \
                                       NamedColors, CurveAppearanceProperties


#URI regexp including slices in fragment (adapted from http://www.ietf.org/rfc/rfc2396.txt (appendix B))
#   '^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*)(\[[0-9,:]*?\]))?'
#     12            3  4          5       6  7        8 9   A  
#
#we base the nexus and ascii file regexps on this one, keeping the group numbers
#The different components of an URI can be obtained from this regexp using match.group(n1,n2,...), where:
#COMPONENT    GROUP_number
#scheme       2
#authority    4
#path         5
#query        7
#fragment     9
#slice        10 (0xA)
                        
NEXUS_SRC = re.compile(r'^((nxfile|nxdata):)(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*)(\[[0-9,: ]*?\]))?')
ASCII_SRC = re.compile(r'^((file):)(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*)(\[[0-9,: ]*?\]))?')                                                                           


#set some named constants
#columns:
NUMCOLS = 4
X, Y, TITLE, VIS = range(NUMCOLS)
SRC_ROLE =  Qt.Qt.UserRole + 1
PROPS_ROLE = Qt.Qt.UserRole + 2

ATTRNAMEVALIDATOR = taurus.core.taurusvalidator.AttributeNameValidator()

class Component(object):
    def __init__(self, src):
        self.src = src
        self.display = ''
        self.icon = Qt.QIcon()
        self.ok = True
        self._attrnamevalidator = ATTRNAMEVALIDATOR
        self._dbCache = taurus.Database()
        self.setSrc(src)
    
    def update(self):
        self.setSrc(self.src)
    
    def setSrc(self, src):
        self.src, self.display, self.icon, self.ok = self.processSrc(src)
        
    def processSrc(self, src):
        '''returns src,display,icon,ok'''
        src = unicode(src)
        #empty
        if src == '':
            return '', '', Qt.QIcon(),True
        #for formulas
        if src.startswith('='):
            #@todo: evaluate/validate the expression
            return src, src[1:].strip(), getThemeIcon('accessories-calculator'),True
        #for tango attributes
        if self._attrnamevalidator.isValid(src):
            pars = self._attrnamevalidator.getParams(src)
            dev = self._dbCache.getDevice(pars['devicename'])
            if dev is None:
                return src, src, getThemeIcon('network-error'),False
            attr = dev.getAttribute(pars['attributename'])
            if attr is None:
                return src, pars['attributename'], getThemeIcon('network-error'),False            
            return src, attr.name(), getThemeIcon('network-server'),True
        #for nexus files
        m = re.match(NEXUS_SRC,src)
        if m is not None:
            host,path,nxpath,slice = m.group(4,5,9,10) 
            #@todo:open file and check the data is accessible
            return src, nxpath, getThemeIcon('x-office-spreadsheet'), True
        #for ascii files
        m = re.match(ASCII_SRC,src)
        if m is not None:
            host,path, = m.group(4,5)
        #@todo: open and check the file
        #If nothing matches...
        return src, src, getThemeIcon('dialog-warning'), False

class CurveConf(object):
    def __init__(self, xsrc='', ysrc='', properties=None, title='', vis=Qwt5.QwtPlot.yLeft ):
        if properties is None: properties = CurveAppearanceProperties()
        self.properties=properties
        self.title=title
        self.vis=vis
        self.x = Component(xsrc)
        self.y = Component(ysrc)
        
    def __repr__(self):
        ret = "CurveConf(xsrc='%s', ysrc='%s', title='%s')"%(self.x.src, self.y.src, self.title)
        return ret
        


class CurvesTableModel(Qt.QAbstractTableModel):
    ''' A model to manage information about curves to be plotted an their appearance
    '''

    def __init__(self,curves=None):
        if curves is None: curves=[]
        super(CurvesTableModel,self).__init__()
        self.ncolumns = NUMCOLS
        self.curves = curves
    
    def addCurve(self, curveconf ):
        self.curves.append(curveconf)
        
    def dumpData(self):
#        return copy.deepcopy(self.curves)
        return copy.copy(self.curves)
#        return self.curves
    
    def rowCount(self,index=Qt.QModelIndex()):
        return len(self.curves)
    
    def columnCount(self,index=Qt.QModelIndex()):
        return self.ncolumns
        
    def data(self, index, role=Qt.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return Qt.QVariant()
        row=index.row()
        column = index.column()
        #Display Role
        if role == Qt.Qt.DisplayRole:
            if column == X: return Qt.QVariant(Qt.QString(self.curves[row].x.display))
            elif column == Y: return Qt.QVariant(Qt.QString(self.curves[row].y.display))
            elif column == TITLE: return Qt.QVariant(Qt.QString(self.curves[row].title))
            elif column == VIS: return Qt.QVariant(Qt.QString(self.curves[row].vis))
            else: return Qt.QVariant()
        elif role == Qt.Qt.DecorationRole:
            if column == X: return Qt.QVariant(self.curves[row].x.icon)
            elif column == Y: return Qt.QVariant(self.curves[row].y.icon)
            elif column == TITLE: return Qt.QVariant(Qt.QColor(self.curves[row].properties.lColor or 'black'))
            else: return Qt.QVariant()
        elif role == Qt.Qt.TextColorRole:
            if column == X: Qt.QVariant(Qt.QColor(self.curves[row].x.ok and 'green' or 'red'))
            elif column == Y: Qt.QVariant(Qt.QColor(self.curves[row].y.ok and 'green' or 'red'))
            else: return Qt.QVariant()
        elif role == SRC_ROLE:
            if column == X: return Qt.QVariant(Qt.QString(self.curves[row].x.src))
            elif column == Y: return Qt.QVariant(Qt.QString(self.curves[row].y.src))
            else: return Qt.QVariant()
        elif role == PROPS_ROLE:
            return self.curves[row].properties
        elif role == Qt.Qt.ToolTipRole:
            if column == X: return Qt.QVariant(Qt.QString(self.curves[row].x.src))
            elif column == Y: return Qt.QVariant(Qt.QString(self.curves[row].y.src))
            else: return Qt.QVariant()
        if role == Qt.Qt.EditRole:
            if column == X: return Qt.QVariant(Qt.QString(self.curves[row].x.src))
            elif column == Y: return Qt.QVariant(Qt.QString(self.curves[row].y.src))
            elif column == TITLE: return Qt.QVariant(Qt.QString(self.curves[row].title))
            else: return Qt.QVariant()
        #Alignment 
#         elif role == Qt.Qt.TextAlignmentRole:
#             return QVariant(int(Qt.AlignHCenter|Qt.AlignVCenter))
        #Text Color
#        elif role == Qt.Qt.TextColorRole:
#            return Qt.QVariant(Qt.QColor(self.curves[row].properties.lColor or 'black'))
        return Qt.QVariant()
    
    def headerData(self, section, orientation, role=Qt.Qt.DisplayRole):
        if role == Qt.Qt.TextAlignmentRole:
            if orientation == Qt.Qt.Horizontal:
                return Qt.QVariant(int(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter))
            return Qt.QVariant(int(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter))
        if role != Qt.Qt.DisplayRole:
            return Qt.QVariant()
        #So this is DisplayRole...
        if orientation == Qt.Qt.Horizontal:
            if section == X: return Qt.QVariant("X source")
            elif section == Y: return Qt.QVariant("Y Source")
            elif section == TITLE: return Qt.QVariant("Title")
            elif section == VIS: return Qt.QVariant("Shown at")
            return Qt.QVariant()
        else:
            return Qt.QVariant(Qt.QString.number(section+1))
        
    def flags(self, index): #use this to set the editable flag when fix is selected
        if not index.isValid():
            return Qt.Qt.ItemIsEnabled
        column = index.column()
        if column in (X,Y):
            return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled |Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsDragEnabled | Qt.Qt.ItemIsDropEnabled | Qt.Qt.ItemIsSelectable)
        elif column == TITLE:
            return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsDragEnabled)
        return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled |Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsDragEnabled)
                     
    def setData(self, index, value=None, role=Qt.Qt.EditRole):
        if index.isValid() and (0 <= index.row() < self.rowCount()):
            row = index.row()
            curve = self.curves[row]
            if role == PROPS_ROLE:
                self.curves[row].properties = value 
                self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),self.index(row,0), self.index(row,self.ncolumns-1))
            else:
                column = index.column()
                value = Qt.from_qvariant(value, unicode)
                if column == X: curve.x.setSrc(value)
                elif column == Y: curve.y.setSrc(value)
                elif column == TITLE: curve.title = value
                elif column == VIS: curve.vis = value
                self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
            return True
        return False
    
    def insertRows(self, position=None,rows=1,parentindex=None):
        if position is None: position = self.rowCount()
        if parentindex is None: parentindex = Qt.QModelIndex()
        self.beginInsertRows(parentindex, position, position + rows -1)
        slice = [CurveConf() for i in range(rows)]
        self.curves = self.curves[:position]+slice+self.curves[position:]
        self.endInsertRows()
        return True
        
    def removeRows(self, position,rows=1,parentindex=None):
        if parentindex is None: parentindex = Qt.QModelIndex()
        self.beginRemoveRows(parentindex, position, position + rows - 1)
        self.curves = self.curves[:position]+self.curves[position+rows:]
        self.endRemoveRows()
        self.reset()
        return True
    
    def mimeTypes(self):
        result = list(Qt.QAbstractTableModel.mimeTypes(self))
        result += [TAURUS_ATTR_MIME_TYPE, 'text/plain']
        return result
    
    def dropMimeData(self, data, action, row, column, parent):
        if row == -1:
            if parent.isValid(): row = parent.row()
            else: row = parent.rowCount()
        if column == -1:
            if parent.isValid(): column = parent.column()
            else: column = parent.columnCount()
        if data.hasFormat(TAURUS_ATTR_MIME_TYPE):
            self.setData(self.index(row,column), 
                         value=Qt.QVariant(str(data.data(TAURUS_ATTR_MIME_TYPE))))
            return True
        elif data.hasFormat(TAURUS_MODEL_LIST_MIME_TYPE):
            models = str(data.data(TAURUS_MODEL_LIST_MIME_TYPE)).split()
            if len(models) == 1:
                self.setData(self.index(row,column), 
                             value=Qt.QVariant(models[0]))
                return True
            else:
                self.insertRows(row,len(models))
                for i,m in enumerate(models):
                    self.setData(self.index(row+i,column), 
                                 value=Qt.QVariant(m))
                return True
        elif data.hasText():
            self.setData(self.index(row,column), Qt.QVariant(data.text()))
            return True
        return False
    
    def mimeData(self, indexes):
        mimedata = Qt.QAbstractTableModel.mimeData(self, indexes)
        if len(indexes)==1:
#            txt = Qt.from_qvariant(self.data(indexes[0], str)
#            mimedata.setData(TAURUS_ATTR_MIME_TYPE, txt)
            txt = Qt.from_qvariant(self.data(indexes[0], role=SRC_ROLE), str)
            mimedata.setText(txt)
        return mimedata
        #mimedata.setData()





class ExtendedSelectionModel(Qt.QItemSelectionModel):
    '''A QItemSelectionModel subclass that provides :meth:`partiallySelectedRows`'''
    def partiallySelectedRows(self):
        '''
        Returns the row numbers of those rows for which at least one column is selected.
                    
        :return: (list<QModelIndex>) a list of indexes corresponding to the
                 first column of the (partially) selected curves
        '''  
        temp = []
        for index in self.selectedIndexes():
            row = index.row()
            if row not in temp:
                temp.append(row)
        
        model = self.model()
        return [model.index(row, 0) for row in temp]





class CurvePropertiesView(Qt.QAbstractItemView):
    '''This widget is a view on a CurvesTableModel. It displays and allows to change the 
    properties of selected curve(s). Note that this widget does not allow to
    change selection by itself, but rather relies on some other view on the same
    model (like a QTableView) to alter the selection.
    '''
    def __init__(self, parent=None, designMode=False):
        super(CurvePropertiesView,self).__init__(parent)
        
        self.ui = Ui_CurvePropertiesView()
        self.ui.setupUi(self)
        
        
        
        self.ui.sStyleCB.insertItems(0,sorted(NamedSymbolStyles.values()))
        self.ui.lStyleCB.insertItems(0,NamedLineStyles.values())
        self.ui.cStyleCB.insertItems(0,NamedCurveStyles.values())
        self.ui.sColorCB.addItem("")
        self.ui.lColorCB.addItem("")
        for color in NamedColors:
            icon=self._colorIcon(color)
            self.ui.sColorCB.addItem(icon, "", Qt.QVariant(Qt.QColor(color)))
            self.ui.lColorCB.addItem(icon, "", Qt.QVariant(Qt.QColor(color)))
        
        self._emptyProps = CurveAppearanceProperties()
        self.showProperties(self._emptyProps)
        
        #Connections
        self.connect(self.ui.sStyleCB,Qt.SIGNAL("currentIndexChanged(const QString&)"),self._onSymbolStyleChanged)
        self.connect(self.ui.sStyleCB,Qt.SIGNAL("currentIndexChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.lStyleCB,Qt.SIGNAL("currentIndexChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.lStyleCB,Qt.SIGNAL("currentIndexChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.lColorCB,Qt.SIGNAL("currentIndexChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.sColorCB,Qt.SIGNAL("currentIndexChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.cStyleCB,Qt.SIGNAL("currentIndexChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.sSizeSB,Qt.SIGNAL("valueChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.lWidthSB,Qt.SIGNAL("valueChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.sFillCB,Qt.SIGNAL("stateChanged(int)"),self.onPropertyControlChanged)
        self.connect(self.ui.cFillCB,Qt.SIGNAL("stateChanged(int)"),self.onPropertyControlChanged)
   
    #------------------------------------------------------------------------------ 
    #Reimplemented functions from base class
                  
    def dataChanged(self, topleft, bottomright):
        '''Reimplemented. See :meth:`Qt.QAbstractItemView.dataChanged` '''
        Qt.QAbstractItemView.dataChanged(self, topleft, bottomright)
        
        #update what the controls are showing only if the changed data affects what is selected
        minrow = topleft.row()
        maxrow = bottomright.row()
        for index in self.selectionModel().partiallySelectedRows():
            row = index.row()
            if row > minrow and row < maxrow:
                self.updateControls()
                return
            
    def selectionChanged(self, selected, deselected):
        '''Reimplemented. See :meth:`Qt.QAbstractItemView.selectionChanged` '''
        Qt.QAbstractItemView.selectionChanged(self, selected, deselected)
        self.updateControls()
    
    def indexAt(self, *args, **kwargs):
        ''' dummy reimplementation'''
        return Qt.QModelIndex()
        
    def visualRect(self, *args, **kwargs):
        ''' dummy reimplementation'''
        return Qt.QRect()
    
    def verticalOffset(self, *args, **kwargs):
        ''' dummy reimplementation'''
        return 0
    
    def horizontalOffset(self, *args, **kwargs):
        ''' dummy reimplementation'''
        return 0
    def visualRegionForSelection(self, *args, **kwargs):
        ''' dummy reimplementation'''
        return Qt.QRegion()
    
    def scrollTo(self, *args, **kwargs):
        ''' dummy reimplementation'''
        pass
    
    #------------------------------------------------------------------------------ 
    
    def _onSymbolStyleChanged(self, text):
        '''Slot called when the Symbol style is changed, to ensure that symbols
        are visible if you choose them
        
        :param text: (str) the new symbol style label
        '''
        text=str(text)
        if self.ui.sSizeSB.value()<2 and not text in ["","No symbol"]:
            self.ui.sSizeSB.setValue(3) #a symbol size of 0 is invisible and 1 means you should use cStyle=dots
            
        
    def blockControlsSignals(self, block):
        '''blocks/unblocks the signals from all the properties controls
        
        :param block: (bool) If True, signals are blocked. If False they are unblocked
        '''
        self.ui.sStyleCB.blockSignals(block)
        self.ui.lStyleCB.blockSignals(block)
        self.ui.lColorCB.blockSignals(block)
        self.ui.cStyleCB.blockSignals(block)
        self.ui.sSizeSB.blockSignals(block)
        self.ui.lWidthSB.blockSignals(block)
        self.ui.sFillCB.blockSignals(block)
        self.ui.cFillCB.blockSignals(block)
        self.ui.sColorCB.blockSignals(block)  
        
    def updateControls(self):
        '''Updates the state of the properties controls to reflect the selection
        '''
        selectedCurves = self.selectionModel().partiallySelectedRows()
        self.showProperties(self._emptyProps)
        if len(selectedCurves) < 1: 
            return
        modeldata = self.model().data
        props = [modeldata(index, PROPS_ROLE) for index in selectedCurves]
        mergedprop = CurveAppearanceProperties.merge(props, conflict=CurveAppearanceProperties.inConflict_none)      
        self.showProperties(mergedprop)
    
        
    def onPropertyControlChanged(self,*args):
        '''slot called whenever one of the controls is changed ''' 
        shownprop = self.getShownProperties()
        data = self.model().data
        setData = self.model().setData
        for index in self.selectionModel().partiallySelectedRows():
            prop = data(index, PROPS_ROLE)
            if prop.conflictsWith(shownprop):
                updatedprop = CurveAppearanceProperties.merge([prop,shownprop], conflict=CurveAppearanceProperties.inConflict_update_a)                   
                setData(index, updatedprop, PROPS_ROLE)
        
    def showProperties(self,prop, blockSignals=True):
        '''Updates the control widgets to show the given properties. 
         
         ..note:: that the signals of the controls may be temporally blocked to
                  prevent loops. See the `blockSignals` parameter.
        
        :param prop: (CurveAppearanceProperties) the properties object
                     containing what should be shown. If a given property is set
                     to None, the corresponding widget will show a "neutral"
                     display
        :param blockSignals: (bool) If True (default) the signals of the control widgets
                             are blocked while updating them to avoid loops.
        '''
        if blockSignals: self.blockControlsSignals(True)
        #set the Style comboboxes
        self.ui.sStyleCB.setCurrentIndex(self.ui.sStyleCB.findText(NamedSymbolStyles[prop.sStyle]))
        self.ui.lStyleCB.setCurrentIndex(self.ui.lStyleCB.findText(NamedLineStyles[prop.lStyle]))
        self.ui.cStyleCB.setCurrentIndex(self.ui.cStyleCB.findText(NamedCurveStyles[prop.cStyle]))
        #set sSize and lWidth spinboxes. if prop.sSize is None, it puts -1 (which is the special value for these switchhboxes)
        self.ui.sSizeSB.setValue(max(prop.sSize,-1)) 
        self.ui.lWidthSB.setValue(max(prop.lWidth,-1))
        #Set the Color combo boxes. The item at index 0 is the empty one in the comboboxes Manage unknown colors by including them
        if prop.sColor is None: index=0 
        else:  index=self.ui.sColorCB.findData(Qt.QVariant(Qt.QColor(prop.sColor)))
        if index==-1: #if the color is not one of the supported colors, add it to the combobox
            index=self.ui.sColorCB.count()  #set the index to what will be the added one
            self.ui.sColorCB.addItem(self._colorIcon(Qt.QColor(prop.sColor)), "", Qt.QVariant(Qt.QColor(prop.sColor)))
        self.ui.sColorCB.setCurrentIndex(index)
        if prop.lColor is None: index=0 
        else:  index=self.ui.lColorCB.findData(Qt.QVariant(Qt.QColor(prop.lColor)))
        if index==-1: #if the color is not one of the supported colors, add it to the combobox
            index=self.ui.lColorCB.count()  #set the index to what will be the added one
            self.ui.lColorCB.addItem(self._colorIcon(Qt.QColor(prop.lColor)), "", Qt.QVariant(Qt.QColor(prop.lColor)))
        self.ui.lColorCB.setCurrentIndex(index)
        #set the Fill Checkbox. The prop.sFill value can be in 3 states: True, False and None
        if prop.sFill is None: checkState=Qt.Qt.PartiallyChecked 
        elif prop.sFill: checkState=Qt.Qt.Checked
        else: checkState=Qt.Qt.Unchecked
        self.ui.sFillCB.setCheckState(checkState)
        #set the Area Fill Checkbox. The prop.cFill value can be in 3 states: True, False and None
        if prop.cFill is None: checkState=Qt.Qt.PartiallyChecked 
        elif prop.cFill: checkState=Qt.Qt.Checked
        else: checkState=Qt.Qt.Unchecked
        self.ui.cFillCB.setCheckState(checkState)
        if blockSignals: self.blockControlsSignals(False)
    
    def getShownProperties(self):
        """Returns a copy of the currently shown properties 
        
        :return: (CurveAppearanceProperties)
        """
        prop=CurveAppearanceProperties()
        #get the values from the Style comboboxes. Note that the empty string ("") translates into None
        prop.sStyle=ReverseNamedSymbolStyles[str(self.ui.sStyleCB.currentText())] 
        prop.lStyle=ReverseNamedLineStyles[str(self.ui.lStyleCB.currentText())]
        prop.cStyle=ReverseNamedCurveStyles[str(self.ui.cStyleCB.currentText())]
        #get sSize and lWidth from the spinboxes
        prop.sSize=self.ui.sSizeSB.value()
        prop.lWidth=self.ui.lWidthSB.value()
        if prop.sSize<0: prop.sSize=None
        if prop.lWidth<0: prop.lWidth=None
        #Get the Color combo boxes. The item at index 0 is the empty one in the comboboxes
        index=self.ui.sColorCB.currentIndex()
        if index==0:prop.sColor=None
        else:prop.sColor=Qt.QColor(self.ui.sColorCB.itemData(index))
        index=self.ui.lColorCB.currentIndex()
        if index==0:prop.lColor=None
        else:prop.lColor=Qt.QColor(self.ui.lColorCB.itemData(index))
        #get the sFill from the Checkbox.
        checkState=self.ui.sFillCB.checkState()
        if checkState==Qt.Qt.PartiallyChecked: prop.sFill=None
        else: prop.sFill=bool(checkState)
        #get the cFill from the Checkbox.
        checkState=self.ui.cFillCB.checkState()
        if checkState==Qt.Qt.PartiallyChecked: prop.cFill=None
        else: prop.cFill=bool(checkState)
        #store the props 
        return copy.deepcopy(prop)

    def _colorIcon(self,color,w=10,h=10):
        '''returns an icon consisting of a rectangle of the given color
        
        :param color: (QColor or something accepted by QColor creator) The color for the icon
        :param w: (int) width of the icon
        :param h: (int) height of the icon
        
        :return: (QIcon)
        '''
        #to do: create a border
        pixmap=Qt.QPixmap(w,h)
        pixmap.fill(Qt.QColor(color))
        return Qt.QIcon(pixmap)
    
    
def main():
    app = Qt.QApplication(sys.argv)
    
    curves=[CurveConf(xsrc='', ysrc='tango://host:1000/a/b/c/d', properties=None, title="tangocurve", vis=Qwt5.QwtPlot.yLeft ),
                CurveConf(xsrc='=[1,2,3]', ysrc='=#2.x**2', properties=None, title="parab", vis=Qwt5.QwtPlot.yLeft)
                ]
    form = CurvePropertiesView()
    form.setModel(CurvesTableModel(curves))
    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    import sys
    main()    
