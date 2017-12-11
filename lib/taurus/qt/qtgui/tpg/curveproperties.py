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

.. warning:: this is Work-in-progress. The API from this module may still
             change. Please
"""

# TODO: WIP

__all__ = ["CurveAppearanceProperties", "CurvePropAdapter",
           "CurvesAppearanceChooser", "serialize_opts", "deserialize_opts"]

import copy

from taurus.external.qt import Qt
from taurus.core.util.containers import CaselessDict
from taurus.qt.qtgui.util.ui import UILoadable
from y2axis import Y2ViewBox
import pyqtgraph


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
                 autoApply=False, Y2Axis=None, curvePropAdapter=None):
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

        self.assignToY1BT.toggled[bool].connect(self.__onY1Toggled)
        self.assignToY2BT.toggled[bool].connect(self.__onY2Toggled)

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

    def __onY1Toggled(self, checked):
        if checked:
            self.assignToY2BT.setChecked(False)

    def __onY2Toggled(self, checked):
        if checked:
            self.assignToY1BT.setChecked(False)

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
        name = item.data(self.NAME_ROLE)
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
                     set to CONFLICT, the corresponding plot_item will show a
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

        if prop.y2 is CONFLICT:
            self.assignToY1BT.setChecked(False)
            self.assignToY2BT.setChecked(False)
        elif prop.y2:
            self.assignToY2BT.setChecked(True)
        else:
            self.assignToY1BT.setChecked(True)

        # set sSize and lWidth spinboxes. if prop.sSize is None, it puts -1
        # (which is the special value for these switchhboxes)
        if prop.sSize is CONFLICT or prop.sStyle is None:
            self.sSizeSB.setValue(-1)
        else:
            self.sSizeSB.setValue(max(prop.sSize, -1))
        if prop.lWidth is CONFLICT:
            self.lWidthSB.setValue(-1)
        else:
            self.lWidthSB.setValue(max(prop.lWidth, -1))

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
        # ("") translates into CONFLICT
        prop.sStyle = ReverseNamedSymbolStyles[
            str(self.sStyleCB.currentText())]
        prop.lStyle = ReverseNamedLineStyles[str(self.lStyleCB.currentText())]
        prop.cStyle = ReverseNamedCurveStyles[str(self.cStyleCB.currentText())]
        # get sSize and lWidth from the spinboxes (-1 means conflict)
        v = self.sSizeSB.value()
        if v == -1:
            prop.sSize = CONFLICT
        else:
            prop.sSize = v
        v = self.lWidthSB.value()
        if v == -1:
            prop.lWidth = CONFLICT
        else:
            prop.lWidth = v
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

        # get the y2 state from the buttons
        y1 = self.assignToY1BT.isChecked()
        y2 = self.assignToY2BT.isChecked()
        if not y1 and not y2:
            prop.y2 = CONFLICT
        elif y1:
            prop.y2 = False
        elif y2:
            prop.y2 = True
        else:
            # both buttons should never be checked simultaneously
            raise RuntimeError('Inconsistent state of Y-axis buttons')

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

        self.curvePropAdapter.setCurveProperties(self.curvePropDict, names)
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

    def __init__(self, dataItems=None, plotItem=None, y2axis=None):
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
            y2 = isinstance(item.getViewBox(), Y2ViewBox)

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
                sStyle=sStyle, sSize=sSize, sColor=sColor, sFill=sFill,
                lStyle=lStyle, lWidth=lWidth, lColor=lColor, cStyle=cStyle,
                cFill=cFill, y2=y2, title=title)
            curves_prop[title] = curve_appearance_properties
            self._curve_items[title] = item
        return curves_prop

    def setCurveProperties(self, properties, names):
        """
        Assign the properties from a CurveAppearanceProperties object to
        a PlotDataItem

        :param properties: (dict) dictionary containing
                           :class:`CurveAppearanceProperties`
                           (keys are curve names)
        :param names: (seq) names of the curves for which to set the
                            curve properties (they must be present in
                            the `properties` dict)
        """
        for name in names:
            prop = properties[name]
            sStyle = prop.sStyle
            sSize = prop.sSize
            sColor = prop.sColor
            sFill = prop.sFill
            lStyle = prop.lStyle
            lWidth = prop.lWidth
            lColor = prop.lColor
            cFill = prop.cFill
            y2 = prop.y2
            # title = properties.title

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

            # Set the Y1 / Y2 axis if required
            old_view = dataItem.getViewBox()  # current view for the curve
            if y2:
                new_view = self.y2axis  # y2 axis view
            elif y2 is False:  # we use "is" to avoid matching None
                new_view = self.plotItem.getViewBox()  # main view

            if new_view is not old_view:
                if old_view is not None:
                    old_view.removeItem(dataItem)
                new_view.addItem(dataItem)
                old_view.autoRange()
                new_view.autoRange()


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


class CurveAppearanceProperties(object):
    """An object describing the appearance of a TaurusCurve"""

    def __init__(self, sStyle=CONFLICT, sSize=CONFLICT, sColor=CONFLICT,
                 sFill=CONFLICT, lStyle=CONFLICT, lWidth=CONFLICT,
                 lColor=CONFLICT, cStyle=CONFLICT, y2=CONFLICT,
                 cFill=CONFLICT, title=CONFLICT, visible=CONFLICT):
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
            - y2= bool
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
            - y2 is True if the curve is associated to the y2 axis
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
        self.y2 = y2
        self.title = title
        self.visible = visible
        self.propertyList = ["sStyle", "sSize", "sColor", "sFill", "lStyle",
                             "lWidth", "lColor", "cStyle", "cFill", "y2",
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
        """
        Compares itself with another CurveAppearanceProperties object
        and returns (a list of then names of) the attributes that are in
        conflict between the two
        """
        result = []
        for aname in self.propertyList:
            vself = getattr(self, aname)
            vother = getattr(other, aname)
            if vself != vother and (
                        strict or not (CONFLICT in (vself, vother))):
                result.append(aname)
        return result

    @staticmethod
    def merge(plist, attributes=None, conflict=None):
        """
        returns a CurveAppearanceProperties object formed by merging a list
        of other CurveAppearanceProperties objects

        :param plist: (sequence<CurveAppearanceProperties>) objects to be
        merged
        :param attributes: (sequence<str>) the name of the attributes to
                           consider for the merge. If None, all the attributes
                           will be merged
        :param conflict: (callable) a function that takes 2 objects (having a
                         different attribute) and returns a value that solves
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
                          "lWidth", "lColor", "cStyle", "cFill", "y2",
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


def deserialize_opts(opts):
    """
    Deserialize opts dict to pass it to a PlotDataItem

    :param opts: (dict) serialized properties (as the output of
                 :meth:`deserialize_opts`)

    :return: (dict) deserialized properties (acceptable by PlotDataItem)
    """
    # pen property
    if opts['pen'] is not None:
        opts['pen'] = _unmarshallingQPainter(
            opts, 'pen', 'pen')

    # shadowPen property
    if opts['shadowPen'] is not None:
        opts['shadowPen'] = _unmarshallingQPainter(
            opts, 'shadowPen', 'pen')

    # symbolPen property
    if opts['symbolPen'] is not None:
        opts['symbolPen'] = _unmarshallingQPainter(
            opts, 'symbolPen', 'pen')

    # fillBrush property
    if opts['fillBrush'] is not None:
        opts['fillBrush'] = _unmarshallingQPainter(
            opts, 'fillBrush', 'brush')

    # symbolBrush property
    if opts['symbolBrush'] is not None:
        opts['symbolBrush'] = _unmarshallingQPainter(
            opts, 'symbolBrush', 'brush')

    return opts


def serialize_opts(opts):
    """
    Serialize all properties from PlotDataItem.

    :param opts: (dict) PlotDataItem opts (may include non-serializable
                 objects)

    :return: (dict) serialized properties (can be pickled)
    """
    # pen property (QPen object)
    if opts['pen'] is not None:
        _marshallingQPainter(opts, 'pen', 'pen')

    # shadowPen property (QPen object)
    if opts['shadowPen'] is not None:
        _marshallingQPainter(opts, 'shadowPen', 'pen')

    # symbolPen property (QPen object)
    if opts['symbolPen'] is not None:
        _marshallingQPainter(opts, 'symbolPen', 'pen')

    # fillBrush property (QBrush object)
    if opts['fillBrush'] is not None:
        _marshallingQPainter(opts, 'fillBrush', 'brush')

    # symbolBrush property (QBrush object)
    if opts['symbolBrush'] is not None:
        _marshallingQPainter(
            opts, 'symbolBrush', 'brush')

    return opts


def _marshallingQPainter(opts, prop_name, qPainter):
    if qPainter == 'pen':
        painter = pyqtgraph.mkPen(opts[prop_name])
        opts[prop_name + '_width'] = painter.width()
        opts[prop_name + '_dash'] = painter.dashPattern()
        opts[prop_name + '_cosmetic'] = painter.isCosmetic()
    elif qPainter == 'brush':
        painter = pyqtgraph.mkBrush(opts[prop_name])
    else:
        return

    color = pyqtgraph.colorStr(painter.color())
    opts[prop_name] = color
    opts[prop_name + '_style'] = painter.style()


def _unmarshallingQPainter(opts, prop_name, qPainter):
    color = opts[prop_name]
    style = opts[prop_name + '_style']
    del opts[prop_name + '_style']

    if qPainter == 'pen':
        width = opts[prop_name + '_width']
        dash = opts[prop_name + '_dash']
        cosmetic = opts[prop_name + '_cosmetic']
        del opts[prop_name + '_width']
        del opts[prop_name + '_dash']
        del opts[prop_name + '_cosmetic']
        painter = pyqtgraph.mkPen(color=color, style=style,
                                  width=width, dash=dash, cosmetic=cosmetic)
    elif qPainter == 'brush':
        painter = pyqtgraph.mkBrush(color=color)
        painter.setStyle(style)
    else:
        return

    return painter
