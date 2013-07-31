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

"""This module provides widgets that display the database in a tree format"""

__docformat__ = 'restructuredtext'

import re

from taurus.qt import Qt

import taurus.core
import taurus.core.util
import taurus.qt.qtgui.base
import taurus.qt.qtgui.resource

ElemType = taurus.core.taurusbasetypes.TaurusElementType
getElementTypeIcon = taurus.qt.qtgui.resource.getElementTypeIcon
getPixmap = taurus.qt.qtgui.resource.getPixmap
getThemeIcon = taurus.qt.qtgui.resource.getThemeIcon
getThemePixmap = taurus.qt.qtgui.resource.getThemePixmap

class BaseFilter(object):
    
    def __init__(self, re_expr):
        if len(re_expr) == 0:
            re_expr = ".*"
        else:
            if re_expr[0] != "^": re_expr = "^" + re_expr
            if re_expr[-1] != "$": re_expr += "$"
        self._re_expr = re.compile(re_expr, re.IGNORECASE)

    def __call__(self, obj):
        return self.filter(obj)


class BaseElementFilter(BaseFilter):
    
    def __init__(self, re_expr, func=None):
        super(BaseElementFilter, self).__init__(re_expr)
        self._klass = func.im_class
        self._func = func
    
    def filter(self, obj):
        if not isinstance(obj, self._klass):
            return obj
        v = self._func(obj)
        if self._re_expr.match(v):
            return obj


class DeviceFilter(BaseElementFilter):
    
    def __init__(self, re_expr, func=taurus.core.taurusdatabase.TaurusDevInfo.name):
        super(DeviceFilter, self).__init__(re_expr, func=func)


class DeviceClassFilter(BaseElementFilter):
    
    def __init__(self, re_expr, func=taurus.core.taurusdatabase.TaurusDevInfo.name):
        super(DeviceClassFilter, self).__init__(re_expr, func=func)


class ServerFilter(BaseElementFilter):

    def __init__(self, re_expr, func=taurus.core.taurusdatabase.TaurusServInfo.name):
        super(ServerFilter, self).__init__(re_expr, func=func)


class AttributeFilter(BaseElementFilter):
    
    def __init__(self, re_expr, func=taurus.core.taurusdatabase.TaurusAttrInfo.name):
        super(AttributeFilter, self).__init__(re_expr, func=func)


class KlassFilter(BaseFilter):
    
    def __init__(self, klass):
        #don't call super on purpose. We don't need/have a regular expression here!
        #super(KlassFilter, self).__init__(re_expr)
        self._klass = klass
        
    def filter(self, obj):
        if isinstance(obj, self._klass):
            return obj


def getFilter(type, re_expr=None):
    if re_expr is None:
        if type == ElemType.Device:
            return KlassFilter(taurus.core.taurusdatabase.TaurusDevInfo)
        elif type == ElemType.Server:
            return KlassFilter(taurus.core.taurusdatabase.TaurusServInfo)
        elif type == ElemType.DeviceClass:
            return KlassFilter(taurus.core.taurusdatabase.TaurusDevInfo)
        return None

    if type == ElemType.Device:
        return DeviceFilter(re_expr)
    elif type == ElemType.Domain:
        return DeviceFilter(re_expr, taurus.core.taurusdatabase.TaurusDevInfo.domain)
    elif type == ElemType.Family:
        return DeviceFilter(re_expr, taurus.core.taurusdatabase.TaurusDevInfo.family)
    elif type == ElemType.Member:
        return DeviceFilter(re_expr, taurus.core.taurusdatabase.TaurusDevInfo.member)
    elif type == ElemType.Server:
        return ServerFilter(re_expr)
    elif type == ElemType.ServerName:
        return ServerFilter(re_expr, taurus.core.taurusdatabase.TaurusServInfo.serverName)
    elif type == ElemType.ServerInstance:
        return ServerFilter(re_expr, taurus.core.taurusdatabase.TaurusServInfo.serverInstance)
    elif type == ElemType.DeviceClass:
        return DeviceClassFilter(re_expr)
    elif type == ElemType.Attribute:
        return AttributeFilter(re_expr)





class TaurusFilterPanelOld1(Qt.QWidget, taurus.qt.qtgui.base.TaurusBaseWidget):
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(taurus.qt.qtgui.base.TaurusBaseWidget, name, designMode=designMode)
        self.init()
    
    def init(self):
        l = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom)
        self.setLayout(l)
        self.addFilterHeader()
        self.insertFilterItem()
        l.addStretch(1)
        
    def addFilterHeader(self):
        label = Qt.QLabel("Type:")
        comboBox = Qt.QComboBox()
        comboBox.addItem(getElementTypeIcon(ElemType.Attribute), "Attribute", ElemType.Attribute)
        comboBox.addItem(getElementTypeIcon(ElemType.Device), "Device", ElemType.Device)
        comboBox.addItem(getElementTypeIcon(ElemType.DeviceClass), "Device type", ElemType.DeviceClass)
        comboBox.addItem(getElementTypeIcon(ElemType.Server), "Server", ElemType.Server)
        comboBox.addItem("Any")
        previewButton = Qt.QPushButton("Preview")
        Qt.QObject.connect(previewButton, Qt.SIGNAL("clicked()"), self.onPreview)
        field = Qt.QWidget()
        l = Qt.QHBoxLayout()
        field.setLayout(l)
        l.addWidget(label)
        l.addWidget(comboBox)
        l.addWidget(previewButton)
        l.addStretch(1)
        self.layout().addWidget(field)
    
    def insertFilterItem(self, row=None):

        sl = self.layout()

        comboBox = Qt.QComboBox()
        self._fillComboBox(comboBox)
        Qt.QObject.connect(comboBox, Qt.SIGNAL("currentIndexChanged(int)"), self.onFilterComboBoxItemSelected)
        
        edit = Qt.QLineEdit()
        
        addButton = Qt.QPushButton(Qt.QIcon(":/actions/list-add.svg"),"")
        Qt.QObject.connect(addButton, Qt.SIGNAL("clicked()"), self.onAddFilterButtonClicked)
        
        removeButton = Qt.QPushButton(Qt.QIcon(":/actions/list-remove.svg"),"")
        Qt.QObject.connect(removeButton, Qt.SIGNAL("clicked()"), self.onRemoveFilterButtonClicked)

        field = Qt.QWidget()
        l = Qt.QHBoxLayout()
        field.setLayout(l)
        l.addWidget(Qt.QLabel("Filter by"))
        l.addWidget(comboBox)
        l.addWidget(edit)
        l.addWidget(addButton)
        l.addWidget(removeButton)
        
        if row is None:
            sl.addWidget(field)
        else:
            sl.insertWidget(row, field)
    
    def _fillComboBox(self, comboBox):
        comboBox.addItem(getElementTypeIcon(ElemType.Attribute), "Attribute", ElemType.Attribute)
        comboBox.addItem(getElementTypeIcon(ElemType.Device), "Device", ElemType.Device)
        comboBox.addItem(getElementTypeIcon(ElemType.DeviceClass), "Device type", ElemType.DeviceClass)
        comboBox.addItem(getElementTypeIcon(ElemType.Domain), "Domain", ElemType.Domain)
        comboBox.addItem(getElementTypeIcon(ElemType.Family), "Family", ElemType.Family)
        comboBox.addItem(getElementTypeIcon(ElemType.Member), "Member", ElemType.Member)
        comboBox.addItem(getElementTypeIcon(ElemType.Server), "Server", ElemType.Server)
        comboBox.addItem(getElementTypeIcon(ElemType.ServerName), "Server Name", ElemType.ServerName)
        comboBox.addItem(getElementTypeIcon(ElemType.ServerInstance), "Server Instance", ElemType.ServerInstance)
    
    def onFilterComboBoxItemSelected(self, index):
        pass
    
    def onAddFilterButtonClicked(self):
        button = self.sender()
        if button is None: 
            return
        field = button.parent()
        index = self.layout().indexOf(field)
        self.insertFilterItem(index+1)
    
    def onRemoveFilterButtonClicked(self):
        l = self.layout()
        # there is a header row, at least one filter row and a stretch at the
        # end, therefore, if there are only three rows, we don't allow to delete
        # the only existing filter
        if l.count() <= 3:
            return
        button = self.sender()
        if button is None: 
            return
        field = button.parent()
        l.removeWidget(field)
        field.setParent(None)

    def onPreview(self):
        import trees
        model = self.getModel()
        dialog = Qt.QDialog()
        dialog.setModal(True)
        w = trees.TaurusTreeWidget(dialog, perspective=self.getHeaderType())
        w.setModel(model)
        w.setFilters( self.calculate() )
        dialog.exec_()

    def getHeaderType(self):
        g_layout = self.layout()
        header = g_layout.itemAt(0).widget()
        headerCombo = header.layout().itemAt(1).widget()
        return Qt.from_qvariant(headerCombo.itemData(headerCombo.currentIndex()))

    def calculate(self):
        db = self.getModelObj()
        if db is None:
            return
        
        g_layout = self.layout()
        
        filters = []
        for i in xrange(1, g_layout.count()-1):
            field_layout = g_layout.itemAt(i).widget().layout()
            comboBox = field_layout.itemAt(1).widget()
            edit = field_layout.itemAt(2).widget()
            
            type = Qt.from_qvariant(comboBox.itemData(comboBox.currentIndex()))
            expr = str(edit.text())
            f = getFilter(type, expr)
            filters.append(f)
        
        finalType = self.getHeaderType()
        filters.append(getFilter(finalType))
        return filters
        
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelClass(self):
        return taurus.core.taurusdatabase.TaurusDatabase

    #: This property holds the unique URI string representing the model name 
    #: with which this widget will get its data from. The convention used for 
    #: the string can be found :ref:`here <model-concept>`.
    #: 
    #: In case the property :attr:`useParentModel` is set to True, the model 
    #: text must start with a '/' followed by the attribute name.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getModel`
    #:     * :meth:`TaurusBaseWidget.setModel`
    #:     * :meth:`TaurusBaseWidget.resetModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    model = Qt.pyqtProperty("QString", taurus.qt.qtgui.base.TaurusBaseWidget.getModel,
                            taurus.qt.qtgui.base.TaurusBaseWidget.setModel,
                            taurus.qt.qtgui.base.TaurusBaseWidget.resetModel)


class TaurusFilterPanelOld2(Qt.QWidget, taurus.qt.qtgui.base.TaurusBaseWidget):
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(taurus.qt.qtgui.base.TaurusBaseWidget, name, designMode=designMode)
        self.init()
    
    def init(self):
        l = Qt.QGridLayout()
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)

        comboBox = Qt.QComboBox()
        comboBox.addItem(getElementTypeIcon(ElemType.Attribute), "Attribute", ElemType.Attribute)
        comboBox.addItem(getElementTypeIcon(ElemType.Device), "Device", ElemType.Device)
        comboBox.addItem(getElementTypeIcon(ElemType.DeviceClass), "Device type", ElemType.DeviceClass)
        comboBox.addItem(getElementTypeIcon(ElemType.Server), "Server", ElemType.Server)
        
        l.addWidget(Qt.QLabel("Filter for:"), 0, 0)
        l.addWidget(comboBox, 0, 1)

        import trees
        self._deviceEdit = Qt.QComboBox()
        self._deviceEdit.setEditable(True)
        self._deviceEdit.setMaxVisibleItems(10)
        self._deviceEdit.setInsertPolicy(Qt.QComboBox.InsertAtTop)
        self._deviceDomainEdit = Qt.QLineEdit()
        self._deviceFamilyEdit = Qt.QLineEdit()
        self._deviceMemberEdit = Qt.QLineEdit()
        self._deviceClass = Qt.QLineEdit()
        self._serverEdit = Qt.QLineEdit()
        self._serverNameEdit = Qt.QLineEdit()
        self._serverInstanceEdit = Qt.QLineEdit()
        self._attributeEdit = Qt.QLineEdit()
        
        lbl = Qt.QLabel("Device type:")
        l.addWidget(lbl, 1, 0)
        l.setAlignment(lbl, Qt.Qt.AlignRight)
        l.addWidget(self._deviceClass, 1, 1)
        l.addWidget(Qt.QLabel("Device:"), 2, 0)
        l.addWidget(self._deviceEdit, 2, 1)
        l.addWidget(Qt.QLabel("Device domain:"), 3, 0)
        l.addWidget(self._deviceDomainEdit, 3, 1)
        l.addWidget(Qt.QLabel("Device family:"), 4, 0)
        l.addWidget(self._deviceFamilyEdit, 4, 1)
        l.addWidget(Qt.QLabel("Device member:"), 5, 0)
        l.addWidget(self._deviceMemberEdit, 5, 1)
        l.addWidget(Qt.QLabel("Server:"), 6, 0)
        l.addWidget(self._serverEdit, 6, 1)
        l.addWidget(Qt.QLabel("Server name:"), 7, 0)
        l.addWidget(self._serverNameEdit, 7, 1)
        l.addWidget(Qt.QLabel("Server instance:"), 8, 0)
        l.addWidget(self._serverInstanceEdit, 8, 1)
        l.addWidget(Qt.QLabel("Attribute:"), 9, 0)
        l.addWidget(self._attributeEdit, 9, 1)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelClass(self):
        return taurus.core.taurusdatabase.TaurusDatabase

    def setModel(self, m):
        taurus.qt.qtgui.base.TaurusBaseWidget.setModel(self, m)
        db = self.getModelObj()
        #model = self._deviceEdit.model()
        #if model is None: return
        #model.setDataSource(db)
        self._deviceEdit.clear()
        if db is not None:
            deviceNames = db.cache().getDeviceNames()
            deviceNames.sort()
            #icon = taurus.core.icons.getElementTypeIcon(ElemType.Device)
            self._deviceEdit.addItems(deviceNames)
        
    #: This property holds the unique URI string representing the model name 
    #: with which this widget will get its data from. The convention used for 
    #: the string can be found :ref:`here <model-concept>`.
    #: 
    #: In case the property :attr:`useParentModel` is set to True, the model 
    #: text must start with a '/' followed by the attribute name.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getModel`
    #:     * :meth:`TaurusBaseWidget.setModel`
    #:     * :meth:`TaurusBaseWidget.resetModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    model = Qt.pyqtProperty("QString", taurus.qt.qtgui.base.TaurusBaseWidget.getModel,
                            taurus.qt.qtgui.base.TaurusBaseWidget.setModel,
                            taurus.qt.qtgui.base.TaurusBaseWidget.resetModel)


import ui_FilterView

class _MessageWidget(Qt.QWidget):

    def __init__(self, parent=None, pixmap=None):
        Qt.QWidget.__init__(self, parent)
        l = Qt.QHBoxLayout()
        self.setLayout(l)
        self._icon = Qt.QLabel()
        if pixmap is None:
            pixmap = getThemePixmap("dialog-warning", 16)
        self._icon.setPixmap(pixmap)
        self._label = Qt.QLabel()
        l.addWidget(self._icon)
        l.addWidget(self._label)
    
    def setText(self, text):
        self._label.setText(text)

class TaurusFilterPanel(Qt.QWidget, taurus.qt.qtgui.base.TaurusBaseWidget):
    
    _Items = "server", "serverName", "serverInstance", \
             "deviceName", "deviceType", "deviceDomain", "deviceFamily", "deviceMember", \
             "attribute"
             
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(taurus.qt.qtgui.base.TaurusBaseWidget, name, designMode=designMode)
        self.init()
    
    def init(self):
        l = Qt.QVBoxLayout()
        self.setLayout(l)

        panel = self._mainPanel = Qt.QWidget()
        l.addWidget(panel, 1)
        form = self.uiForm = ui_FilterView.Ui_FilterForm()
        form.setupUi(panel)
        
        comboBox = form.filterTypeCombo
        comboBox.addItem(getElementTypeIcon(ElemType.Attribute), "Attribute", ElemType.Attribute)
        comboBox.addItem(getElementTypeIcon(ElemType.Device), "Device", ElemType.Device)
        comboBox.addItem(getElementTypeIcon(ElemType.DeviceClass), "Device type", ElemType.DeviceClass)
        comboBox.addItem(getElementTypeIcon(ElemType.Server), "Server", ElemType.Server)

        clickedSig = Qt.SIGNAL("clicked()")
        idxChangedSig = Qt.SIGNAL("currentIndexChanged(int)")
        Qt.QObject.connect(form.serverNameCombo, idxChangedSig, self._updateServerInstanceCombo)
        Qt.QObject.connect(form.deviceDomainCombo, idxChangedSig, self._updateDeviceFamilyCombo)
        Qt.QObject.connect(form.deviceFamilyCombo, idxChangedSig, self._updateDeviceMemberCombo)

        class clearSelection(object):
            def __init__(self, cb):
                self._cb=cb
            def __call__(self):
                self._cb.setCurrentIndex(-1)

        clear_icon = getThemeIcon("edit-clear")
        for combo, clearButton in zip(self.combos(), self.clearButtons()):
            Qt.QObject.connect(combo, idxChangedSig, self._updateStatusBar)
            Qt.QObject.connect(clearButton, clickedSig, clearSelection(combo))
            clearButton.setIcon(clear_icon)
        
        sb = self._statusbar = Qt.QStatusBar()
        sb.setSizeGripEnabled(False)
        l.addWidget(sb)
        sbWarningMsg = self._sbWarningMsg = _MessageWidget()
        sbWarningMsg.setVisible(False)
        sb.addWidget(sbWarningMsg)
    
    def combos(self):
        if not hasattr(self, "_combos"):
            f = self.uiForm
            self._combos = [ getattr(f, name + "Combo") for name in self._Items ]
        return self._combos

    def clearButtons(self):
        if not hasattr(self, "_clearButtons"):
            f = self.uiForm
            self._clearButtons = [ getattr(f, name + "ClearButton") for name in self._Items ]
        return self._clearButtons
    
    def _db_cache(self):
        db = self.getModelObj()
        if db is None: return
        return db.cache()

    def _updateStatusBar(self, index=None):
        form = self.uiForm
        server = str(form.serverCombo.currentText())
        serverName = str(form.serverNameCombo.currentText())
        serverInstance = str(form.serverInstanceCombo.currentText())
        
        msg = self._sbWarningMsg
        msg.setVisible(False)

        if server and (serverName or serverInstance):
            sb = self._statusbar
            s = "Specifying name filter and type/instance filters at the same " \
                "time may result in an empty filter"
            msg.setVisible(True)
            msg.setText(s)
        
        deviceName = str(form.deviceNameCombo.currentText())
        deviceDomain = str(form.deviceDomainCombo.currentText())
        deviceFamily = str(form.deviceFamilyCombo.currentText())
        deviceMember = str(form.deviceMemberCombo.currentText())
        
        if deviceName and (deviceDomain or deviceFamily or deviceMember):
            sb = self._statusbar
            s = "Specifying name filter and domain/family/member filters at the same " \
                "time may result in an empty filter"
            msg.setVisible(True)
            msg.setText(s)
        
        
    def _updateServerCombo(self, index=None):
        combo = self.uiForm.serverCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return
        servers = db_cache.servers()
        icon = getElementTypeIcon(ElemType.Server)
        for serverName in sorted(servers):
            serverInfo = servers[serverName]
            combo.addItem(icon, serverName, serverInfo)
        combo.setCurrentIndex(-1)

    def _updateServerNameCombo(self, index=None):
        combo = self.uiForm.serverNameCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return
        servers = db_cache.servers()
        serverNames = []
        for server in servers.values():
            name = server.serverName()
            if name not in serverNames:
                serverNames.append(name)
        serverNames.sort()
        icon = getElementTypeIcon(ElemType.ServerName)
        for serverName in serverNames:
            combo.addItem(icon, serverName)
        combo.setCurrentIndex(-1)

    def _updateServerInstanceCombo(self, index=None):
        combo = self.uiForm.serverInstanceCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return
        if index is None or index == -1: return
        serverName = str(self.sender().currentText())
        servers = db_cache.servers()
        serverInstances = []
        for server in servers.values():
            if server.serverName() == serverName:
                serverInstances.append(server.serverInstance())
        serverInstances.sort()
        icon = getElementTypeIcon(ElemType.ServerInstance)
        for serverInstance in serverInstances:
            combo.addItem(icon, serverInstance)
        combo.setCurrentIndex(-1)
        
    def _updateDeviceTypeCombo(self, index=None):
        combo = self.uiForm.deviceTypeCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return
        deviceKlasses = db_cache.klasses()
        icon = getElementTypeIcon(ElemType.DeviceClass)
        for klassName in sorted(deviceKlasses):
            klassInfo = deviceKlasses[klassName]
            combo.addItem(icon, klassName, klassInfo)
        combo.setCurrentIndex(-1)

    def _updateDeviceNameCombo(self, index=None):
        combo = self.uiForm.deviceNameCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return
        devices = db_cache.devices()
        icon = getElementTypeIcon(ElemType.Device)
        for deviceName in sorted(devices):
            deviceInfo = devices[deviceName]
            combo.addItem(icon, deviceName, deviceInfo)
        combo.setCurrentIndex(-1)

    def _updateDeviceDomainCombo(self, index=None):
        combo = self.uiForm.deviceDomainCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return
        domains = db_cache.getDeviceDomainNames()
        domains.sort()
        icon = getElementTypeIcon(ElemType.Domain)
        for domain in domains:
            combo.addItem(icon, domain)
        combo.setCurrentIndex(-1)

    def _updateDeviceFamilyCombo(self, index=None):
        combo = self.uiForm.deviceFamilyCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return
        
        deviceDomain = str(self.uiForm.deviceDomainCombo.currentText())
        if deviceDomain == "": return
        families = db_cache.getDeviceFamilyNames(deviceDomain)
        families.sort()
        icon = getElementTypeIcon(ElemType.Family)
        for family in families:
            combo.addItem(icon, family)
        combo.setCurrentIndex(-1)

    def _updateDeviceMemberCombo(self, index=None):
        combo = self.uiForm.deviceMemberCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return

        deviceDomain = str(self.uiForm.deviceDomainCombo.currentText())
        if deviceDomain == "": return
        deviceFamily = str(self.uiForm.deviceFamilyCombo.currentText())
        if deviceFamily == "": return
        members = db_cache.getDeviceMemberNames(deviceDomain, deviceFamily)
        members.sort()
        icon = getElementTypeIcon(ElemType.Member)
        for member in members:
            combo.addItem(icon, member)
        combo.setCurrentIndex(-1)
        
    def _updateAttributeCombo(self, index=None):
        combo = self.uiForm.attributeCombo
        combo.clear()
        db_cache = self._db_cache()
        if db_cache is None: return

    def _fillItems(self):
        self._updateServerCombo()
        self._updateServerNameCombo()
        self._updateServerInstanceCombo()
        self._updateDeviceTypeCombo()
        self._updateDeviceNameCombo()
        self._updateDeviceDomainCombo()
        self._updateDeviceFamilyCombo()
        self._updateDeviceMemberCombo()
        self._updateAttributeCombo()
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelClass(self):
        return taurus.core.taurusdatabase.TaurusDatabase

    def setModel(self, m):
        taurus.qt.qtgui.base.TaurusBaseWidget.setModel(self, m)
        db = self.getModelObj()
        #model = self._deviceEdit.model()
        #if model is None: return
        #model.setDataSource(db)
        self.uiForm.deviceNameCombo.clear()
        self._fillItems()
        
    #: This property holds the unique URI string representing the model name 
    #: with which this widget will get its data from. The convention used for 
    #: the string can be found :ref:`here <model-concept>`.
    #: 
    #: In case the property :attr:`useParentModel` is set to True, the model 
    #: text must start with a '/' followed by the attribute name.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getModel`
    #:     * :meth:`TaurusBaseWidget.setModel`
    #:     * :meth:`TaurusBaseWidget.resetModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    model = Qt.pyqtProperty("QString", taurus.qt.qtgui.base.TaurusBaseWidget.getModel,
                            taurus.qt.qtgui.base.TaurusBaseWidget.setModel,
                            taurus.qt.qtgui.base.TaurusBaseWidget.resetModel)


def main():
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    import sys
    
    parser = argparse.get_taurus_parser()
    parser.usage = "%prog [options] [hostname]"
    
    app = TaurusApplication(cmd_line_parser=parser)
    args = app.get_command_line_args()
    
    if len(args)>0: 
        host=args[0]
    else: 
        host = taurus.Database().getNormalName()
    
    w = TaurusFilterPanel()
    w.setWindowIcon(Qt.QIcon(":/actions/system-shutdown.svg"))
    w.setWindowTitle("A Taurus Filter Example")
    w.setModel(host)
    w.show()

    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
