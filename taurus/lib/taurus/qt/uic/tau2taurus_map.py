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

"""The taurus.qt.uic submodule. It contains uic tools"""

__all__ = [""]

__docformat__ = 'restructuredtext'

TAU_2_TAURUS_LIST = [
["tau.widget","AbstractGraphicsFactory","taurus.qt.qtgui.graphic","TaurusBaseGraphicsFactory"],
["tau.widget","ActionFactory","taurus.qt.qtgui.util","ActionFactory"],
["tau.widget","BaseConfigurableClass","taurus.qt.qtcore.configuration","BaseConfigurableClass"],
["tau.widget","Led","taurus.qt.qtgui.display","QLed"],
["tau.widget","LedColor","taurus.qt.qtgui.display","LedColor"],
["tau.widget","LedSize","taurus.qt.qtgui.display","LedSize"],
["tau.widget","LedStatus","taurus.qt.qtgui.display","LedStatus"],
["tau.widget","QT_ATTRIBUTE_QUALITY_PALETTE","taurus.qt.qtgui.util","QT_ATTRIBUTE_QUALITY_PALETTE"],
["tau.widget","QT_DEVICE_STATE_PALETTE","taurus.qt.qtgui.util","QT_DEVICE_STATE_PALETTE"],
["tau.widget","Release","taurus.core","Release"],
["tau.widget","TauAttrForm","taurus.qt.qtgui.panel","TaurusAttrForm"],
["tau.widget","TauAttrListComboBox","taurus.qt.qtgui.input","TaurusAttrListComboBox"],
["tau.widget","TauBaseComponent","taurus.qt.qtgui.base","TaurusBaseComponent"],
["tau.widget","TauBaseConfigurableClass","None","None"],
["tau.widget","TauBaseContainer","taurus.qt.qtgui.container","TaurusBaseContainer"],
["tau.widget","TauBaseWidget","taurus.qt.qtgui.base","TaurusBaseWidget"],
["tau.widget","TauBaseWritableWidget","taurus.qt.qtgui.base","TaurusBaseWritableWidget"],
["tau.widget","TauBoolLed","taurus.qt.qtgui.display","TaurusLed"],
["tau.widget","TauButtonBox","taurus.qt.qtgui.button","QButtonBox"],
["tau.widget","TauCircularGauge","taurus.qt.qtgui.gauge","TaurusCircularGauge"],
["tau.widget","TauClassTable","None","None"],
["tau.widget","TauCommandButton","taurus.qt.qtgui.button","TaurusCommandButton"],
["tau.widget","TauCommandsForm","taurus.qt.qtgui.panel","TaurusCommandsForm"],
["tau.widget","TauConfigLabel","taurus.qt.qtgui.display","TaurusLabel"],
["tau.widget","TauConfigLineEdit","taurus.qt.qtgui.input","TaurusConfigLineEdit"],
["tau.widget","TauDevTree","taurus.qt.qtgui.tree","TaurusDevtree"],
["tau.widget","TauEllipseStateItem","taurus.qt.qtgui.graphic","TaurusEllipseStateItem"],
["tau.widget","TauForm","taurus.qt.qtgui.panel","TaurusForm"],
["tau.widget","TauFrame","taurus.qt.qtgui.container","TaurusFrame"],
["tau.widget","TauGraphicsAttributeItem","taurus.qt.qtgui.graphic","TaurusGraphicsAttributeItem"],
["tau.widget","TauGraphicsItem","taurus.qt.qtgui.graphic","TaurusGraphicsItem"],
["tau.widget","TauGraphicsScene","taurus.qt.qtgui.graphic","TaurusGraphicsScene"],
["tau.widget","TauGraphicsStateItem","taurus.qt.qtgui.graphic","TaurusGraphicsStateItem"],
["tau.widget","TauGraphicsView","taurus.qt.qtgui.graphic","TaurusGraphicsView"],
["tau.widget","TauGrid","taurus.qt.qtgui.table","TaurusGrid"],
["tau.widget","TauGroupBox","taurus.qt.qtgui.container","TaurusGroupBox"],
["tau.widget","TauGroupStateItem","taurus.qt.qtgui.graphic","TaurusGroupStateItem"],
["tau.widget","TauJDrawSynopticsView","taurus.qt.qtgui.graphic","TaurusJDrawSynopticsView"],
["tau.widget","TauLCDValue","taurus.qt.qtgui.display","TaurusLCD"],
["tau.widget","TauLauncherButton","taurus.qt.qtgui.button","TaurusLauncherButton"],
["tau.widget","TauLimitSwitch","taurus.qt.qgui.display","TaurusLed"],
["tau.widget","TauLinearGauge","taurus.qt.qtgui.gauge","TaurusLinearGauge"],
["tau.widget","TauLoggerTable","taurus.qt.qtgui.table","TaurusLoggerTable"],
["tau.widget","TauLoggerWidget","taurus.qt.qtgui.table","TaurusLoggerWidget"],
["tau.widget","TauLogo","taurus.qt.qtgui.display","QLogo"],
["tau.widget","TauMainWindow","taurus.qt.qtgui.container","TaurusMainWindow"],
["tau.widget","TauPolygonStateItem","taurus.qt.qtgui.graphic","TaurusPolygonStateItem"],
["tau.widget","TauPropTable","taurus.qt.qtgui.table","TaurusPropTable"],
["tau.widget","TauQueryComboBox","None","None"],
["tau.widget","TauRectStateItem","taurus.qt.qtgui.graphic","TaurusRectStateItem"],
["tau.widget","TauScrollArea","taurus.qt.qtgui.container","TaurusScrollArea"],
["tau.widget","TauStateLabel","taurus.qt.qtgui.display","TaurusLabel"],
["tau.widget","TauStateLed","taurus.qt.qtgui.display","TaurusLed"],
["tau.widget","TauTextAttributeItem","taurus.qt.qtgui.graphic","TaurusTextAttributeItem"],
["tau.widget","TauTextStateItem","taurus.qt.qtgui.graphic","TaurusTextStateItem"],
["tau.widget","TauValue","taurus.qt.qtgui.panel","TaurusValue"],
["tau.widget","TauValueCheckBox","taurus.qt.qtgui.input","TaurusValueCheckBox"],
["tau.widget","TauValueComboBox","taurus.qt.qtgui.input","TaurusValueComboBox"],
["tau.widget","TauValueLabel","taurus.qt.qtgui.display","TaurusLabel"],
["tau.widget","TauValueLineEdit","taurus.qt.qtgui.input","TaurusValueLineEdit"],
["tau.widget","TauValueSpinBox","taurus.qt.qtgui.input","TaurusValueSpinBox"],
["tau.widget","TauValuesFrame","taurus.qt.qtgui.container","TaurusValuesFrame"],
["tau.widget","TauValuesTable","taurus.qt.qtgui.table","TaurusValuesTable"],
["tau.widget","TauWheelEdit","taurus.qt.qtgui.input","TaurusWheelEdit"],
["tau.widget","TauWidget","taurus.qt.qtgui.container","TaurusWidget"],
["tau.widget","TauWidgetFactory","taurus.qt.qtgui.util","TaurusWidgetFactory"],
["tau.widget.actions","AttributeAllConfigAction","taurus.qt.qtgui.util","AttributeAllConfigAction"],
["tau.widget.actions","AttributeDisplayAction","taurus.qt.qtgui.util","AttributeDisplayAction"],
["tau.widget.actions","AttributeHistoryAction","taurus.qt.qtgui.util","AttributeHistoryAction"],
["tau.widget.actions","AttributeImageDisplayAction","taurus.qt.qtgui.util","AttributeImageDisplayAction"],
["tau.widget.actions","AttributeMenu","taurus.qt.qtgui.util","AttributeMenu"],
["tau.widget.actions","AttributeMonitorDeviceAction","taurus.qt.qtgui.util","AttributeMonitorDeviceAction"],
["tau.widget.actions","AttributeRangesAction ","taurus.qt.qtgui.util","AttributeRangesAction "],
["tau.widget.actions","AttributeUnitsAction","taurus.qt.qtgui.util","AttributeUnitsAction"],
["tau.widget.actions","ConfigurationMenu","taurus.qt.qtgui.util","ConfigurationMenu"],
["tau.widget.actions","SeparatorAction","taurus.qt.qtgui.util","SeparatorAction"],
["tau.widget.actions","TauAction","taurus.qt.qtgui.util","TauAction"],
["tau.widget.actions","TauMenu","taurus.qt.qtgui.util","TauMenu"],
["tau.widget.configbrowser","ConfigViewer","taurus.qt.qtgui.panel","QConfigViewer"],
["tau.widget.dialog","AttrChooser","taurus.qt.qtgui.panel","TaurusAttributeChooser"],
["tau.widget.dialog","DataExportDlg","taurus.qt.qtgui.panel","QDataExportDialog"],
["tau.widget.dialog","RawDataWidget","taurus.qt.qtgui.panel","QRawDataWidget"],
["tau.widget.edit","WheelEdit","taurus.qt.qtgui.input","QWheelEdit"],
["tau.widget.qwt","TauArrayEditor","taurus.qt.qtgui.plot","TaurusArrayEditor"],
["tau.widget.qwt","TauPlot","taurus.qt.qtgui.plot","TaurusPlot"],
["tau.widget.qwt","TauTrend","taurus.qt.qtgui.plot","TaurusTrend"],
["tau.widget.utils","initTauQtLogger","taurus.qt.qtcore.util","initTaurusQtLogger"],
["tau.widget.utils","getQtLogger","taurus.qt.qtcore.util","getQtLogger"],
["tau.widget.extra_xterm","XTermWidget","taurus.qt.qtgui.extra_xterm","QXTermWidget"],
["tau.widget.extra_tauservers","TauServersWidget","taurus.qt.qtgui.extra_tauservers","TaurusServersWidget"],
["tau.widget.extra_motor","TauMotorH","taurus.qt.qtgui.extra_pool","TaurusMotorH"],
["tau.widget.extra_motor","TauMotorH2","taurus.qt.qtgui.extra_pool","TaurusMotorH2"],
["tau.widget.extra_motor","TauMotorV","taurus.qt.qtgui.extra_pool","TaurusMotorV"],
["tau.widget.extra_motor","TauMotorV2","taurus.qt.qtgui.extra_pool","TaurusMotorV2"],
["tau.widget.extra_motor","PoolMotorSlim","taurus.qt.qtgui.extra_pool","PoolMotorSlim"],
["tau.widget.macroexecutor","TauMacroExecutorWidget","taurus.qt.qtgui.extra_macroexecutor","TaurusMacroExecutorWidget"],
["tau.widget.macroexecutor","TauMacroExecutor","taurus.qt.qtgui.extra_macroexecutor","TaurusMacroExecutor"],
["tau.widget.macroexecutor","TauSequencer","taurus.qt.qtgui.extra_macroexecutor","TaurusSequencer"],
["tau.widget.macroexecutor","TauMacroConfigurationDialog","taurus.qt.qtgui.extra_macroexecutor","TaurusMacroConfigurationDialog"],
["tau.widget.macroexecutor","TauMacroDescriptionViewer","taurus.qt.qtgui.extra_macroexecutor","TaurusMacroDescriptionViewer"],
["tau.widget.macroexecutor","DoorOutput","taurus.qt.qtgui.extra_macroexecutor","DoorOutput"],
["tau.widget.macroexecutor","DoorDebug","taurus.qt.qtgui.extra_macroexecutor","DoorDebug"],
["tau.widget.macroexecutor","DoorResult","taurus.qt.qtgui.extra_macroexecutor","DoorResult"],
]

TAU_2_TAURUS_MAP = {}
for old_mod, old_klass, new_mod, new_klass in TAU_2_TAURUS_LIST:
    item = TAU_2_TAURUS_MAP.get(old_mod)
    if item is None:
        item = {}
        TAU_2_TAURUS_MAP[old_mod] = item
    item[old_klass] = new_mod, new_klass
    
