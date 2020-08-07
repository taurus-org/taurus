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
taurusvalue.py:
"""

__all__ = ["TaurusValue", "TaurusValuesFrame", "DefaultTaurusValueCheckBox",
           "DefaultUnitsWidget", "TaurusPlotButton", "TaurusArrayEditorButton",
           "TaurusValuesTableButton", "TaurusValuesTableButton_W",
           "DefaultLabelWidget", "DefaultReadWidgetLabel", "TaurusDevButton",
           "TaurusImageButton"]

__docformat__ = 'restructuredtext'

from future.utils import string_types
from future.builtins import str

import weakref
import re
from taurus.external.qt import Qt
import taurus.core
from taurus.core import DataType, DataFormat, TaurusEventType

from taurus.core.taurusbasetypes import TaurusElementType
from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.container import TaurusFrame
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.display import TaurusLed
from taurus.qt.qtgui.input import TaurusValueSpinBox, TaurusValueCheckBox
from taurus.qt.qtgui.input import TaurusWheelEdit, TaurusValueLineEdit
from taurus.qt.qtgui.button import TaurusLauncherButton
from taurus.qt.qtgui.util import TaurusWidgetFactory, ConfigurationMenu
from taurus.qt.qtgui.compact import TaurusReadWriteSwitcher
from taurus.core.util.log import deprecation_decorator


class DefaultTaurusValueCheckBox(TaurusValueCheckBox):

    def __init__(self, *args):
        TaurusValueCheckBox.__init__(self, *args)
        self.setShowText(False)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class DefaultLabelWidget(TaurusLabel):
    '''
    The base class used by default for showing the label of a TaurusValue.

    .. note:: It only makes sense to use this class as a part of a TaurusValue,
              since it assumes that it can get a reference to a TaurusValue via
              the :meth:`getTaurusValueBuddy` member
    '''

    _dragEnabled = True

    def __init__(self, *args):
        TaurusLabel.__init__(self, *args)
        self.setAlignment(Qt.Qt.AlignRight)
        self.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Maximum)
        self.setBgRole(None)
        self.autoTrim = False
        self.setStyleSheet(
            'DefaultLabelWidget {border-style: solid; border-width: 1px; border-color: transparent; border-radius: 4px;}')

    def setModel(self, model):
        if model is None or model == '':
            return TaurusLabel.setModel(self, None)
        try:
            config = self.taurusValueBuddy().getLabelConfig()
        except Exception:
            config = '{attr.label}'
        elementtype = self.taurusValueBuddy().getModelType()
        fullname = self.taurusValueBuddy().getModelObj().getFullName()
        if elementtype == TaurusElementType.Attribute:
            config = self.taurusValueBuddy().getLabelConfig()
            TaurusLabel.setModel(self, '%s#%s' % (fullname, config))
        elif elementtype == TaurusElementType.Device:
            devName = self.taurusValueBuddy().getModelObj().getSimpleName()
            TaurusLabel.setModel(self, model)
            self.setText(devName)

    _BCK_COMPAT_TAGS = {'<attr_name>': '{attr.name}',
                        '<attr_fullname>': '{attr.fullname}',
                        '<dev_alias>': '{dev.name}',
                        '<dev_name>': '{dev.name}',
                        '<dev_fullname>': '{dev.fullname}',
                        }

    def getDisplayValue(self, cache=True, fragmentName=None):
        """Reimplementation of getDisplayValue"""
        if self.modelObj is None or fragmentName is None:
            return self.getNoneValue()
        # support bck-compat tags
        for old in re.findall('<.+?>', fragmentName):
            new = self._BCK_COMPAT_TAGS.get(old, '{attr.%s}' % old)
            self.deprecated(dep=old, alt=new)
            fragmentName = fragmentName.replace(old, new)

        return TaurusLabel.displayValue(self, fragmentName)

    def sizeHint(self):
        return Qt.QSize(Qt.QLabel.sizeHint(self).width(), 18)

    def contextMenuEvent(self, event):
        """ The label widget will be used for handling the actions of the whole TaurusValue

        see :meth:`QWidget.contextMenuEvent`"""
        menu = Qt.QMenu(self)
        # @todo: This should be done more Taurus-ish
        menu.addMenu(ConfigurationMenu(self.taurusValueBuddy()))
        if hasattr(self.taurusValueBuddy().writeWidget(followCompact=True), 'resetPendingOperations'):
            r_action = menu.addAction("reset write value", self.taurusValueBuddy(
            ).writeWidget(followCompact=True).resetPendingOperations)
            r_action.setEnabled(self.taurusValueBuddy().hasPendingOperations())
        if self.taurusValueBuddy().isModifiableByUser():
            menu.addAction("Change label",
                           self.taurusValueBuddy()._onChangeLabelText)
            menu.addAction("Change Read Widget",
                           self.taurusValueBuddy().onChangeReadWidget)
            menu.addAction("Set Formatter",
                           self.taurusValueBuddy().onSetFormatter)
            cw_action = menu.addAction(
                "Change Write Widget", self.taurusValueBuddy().onChangeWriteWidget)
            # disable the action if the taurusValue is readonly
            cw_action.setEnabled(not self.taurusValueBuddy().isReadOnly())
            cm_action = menu.addAction("Compact")
            cm_action.setCheckable(True)
            cm_action.setChecked(self.taurusValueBuddy().isCompact())
            cm_action.toggled.connect(self.taurusValueBuddy().setCompact)
        menu.exec_(event.globalPos())
        event.accept()

    def getModelMimeData(self):
        """
        reimplemented to use the taurusValueBuddy model instead of its own
        model
        """
        mimeData = TaurusLabel.getModelMimeData(self)
        _modelname = str(self.taurusValueBuddy().getModelName())
        modelname = _modelname.encode(encoding='utf8')
        mimeData.setData(TAURUS_MODEL_MIME_TYPE, modelname)
        if self.taurusValueBuddy().getModelType() == TaurusElementType.Device:
            mimeData.setData(TAURUS_DEV_MIME_TYPE, modelname)
        elif self.taurusValueBuddy().getModelType() == TaurusElementType.Attribute:
            mimeData.setData(TAURUS_ATTR_MIME_TYPE, modelname)
        return mimeData

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class ExpandingLabel(TaurusLabel):
    '''just a expanding TaurusLabel'''

    def __init__(self, *args):
        TaurusLabel.__init__(self, *args)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Preferred)


class DefaultReadWidgetLabel(ExpandingLabel):
    """A customised label for the read widget"""

    def setModel(self, m):
        TaurusLabel.setModel(self, m)
        fgrole = 'rvalue'
        model_obj = self.getModelObj()
        if model_obj is None:
            return
        if model_obj.getType() in (DataType.Integer, DataType.Float):
            fgrole += '.magnitude'
        self.setFgRole(fgrole)


class CenteredLed(TaurusLed):
    '''just a centered TaurusLed'''
    DefaultAlignment = Qt.Qt.AlignHCenter | Qt.Qt.AlignVCenter


class UnitLessLineEdit(TaurusValueLineEdit):
    """A customised TaurusValueLineEdit that always shows the magnitude"""
    def setModel(self, model):
        if model is None or model == '':
            return TaurusValueLineEdit.setModel(self, None)
        return TaurusValueLineEdit.setModel(self, model + "#wvalue.magnitude")



class DefaultUnitsWidget(TaurusLabel):

    FORMAT = "{}"

    def __init__(self, *args):
        TaurusLabel.__init__(self, *args)
        self.setNoneValue('')
        self.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Maximum)
        self.autoTrim = False
        self.setBgRole(None)
        self.setAlignment(Qt.Qt.AlignLeft)

    def setModel(self, model):
        if model is None or model == '':
            return TaurusLabel.setModel(self, None)
        TaurusLabel.setModel(self, model + "#rvalue.units")

    def sizeHint(self):
        # print "UNITSSIZEHINT:",Qt.QLabel.sizeHint(self).width(),
        # self.minimumSizeHint().width(),
        # Qt.QLabel.minimumSizeHint(self).width()
        return Qt.QSize(Qt.QLabel.sizeHint(self).width(), 24)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class _AbstractTaurusValueButton(TaurusLauncherButton):
    _deleteWidgetOnClose = True
    _text = 'Show'

    def __init__(self, parent=None, designMode=False):
        TaurusLauncherButton.__init__(
            self, parent=parent, designMode=designMode)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Maximum)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class TaurusPlotButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusPlot'''
    _widgetClassName = 'TaurusPlot'
    _icon = 'designer:qwtplot.png'


class TaurusArrayEditorButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusArrayEditor'''
    _widgetClassName = 'TaurusArrayEditor'
    _icon = 'designer:arrayedit.png'
    _text = 'Edit'


class TaurusImageButton(_AbstractTaurusValueButton):
    '''A button that launches an ImageDialog'''
    _widgetClassName = 'TaurusImageDialog'
    _icon = 'mimetypes:image-x-generic.svg'


class TaurusValuesTableButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusValuesTable'''
    _widgetClassName = 'TaurusValuesTable'
    _icon = 'designer:table.png'
    _kwargs = {'defaultWriteMode': 'r'}


class TaurusValuesTableButton_W(TaurusValuesTableButton):
    '''A button that launches a TaurusValuesTable'''
    _text = 'Edit'
    _kwargs = {'defaultWriteMode': 'w'}


class TaurusDevButton(_AbstractTaurusValueButton):
    '''A button that launches a TaurusAttrForm'''
    _widgetClassName = 'TaurusDevicePanel'
    _icon = 'places:folder-remote.svg'
    _text = 'Show Device'


class TaurusStatusLabel(TaurusLabel):
    '''just a taurusLabel but showing the state as its background by default'''

    def __init__(self, parent=None, designMode=False):
        TaurusLabel.__init__(self, parent=parent, designMode=designMode)
        self.setBgRole('state')
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Maximum)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class TaurusValue(Qt.QWidget, TaurusBaseWidget):
    '''
    Internal TaurusValue class

    .. warning::

        :class:`TaurusValue` (and any derived class from it) should never be instantiated directly.
        It is designed to be instantiated by a :class:`TaurusForm` class, since it
        breaks some conventions on the way it manages layouts of its parent model.
    '''
    _compact = False

    def __init__(self, parent=None, designMode=False, customWidgetMap=None):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

        self.__error = False
        self.__modelClass = None
        self._designMode = designMode

        # This is a hack to show something usable when in designMode
        if self._designMode:
            layout = Qt.QHBoxLayout(self)
            dummy = ExpandingLabel()
            layout.addWidget(dummy)
            #dummy.setUseParentModel(True)
            dummy.setModel("#attr_fullname")
            dummy.setPrefixText("< TaurusValue: ")
            dummy.setSuffixText(" >")
        else:
            self.setFixedSize(0, 0)

        self._labelWidget = None
        self._readWidget = None
        self._writeWidget = None
        self._unitsWidget = None
        self._customWidget = None  # deprecated
        self._extraWidget = None

        if customWidgetMap is None:
            customWidgetMap = {}
        else:
            self.deprecated(
                dep="customWidgetMap arg",
                alt="Form item factories",
                rel="4.6.5"
            )
        self._customWidgetMap = customWidgetMap  # deprecated


        self.labelWidgetClassID = 'Auto'
        self.readWidgetClassID = 'Auto'
        self.writeWidgetClassID = 'Auto'
        self.unitsWidgetClassID = 'Auto'
        self.customWidgetClassID = 'Auto'  # deprecated
        self.extraWidgetClassID = 'Auto'
        self.setPreferredRow(-1)
        self._row = None

        self._allowWrite = True
        self._minimumHeight = None
        self._labelConfig = '{attr.label}'
        self.setModifiableByUser(False)

        if parent is not None:
            self.setParent(parent)

        self.registerConfigProperty(
            self.getLabelConfig, self.setLabelConfig, 'labelConfig')
        self.registerConfigProperty(self.isCompact, self.setCompact, 'compact')

    def setVisible(self, visible):
        for w in (self.labelWidget(), self.readWidget(), self.writeWidget(),
                  self.unitsWidget(), self._customWidget, self.extraWidget()):
            if w is not None:
                w.setVisible(visible)
        Qt.QWidget.setVisible(self, visible)

    def labelWidget(self):
        '''Returns the label widget'''
        return self._labelWidget

    def readWidget(self, followCompact=False):
        '''
        Returns the read widget. If followCompact=True, and compact mode is
        used, it returns the switcher's readWidget instead of the switcher
        itself.
        '''
        if followCompact and self.isCompact():
            return getattr(self._readWidget, 'readWidget', self._readWidget)
        return self._readWidget

    def writeWidget(self, followCompact=False):
        '''
        Returns the write widget. If followCompact=True, and compact mode is
        used, it returns the switcher's writeWidget instead of None.
        '''
        if followCompact and self.isCompact():
            return getattr(self._readWidget, 'writeWidget', None)
        return self._writeWidget

    def unitsWidget(self):
        '''Returns the units widget'''
        return self._unitsWidget

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def customWidget(self):
        '''Returns the custom widget'''
        return self._customWidget

    def extraWidget(self):
        '''Returns the extra widget'''
        return self._extraWidget

    def setParent(self, parent):

        # make sure that the parent has a QGriLayout
        pl = parent.layout()
        if pl is None:
            pl = Qt.QGridLayout(parent)  # creates AND sets the parent layout
        if not isinstance(pl, Qt.QGridLayout):
            raise ValueError(
                'layout must be a QGridLayout (got %s)' % type(pl))

        if self._row is None:
            # @TODO we should check that the Preferred row is empty in pl
            self._row = self.getPreferredRow()
            if self._row < 0:
                self._row = pl.rowCount()
        # print 'ROW:',self, self.getRow()

        # insert self into the 0-column
        # this widget is invisible (except in design mode)
        pl.addWidget(self, self._row, 0)

        # Create/update the subwidgets (this also inserts them in the layout)
        if not self._designMode:  # in design mode, no subwidgets are created
            self.updateLabelWidget()
            self.updateReadWidget()
            self.updateWriteWidget()
            self.updateUnitsWidget()
            self.updateExtraWidget()

        # do the base class stuff too
        Qt.QWidget.setParent(self, parent)

    def onSetFormatter(self):
        """
        Reimplemented to call onSetFormatter of the read widget (if provided)
        """
        rw = self.readWidget(followCompact=True)
        if hasattr(rw, 'onSetFormatter'):
            return rw.onSetFormatter()

    def setFormat(self, format):
        """
        Reimplemented to call setFormat of the read widget (if provided)
        """
        TaurusBaseWidget.setFormat(self, format)
        try:
            rw = self.readWidget(followCompact=True)
        except AttributeError:
            return
        if hasattr(rw, 'setFormat'):
            rw.setFormat(format)

    def getAllowWrite(self):
        return self._allowWrite

    @Qt.pyqtSlot(bool)
    def setAllowWrite(self, mode):
        self._allowWrite = mode

    def resetAllowWrite(self):
        self._allowWrite = True

    def getPreferredRow(self):
        return self._preferredRow

    @Qt.pyqtSlot(int)
    def setPreferredRow(self, row):
        self._preferredRow = row

    def resetPreferredRow(self):
        self.setPreferredRow(-1)

    def getRow(self):
        return self._row

    def setMinimumHeight(self, minimumHeight):
        self._minimumHeight = minimumHeight

    def minimumHeight(self):
        return self._minimumHeight

    def getDefaultLabelWidgetClass(self):
        return DefaultLabelWidget

    def getDefaultReadWidgetClass(self, returnAll=False):
        '''
        Returns the default class (or classes) to use as read widget for the
        current model.

        :param returnAll: (bool) if True, the return value is a list of valid
                          classes instead of just one class

        :return: (class or list<class>) the default class  to use for the read
                 widget (or, if returnAll==True, a list of classes that can show
                 the attribute ). If a list is returned, it will be loosely
                 ordered by preference, being the first element always the
                 default one.
        '''
        modelobj = self.getModelObj()
        if modelobj is None:
            if returnAll:
                return [DefaultReadWidgetLabel]
            else:
                return DefaultReadWidgetLabel

        modeltype = self.getModelType()
        if modeltype == TaurusElementType.Attribute:
            # The model is an attribute
            # print "---------ATTRIBUTE OBJECT:----------\n",modelobj.read()
            try:
                if modelobj.isBoolean():
                    result = [CenteredLed, DefaultReadWidgetLabel]
            except:
                pass
            if modelobj.data_format == DataFormat._0D:
                if modelobj.type == DataType.Boolean:
                    result = [CenteredLed, DefaultReadWidgetLabel]
                elif modelobj.type == DataType.DevState:
                    result = [CenteredLed, DefaultReadWidgetLabel]
                elif str(self.getModel()).lower().endswith('/status'):  # @todo: tango-centric!!
                    result = [TaurusStatusLabel, DefaultReadWidgetLabel]
                else:
                    result = [DefaultReadWidgetLabel]
            elif modelobj.data_format == DataFormat._1D:
                if modelobj.type in (DataType.Float, DataType.Integer):
                    result = [TaurusPlotButton,
                              TaurusValuesTableButton, DefaultReadWidgetLabel]
                else:
                    result = [TaurusValuesTableButton, DefaultReadWidgetLabel]
            elif modelobj.data_format == DataFormat._2D:
                if modelobj.type in (DataType.Float, DataType.Integer):
                    try:
                        # unused import but useful to determine if
                        # TaurusImageButton should be added
                        from taurus.qt.qtgui.extra_guiqwt import TaurusImageDialog
                        result = [TaurusImageButton,
                                  TaurusValuesTableButton, DefaultReadWidgetLabel]
                    except ImportError:
                        result = [TaurusValuesTableButton,
                                  DefaultReadWidgetLabel]
                else:
                    result = [TaurusValuesTableButton, DefaultReadWidgetLabel]
            else:
                self.warning('Unsupported attribute type %s' % modelobj.type)
                result = None

        elif modeltype == TaurusElementType.Device:
            result = [TaurusDevButton]
        else:
            msg = "Unsupported model type ('%s')" % modeltype
            self.warning(msg)
            raise ValueError(msg)

        if returnAll:
            return result
        else:
            return result[0]

    def getDefaultWriteWidgetClass(self, returnAll=False):
        '''
        Returns the default class (or classes) to use as write widget for the
        current model.

        :param returnAll: (bool) if True, the return value is a list of valid
                          classes instead of just one class

        :return: (class or list<class>) the default class  to use for the write
                 widget (or, if returnAll==True, a list of classes that can show
                 the attribute ). If a list is returned, it will be loosely
                 ordered by preference, being the first element always the
                 default one.
        '''
        modelclass = self.getModelClass()
        if self.isReadOnly() or (modelclass and modelclass.getTaurusElementType() != TaurusElementType.Attribute):
            if returnAll:
                return []
            else:
                return None
        modelobj = self.getModelObj()
        if modelobj is None:
            if returnAll:
                return [UnitLessLineEdit]
            else:
                return UnitLessLineEdit
        modelType = modelobj.getType()
        if modelobj.data_format == DataFormat._0D:
            if modelType == DataType.Boolean:
                result = [DefaultTaurusValueCheckBox, TaurusValueLineEdit]
            else:
                result = [UnitLessLineEdit,
                          TaurusValueSpinBox, TaurusWheelEdit]
        elif modelobj.data_format == DataFormat._1D:
            result = [TaurusValuesTableButton_W, TaurusValueLineEdit]
            if modelType in (DataType.Float, DataType.Integer):
                try:
                    import PyQt4.Qwt5  # noqa
                    result.insert(0, TaurusArrayEditorButton)
                except:
                    pass
        elif modelobj.data_format == DataFormat._2D:
            result = [TaurusValuesTableButton_W]
        else:
            self.debug('Unsupported attribute type for writing: %s' %
                       str(DataType.whatis(modelType)))
            result = [None]

        if returnAll:
            return result
        else:
            return result[0]

    def getDefaultUnitsWidgetClass(self):
        #        if self.getModelClass() != taurus.core.taurusattribute.TaurusAttribute:
        #            return DefaultUnitsWidget
        return DefaultUnitsWidget

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def getDefaultCustomWidgetClass(self):
        self.__getDefaultCustomWidgetClass()

    def __getDefaultCustomWidgetClass(self):
        """
        renamed from __getDefaultCustomWidgetClass to avoid deprecation
        warnings. To be removed.
        """
        modelclass = self.getModelClass()
        if modelclass and modelclass.getTaurusElementType() != TaurusElementType.Device:
            return None
        try:
            key = self.getModelObj().getDeviceProxy().info().dev_class
        except:
            return None
        return self._customWidgetMap.get(key, None)

    def getDefaultExtraWidgetClass(self):
        return None

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def setCustomWidgetMap(self, cwmap):
        '''Sets a map map for custom widgets.

        :param cwmap: (dict<str,Qt.QWidget>) a dictionary whose keys are device
                      class strings (see :class:`PyTango.DeviceInfo`) and
                      whose values are widget classes to be used
        '''
        self._customWidgetMap = cwmap

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def getCustomWidgetMap(self):
        '''Returns the map used to create custom widgets.

        :return: (dict<str,Qt.QWidget>) a dictionary whose keys are device
                 type strings (i.e. see :class:`PyTango.DeviceInfo`) and whose
                 values are widgets to be used
        '''
        return self._customWidgetMap

    def onChangeLabelConfig(self):
        self.deprecated(msg="onChangeLabelConfig is deprecated", rel="Jan2018")
        self._onChangeLabelText()

    def _onChangeLabelText(self):
        keys = ['{attr.label}', '{attr.name}', '{attr.fullname}', '{dev.name}',
                '{dev.fullname}']

        try:
            current = keys.index(self.labelConfig)
        except:
            current = len(keys)
            keys.append(self.labelConfig)

        msg = 'Choose the label format. \n' + \
              'You may use Python format() syntax. The TaurusDevice object\n' + \
              'can be referenced as "dev" and the TaurusAttribute object\n' + \
              'as "attr"'

        labelConfig, ok = Qt.QInputDialog.getItem(self, 'Change Label', msg,
                                                  keys, current, True)
        if ok:
            self.labelConfig = labelConfig

    def onChangeReadWidget(self):
        classnames = ['None', 'Auto'] + \
            [c.__name__ for c in self.getDefaultReadWidgetClass(
                returnAll=True)]
        cname, ok = Qt.QInputDialog.getItem(
            self, 'Change Read Widget', 'Choose a new read widget class', classnames, 1, True)
        if ok:
            self.setReadWidgetClass(str(cname))

    def onChangeWriteWidget(self):
        classnames = ['None', 'Auto'] + \
            [c.__name__ for c in self.getDefaultWriteWidgetClass(
                returnAll=True)]
        cname, ok = Qt.QInputDialog.getItem(
            self, 'Change Write Widget', 'Choose a new write widget class', classnames, 1, True)
        if ok:
            self.setWriteWidgetClass(str(cname))

    def _destroyWidget(self, widget):
        '''get rid of a widget in a safe way'''
        widget.hide()
        widget.setParent(None)
        if hasattr(widget, 'setModel'):
            widget.setModel(None)
        # COULD NOT INVESTIGATE DEEPER, BUT THE STARTUP-HANGING
        # HAPPENS WITH SOME SIGNALS RELATED WITH THE LINEEDIT...
        # MAYBE OTHER 'WRITE WIDGETS' HAVE THE SAME PROBLEM ?!?!?!
        if isinstance(widget, Qt.QLineEdit):
            widget.blockSignals(True)
        # THIS HACK REDUCES THE STARTUP-HANGING RATE
        widget.deleteLater()

    def _newSubwidget(self, oldWidget, newClass):
        '''eliminates oldWidget and returns a new one.
        If newClass is None, None is returned
        If newClass is the same as the olWidget class, nothing happens'''
        if oldWidget.__class__ == newClass:
            return oldWidget
        if oldWidget is not None:
            self._destroyWidget(oldWidget)
        if newClass is None:
            result = None
        else:
            result = newClass()
        return result

    def labelWidgetClassFactory(self, classID):
        if self._customWidget is not None:
            return None
        if classID is None or classID == 'None':
            return None
        classID = globals().get(classID, classID)
        if isinstance(classID, type):
            return classID
        elif str(classID) == 'Auto':
            return self.getDefaultLabelWidgetClass()
        else:
            return TaurusWidgetFactory().getWidgetClass(classID)

    def readWidgetClassFactory(self, classID):
        if self._customWidget is not None:
            return None
        if classID is None or classID == 'None':
            return None
        classID = globals().get(classID, classID)
        if isinstance(classID, type):
            ret = classID
        elif str(classID) == 'Auto':
            ret = self.getDefaultReadWidgetClass()
        else:
            ret = TaurusWidgetFactory().getWidgetClass(classID)

        if self._compact:
            R = ret
            W = self.writeWidgetClassFactory(
                self.writeWidgetClassID, ignoreCompact=True)
            if W is None:
                return R
            switcherClass = self.getSwitcherClass()
            switcherClass.readWClass = R
            switcherClass.writeWClass = W
            return switcherClass
        return ret

    def writeWidgetClassFactory(self, classID, ignoreCompact=False):
        if self._customWidget is not None:
            return None
        if classID is None or classID == 'None':
            return None
        if self._compact and not ignoreCompact:
            return None
        classID = globals().get(classID, classID)
        if isinstance(classID, type):
            return classID
        elif str(classID) == 'Auto':
            return self.getDefaultWriteWidgetClass()
        else:
            return TaurusWidgetFactory().getWidgetClass(classID)

    def unitsWidgetClassFactory(self, classID):
        if self._customWidget is not None:
            return None
        if classID is None or classID == 'None':
            return None
        classID = globals().get(classID, classID)
        if isinstance(classID, type):
            return classID
        elif str(classID) == 'Auto':
            return self.getDefaultUnitsWidgetClass()
        else:
            return TaurusWidgetFactory().getWidgetClass(classID)

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def customWidgetClassFactory(self, classID):
        return self.__customWidgetClassFactory(self, classID)

    def __customWidgetClassFactory(self, classID):
        """
        renamed from customWidgetClassFactory to avoid deprecation warnings.
        To be removed.
        """
        if classID is None or classID == 'None':
            return None
        classID = globals().get(classID, classID)
        if isinstance(classID, type):
            return classID
        elif str(classID) == 'Auto':
            return self.__getDefaultCustomWidgetClass()
        else:
            return TaurusWidgetFactory().getWidgetClass(classID)

    def extraWidgetClassFactory(self, classID):
        if self._customWidget is not None:
            return None
        if classID is None or classID == 'None':
            return None
        classID = globals().get(classID, classID)
        if isinstance(classID, type):
            return classID
        elif str(classID) == 'Auto':
            return self.getDefaultExtraWidgetClass()
        else:
            return TaurusWidgetFactory().getWidgetClass(classID)

    def updateLabelWidget(self):
        # get the class for the widget and replace it if necessary
        klass = self.labelWidgetClassFactory(self.labelWidgetClassID)
        self._labelWidget = self._newSubwidget(self._labelWidget, klass)

        # take care of the layout
        self.addLabelWidgetToLayout()

        if self._labelWidget is not None:
            # give the new widget a reference to its buddy TaurusValue object
            self._labelWidget.taurusValueBuddy = weakref.ref(self)

            # tweak the new widget
            if self.minimumHeight() is not None:
                self._labelWidget.setMinimumHeight(self.minimumHeight())

            # set the model for the subwidget
            if hasattr(self._labelWidget, 'setModel'):
                self._labelWidget.setModel(self.getFullModelName())

    def updateReadWidget(self):
        # get the class for the widget and replace it if necessary
        try:
            klass = self.readWidgetClassFactory(self.readWidgetClassID)
            self._readWidget = self._newSubwidget(self._readWidget, klass)
        except Exception as e:
            self._destroyWidget(self._readWidget)
            self._readWidget = Qt.QLabel('[Error]')
            msg = 'Error creating read widget:\n' + str(e)
            self._readWidget.setToolTip(msg)
            self.debug(msg)
            # self.traceback(30) #warning level=30

        # take care of the layout
        self.addReadWidgetToLayout()

        if self._readWidget is not None:
            # give the new widget a reference to its buddy TaurusValue object
            self._readWidget.taurusValueBuddy = weakref.ref(self)
            if isinstance(self._readWidget, TaurusReadWriteSwitcher):
                self._readWidget.readWidget.taurusValueBuddy = weakref.ref(
                    self)
                self._readWidget.writeWidget.taurusValueBuddy = weakref.ref(
                    self)

            # tweak the new widget
            if self.minimumHeight() is not None:
                self._readWidget.setMinimumHeight(self.minimumHeight())

            # set the model for the subwidget
            if hasattr(self._readWidget, 'setModel'):
                self._readWidget.setModel(self.getFullModelName())

    def updateWriteWidget(self):
        # get the class for the widget and replace it if necessary
        klass = self.writeWidgetClassFactory(self.writeWidgetClassID)
        self._writeWidget = self._newSubwidget(self._writeWidget, klass)

        # take care of the layout
        # this is needed because the writeWidget affects to the readWritget
        # layout
        self.addReadWidgetToLayout()
        self.addWriteWidgetToLayout()

        if self._writeWidget is not None:
            # give the new widget a reference to its buddy TaurusValue object
            self._writeWidget.taurusValueBuddy = weakref.ref(self)

            # tweak the new widget
            # hide getPendingOperations of the writeWidget so that containers don't get duplicate lists
            #self._writeWidget._getPendingOperations = self._writeWidget.getPendingOperations
            #self._writeWidget.getPendingOperations = lambda : []
            self._writeWidget.valueChangedSignal.connect(self.updatePendingOpsStyle)
            self._writeWidget.setDangerMessage(self.getDangerMessage())
            self._writeWidget.setForceDangerousOperations(
                self.getForceDangerousOperations())
            if self.minimumHeight() is not None:
                self._writeWidget.setMinimumHeight(self.minimumHeight())

            # set the model for the subwidget
            if hasattr(self._writeWidget, 'setModel'):
                self._writeWidget.setModel(self.getFullModelName())

    def updateUnitsWidget(self):
        # get the class for the widget and replace it if necessary
        klass = self.unitsWidgetClassFactory(self.unitsWidgetClassID)
        self._unitsWidget = self._newSubwidget(self._unitsWidget, klass)

        # take care of the layout
        self.addUnitsWidgetToLayout()

        if self._unitsWidget is not None:
            # give the new widget a reference to its buddy TaurusValue object
            self._unitsWidget.taurusValueBuddy = weakref.ref(self)
            # tweak the new widget
            if self.minimumHeight() is not None:
                self._unitsWidget.setMinimumHeight(self.minimumHeight())

            # set the model for the subwidget
            if hasattr(self._unitsWidget, 'setModel'):
                self._unitsWidget.setModel(self.getFullModelName())

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def updateCustomWidget(self):
        self.__updateCustomWidget()

    def __updateCustomWidget(self):
        # get the class for the widget and replace it if necessary
        klass = self.__customWidgetClassFactory(self.customWidgetClassID)
        self._customWidget = self._newSubwidget(self._customWidget, klass)

        # take care of the layout
        self.__addCustomWidgetToLayout()

        if self._customWidget is not None:
            # set the model for the subwidget
            if hasattr(self._customWidget, 'setModel'):
                self._customWidget.setModel(self.getFullModelName())

    def updateExtraWidget(self):
        # get the class for the widget and replace it if necessary
        klass = self.extraWidgetClassFactory(self.extraWidgetClassID)
        self._extraWidget = self._newSubwidget(self._extraWidget, klass)

        # take care of the layout
        self.addExtraWidgetToLayout()

        if self._extraWidget is not None:
            # give the new widget a reference to its buddy TaurusValue object
            self._extraWidget.taurusValueBuddy = weakref.ref(self)

            # set the model for the subwidget
            if hasattr(self._extraWidget, 'setModel'):
                self._extraWidget.setModel(self.getFullModelName())

    def addLabelWidgetToLayout(self):

        if self._labelWidget is not None and self.parent() is not None:
            alignment = getattr(self._labelWidget, 'layoutAlignment',
                                Qt.Qt.AlignmentFlag(0))
            self.parent().layout().addWidget(self._labelWidget, self._row, 1, 1,
                                             1, alignment)

    def addReadWidgetToLayout(self):
        if self._readWidget is not None and self.parent() is not None:
            alignment = getattr(self._readWidget, 'layoutAlignment',
                                Qt.Qt.AlignmentFlag(0))
            if self._writeWidget is None:
                self.parent().layout().addWidget(self._readWidget, self._row,
                                                 2, 1, 2, alignment)
            else:
                self.parent().layout().addWidget(self._readWidget, self._row,
                                                 2, 1, 1, alignment)

    def addWriteWidgetToLayout(self):
        if self._writeWidget is not None and self.parent() is not None:
            alignment = getattr(self._writeWidget, 'layoutAlignment',
                                Qt.Qt.AlignmentFlag(0))
            self.parent().layout().addWidget(self._writeWidget, self._row,
                                             3, 1, 1, alignment)

    def addUnitsWidgetToLayout(self):
        if self._unitsWidget is not None and self.parent() is not None:
            alignment = getattr(self._unitsWidget, 'layoutAlignment',
                                Qt.Qt.AlignmentFlag(0))
            self.parent().layout().addWidget(self._unitsWidget, self._row,
                                             4, 1, 1, alignment)

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def addCustomWidgetToLayout(self):
        self.__addCustomWidgetToLayout()

    def __addCustomWidgetToLayout(self):
        """
        Renamed from addCustomWidgetToLayout to avoid deprecation warnings.
        To be removed.
        """
        if self._customWidget is not None and self.parent() is not None:
            alignment = getattr(self._customWidget, 'layoutAlignment',
                                Qt.Qt.AlignmentFlag(0))
            self.parent().layout().addWidget(self._customWidget, self._row,
                                             1, 1, -1, alignment)

    def addExtraWidgetToLayout(self):
        parent = self.parent()
        if parent is not None:
            if self._extraWidget is None:
                # Adding this spacer is some voodoo magic to avoid bug #142
                # See: http://sf.net/p/tauruslib/tickets/142/
                parent.layout().addItem(Qt.QSpacerItem(0, 0), self._row, 5)
            else:
                alignment = getattr(self._extraWidget, 'layoutAlignment',
                                    Qt.Qt.AlignmentFlag(0))
                parent.layout().addWidget(self._extraWidget, self._row,
                                          5, 1, 1, alignment)

    @Qt.pyqtSlot('QString')
    def parentModelChanged(self, parentmodel_name):
        """Invoked when the parent model changes

        :param parentmodel_name: (str) the new name of the parent model
        """
        TaurusBaseWidget.parentModelChanged(self, parentmodel_name)
        if not self._designMode:  # in design mode, no subwidgets are created
            self.__updateCustomWidget()
            self.updateLabelWidget()
            self.updateReadWidget()
            self.updateWriteWidget()
            self.updateUnitsWidget()
            self.updateExtraWidget()

    @Qt.pyqtSlot('QString', name='setLabelWidget')
    def setLabelWidgetClass(self, classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.labelWidgetClassID = classID
        self.updateLabelWidget()

    def getLabelWidgetClass(self):
        return self.labelWidgetClassID

    def resetLabelWidgetClass(self):
        self.labelWidgetClassID = 'Auto'

    @Qt.pyqtSlot('QString', name='setReadWidget')
    def setReadWidgetClass(self, classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.readWidgetClassID = classID
        self.updateReadWidget()

    def getReadWidgetClass(self):
        return self.readWidgetClassID

    def resetReadWidgetClass(self):
        self.readWidgetClassID = 'Auto'

    @Qt.pyqtSlot('QString', name='setWriteWidget')
    def setWriteWidgetClass(self, classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.writeWidgetClassID = classID
        self.updateWriteWidget()

    def getWriteWidgetClass(self):
        return self.writeWidgetClassID

    def resetWriteWidgetClass(self):
        self.writeWidgetClassID = 'Auto'

    @Qt.pyqtSlot('QString', name='setUnitsWidget')
    def setUnitsWidgetClass(self, classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.unitsWidgetClassID = classID
        self.updateUnitsWidget()

    def getUnitsWidgetClass(self):
        return self.unitsWidgetClassID

    def resetUnitsWidgetClass(self):
        self.unitsWidgetClassID = 'Auto'

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    @Qt.pyqtSlot('QString', name='setCustomWidget')
    def setCustomWidgetClass(self, classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.customWidgetClassID = classID
        self.__updateCustomWidget()

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def getCustomWidgetClass(self):
        return self.customWidgetClassID

    @deprecation_decorator(alt="item factories", rel="4.6.5")
    def resetCustomWidgetClass(self):
        self.customWidgetClassID = 'Auto'

    @Qt.pyqtSlot('QString', name='setExtraWidget')
    def setExtraWidgetClass(self, classID):
        '''substitutes the current widget by a new one. classID can be one of:
        None, 'Auto', a TaurusWidget class name, or any class'''
        self.extraWidgetClassID = classID
        self.updateExtraWidget()

    def getExtraWidgetClass(self):
        return self.extraWidgetClassID

    def resetExtraWidgetClass(self):
        self.extraWidgetClassID = 'Auto'

    def setCompact(self, compact):

        # don't do anything if it is already done
        if compact == self._compact:
            return

        #do not switch to compact mode if the write widget is None
        if compact and self.writeWidget() is None:
            self.debug('No write widget. Ignoring setCompact(True)')
            return

        # Backup the current RW format
        rw = self.readWidget(followCompact=True)
        format = rw.getFormat()

        self._compact = compact
        if self.getModel():
            self.updateReadWidget()
            self.updateWriteWidget()

        # Apply the format to the new RW
        rw = self.readWidget(followCompact=True)
        rw.setFormat(format)

    def isCompact(self):
        return self._compact

    def isReadOnly(self):
        if not self.getAllowWrite():
            return True
        modelObj = self.getModelObj()
        if modelObj is None:
            return False
        return not modelObj.isWritable()

    def getModelClass(self):
        return self.__modelClass

#    def destroy(self):
#        if not self._designMode:
#            for w in [self._labelWidget, self._readWidget, self._writeWidget, self._unitsWidget, self._extraWidget]:
#                if isinstance(w,Qt.QWidget):
#                    w.setParent(self)   #reclaim the parental rights over subwidgets before destruction
#        Qt.QWidget.setParent(self,None)
#        Qt.QWidget.destroy(self)

    def createConfig(self, allowUnpickable=False):
        '''
        extending  :meth:`TaurusBaseWidget.createConfig` to store also the class names for subwidgets

        :param alllowUnpickable:  (bool)

        :return: (dict<str,object>) configurations (which can be loaded with :meth:`applyConfig`).

        .. seealso: :meth:`TaurusBaseWidget.createConfig`, :meth:`applyConfig`
        '''
        configdict = TaurusBaseWidget.createConfig(
            self, allowUnpickable=allowUnpickable)
        # store the subwidgets classIDs and configs
        for key in ('LabelWidget', 'ReadWidget', 'WriteWidget', 'UnitsWidget',
                    'ExtraWidget'):
            # calls self.getLabelWidgetClass, self.getReadWidgetClass,...
            classID = getattr(self, 'get%sClass' % key)()
            if isinstance(classID, type):
                # If the class is not from taurus, it doesn't have classid, so we generate it.
                classID = "{0.__module__}:{0.__name__}".format(classID)

            if (isinstance(classID, string_types)
                    or allowUnpickable):
                configdict[key] = {'classid': classID}
                widget = getattr(self, key[0].lower() + key[1:])()
                if isinstance(widget, BaseConfigurableClass):
                    configdict[key]['delegate'] = widget.createConfig()
            else:
                self.info('createConfig: %s not saved because it is not Pickable (%s)' % (
                    key, str(classID)))

        return configdict

    def applyConfig(self, configdict, **kwargs):
        """extending :meth:`TaurusBaseWidget.applyConfig` to restore the subwidget's classes

        :param configdict: (dict)

        .. seealso:: :meth:`TaurusBaseWidget.applyConfig`, :meth:`createConfig`
        """
        # first do the basic stuff...
        TaurusBaseWidget.applyConfig(self, configdict, **kwargs)
        # restore the subwidgets classIDs
        for key in ('LabelWidget', 'ReadWidget', 'WriteWidget', 'UnitsWidget',
                    'ExtraWidget'):
            if key in configdict:
                widget_configdict = configdict[key]
                classID = widget_configdict.get('classid', None)
                if classID is not None and ":" in classID:
                    # classid is of type "module:type" instead of a taurus class name
                    import importlib
                    module, name = classID.split(":")
                    module = importlib.import_module(module)
                    classID = getattr(module, name)
                getattr(self, 'set%sClass' % key)(classID)

                if 'delegate' in widget_configdict:
                    widget = getattr(self, key[0].lower() + key[1:])()
                    if isinstance(widget, BaseConfigurableClass):
                        widget.applyConfig(widget_configdict[
                                           'delegate'], **kwargs)

    @Qt.pyqtSlot('QString')
    def setModel(self, model):
        """extending :meth:`TaurusBaseWidget.setModel` to change the modelclass
        dynamically and to update the subwidgets"""
        self.__modelClass = taurus.Manager().findObjectClass(model or '')
        TaurusBaseWidget.setModel(self, model)
        if not self._designMode:  # in design mode, no subwidgets are created
            self.__updateCustomWidget()
            self.updateLabelWidget()
            self.updateReadWidget()
            self.updateWriteWidget()
            self.updateUnitsWidget()
            self.updateExtraWidget()

    def handleEvent(self, evt_src, evt_type, evt_value):
        """Reimplemented from :meth:`TaurusBaseWidget.handleEvent`
        to update subwidgets on config events
        """
        if self._designMode:
            return

        if self.__error or evt_type == TaurusEventType.Config:
            self.__updateCustomWidget()
            self.updateLabelWidget()
            self.updateReadWidget()
            self.updateWriteWidget()
            self.updateUnitsWidget()
            self.updateExtraWidget()

        # set/unset the error flag
        self.__error = (evt_type == TaurusEventType.Error)

    def isValueChangedByUser(self):
        try:
            return self._writeWidget.isValueChangedByUser()
        except AttributeError:
            return False

    def setDangerMessage(self, dangerMessage=None):
        TaurusBaseWidget.setDangerMessage(self, dangerMessage)
        try:
            return self._writeWidget.setDangerMessage(dangerMessage)
        except AttributeError:
            pass

    def setForceDangerousOperations(self, yesno):
        TaurusBaseWidget.setForceDangerousOperations(self, yesno)
        try:
            return self._writeWidget.setForceDangerousOperations(yesno)
        except AttributeError:
            pass

    def hasPendingOperations(self):
        '''self.getPendingOperations will always return an empty list, but still
        self.hasPendingOperations will look at the writeWidget's operations.
        If you want to ask the TaurusValue for its pending operations, call
        self.writeWidget().getPendingOperations()'''
        w = self.writeWidget(followCompact=True)
        if w is None:
            return False
        return w.hasPendingOperations()

    def updatePendingOpsStyle(self):
        if self._labelWidget is None:
            return
        if self.hasPendingOperations():
            newstyle = '%s {border-style: solid ; border-width: 1px; ' \
                       'border-color: blue; color: blue; border-radius:4px;}' \
                       % self._labelWidget.__class__.__name__
            oldstyle = self._labelWidget.styleSheet()
            if newstyle != oldstyle:
                self._labelWidget.setStyleSheet(newstyle)
        else:
            newstyle = '%s {border-style: solid; border-width: 1px; ' \
                       'border-color: transparent; color: black;  ' \
                       'border-radius:4px;}' % self._labelWidget.__class__.__name__
            oldstyle = self._labelWidget.styleSheet()
            if newstyle != oldstyle:
                self._labelWidget.setStyleSheet(newstyle)

    def getLabelConfig(self):
        return self._labelConfig

    @Qt.pyqtSlot('QString')
    def setLabelConfig(self, config):
        """Sets fragment configuration to the label widget.

        :param config: fragment
        :type config: str
        """
        self._labelConfig = config
        # backwards compatibility: this method used to work for setting
        # an arbitrary text to the label widget
        try:
            self.getModelFragmentObj(config)
            self._labelWidget._permanentText = None
        except Exception:
            try:
                for old in re.findall('<.+?>', config):
                    new = self._BCK_COMPAT_TAGS.get(old, old)
                    self.deprecated(dep=old, alt=new)
                    config = config.replace(old, new)

                self._labelWidget.setText(config)
            except:
                self.debug("Setting permanent text to the label widget failed")
            return

        self.updateLabelWidget()

    def resetLabelConfig(self):
        self._labelConfig = '{attr.label}'
        self.updateLabelWidget()

    def getSwitcherClass(self):
        '''Returns the TaurusValue switcher class (used in compact mode).
        Override this method if you want to use a custom switcher in
        TaurusValue subclasses.
        '''
        class TVSwitcher(TaurusReadWriteSwitcher):
            pass
        return TVSwitcher

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
        #ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        #ret['module'] = 'taurus.qt.qtgui.panel'
        #ret['icon'] = "designer:label.png"
        # return ret

    ########################################################
    # Qt properties (for designer)
    model = Qt.pyqtProperty(
        "QString", TaurusBaseWidget.getModel,  setModel, TaurusBaseWidget.resetModel)
    preferredRow = Qt.pyqtProperty(
        "int", getPreferredRow, setPreferredRow, resetPreferredRow)
    labelWidgetClass = Qt.pyqtProperty(
        "QString", getLabelWidgetClass, setLabelWidgetClass, resetLabelWidgetClass)
    readWidgetClass = Qt.pyqtProperty(
        "QString", getReadWidgetClass, setReadWidgetClass, resetReadWidgetClass)
    writeWidgetClass = Qt.pyqtProperty(
        "QString", getWriteWidgetClass, setWriteWidgetClass, resetWriteWidgetClass)
    unitsWidgetClass = Qt.pyqtProperty(
        "QString", getUnitsWidgetClass, setUnitsWidgetClass, resetUnitsWidgetClass)
    extraWidgetClass = Qt.pyqtProperty(
        "QString", getExtraWidgetClass, setExtraWidgetClass, resetExtraWidgetClass)
    labelConfig = Qt.pyqtProperty(
        "QString", getLabelConfig, setLabelConfig, resetLabelConfig)
    allowWrite = Qt.pyqtProperty(
        "bool", getAllowWrite, setAllowWrite, resetAllowWrite)
    modifiableByUser = Qt.pyqtProperty("bool", TaurusBaseWidget.isModifiableByUser,
                                       TaurusBaseWidget.setModifiableByUser, TaurusBaseWidget.resetModifiableByUser)


class TaurusValuesFrame(TaurusFrame):
    '''This is a container specialized into containing TaurusValue widgets.
    It should be used Only for TaurusValues'''

    _model = []

    @Qt.pyqtSlot('QStringList')
    def setModel(self, model):
        self._model = model
        for tv in self.getTaurusValues():
            tv.destroy()
        for m in self._model:
            taurusvalue = TaurusValue(self, self.designMode)
            taurusvalue.setMinimumHeight(20)
            taurusvalue.setModel(str(m))
            taurusvalue.setModifiableByUser(self.isModifiableByUser())

    def getModel(self):
        return self._model

    def resetModel(self):
        self.setModel([])

    def getTaurusValueByIndex(self, index):
        '''returns the TaurusValue item at the given index position'''
        return self.getTaurusValues()[index]

    def getTaurusValues(self):
        '''returns the list of TaurusValue Objects contained by this frame'''
        return [obj for obj in self.children() if isinstance(obj, TaurusValue)]

    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''we don't want this widget in designer'''
        return None

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QStringList", getModel, setModel, resetModel)


if __name__ == "__main__":
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.panel import TaurusForm
    import sys
    app = TaurusApplication(cmd_line_parser=None)

    w = TaurusForm()

    models = ["sys/tg_test/1/short_scalar"] * 4
    w.setModel(models)

    w[0].writeWidget().setDangerMessage('BOOO')
    w[1].setWriteWidgetClass(TaurusValueLineEdit)
    w[2].setWriteWidgetClass('None')

    class DummyCW(Qt.QLabel):
        def setModel(self, name):
            Qt.QLabel.setText(self, name)

    w[3].setCustomWidgetClass(DummyCW)

    w.setModifiableByUser(True)
    w.show()

    sys.exit(app.exec_())

