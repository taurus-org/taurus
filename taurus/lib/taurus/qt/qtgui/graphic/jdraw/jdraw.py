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

"""This module contains the graphics factory for the jdraw file format"""

__all__ = ["TaurusJDrawGraphicsFactory"]

__docformat__ = 'restructuredtext'

import os
import traceback

from taurus.qt import Qt
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.core.util.containers import CaselessDict
from taurus.qt.qtgui.graphic import TaurusBaseGraphicsFactory, \
    TaurusGraphicsScene, TaurusGraphicsItem, parseTangoUri, \
    TaurusTextAttributeItem,TaurusTextStateItem


LINESTYLE_JDW2QT = { 0: Qt.Qt.SolidLine,
                     1: Qt.Qt.DotLine,
                     2: Qt.Qt.DashLine,
                     3: Qt.Qt.DashLine,
                     4: Qt.Qt.DashDotLine }

FILLSTYLE_JDW2QT = { 0: Qt.Qt.NoBrush,
                     1: Qt.Qt.SolidPattern,
                     2: Qt.Qt.BDiagPattern,
                     3: Qt.Qt.FDiagPattern,
                     4: Qt.Qt.DiagCrossPattern,
                     5: Qt.Qt.BDiagPattern,
                     6: Qt.Qt.FDiagPattern,
                     7: Qt.Qt.Dense5Pattern,
                     8: Qt.Qt.Dense7Pattern,
                     9: Qt.Qt.Dense6Pattern,
                     10:Qt.Qt.Dense4Pattern,
                     11:Qt.Qt.RadialGradientPattern }

TEXTHINT_JDW2QT = CaselessDict({ 
    'helvetica'  : Qt.QFont.Helvetica,
    'serif'      : Qt.QFont.Serif,
    'sansserif'  : Qt.QFont.SansSerif,
    'courier'    : Qt.QFont.Courier,
    'Monospaced' : Qt.QFont.Courier,
    'times'      : Qt.QFont.Times,
    ''           : Qt.QFont.AnyStyle,})


class TaurusJDrawGraphicsFactory(Singleton, TaurusBaseGraphicsFactory, Logger):
    
    def __init__(self,parent,alias = None, delayed = False):
        """ Initialization. Nothing to be done here for now."""
        self.myparent=parent
        self.call__init__wo_kw(TaurusBaseGraphicsFactory, parent)
        self._zBufferLevel = 0
        self._delayed = delayed
        self.alias = alias if alias is not None else {}

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        self.call__init__(Logger, self.__class__.__name__) 
        self.call__init__(TaurusBaseGraphicsFactory)
        
    def getZBufferLevel(self):
        return self._zBufferLevel

    def incZBufferLevel(self):
        self._zBufferLevel += 1
        return self._zBufferLevel
        
    def setZBufferLevel(self, level):
        self._zBufferLevel = level
    
    def resetZBufferLevel(self):
        self.setZBufferLevel(0)
    
    def getSceneObj(self,items):
        scene = TaurusGraphicsScene(self.myparent)
        for item in items:
            try:
                if isinstance(item, Qt.QWidget):
                    scene.addWidget(item)
                elif isinstance(item, Qt.QGraphicsItem):
                    scene.addItem(item)
            except:
                self.warning("Unable to add item %s to scene" % str(item))
                self.debug("Details:", exc_info=1)
        return scene
    
    def getObj(self,name,params):
        method_name = 'get' + name.lstrip('JD') + 'Obj'
        try:
            method = getattr(self, method_name)
            obj = method(params)
            obj.setZValue(self.incZBufferLevel())
            return obj
        except:
            self.warning("Error fetching object")
            self.info("Details:", exc_info=1)
            pass
        return None
    
    def getRectangleObj(self,params):
        item = self.getGraphicsItem('Rectangle',params)
        x1, y1, x2, y2 = params.get('summit')
        width = x2 - x1
        height = y2 - y1
        #item.setPos(x1,y1)
        item.setRect(x1,y1,width,height)
        
        return item

    def getRoundRectangleObj(self,params):
        item = self.getGraphicsItem('RoundRectangle',params)
        x1, y1, x2, y2 = params.get('summit')
        width = x2 - x1
        height = y2 - y1
        #item.setPos(x1,y1)
        item.setRect(x1,y1,width,height)
        
        return item
        
    def getLineObj(self,params):
        item = self.getGraphicsItem('Line',params)
        x1,y1,x2,y2 = params.get('summit')
        item.setLine(x1,y1,x2,y2)
        
        return item
    
    def getEllipseObj(self,params):
        item = self.getGraphicsItem('Ellipse',params)
        
        x1, y1, x2, y2 = params.get('summit')
        width = x2 - x1
        height = y2 - y1
        item.setRect(x1,y1,width,height)

        return item        

    def getPolylineObj(self,params):
        item = self.getGraphicsItem('Polyline',params)
        
        polygon = Qt.QPolygonF()
        p = params.get('summit')
        for i in xrange(0,len(p),2):
            polygon.append(Qt.QPointF(p[i],p[i+1]))
        item.setPolygon(polygon)

        return item

    def getSplineObj(self, params):
        item = self.getGraphicsItem('Spline', params)
                
        p = params.get('summit')
        p = [Qt.QPointF(p[i],p[i+1]) for i in xrange(0,len(p),2)]
        item.setControlPoints(p)

        return item

    def getLabelObj(self,params):
        item = self.getGraphicsItem('Label',params)
        
        s = params.get('summit')
        x1, y1 = s[0], s[1]
        item.setPos(x1,y1)
        #Font size and type is set at set_common_params
        txt = params.get('text')
        if txt:
            if any(isinstance(txt,t) for t in (list,tuple,set)): #Parsing several lines of text
                txt = '\n'.join(txt)            
            item.setPlainText(Qt.QString(txt))
            item._currText = txt
        return item        
    
    def getGroupObj(self,params):
        item = self.getGraphicsItem('Group',params)
        s = params.get('summit')
        x1, y1 = s[0], s[1]
        item.setPos(x1,y1)
        children = params.get('children')
        if children:
            for child in children:
                if child:
                    #self.info('jdraw.py: "%s".addItem("%s")'%(str(params.get('name')),str(child)))
                    item.addToGroup(child)
        if item._fillStyle: self.set_item_filling(item,expand=True)
        return item
    
    def getSwingObjectObj(self,params):
        item = self.getGraphicsItem('SwingObject', params)
        s = params.get('summit')
        x1, y1 = s[0], s[1]
        item.setPos(x1,y1)
        ext = params.get('extensions')
        #Font size and type is set at set_common_params
        return item
    
    def getImageObj(self,params):
        item = self.getGraphicsItem('Image',params)
        s = params.get('summit')
        x1, y1 , x2, y2 = s
        item.setPos(x1,y1)
        
        fname = params.get('file_name')
        if fname:
            if os.path.isfile(fname):
                fname = os.path.realpath(fname)
            elif hasattr(self.myparent,'path'):
                #self.info('using path param ...')
                fname = self.myparent.path+os.path.sep+fname
            self.debug('Opening JDImage(%s) = x,y,w,h=%f,%f,%f,%f' % (fname,x1,y1,x2-x1,y2-y1))
            pixmap = Qt.QPixmap(fname)
            item.setPixmap(pixmap.scaled(x2-x1,y2-y1))
            #item.scale(float(w)/pixmap.width(), float(h)/pixmap.height())
        else: 
            self.warning('No filename for image!?!')
        return item
        
    def set_common_params(self,item,params):
        if not item:
            return
        item._params = params
        name = params.get('name')  
        if self.alias: 
            for k,v in self.alias.items():
                name = str(name).replace(k,v)

        #Forcing not-Taurus items to have a name and be able to trigger events
        setattr(item,'_name',name)
        if name and not self._delayed:
            if isinstance(item, TaurusGraphicsItem):
                #self.debug('TaurusJDrawGraphicsFactory.set_common_params(): %s.setModel(%s)'%(item,name))
                item.setModel(name)
            else:
                self.debug('TaurusJDrawGraphicsFactory.set_common_params(%s): %s is not a TaurusGraphicsItem'%(name,type(item).__name__))

        visibilitymapper = params.get('visibilitymapper')
        if not visibilitymapper is None:
            mapping_type = visibilitymapper['mapping_type']
            mode = visibilitymapper['mode']
            default = visibilitymapper['default']
            item._default = default
            item._map = visibilitymapper['map']

        visible = params.get('visible')
        if not visible is None:
            item.setVisible(visible)

        extensions = params.get('extensions')
        if extensions:
            item._extensions = extensions

        if isinstance(item,Qt.QGraphicsTextItem):
            try:
                fnt = params.get('font',None)
                if fnt:
                    family,style,size = fnt
                    f = Qt.QFont(family, int(.85*size), Qt.QFont.Light, False)
                    f.setStyleHint(TEXTHINT_JDW2QT.get(family, Qt.QFont.AnyStyle))
                    f.setStyleStrategy(Qt.QFont.PreferMatch)
                    if style == 1:
                        f.setWeight(Qt.QFont.DemiBold)
                    elif style == 2:
                        f.setItalic(True)
                    elif style == 3:
                        f.setWeight(Qt.QFont.DemiBold)
                        f.setItalic(True)
                    #TODO: Improve code in order to be able to set a suitable font
                    item.setFont(f)                
                fg = params.get("foreground", (0,0,0))
                color = Qt.QColor(fg[0],fg[1],fg[2])
                item.setDefaultTextColor(color)
            except:
                self.warning('jdraw.set_common_params(%s(%s)).(foreground,width,style) failed!: \n\t%s'%(type(item).__name__,name,traceback.format_exc()))

        else:
          try:
              getattr(item,'setPen')
              fg = params.get("foreground", (0,0,0))
              pen = Qt.QPen(Qt.QColor(fg[0],fg[1],fg[2]))
              pen.setWidth(params.get("lineWidth", 1))
              pen.setStyle(LINESTYLE_JDW2QT[params.get("lineStyle", 0)])
              item.setPen(pen)
          except AttributeError,ae:
              pass
          except Exception,e:
              self.warning('jdraw.set_common_params(%s(%s)).(foreground,width,style) failed!: \n\t%s'%(type(item).__name__,name,traceback.format_exc()))

          fillStyle = FILLSTYLE_JDW2QT[params.get('fillStyle', 0)]
          item._fillStyle = fillStyle
          try:
              if hasattr(item,'brush'):
                  brush = Qt.QBrush()
                  if fillStyle == Qt.Qt.RadialGradientPattern:
                      x1, y1, x2, y2 = params.get('summit')
                      w, h = (x2-x1)/2.0, (y2-y1)/2.0
                      gradient = Qt.QLinearGradient(params.get('gradX1',0)+w,
                                                      params.get('gradY1',0)+h,
                                                      params.get('gradX2',0)+w,
                                                      params.get('gradY2',0)+h)
                      c = params.get('gradC1',(0,0,0))
                      gradient.setColorAt(0,Qt.QColor(c[0],c[1],c[2]))
                      c = params.get('gradC2',(255,255,255))
                      gradient.setColorAt(1,Qt.QColor(c[0],c[1],c[2]))
                      brush = Qt.QBrush(gradient)
                  else:
                      brush.setStyle(fillStyle)

                  bg = params.get('background',(255,255,255))
                  brush.setColor(Qt.QColor(bg[0],bg[1],bg[2]))
                  item.setBrush(brush)
          #except AttributeError,ae: pass
          except Exception,e:
              self.warning('jdraw.set_common_params(%s(%s)).(background,gradient,style) failed!: \n\t%s'%(type(item).__name__,name,traceback.format_exc()))
        #self.debug('Out of TaurusJDrawGraphicsFactory.%s.set_common_params(%s)'%(type(item).__name__,name))
        
    def set_item_filling(self,item,pattern=Qt.Qt.Dense4Pattern,expand=False):
        count = 0
        item._fillStyle = item._fillStyle or pattern
        if hasattr(item,'brush'):
            br = item.brush()
            br.setStyle(item._fillStyle)
            item.setBrush(br)
        if expand:
            for c in item.childItems():
                if not c._fillStyle:
                    self.set_item_filling(c,pattern=pattern,expand=True)
        return

if __name__ == "__main__":
    import jdraw_view
    jdraw_view.jdraw_view_main()
