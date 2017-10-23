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

"""
A Qt dialog for choosing plot appearance (symbols and lines)
for a Pyqtgraph.PlotDataItem or taurus-derived class
like TaurusPlotDataItem
"""
__all__ = ["CurveAppearanceProperties", "CurvePropAdapter",
           "CurvesAppearanceChooser"]

import copy

import pyqtgraph
from taurus.external.qt import Qt
from taurus.core.util.containers import CaselessDict
from taurus.qt.qtgui.util.ui import UILoadable
from y2axis import Y2ViewBox


class CONFLICT(object):
    """
    This is just a do-nothing class to be used to indicate that there are
    conflicting values when merging properties from different curves
    """
    pass


NamedLineStyles = {CONFLICT: "",
                   Qt.Qt.NoPen: "No line",
                   Qt.Qt.SolidLine: "_____",
                   Qt.Qt.DashLine: "_ _ _",
                   Qt.Qt.DotLine: ".....",
                   Qt.Qt.DashDotLine: "_._._",
                   Qt.Qt.DashDotDotLine: ".._..",
                   }


ReverseNamedLineStyles = {}
for k, v in NamedLineStyles.iteritems():
    ReverseNamedLineStyles[v] = k


# TODO:allow the dialog to use this curve styles
NamedCurveStyles = {CONFLICT: "",
                    None: "",
                    "No curve": "No curve",
                    "Lines": "Lines",
                    "Sticks": "Sticks",
                    "Steps": "Steps",
                    "Dots": "Dots"
                    }


ReverseNamedCurveStyles = {}
for k, v in NamedCurveStyles.iteritems():
    ReverseNamedCurveStyles[v] = k

NamedSymbolStyles = {
    CONFLICT: "",
    None: "No symbol",
    'o': "Circle",
    's': "Square",
    'd': "Diamond",
    't': "Down Triangle",
    't1': "Up triangle",
    't3': "Left Triangle",
    't2': "Right Triangle",
    '+': "Cross",
    'star': "Star",
    'p': "Pentagon",
    'h': "Hexagon"
}


ReverseNamedSymbolStyles = {}
for k, v in NamedSymbolStyles.iteritems():
    ReverseNamedSymbolStyles[v] = k


NamedColors = ["Black", "Red", "Blue", "Magenta",
               "Green", "Cyan", "Yellow", "Gray", "White"]


@UILoadable
class CurvesAppearanceChooser(Qt.QWidget):
    """
    A plot_item for choosing plot appearance for one or more curves.
    The current curves properties are passed using the setCurves() method using
    a dictionary with the following structure::

        curvePropDict={name1:prop1, name2:prop2,...}

    where propX is an instance of :class:`CurveAppearanceProperties`
    When applying, a signal is emitted and the chosen properties are made
    available in a similar dictionary. """

    NAME_ROLE = Qt.Qt.UserRole

    controlChanged = Qt.pyqtSignal()
    curveAppearanceChanged = Qt.pyqtSignal(object, list)
    CurveTitleEdited = Qt.pyqtSignal('QString', 'QString')

    def __init__(self, parent=None, curvePropDict={}, showButtons=False,
                 autoApply=False, Y2Axis=None, curvePropAdapter = None):
        # try:
        super(CurvesAppearanceChooser, self).__init__(parent)
        self.loadUi()
        self.autoApply = autoApply
        self.sStyleCB.insertItems(0, sorted(NamedSymbolStyles.values()))
        self.lStyleCB.insertItems(0, NamedLineStyles.values())
        self.cStyleCB.insertItems(0, NamedCurveStyles.values())
        self.sColorCB.addItem("")
        self.lColorCB.addItem("")
        if not showButtons:
            self.applyBT.hide()
            self.resetBT.hide()
        for color in NamedColors:
            icon = self._colorIcon(color)
            self.sColorCB.addItem(icon, "", Qt.QColor(color))
            self.lColorCB.addItem(icon, "", Qt.QColor(color))
        self.__itemsDict = CaselessDict()
        self.setCurves(curvePropDict)
        # set the icon for the background button (stupid designer limitations
        # forces to do it programatically)
        self.bckgndBT.setIcon(Qt.QIcon(":color-fill.svg"))

        # connections.
        self.curvesLW.itemSelectionChanged.connect(self._onSelectedCurveChanged)
        self.curvesLW.itemChanged.connect(self._onItemChanged)
        self.applyBT.clicked.connect(self.onApply)
        self.resetBT.clicked.connect(self.onReset)
        self.sStyleCB.currentIndexChanged.connect(self._onSymbolStyleChanged)

        self.sStyleCB.currentIndexChanged.connect(self._onControlChanged)
        self.lStyleCB.currentIndexChanged.connect(self._onControlChanged)
        self.sColorCB.currentIndexChanged.connect(self._onControlChanged)
        self.lColorCB.currentIndexChanged.connect(self._onControlChanged)
        self.cStyleCB.currentIndexChanged.connect(self._onControlChanged)
        self.sSizeSB.valueChanged.connect(self._onControlChanged)
        self.lWidthSB.valueChanged.connect(self._onControlChanged)
        self.cAreaDSB.valueChanged.connect(self._onControlChanged)
        self.sFillCB.stateChanged.connect(self._onControlChanged)
        self.cFillCB.stateChanged.connect(self._onControlChanged)

        # self.bckgndBT.clicked.connect(self.changeBackgroundColor)

        # Disabled buttons until future implementations
        # (set background color and set curve labels)
        self.changeTitlesBT.setEnabled(False)
        self.bckgndBT.setEnabled(False)

        # disable the group box with the options for swap curves between Y axes
        if Y2Axis is None:
            self.groupBox.setEnabled(False)

        # set properties from curves for first launch of config dialog and
        # keeps a curvePropAdapter object
        self._onSelectedCurveChanged()
        self.curvePropAdapter = curvePropAdapter
        self.axis = None

    def changeBackgroundColor(self):
        """Launches a dialog for choosing the parent's canvas background color
        """
        color = Qt.QColorDialog.getColor(
            self.curvePropAdapter.getBackgroundColor(), self)
        if Qt.QColor.isValid(color):
            self.curvePropAdapter.setBackgroundColor(color)

    def setCurves(self, curvePropDict):
        """Populates the list of curves from the properties dictionary. It uses
        the curve title for display, and stores the curve name as the item data
        (with role=CurvesAppearanceChooser.NAME_ROLE)

        :param curvePropDict:  (dict) a dictionary whith keys=curvenames and
                               values= :class:`CurveAppearanceProperties`
                               object
        """
        self.curvePropDict = curvePropDict
        self._curvePropDictOrig = copy.deepcopy(curvePropDict)
        self.curvesLW.clear()
        self.__itemsDict = CaselessDict()
        for name, prop in self.curvePropDict.iteritems():
            # create and insert the item
            item = Qt.QListWidgetItem(prop.title, self.curvesLW)
            self.__itemsDict[name] = item
            item.setData(self.NAME_ROLE, name)
            item.setToolTip("<b>Curve Name:</b> %s" % name)
            item.setFlags(Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsSelectable |
                          Qt.Qt.ItemIsUserCheckable | Qt.Qt.ItemIsDragEnabled |
                          Qt.Qt.ItemIsEditable)
        self.curvesLW.setCurrentRow(0)

    def _onItemChanged(self, item):
        """slot used when an item data has changed"""
        name =item.data(self.NAME_ROLE)
        previousTitle = self.curvePropDict[name].title
        currentTitle = item.text()
        if previousTitle != currentTitle:
            self.curvePropDict[name].title = currentTitle
            self.CurveTitleEdited.emit(name, currentTitle)

    def updateTitles(self, newTitlesDict=None):
        """
        Updates the titles of the curves that are displayed in the curves list.

        :param newTitlesDict: (dict<str,str>) dictionary with key=curve_name
                                and value=title
        """
        if newTitlesDict is None:
            return
        for name, title in newTitlesDict.iteritems():
            self.curvePropDict[name].title = title
            self.__itemsDict[name].setText(title)

    def getSelectedCurveNames(self):
        """Returns the curve names for the curves selected at the curves list.

        *Note*: The names may differ from the displayed text, which
        corresponds to the curve titles (this method is what you likely need if
        you want to get keys to use in curves or curveProp dicts).

        :return: (string_list) the names of the selected curves
        """
        return [item.data(self.NAME_ROLE)
                for item in self.curvesLW.selectedItems()]

    def showProperties(self, prop=None):
        """Updates the dialog to show the given properties.

        :param prop: (CurveAppearanceProperties) the properties object
                     containing what should be shown. If a given property is
                     set to None, the corresponding plot_item will show a
                     "neutral" display
        """

        if prop is None:
            prop = self._shownProp
        # set the Style comboboxes
        self.sStyleCB.setCurrentIndex(
            self.sStyleCB.findText(NamedSymbolStyles[prop.sStyle]))
        self.lStyleCB.setCurrentIndex(
            self.lStyleCB.findText(NamedLineStyles[prop.lStyle]))
        self.cStyleCB.setCurrentIndex(
            self.cStyleCB.findText(NamedCurveStyles[prop.cStyle]))

        if prop.yAxis is CONFLICT:
            self.assignToY1BT.setChecked(False)
            self.assignToY2BT.setChecked(False)
        elif prop.yAxis:
            self.assignToY2BT.setChecked(True)
        else:
            self.assignToY1BT.setChecked(True)


        # set sSize and lWidth spinboxes. if prop.sSize is None, it puts -1
        # (which is the special value for these switchhboxes)
        if prop.sSize is CONFLICT or prop.sStyle is None:
            self.sSizeSB.setValue(-1)
        else:
            self.sSizeSB.setValue(max(prop.sSize,-1))
        if prop.lWidth is CONFLICT:
            self.lWidthSB.setValue(-1)
        else:
            self.lWidthSB.setValue(max(prop.lWidth,-1))

        # Set the Color combo boxes. The item at index 0 is the empty one in
        # the comboboxes Manage unknown colors by including them
        if prop.sColor in (None, CONFLICT) or prop.sStyle is None:
            index = 0
        else:
            index = self.sColorCB.findData(Qt.QColor(prop.sColor))
        if index == -1:  # if the color is not supported, add it to combobox
            index = self.sColorCB.count()
            self.sColorCB.addItem(self._colorIcon(
                Qt.QColor(prop.sColor)), "", Qt.QColor(prop.sColor))
        self.sColorCB.setCurrentIndex(index)
        if prop.lColor is None or prop.lColor is CONFLICT:
            index = 0
        else:
            index = self.lColorCB.findData(Qt.QColor(prop.lColor))
        if index == -1:  # if the color is not supported, add it to combobox
            index = self.lColorCB.count()
            self.lColorCB.addItem(self._colorIcon(
                Qt.QColor(prop.lColor)), "", Qt.QColor(prop.lColor))
        self.lColorCB.setCurrentIndex(index)
        # set the Fill Checkbox. The prop.sFill value can be in 3 states: True,
        # False and None
        if prop.sFill is None or prop.sFill is CONFLICT:
            checkState = Qt.Qt.PartiallyChecked
        elif prop.sFill:
            checkState = Qt.Qt.Checked
        else:
            checkState = Qt.Qt.Unchecked
        self.sFillCB.setCheckState(checkState)
        # set the Area Fill Checkbox. The prop.cFill value can be in 3 states:
        # True, False and None
        if prop.cFill is CONFLICT:
            checkState = Qt.Qt.PartiallyChecked
            self.cAreaDSB.setValue(0.0)
        elif prop.cFill is None:
            checkState = Qt.Qt.Unchecked
            self.cAreaDSB.setValue(0.0)
        else:
            checkState = Qt.Qt.Checked
            self.cAreaDSB.setValue(prop.cFill)
        self.cFillCB.setCheckState(checkState)

    def _onControlChanged(self, *args):
        """
        Slot to be called whenever a control plot_item is changed. It emits a
        `controlChanged` signal and applies the change if in autoapply mode.
        It ignores any arguments passed
        """

        self.controlChanged.emit()
        if self.autoApply:
            self.onApply()

    def _onSelectedCurveChanged(self):
        """Updates the shown properties when the curve selection changes"""
        plist = [self.curvePropDict[name]
                 for name in self.getSelectedCurveNames()]
        if len(plist) == 0:
            plist = [CurveAppearanceProperties()]
            self.lineGB.setEnabled(False)
            self.symbolGB.setEnabled(False)
            self.otherGB.setEnabled(False)
        else:
            self.lineGB.setEnabled(True)
            self.symbolGB.setEnabled(True)
            self.otherGB.setEnabled(True)

        self._shownProp = CurveAppearanceProperties.merge(plist)
        self.showProperties(self._shownProp)

    def _onSymbolStyleChanged(self, text):
        """Slot called when the Symbol style is changed, to ensure that symbols
        are visible if you choose them

        :param text: (str) the new symbol style label
        """
        text = str(text)
        if self.sSizeSB.value() < 2 and not text in ["", "No symbol"]:
            # a symbol size of 0 is invisible and 1 means you should use
            # cStyle=dots
            self.sSizeSB.setValue(3)

    def getShownProperties(self):
        """Returns a copy of the currently shown properties and updates
        self._shownProp

        :return: (CurveAppearanceProperties)
        """
        prop = CurveAppearanceProperties()

        for name in self.getSelectedCurveNames():
            prop.title = self.curvePropDict[name].title

        # get the values from the Style comboboxes. Note that the empty string
        # ("") translates into None
        prop.sStyle = ReverseNamedSymbolStyles[
            str(self.sStyleCB.currentText())]
        prop.lStyle = ReverseNamedLineStyles[str(self.lStyleCB.currentText())]
        prop.cStyle = ReverseNamedCurveStyles[str(self.cStyleCB.currentText())]
        # get sSize and lWidth from the spinboxes
        prop.sSize = self.sSizeSB.value()
        prop.lWidth = self.lWidthSB.value()

        # Get the Color combo boxes. The item at index 0 is the empty one in
        # the comboboxes
        index = self.sColorCB.currentIndex()
        if index == 0:
            prop.sColor = CONFLICT
        else:
            prop.sColor = Qt.QColor(self.sColorCB.itemData(index))
        index = self.lColorCB.currentIndex()
        if index == 0:
            prop.lColor = CONFLICT
        else:
            prop.lColor = Qt.QColor(self.lColorCB.itemData(index))
        # get the sFill from the Checkbox.
        checkState = self.sFillCB.checkState()
        if checkState == Qt.Qt.PartiallyChecked:
            prop.sFill = CONFLICT
        else:
            prop.sFill = bool(checkState)
        # get the cFill from the Checkbox.
        checkState = self.cFillCB.checkState()
        if checkState == Qt.Qt.PartiallyChecked:
            prop.cFill = CONFLICT
        elif checkState == Qt.Qt.Checked:
            prop.cFill = self.cAreaDSB.value()
        else:
            prop.cFill = None

        # prop.yAxis = CONFLICT
            
        # store the props
        self._shownProp = copy.deepcopy(prop)
        return copy.deepcopy(prop)

    def onApply(self):
        """Apply does 2 things:

            - It updates `self.curvePropDict` using the current values
              chosen in the dialog
            - It emits a curveAppearanceChanged signal that indicates the names
              of the curves that changed and the new properties.  (TODO)

        :return: (tuple<CurveAppearanceProperties,list>) a tuple containing the
                 curve properties and a list of the selected curve names (as a
                 list<str>)
        """
        names = self.getSelectedCurveNames()
        prop = self.getShownProperties()
        # Update self.curvePropDict for selected properties
        for n in names:
            self.curvePropDict[n] = CurveAppearanceProperties.merge(
                [self.curvePropDict[n], prop],
                conflict=CurveAppearanceProperties.inConflict_update_a)
        # emit a (PyQt) signal telling what properties (first argument) need to
        # be applied to which curves (second argument)
        # self.curveAppearanceChanged.emit(prop, names)
        # return both values

        if self.assignToY2BT.isChecked():
            axis = 'right'
        else:
            axis = 'left'

        self.curvePropAdapter.setCurveProperties(self.curvePropDict, names,
                                                 axis)
        return prop, names

    def onReset(self):
        """slot to be called when the reset action is triggered. It reverts to
        the original situation"""
        self.setCurves(self._curvePropDictOrig)
        self.curvesLW.clearSelection()

    def _colorIcon(self, color, w=10, h=10):
        # to do: create a border
        pixmap = Qt.QPixmap(w, h)
        pixmap.fill(Qt.QColor(color))
        return Qt.QIcon(pixmap)


class CurvePropAdapter(object):
    """
    This class allows to extract the curve properties
    (:class:`CurveAppearanceProperties`)  from curves
    (:class:`pyqtgraph.PlotDataItem`) in a given plot
    (:class:`pyqtgraph.PlotItem`).
    """
    def __init__(self, dataItems=None, plotItem = None, y2axis = None):
        self.dataItems = dataItems
        self.plotItem = plotItem
        self._curve_items = dict()
        self.y2axis = y2axis

    def getCurveProperties(self):
        """
        Returns CurveAppearanceProperties objects for all curves in the
        associated PlotItem

        :return: A dictionary(key, value), whose keys are curve names and
        values are the corresponding CurveApearanceProperties object
        """
        curves_prop = {}
        for item in self.dataItems:
            if isinstance(item.getViewBox(), Y2ViewBox):
                yAxis = True
            else:
                yAxis = False

            opts = item.opts
            pen = pyqtgraph.mkPen(opts['pen'])
            symbol_pen = pyqtgraph.mkPen(opts['symbolPen'])
            symbol_brush = pyqtgraph.mkBrush(opts['symbolBrush'])
            title = opts.get('name')
            sStyle = opts['symbol']
            sSize = opts['symbolSize']

            if sStyle is None:
                sColor = None
                sSize = -1
            else:
                sColor = symbol_pen.color()

            sFill = symbol_brush.color()
            if sFill is None or sStyle is None:
                sFill = False
            else:
                sFill = True

            lStyle = pen.style()
            lWidth = pen.width()
            lColor = pen.color()
            cStyle = None

            cFill = opts['fillLevel']

            curve_appearance_properties = CurveAppearanceProperties(
                sStyle=sStyle, sSize=sSize, sColor=sColor,sFill=sFill,
                lStyle=lStyle, lWidth=lWidth, lColor=lColor, cStyle=cStyle,
                cFill=cFill, yAxis=yAxis, title=title)
            curves_prop[title] = curve_appearance_properties
            self._curve_items[title] = item
        return curves_prop

    def setCurveProperties(self, prop, names, axis):
        """
        Assign Assign the properties from a CurveApareanceProperties object to
        a PlotDataItem

        :param prop: dict of CurveApareanceProperties
        :param names: names of curves contained in prop dict
        :param axis: String (right or left)
        """
        for name in names:
            curve = prop[name]
            sStyle = curve.sStyle
            sSize = curve.sSize
            sColor = curve.sColor
            sFill = curve.sFill
            lStyle = curve.lStyle
            lWidth = curve.lWidth
            lColor = curve.lColor
            cFill = curve.cFill
            # title = prop.title

            dataItem = self._curve_items[name]

            dataItem.setPen(dict(style=lStyle, width=lWidth, color=lColor))
            if cFill is not None:
                dataItem.setFillLevel(cFill)
                try:
                    cFillColor = Qt.QColor(lColor)
                    cFillColor.setAlphaF(0.5)  # set to semitransparent
                except:
                    cFillColor = lColor
                dataItem.setFillBrush(cFillColor)
            else:
                dataItem.setFillLevel(None)

            dataItem.setSymbol(sStyle)
            dataItem.setSymbolPen(pyqtgraph.mkPen(color=sColor))
            if sStyle is None or sSize < 0:
                dataItem.setSymbolSize(0)
            else:
                dataItem.setSymbolSize(sSize)

            if sFill is True:
                dataItem.setSymbolBrush(sColor)
            else:
                dataItem.setSymbolBrush(None)

            self.setCurveYAxis(prop, names , axis=axis)

    # change background color of the whole window, not just the plot area
    # def setBackgroundColor(self, color):
    #     self.plot_item.setBackground(color)

    def setBackgroundColor(self, color):
        # background=None for default in plotting (black color)
        if color.value() == 0:
            color = None
        self.plotItem.getViewBox().setBackgroundColor(color)


    def getBackgroundColor(self):
        backgroundColor = self.plotItem.getViewBox().state['background']
        if backgroundColor is None:
            return Qt.QColor('black')
        return backgroundColor

    def setCurveYAxis(self, properties, curve_names, axis=None):
        """
        This method manage the assignment of Y axis where the
        curve will be plotted

        :param properties: dict of CurveApareanceProperties
        :param curve_names: name of curves contained in properties dict
        :param axis: Y destination axis, String (right, left) or None
        """
        mainView = self.plotItem.getViewBox()
        for name in curve_names:
            yAxis = properties[name].yAxis
            dataItem = self._curve_items[name]

            if axis == 'right':
                if yAxis is False:
                    mainView.removeItem(dataItem)
                    self.y2axis.addItem(dataItem)
                    mainView.autoRange()
                    self.y2axis.autoRange()
                    properties[name].yAxis = True
            elif axis == 'left':
                if yAxis is True:
                    self.y2axis.removeItem(dataItem)
                    mainView.addItem(dataItem)

                    mainView.autoRange()
                    properties[name].yAxis = False


class CurveAppearanceProperties(object):
    """An object describing the appearance of a TaurusCurve"""

    #if we don't choose a curve, dialog need to be in conflict, for that we
    # need define some default values to CONFLICT instead of None.
    def __init__(self, sStyle=CONFLICT, sSize=None, sColor=None, sFill=None,
                 lStyle=CONFLICT, lWidth=None, lColor=None, cStyle=None,
                 yAxis=CONFLICT, cFill=CONFLICT, title=None, visible=None):
        """
        Possible keyword arguments are:
            - sStyle= symbolstyle
            - sSize= int
            - sColor= color
            - sFill= bool
            - lStyle= linestyle
            - lWidth= int
            - lColor= color
            - cStyle= curvestyle
            - cFill= float or None
            - yAxis= bool
            - visible = bool
            - title= str

        Where:
            - color is a color that QColor() understands (i.e. a
              Qt.Qt.GlobalColor, a color name, or a Qt.Qcolor)
            - symbolstyle is a key of NamedSymbolStyles
            - linestyle is a key of Qt.Qt.PenStyle
            - curvestyle is a key of NamedCurveStyles
            - cFill can either be None (meaning not to fill) or a float that
              indicates the baseline from which to fill
        """
        self.sStyle = sStyle
        self.sSize = sSize
        self.sColor = sColor
        self.sFill = sFill
        self.lStyle = lStyle
        self.lWidth = lWidth
        self.lColor = lColor
        self.cStyle = cStyle
        self.cFill = cFill
        self.yAxis = yAxis
        self.title = title
        self.visible = visible
        self.propertyList = ["sStyle", "sSize", "sColor", "sFill", "lStyle",
                             "lWidth", "lColor", "cStyle", "cFill", "yAxis",
                             "title", "visible"]

    @staticmethod
    def inConflict_update_a(a, b):
        """
        This  function can be passed to CurvesAppearance.merge()
        if one wants to update prop1 with prop2 except for those
        attributes of prop2 that are set to CONFLICT
        """
        if b is CONFLICT:
            return a
        else:
            return b

    @staticmethod
    def inConflict_CONFLICT(a, b):
        """In case of conflict, returns CONFLICT"""
        return CONFLICT

    def conflictsWith(self, other, strict=True):
        """returns a list of attribute names that are in conflict between this
        self and other"""
        result = []
        for aname in self.propertyList:
            vself = getattr(self, aname)
            vother = getattr(other, aname)
            if vself != vother and (
                        strict or not(CONFLICT in (vself, vother))):
                result.append(aname)
        return result

    @classmethod
    def merge(self, plist, attributes=None, conflict=None):
        """
        returns a CurveAppearanceProperties object formed by merging a list
        of other CurveAppearanceProperties objects

        **Note:** This is a class method, so it can be called without
        previously instantiating an object

        :param plist: (sequence<CurveAppearanceProperties>) objects to be
        merged
        :param attributes: (sequence<str>) the name of the attributes to
                           consider for the merge. If None, all the attributes
                           will be merged
        :param conflict: (callable) a function that takes 2 objects (having a
                         different attribute)and returns a value that solves
                         the conflict. If None is given, any conflicting
                         attribute will be set to CONFLICT.

        :return: (CurveAppearanceProperties) merged properties
        """
        n = len(plist)
        if n < 1:
            raise ValueError("plist must contain at least 1 member")
        plist = copy.deepcopy(plist)
        if n == 1:
            return plist[0]
        if attributes is None:
            attributes = ["sStyle", "sSize", "sColor", "sFill", "lStyle",
                          "lWidth", "lColor", "cStyle", "cFill", "yAxis",
                          "title"]
        if conflict is None:
            conflict = CurveAppearanceProperties.inConflict_CONFLICT
        p = CurveAppearanceProperties()

        for a in attributes:
            alist = [p.__getattribute__(a) for p in plist]
            p.__setattr__(a, alist[0])
            for ai in alist[1:]:
                if alist[0] != ai:
                    # print "MERGING:",a,alist[0],ai,conflict(alist[0],ai)
                    p.__setattr__(a, conflict(alist[0], ai))
                    break
        return p


