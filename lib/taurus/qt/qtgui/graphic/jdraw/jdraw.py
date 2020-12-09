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

"""This module contains the graphics factory for the jdraw file format"""

from __future__ import absolute_import

from builtins import str
from builtins import range

import os
import traceback

from taurus.external.qt import Qt
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
from taurus.core.util.containers import CaselessDict
from taurus.qt.qtgui.graphic import (TaurusBaseGraphicsFactory,
                                     TaurusGraphicsScene, TaurusGraphicsItem)


__all__ = ["TaurusJDrawGraphicsFactory"]

__docformat__ = 'restructuredtext'


LINESTYLE_JDW2QT = {0: Qt.Qt.SolidLine,
                    1: Qt.Qt.DotLine,
                    2: Qt.Qt.DashLine,
                    3: Qt.Qt.DashLine,
                    4: Qt.Qt.DashDotLine}

FILLSTYLE_JDW2QT = {0: Qt.Qt.NoBrush,
                    1: Qt.Qt.SolidPattern,
                    2: Qt.Qt.FDiagPattern,
                    3: Qt.Qt.BDiagPattern,
                    4: Qt.Qt.DiagCrossPattern,
                    5: Qt.Qt.FDiagPattern,
                    6: Qt.Qt.BDiagPattern,
                    7: Qt.Qt.Dense5Pattern,
                    8: Qt.Qt.Dense7Pattern,
                    9: Qt.Qt.Dense6Pattern,
                    10: Qt.Qt.Dense4Pattern,
                    11: Qt.Qt.LinearGradientPattern}

TEXTHINT_JDW2QT = CaselessDict({
    'helvetica': Qt.QFont.Helvetica,
    'serif': Qt.QFont.Serif,
    'sansserif': Qt.QFont.SansSerif,
    'courier': Qt.QFont.Courier,
    'Monospaced': Qt.QFont.Courier,
    'times': Qt.QFont.Times,
    '': Qt.QFont.AnyStyle, })

ALIGNMENT = {
    0: Qt.Qt.AlignHCenter,
    1: Qt.Qt.AlignLeft,
    2: Qt.Qt.AlignRight,
}

VALIGNMENT = {
    0: Qt.Qt.AlignVCenter,
    1: Qt.Qt.AlignTop,
    2: Qt.Qt.AlignBottom,
}


class TaurusJDrawGraphicsFactory(Singleton, TaurusBaseGraphicsFactory, Logger):

    def __init__(self, parent, alias=None, delayed=False):
        """ Initialization. Nothing to be done here for now."""
        self.myparent = parent
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

    def getSceneObj(self, items):
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

    def getObj(self, name, params):
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

    def getRectangleObj(self, params):
        item = self.getGraphicsItem('Rectangle', params)
        x1, y1, x2, y2 = params.get('summit')
        width = x2 - x1
        height = y2 - y1
        # item.setPos(x1,y1)
        item.setRect(x1, y1, width, height)

        return item

    def getBarObj(self, params):
        # TODO: properly implement JDBar support
        # As a workaround, use a filled rectangle as a substitute of a JDBar
        self.warning('JDBar not yet supported. Using a JDRectangle instead')
        if 'fillStyle' not in params:
            params['fillStyle'] = 1

        return self.getRectangleObj(params)

    def getRoundRectangleObj(self, params):
        item = self.getGraphicsItem('RoundRectangle', params)
        x1, y1, x2, y2 = params.get('summit')
        width = x2 - x1
        height = y2 - y1
        cornerWidth = params.get('cornerWidth', 24)
        nbPoints = params.get('step', 6)
        # item.setPos(x1,y1)
        item.setRect(x1, y1, width, height)
        item.setCornerWidth(cornerWidth, nbPoints)

        return item

    def getLineObj(self, params):
        item = self.getGraphicsItem('Line', params)
        x1, y1, x2, y2 = params.get('summit')
        item.setLine(x1, y1, x2, y2)

        return item

    def getEllipseObj(self, params):
        item = self.getGraphicsItem('Ellipse', params)

        x1, y1, x2, y2 = params.get('summit')
        width = x2 - x1
        height = y2 - y1
        item.setRect(x1, y1, width, height)

        return item

    def getPolylineObj(self, params):
        item = self.getGraphicsItem('Polyline', params)

        polygon = Qt.QPolygonF()
        p = params.get('summit')
        for i in range(0, len(p), 2):
            polygon.append(Qt.QPointF(p[i], p[i + 1]))
        item.setPolygon(polygon)

        return item

    def getSplineObj(self, params):
        item = self.getGraphicsItem('Spline', params)
        p = params.get('summit')
        p = [Qt.QPointF(p[i], p[i + 1]) for i in range(0, len(p), 2)]
        item.setControlPoints(p)
        isClosed = params.get('isClosed', True)
        item.setClose(isClosed)
        return item

    def getLabelObj(self, params):
        item = self.getGraphicsItem('Label', params)
        self.readLabelObj(item, params)
        return item

    def readLabelObj(self, item, params):
        origin = params.get('origin')
        item.setPos(origin[0], origin[1])

        summit = params.get('summit')
        x, y = summit[0] - origin[0], summit[1] - origin[1]
        width, height = summit[2] - summit[0], summit[3] - summit[1]
        item.setRect(x, y, width, height)

        # it is parsed as a float
        vAlignment = int(params.get('vAlignment', 0))
        hAlignment = int(params.get('hAlignment', 0))
        assert(vAlignment in VALIGNMENT)
        assert(hAlignment in ALIGNMENT)
        vAlignment = VALIGNMENT[vAlignment]
        hAlignment = ALIGNMENT[hAlignment]
        item.setAlignment(hAlignment | vAlignment)

        fnt = params.get('font', None)
        if fnt:
            family, style, size = fnt
            f = Qt.QFont(family, int(.85 * size), Qt.QFont.Light, False)
            f.setStyleHint(TEXTHINT_JDW2QT.get(family, Qt.QFont.AnyStyle))
            f.setStyleStrategy(Qt.QFont.PreferMatch)
            if style == 1:
                f.setWeight(Qt.QFont.DemiBold)
            elif style == 2:
                f.setItalic(True)
            elif style == 3:
                f.setWeight(Qt.QFont.DemiBold)
                f.setItalic(True)
            # TODO: Improve code in order to be able to set a suitable font
            item.setFont(f)
        fg = params.get("foreground", (0, 0, 0))
        color = Qt.QColor(fg[0], fg[1], fg[2])
        item.setDefaultTextColor(color)

        txt = params.get('text')
        if txt:
            if any(isinstance(txt, t) for t in (list, tuple, set)):  # Parsing several lines of text
                txt = '\n'.join(txt)
            item.setPlainText(str(txt))
            item._currText = txt

    def getGroupObj(self, params):
        item = self.getGraphicsItem('Group', params)
        s = params.get('summit')
        x1, y1 = s[0], s[1]
        item.setPos(x1, y1)
        children = params.get('children')
        if children:
            for child in children:
                if child:
                    #self.info('jdraw.py: "%s".addItem("%s")'%(str(params.get('name')),str(child)))
                    item.addToGroup(child)
        if item._fillStyle:
            self.set_item_filling(item, expand=True)
        return item

    def getSwingObjectObj(self, params):
        item = self.getGraphicsItem('SwingObject', params)
        s = params.get('summit')
        x1, y1 = s[0], s[1]
        item.setPos(x1, y1)

        className = params.get('className')
        if className == "fr.esrf.tangoatk.widget.attribute.SimpleScalarViewer":
            self.readSimpleScalarViewerObj(item, params)

        return item

    def readSimpleScalarViewerObj(self, item, params):
        self.readLabelObj(item, params)

        ext = params.get('extensions')

        c = ext.get('validBackground')
        c = [int(x) for x in c.split(",")]
        if c:
            validBackground = Qt.QColor(*c)
            item.setValidBackground(validBackground)

        invalidText = ext.get('invalidText', "-----")
        item.setNoneValue(invalidText)

        alarmEnabled = ext.get('alarmEnabled', True)
        alarmEnabled = alarmEnabled.lower().strip() in ["yes", "true", "1"]
        item.setShowQuality(alarmEnabled)

        unitVisible = ext.get('unitVisible', True)
        unitVisible = unitVisible.lower().strip() in ["yes", "true", "1"]
        item.setUnitVisible(unitVisible)

        userFormat = ext.get('userFormat', None)
        item.setUserFormat(userFormat)

    def getImageObj(self, params):
        item = self.getGraphicsItem('Image', params)
        s = params.get('summit')
        x1, y1, x2, y2 = s
        item.setPos(x1, y1)

        fname = params.get('file_name')
        if fname:
            if os.path.isfile(fname):
                fname = os.path.realpath(fname)
            elif hasattr(self.myparent, 'path'):
                #self.info('using path param ...')
                fname = self.myparent.path + os.path.sep + fname
            self.debug('Opening JDImage(%s) = x,y,w,h=%f,%f,%f,%f' %
                       (fname, x1, y1, x2 - x1, y2 - y1))
            pixmap = Qt.QPixmap(fname)
            item.setPixmap(pixmap.scaled(x2 - x1, y2 - y1))
            #item.scale(float(w)/pixmap.width(), float(h)/pixmap.height())
        else:
            self.warning('No filename for image!?!')
        return item

    def set_common_params(self, item, params):
        if not item:
            return
        item._params = params
        name = params.get('name')

        if name.lower() == "ignorerepaint":
            name = ""
            if not 'extensions' in params:
                params['extensions'] = {}
            params.get('extensions')["ignoreRepaint"] = "true"

        if self.alias:
            for k, v in self.alias.items():
                name = str(name).replace(k, v)

        # Forcing not-Taurus items to have a name and be able to trigger events
        setattr(item, '_name', name)
        if name and not self._delayed:
            if isinstance(item, TaurusGraphicsItem):
                #self.debug('TaurusJDrawGraphicsFactory.set_common_params(): %s.setModel(%s)'%(item,name))
                item.setModel(name)
            else:
                self.debug('TaurusJDrawGraphicsFactory.set_common_params(%s): %s is not a TaurusGraphicsItem' % (
                    name, type(item).__name__))

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

        try:
            getattr(item, 'setPen')
            fg = params.get("foreground", (0, 0, 0))
            lineWidth = params.get("lineWidth", 1)
            if lineWidth == 0:
                pen = Qt.QPen(Qt.Qt.NoPen)
            else:
                pen = Qt.QPen(Qt.QColor(fg[0], fg[1], fg[2]))
                pen.setWidth(lineWidth)
                pen.setStyle(LINESTYLE_JDW2QT[params.get("lineStyle", 0)])
            item.setPen(pen)
        except AttributeError as ae:
            pass
        except Exception as e:
            self.warning('jdraw.set_common_params(%s(%s)).(foreground,width,style) failed!: \n\t%s' % (
                type(item).__name__, name, traceback.format_exc()))

        fillStyle = FILLSTYLE_JDW2QT[params.get('fillStyle', 0)]
        item._fillStyle = fillStyle

        if hasattr(item, 'brush'):
            brush = Qt.QBrush()
            if fillStyle == Qt.Qt.LinearGradientPattern:
                ox, oy = params.get('origin', (0, 0))
                gradient = Qt.QLinearGradient(ox + params.get('gradX1', 0),
                                              oy + params.get('gradY1', 0),
                                              ox + params.get('gradX2', 0),
                                              oy + params.get('gradY2', 0))
                c = params.get('gradC1', (0, 0, 0))
                gradient.setColorAt(0, Qt.QColor(c[0], c[1], c[2]))
                c = params.get('gradC2', (255, 255, 255))
                gradient.setColorAt(1, Qt.QColor(c[0], c[1], c[2]))

                gradCyclic = params.get('gradCyclic', False)
                if gradCyclic:
                    gradient.setSpread(Qt.QGradient.ReflectSpread)

                brush = Qt.QBrush(gradient)
            else:
                brush.setStyle(fillStyle)

            bg = params.get('background', (255, 255, 255))
            brush.setColor(Qt.QColor(bg[0], bg[1], bg[2]))
            item.setBrush(brush)

    def set_item_filling(self, item, pattern=Qt.Qt.Dense4Pattern, expand=False):
        count = 0
        item._fillStyle = item._fillStyle or pattern
        if hasattr(item, 'brush'):
            br = item.brush()
            br.setStyle(item._fillStyle)
            item.setBrush(br)
        if expand:
            for c in item.childItems():
                if not c._fillStyle:
                    self.set_item_filling(c, pattern=pattern, expand=True)
        return

if __name__ == "__main__":
    from taurus.qt.qtgui.graphic.jdraw import jdraw_view
    jdraw_view.jdraw_view_main()
