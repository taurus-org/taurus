#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""This module provides the set of base classes from which the Qt taurus widgets
should inherit to be considered valid taurus widgets."""

import sys
import threading
import pkg_resources
from types import MethodType
from future.builtins import str
from future.utils import string_types

from taurus.external.qt import Qt
from enum import Enum

import taurus
from taurus import warning
from taurus.core.util import eventfilters
from taurus.core.util.timer import Timer
from taurus.core.taurusbasetypes import TaurusElementType, TaurusEventType
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusconfiguration import TaurusConfigurationProxy
from taurus.core.tauruslistener import TaurusListener, TaurusExceptionListener
from taurus.core.taurusoperation import WriteAttrOperation
from taurus.core.util.eventfilters import filterEvent
from taurus.core.util.log import deprecation_decorator
from taurus.qt.qtcore.util import baseSignal
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE
from taurus.qt.qtcore.mimetypes import TAURUS_DEV_MIME_TYPE
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_MIME_TYPE
from taurus.qt.qtgui.util import ActionFactory

from taurus.core.units import Quantity


__all__ = [
    "TaurusBaseComponent",
    "TaurusBaseWidget",
    "TaurusBaseWritableWidget",
    "defaultFormatter",
    "expFormatter",
    "floatFormatter",
]

__docformat__ = 'restructuredtext'


DefaultNoneValue = "-----"



def defaultFormatter(dtype=None, basecomponent=None, **kwargs):
    """
    Default formatter callable. Returns a format string based on dtype
    and the mapping provided by :attr:`TaurusBaseComponent.defaultFormatDict`

    :param dtype: (object) data type
    :param basecomponent: widget whose display is to be formatted
    :param kwargs: other keyworld arguments

    :return: (str) The format string corresponding to the given dtype.
    """
    if issubclass(dtype, Enum):
        dtype = Enum
    return basecomponent.defaultFormatDict.get(dtype, "{0}")


expFormatter = '{:2.3e}'
floatFormatter = '{:.5f}'
kkFormatter = '{:.7g}'
def kkFormatter2(*a, **kw):return {}

class TaurusBaseComponent(TaurusListener, BaseConfigurableClass):
    """A generic Taurus component.

       .. note::
           Any class which inherits from TaurusBaseComponent is expected to also
           inherit from QObject (or from a QObject derived class).
       .. note::
           :meth:`getSignaller` is now unused and deprecated. This is because
           `taurusEvent` is implemented using :func:`baseSignal`, that doesn't
           require the class to inherit from QObject.

    """
    _modifiableByUser = False
    _showQuality = True
    _eventBufferPeriod = 0

    # Python format string or Formatter callable
    # (None means that the default formatter will be used)
    FORMAT = None

    # Dictionary mapping dtypes to format strings
    defaultFormatDict = {float: "{:.{bc.modelObj.precision}f}",
                         Enum: "{0.name}",
                         Quantity: "{:~.{bc.modelObj.precision}f}"
                         }

    taurusEvent = baseSignal('taurusEvent', object, object, object)

    def __init__(self, name='', parent=None, designMode=False, **kwargs):
        """Initialization of TaurusBaseComponent"""
        self.modelObj = None
        self.modelName = ''
        self.modelFragmentName = None
        self.noneValue = DefaultNoneValue
        self._designMode = designMode
        self.call__init__(TaurusListener, name, parent)

        BaseConfigurableClass.__init__(self)

        # --------------------------------------------------------------
        # Deprecated API for context menu
        self.taurusMenu = None  # deprecated since 4.5.3a. Do not use
        self.taurusMenuData = ''  # deprecated since 4.5.3a. Do not use
        self.__explicitPopupMenu = False
        # --------------------------------------------------------------

        # attributes storing property values
        self._format = None
        self._localModelName = ''
        self._useParentModel = False
        self._showText = True
        self._attached = False
        self._dangerMessage = ""
        self._isDangerous = False
        self._forceDangerousOperations = False
        self._eventFilters = []
        self._preFilters = []
        self._isPaused = False
        self._operations = []
        self._modelInConfig = False
        self._autoProtectOperation = True

        self._bufferedEvents = {}
        self._bufferedEventsTimer = None
        self.setEventBufferPeriod(self._eventBufferPeriod)

        if parent is not None and hasattr(parent, "_exception_listener"):
            self._exception_listener = parent._exception_listener
        else:
            self._exception_listener = set([TaurusExceptionListener()])

        # Use default formatter if none has been set by the class
        if self.FORMAT is None:
            self.setFormat(getattr(taurus.tauruscustomsettings,
                                   'DEFAULT_FORMATTER',
                                   defaultFormatter))

        # register configurable properties
        self.registerConfigProperty(self.isModifiableByUser,
                                    self.setModifiableByUser,
                                    "modifiableByUser")
        self.registerConfigProperty(
            self.getModelInConfig, self.setModelInConfig, "ModelInConfig")
        self.registerConfigProperty(self.getFormat, self.setFormat,
                                    'formatter')
        self.resetModelInConfig()

        # connect taurusEvent signal to filterEvent
        try:
            self.taurusEvent.connect(self.filterEvent)
        except Exception as e:
            self.warning('Could not connect taurusEvent signal: %r', e)

    @staticmethod
    def get_registered_formatters():
        """ Static method to get the registered formatters
        """
        # Note: this is an experimental feature introduced in v 4.6.4a
        # It may be removed or changed in future releases

        formatters = {}
        for ep in pkg_resources.iter_entry_points('taurus.qt.formatters'):
            try:
                formatters[ep.name] = ep.load()
            except Exception as e:
                taurus.warning('Cannot load "%s" formatter. Reason: %r',
                               ep.name, e)

        return formatters

    @deprecation_decorator(rel='4.0')
    def getSignaller(self):
        return self

    def deleteLater(self):
        '''Reimplements the Qt.QObject deleteLater method to ensure that the
        this object stops listening its model.'''
        self.setUseParentModel(False)
        self.resetModel()
        Qt.QObject.deleteLater(self)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Utility methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getTaurusManager(self):
        """Returns the taurus manager singleton. This is just a helper method.
        It is the equivalent of doing::

            import taurus
            manager = taurus.Manager()

        :return: (taurus.core.taurusmanager.TaurusManager) the TaurusManager
        """
        return taurus.Manager()

    def getTaurusFactory(self, scheme=''):
        """Returns the taurus factory singleton for the given scheme.
        This is just a helper method. It is the equivalent of doing::

            import taurus
            factory = taurus.Factory(scheme)

        :param scheme: (str or None) the scheme. If scheme is an empty string,
                       or is not passed, the scheme will be obtained from the
                       model name. For backwards compatibility (but deprecated),
                       passing None is equivalent to 'tango'.

        :return: (taurus.core.taurusfactory.TaurusFactory) the TaurusFactory
        """
        if scheme == '':
            scheme = taurus.getSchemeFromName(self.getModelName() or '')
        if scheme is None:
            scheme = 'tango'

        return taurus.Factory(scheme)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Context menu behavior
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def contextMenuEvent(self, event):
        """
        DEPRECATED:
        Until v4.5.3a, the default implementation of contextMenuEvent showed
        the content of taurusMenu as a context menu. But this resulted in
        unwanted behaviour when the widget already implemented its own context
        menu (see https://github.com/taurus-org/taurus/issues/905 )

        Therefore this feature was disabled in 4.5.3a.

        If you still want to show the contents of taurusMenu as a context menu,
        you can explicitly reimplement the contextMenuEvent method as::

            def contextMenuEvent(self, event):
                self.taurusMenu.exec_(event.globalPos())
        """
        if self.taurusMenu is not None:
            if self.__explicitPopupMenu:
                # bck-compat: show taurusMenu as a contextMenu if it was
                # explicitly created via the (deprecated) "setTaurusPopupMenu"
                # API
                self.taurusMenu.exec_(event.globalPos())
                return
            else:
                self.deprecated(
                    dep='taurusMenu context Menu API',
                    alt='custom contextMenuEvent to show taurusMenu',
                    rel='4.5.3a'
                 )
        event.ignore()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory methods to be implemented in subclass implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

    def updateStyle(self):
        """Method called when the component detects an event that triggers a
        change in the style.
        Default implementation doesn't do anything. Overwrite when necessary
        """
        pass

    def getParentTaurusComponent(self):
        """ Returns a parent Taurus component or None if no parent
        :class:`taurus.qt.qtgui.base.TaurusBaseComponent` is found.

        :raises: RuntimeError
        """
        raise RuntimeError(
            "Not allowed to call TaurusBaseComponent::getParentTaurusComponent()")

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Event handling chain
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setEventBufferPeriod(self, period):
        '''Set the period at wich :meth:`fireBufferedEvents` will be called.
        If period is 0, the event buffering is disabled (i.e., events are fired
        as soon as they are received)

        :param period: (float) period in seconds for the automatic event firing.
                    period=0 will disable the event buffering.
        '''
        self._eventBufferPeriod = period
        if period == 0:
            if self._bufferedEventsTimer is not None:
                self._bufferedEventsTimer.stop()
                self._bufferedEventsTimer = None
                self.fireBufferedEvents()  # flush the buffer
        else:
            self._eventsBufferLock = threading.RLock()
            self._bufferedEventsTimer = Timer(period, self.fireBufferedEvents,
                                              self)
            self._bufferedEventsTimer.start()

    def getEventBufferPeriod(self):
        '''Returns the event buffer period

        :return: (float) period (in s). 0 means event buffering is disabled.
        '''
        return self._eventBufferPeriod

    def eventReceived(self, evt_src, evt_type, evt_value):
        """The basic implementation of the event handling chain is as
        follows:

            - eventReceived just calls :meth:`fireEvent` which emits a "taurusEvent"
              PyQt signal that is connected (by :meth:`preAttach`) to the
              :meth:`filterEvent` method.
            - After filtering, :meth:`handleEvent` is invoked with the resulting
              filtered event

        .. note::
            in the earlier steps of the chain (i.e., in :meth:`eventReceived`/
            :meth:`fireEvent`), the code is executed in a Python thread, while
            from eventFilter ahead, the code is executed in a Qt thread.
            When writing widgets, one should normally work on the Qt thread
            (i.e. reimplementing :meth:`handleEvent`)

        :param evt_src: (object) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType) type of event
        :param evt_value: (object) event value
        """
        evt = filterEvent(evt_src, evt_type, evt_value,
                          filters=self._preFilters)
        if evt is not None:
            self.fireEvent(*evt)

    def fireEvent(self, evt_src=None, evt_type=None, evt_value=None):
        """Emits a "taurusEvent" signal.
        It is unlikely that you need to reimplement this method in subclasses.
        Consider reimplementing :meth:`eventReceived` or :meth:`handleEvent`
        instead depending on whether you need to execute code in the python
        or Qt threads, respectively

        :param evt_src: (object or None) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType or None)
                         type of event
        :param evt_value: (object or None) event value
        """
        if self._eventBufferPeriod:
            # If we have an active event buffer delay, store the event...
            with self._eventsBufferLock:
                self._bufferedEvents[(evt_src, evt_type)] = (evt_src, evt_type,
                                                             evt_value)
        else:
            # if we are not buffering, directly emit the signal
            try:
                self.taurusEvent.emit(evt_src, evt_type, evt_value)
            except:
                pass  # self.error('%s.fireEvent(...) failed!'%type(self))

    def fireBufferedEvents(self):
        '''Fire all events currently buffered (and flush the buffer)

        Note: this method is normally called from an event buffer timer thread
              but it can also be called any time the buffer needs to be flushed
        '''
        with self._eventsBufferLock:
            for evt in self._bufferedEvents.values():
                self.taurusEvent.emit(*evt)
            self._bufferedEvents = {}

    def filterEvent(self, evt_src=-1, evt_type=-1, evt_value=-1):
        """The event is processed by each and all filters in strict order
        unless one of them returns None (in which case the event is discarded)

        :param evt_src: (object) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType) type of event
        :param evt_value: (object) event value
        """
        evt = evt_src, evt_type, evt_value

        if evt == (-1, -1, -1):
            # @todo In an ideal world the signature of this method should be
            # (evt_src, evt_type, evt_value). However there's a bug in PyQt:
            # If a signal is disconnected between the moment it is emitted and
            # the moment the slot is called, then the slot is called without
            # parameters (!?). We added this default values to detect if
            # this is the case without printing an error message each time.
            # If this gets fixed, we should remove this line.
            return

        evt = filterEvent(*evt, filters=self._eventFilters)
        if evt is not None:
            self.handleEvent(*evt)

    def handleEvent(self, evt_src, evt_type, evt_value):
        """Event handling. Default implementation does nothing.
        Reimplement as necessary

        :param evt_src: (object or None) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType or None) type of event
        :param evt_value: (object or None) event value
        """
        pass

    def setEventFilters(self, filters=None, preqt=False):
        """sets the taurus event filters list.
        The filters are run in order, using each output to feed the next filter.
        A filter must be a function that accepts 3 arguments ``(evt_src, evt_type, evt_value)``
        If the event is to be ignored, the filter must return None.
        If the event is  not to be ignored, filter must return a
        ``(evt_src, evt_type, evt_value)`` tuple which may (or not) differ from the input.

        For a library of common filters, see taurus/core/util/eventfilters.py

        :param filters: (sequence) a sequence of filters
        :param preqt: (bool) If true, set the pre-filters (that are applied in
                      eventReceived, at the python thread),
                      otherwise, set the filters to be applied at the main
                      Qt thread (default)

        *Note*: If you are setting a filter that applies a transformation on
        the parameters, you may want to generate a fake event to force the last
        value to be filtered as well. This can be done as in this example::

            TaurusBaseComponent.fireEvent( TaurusBaseComponent.getModelObj(),
                                        taurus.core.taurusbasetypes.TaurusEventType.Periodic,
                                        TaurusBaseComponent.getModelObj().getValueObj())

        See also: insertEventFilter
        """
        if filters is None:
            filters = []
        if preqt:
            self._preFilters = list(filters)
        else:
            self._eventFilters = list(filters)

    def getEventFilters(self, preqt=False):
        """Returns the list of event filters for this widget

        :param preqt: (bool) If true, return the pre-filters (that are applied
                      in eventReceived, at the python thread),
                      otherwise, return the filters to be applied at the main
                      Qt thread (default)

        :return: (sequence<callable>) the event filters
        """
        return (self._preFilters if preqt else self._eventFilters)

    def insertEventFilter(self, filter, index=-1, preqt=False):
        """insert a filter in a given position

        :param filter: (callable(evt_src, evt_type, evt_value)) a filter
        :param index: (int) index to place the filter (default = -1 meaning place at the end)
        :param preqt: (bool) If true, set the pre-filters (that are applied in
                      eventReceived, at the python thread),
                      otherwise, set the filters to be applied at the main
                      Qt thread (default)


        See also: setEventFilters
        """
        if preqt:
            self._preFilters.insert(index, filter)
        else:
            self._eventFilters.insert(index, filter)

    def setPaused(self, paused=True):
        """Toggles the pause mode.

        :param paused: (bool) whether or not to pause (default = True)
        """
        if paused == self._isPaused:
            return  # nothing to do
        if paused:  # pausing
            self.insertEventFilter(eventfilters.IGNORE_ALL, 0)
            self.debug('paused')
        else:  # unpausing
            try:
                self._eventFilters.remove(eventfilters.IGNORE_ALL)
                self.debug('Unpaused')
            except ValueError:
                self.warning('Unpause failed')
        self._isPaused = paused

    def isPaused(self):
        """Return the current pause state

        :return: (bool) wheater or not the widget is paused
        """
        return self._isPaused

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Model class methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelClass(self):
        """Return the class object for the widget.
        Default behavior is to do a 'best effort' to determine which model
        type corresponds to the current model name.
        Overwrite as necessary.

        :return: (class TaurusModel or None) The class object corresponding to the type
                 of Taurus model this widget handles or None if no valid class is found.
        """
        return self.findModelClass()

    def findModelClass(self):
        """Do a "best effort" to determine which model type corresponds to the
        given model name.

        :return: (class TaurusModel or None) The class object corresponding to the type
                 of Taurus model this widget handles or None if no valid class is found.
        """
        if self.getUseParentModel():
            return self._findRelativeModelClass(self.getModel())
        else:
            return self._findAbsoluteModelClass(self.getModel())

    def _findAbsoluteModelClass(self, absolute_name):
        return taurus.Manager().findObjectClass(absolute_name)

    def _findRelativeModelClass(self, relative_name):
        parent_widget = self.getParentTaurusComponent()
        if parent_widget is None:
            return None

        parent_obj = parent_widget.getModelObj()
        if parent_obj is None:
            return None

        if relative_name is None or len(relative_name) == 0:
            return parent_widget.getModelClass()

        obj = parent_obj.getChildObj(relative_name)
        if obj is None:
            return None
        if isinstance(obj, TaurusConfigurationProxy):
            return obj.getRealConfigClass()
        else:
            return obj.__class__

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Model related methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setModelName(self, modelName, parent=None):
        """This method will detach from the previous taurus model (if any), it
        will set the new model to the given modelName and it will attach
        this component to the new taurus model.

        :param modelName: (str) the new taurus model name (according to the taurus convention)
        :param parent: (TaurusBaseComponent) the parent or None (default) if this
                       component does not have a parent Taurus component
        """
        modelName = str(modelName)
        if parent:
            modelClass = self.getModelClass()
            if modelClass is not None:
                parent_model = self.getParentModelObj()
                modelName = modelClass.buildModelName(parent_model, modelName)
        self._detach()
        self.modelName = modelName
        # update modelFragmentName
        try:
            scheme = self.getTaurusManager().getScheme(modelName)
            factory = taurus.Factory(scheme)
            v = factory.getAttributeNameValidator()
            self.modelFragmentName = v.getUriGroups(self.modelName)['fragment']
        except (AttributeError, TypeError):
            self.modelFragmentName = None
        self._attach()

    def getModelName(self):
        """Returns the current model name.

        :return: (str) the model name
        """
        return self.modelName

    def getFullModelName(self):
        """Returns the full name of the current model object.

        :return: (str) the model name
        """
        obj = self.getModelObj()
        if obj is None:
            return None
        return obj.getFullName()

    def getParentModelName(self):
        """Returns the parent model name or an empty string if the component
        has no parent

        :return: (str) the parent model name
        """
        try:
            p = self.getParentTaurusComponent()
            if p is None:
                return ''
        except:
            return ''
        return p.getModelName()

    def getParentModelObj(self):
        """Returns the parent model object or None if the component has no
        parent or if the parent's model is None

        :return: (taurus.core.taurusmodel.TaurusModel or None) the parent taurus model object
        """
        try:
            p = self.getParentTaurusComponent()
            if p is None:
                return None
        except:
            return None
        return p.getModelObj()

    def getModelObj(self):
        """Returns the taurus model obj associated with this component or None if
        no taurus model is associated.

        :return: (taurus.core.taurusmodel.TaurusModel or None) the taurus model object
        """
        return self.modelObj

    def getModelType(self):
        """Returns the taurus model type associated with this component or
        taurus.core.taurusbasetypes.TaurusElementType.Unknown if no taurus model is associated.

        :return: (taurus.core.taurusbasetypes.TaurusElementType) the taurus model type
        """
        model_obj = self.getModelObj()
        if model_obj is None:
            return TaurusElementType.Unknown
        return model_obj.getTaurusElementType()

    def getModelValueObj(self, cache=True):
        """Returns the tango obj value associated with this component or None
        if no taurus model is associated.

        :param cache: (bool) if set to True (default) use the cache value. If set to
                      False will force a connection to the server.

        :return: (TaurusAttrValue) the tango value object.
        """
        if self.modelObj is None:
            return None
        return self.modelObj.getValueObj(cache=cache)

    def getModelFragmentObj(self, fragmentName=None):
        """Returns a fragment object of the model. A fragment of a model is a
        python attribute of the model object.

        Fragment names including dots will be used to recursively get fragments
        of fragments.

        For a simple fragmentName (no dots), this is roughly equivalent to
        getattr(self.getModelObj(), fragmentName)

        If the model does not have that fragment, :class:`AttributeError` is
        raised (other exceptions may be raised when accessing the fragment as
        well)

        :param fragmentName: (str or None) the returned value will correspond to
                         the given fragmentName. If None passed,
                         self.modelFragmentName will be used, and if None is
                         set, the defaultFragmentName of the model will be used
                         instead.

        :return: (obj) the member of the modelObj referred by the fragment.
        """
        if fragmentName is None:  # no fragmentName passed in kwargs
            fragmentName = self.modelFragmentName
        return self.modelObj.getFragmentObj(fragmentName)

    def getModelIndexValue(self):
        """
        Called inside getDisplayValue to use with spectrum attributes.
        By default not used, but some widget might want to support this
        feature.

        Override when needed.
        """
        return None

    def getFormatedToolTip(self, cache=True):
        """Returns a string with contents to be displayed in a tooltip.

        :param cache: (bool) if set to True (default) use the cache value. If set to
                      False will force a connection to the server.

        :return: (str) a tooltip
        """
        if self.modelObj is None:
            return self.getNoneValue()
        obj = self.modelObj.getDisplayDescrObj()
        return self.toolTipObjToStr(obj)

    def toolTipObjToStr(self, toolTipObj):
        """Converts a python dict to a tooltip string.

        :param toolTipObj: (dict) a python object

        :return: (str) a tooltip
        """
        if toolTipObj is None:
            return self.getNoneValue()
        ret = u'<TABLE width="500" border="0" cellpadding="1" cellspacing="0">'

        for id, value in toolTipObj:
            ret += u'<TR><TD WIDTH="80" ALIGN="RIGHT" VALIGN="MIDDLE"><B>%s:</B></TD><TD>%s</TD></TR>' % (
                id.capitalize(), value)
        ret += u'</TABLE>'
        return ret

    def displayValue(self, v):
        """
        Returns a string representation of the given value

        This method will use a format string which is determined 
        dynamically from :attr:`FORMAT`.

        By default `TaurusBaseComponent.FORMAT` is set to 
        :func:`defaultFormatter`, which makes use of
        :attr:`defaultFormatDict`.
 
        In order to customize the formatting behaviour, one can
        use :meth:`setFormat` to alter the formatter of an specific instance
        (recommended) or change :attr:`defaultFormatDict` or
        :attr:`FORMAT` directly at class level.
        
        The formatter can be set to a python format string [1] or a callable
        that returns a python format string.
        If a callable is used, it will be called with the following 
        keyword arguments:

        - dtype: the data type of the value to be formatted
        - basecomponent: the affected widget
  
        The following are some examples for customizing the formatting::

        - Change the format for widget instance `foo`::

            foo.setFormat("{:.2e}")

        - Change FORMAT for all widgets (using a string)::

            TaurusBaseComponent.FORMAT = "{:.2e}"
            
        - Change FORMAT for all TaurusLabels (using a callable)::
        
            def baseFormatter(dtype=None, basecomponent=None, **kwargs):
                return "{:.1f}"

            TaurusLabel.FORMAT = baseFormatter

        - Use the defaultFormatDict but modify the format string for
          dtype=str::

            TaurusLabel.defaultFormatDict.update({"str": "{!r}"})


        .. seealso:: :attr:`tauruscustomsettings.DEFAULT_FORMATTER`,
                     `--default-formatter` option in :class:`TaurusApplication`,
                     :meth:`TaurusBaseWidget.onSetFormatter`


        [1] https://docs.python.org/2/library/string.html

        :param v: (object) the value to be translated to string

        :return: (str) a string representing the given value
        """
        if self._format is None:
            try:
                self._updateFormat(type(v))
            except Exception as e:
                self.warning(('Cannot update format. Reverting to default.' +
                              ' Reason: %r'), e)
                self.setFormat(defaultFormatter)
        try:
            fmt_v = self._format.format(v, bc=self)
        except Exception:
            self.debug("Invalid format %r for %r. Using '{0}'", self._format, v)
            fmt_v = u"{0}".format(v)

        return fmt_v

    def _updateFormat(self, dtype, **kwargs):
        """ Method to update the internal format string used by 
        :meth:`displayValue`
        The internal format string is calculated using :attribute:`FORMAT`,
        which can be a string or a callable that returns a string
        (see :meth:`displayValue`).

        :param dtype: (object) data type
        :param kwargs: keyword arguments that will be passed to
                       :attribute:`FORMAT` if it is a callable
        """
        if self.FORMAT is None or isinstance(self.FORMAT, string_types):
            self._format = self.FORMAT
        else:
            # unbound method to callable
            if isinstance(self.FORMAT, MethodType):
                self.FORMAT = self.FORMAT.__func__
            self._format = self.FORMAT(dtype=dtype, basecomponent=self,  
                                       **kwargs)

    def setFormat(self, format):
        """ Method to set the `FORMAT` attribute for this instance.
        It also resets the internal format string, which will be recalculated
        in the next call to :meth:`displayValue`

        :param format: (str or callable) A format string
                       or a formatter callable (or the callable name in
                       "full.module.callable" format)
        """
        # Check if the format is a callable string representation
        if isinstance(format, string_types):
            try:
                moduleName, formatterName = format.rsplit('.', 1)
                __import__(moduleName)
                module = sys.modules[moduleName]
                format = getattr(module, formatterName)
            except:
                format = str(format)
        self.FORMAT = format
        self.resetFormat()

    def getFormat(self):
        """ Method to get the `FORMAT` attribute for this instance.

        :return: (str) a string of the current format. It could be a python
                 format string or a callable string representation.
        """
        if isinstance(self.FORMAT, string_types):
            formatter = self.FORMAT
        else:
            formatter = '{0}.{1}'.format(self.FORMAT.__module__,
                                         self.FORMAT.__name__)
        return formatter

    def resetFormat(self):
        """Reset the internal format string. It forces a recalculation
        in the next call to :meth:`displayValue`.
        """
        self._format = None

    def getDisplayValue(self, cache=True, fragmentName=None):
        """Returns a string representation of the model value associated with
        this component.

        :param cache: (bool) (ignored, just for bck-compat).
        :param fragmentName: (str or None) the returned value will correspond to
                         the given fragmentName. If None passed,
                         self.modelFragmentName will be used, and if None is
                         set, the defaultFragmentName of the model will be used
                         instead.

        :return: (str) a string representation of the model value.
        """
        if self.modelObj is None:
            return self.getNoneValue()
        try:
            v = self.getModelFragmentObj(fragmentName=fragmentName)
        except:
            return self.getNoneValue()

        idx = self.getModelIndexValue()
        if v is not None and idx:
            try:
                for i in idx:
                    v = v[i]
            except Exception as e:
                self.debug('Problem with applying model index: %r', e)
                return self.getNoneValue()
        return self.displayValue(v)

    def setNoneValue(self, v):
        """Sets the new string representation when no model or no model value exists.

        :param v: (str) the string representation for an invalid value
        """
        self.noneValue = v

    def getNoneValue(self):
        """Returns the current string representation when no valid model or model value exists.

        :return: (str) a string representation for an invalid value
        """
        return self.noneValue

    def isChangeable(self):
        """Tells if this component value can be changed by the user. Default implementation
        will return True if and only if:

            - this component is attached to a valid taurus model and
            - the taurus model is writable and
            - this component is not read-only

        :return: (bool) True if this component value can be changed by the user or False otherwise
        """
        res = False
        if not self.modelObj is None:
            res = self.modelObj.isWritable()
        res = res and not self.isReadOnly()
        return res

    def isReadOnly(self):
        """Determines if this component is read-only or not in the sense that the
        user can interact with it. Default implementation returns True.

        Override when necessary.

        :return: (bool) whether or not this component is read-only
        """
        return True

    def isAttached(self):
        """Determines if this component is attached to the taurus model.

        :return: (bool) True if the component is attached or False otherwise.
        """
        return self._attached

    def preAttach(self):
        """Called inside self.attach() before actual attach is performed.
        Default implementation does nothing.

        Override when necessary.
        """
        pass

    def postAttach(self):
        """Called inside self.attach() after actual attach is performed.
        Default implementation does not do anything.

        Override when necessary.
        """
        pass

    def preDetach(self):
        """Called inside self.detach() before actual deattach is performed.
        Default implementation does nothing.

        Override when necessary.
        """
        pass

    def postDetach(self):
        """Called inside self.detach() after actual deattach is performed.
        Default implementation does not do anything.

        Override when necessary.
        """
        pass

    def _attach(self):
        """Attaches the component to the taurus model.
        In general it should not be necessary to overwrite this method in a
        subclass.

        :return: (bool) True if success in attachment or False otherwise.
        """
        if self.isAttached():
            return self._attached

        self.preAttach()

        cls = self.getModelClass()

        if cls is None:
            self._attached = False
            #self.trace("Failed to attach: Model class not found")
        elif self.modelName == '':
            self._attached = False
            self.modelObj = None
        else:
            try:
                self.modelObj = taurus.Manager().getObject(cls, self.modelName)
                if self.modelObj is not None:
                    self.modelObj.addListener(self)
                    self._attached = True
                    self.changeLogName(self.log_name + "." + self.modelName)
            except Exception:
                self.modelObj = None
                self._attached = False
                self.debug(
                    "Exception occured while trying to attach '%s'" % self.modelName)
                self.traceback()

        self.postAttach()
        return self._attached

    def _detach(self):
        """Detaches the component from the taurus model"""
        self.preDetach()

        if self.isAttached():
            m = self.getModelObj()
            if not m is None:
                m.removeListener(self)

            pos = self.log_name.find('.')
            if pos >= 0:
                new_log_name = self.log_name[:self.log_name.rfind('.')]
                self.changeLogName(new_log_name)
            self.modelObj = None
            self._attached = False
            self.fireEvent(m, TaurusEventType.Change, None)

        self.postDetach()

    def setModelInConfig(self, yesno):
        '''
        Sets whether the model-related properties should be stored for this
        widget when creating the config dict with :meth:`createConfig` (and
        restored when calling :meth:`applyConfig`).
        By default this is not enabled.
        The following properties are affected by this:

        - "model"

        :param yesno: (bool) If True, the model-related properties will be
                      registered as config properties. If False, they will be
                      unregistered.

        .. seealso:: :meth:`registerConfigProperty`, :meth:`createConfig`,
                     :meth:`applyConfig`

        '''
        if yesno == self._modelInConfig:
            return
        if yesno:
            self.registerConfigProperty(self.getModel, self.setModel, "model")
        else:
            self.unregisterConfigurableItem("model", raiseOnError=False)
        self._modelInConfig = yesno

    def getModelInConfig(self):
        return self._modelInConfig

    def resetModelInConfig(self):
        return self.setModelInConfig(False)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Pending operations related methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def applyPendingOperations(self, ops=None):
        """Applies operations without caring about danger messages.
        Use :meth:`TaurusBaseWidget.safeApplyOperation` if you want to warn the
        user before applying

        :param ops: (sequence<taurus.core.taurusoperation.TaurusOperation> or None) list of operations to apply.
                    If None is given (default) the component fetches the pending operations
        """
        self.debug("Apply changes")
        if ops is None:
            ops = self.getPendingOperations()

        if self.isAutoProtectOperation():
            import taurus.qt.qtgui.dialog

            @taurus.qt.qtgui.dialog.protectTaurusMessageBox
            def go():
                self.getTaurusManager().applyPendingOperations(ops)
            go()
        else:
            self.getTaurusManager().applyPendingOperations(ops)

    def hasPendingOperations(self):
        """Returns if the component has pending operations

        :return: (bool) True if there are pending operations or False otherwise
        """
        return len(self.getPendingOperations()) > 0

    def getPendingOperations(self):
        """Returns the sequence of pending operations

        :return:  (sequence<taurus.core.taurusoperation.TaurusOperation>) a list of pending operations
        """
        return self._operations

    def resetPendingOperations(self):
        """Clears the list of pending operations"""
        self._operations = []

    def setDangerMessage(self, dangerMessage=""):
        """Sets the danger message when applying an operation. If dangerMessage is None,
        the apply operation is considered safe

        :param dangerMessage: (str or None) the danger message. If None is given (default)
                              the apply operation is considered safe
        """
        self._dangerMessage = dangerMessage
        self._isDangerous = len(dangerMessage) > 0

    def getDangerMessage(self):
        """Returns the current apply danger message or None if the apply operation is safe

        :return: (str or None) the apply danger message
        """
        return self._dangerMessage

    def resetDangerMessage(self):
        """Clears the danger message. After this method is executed the apply operation
        for this component will be considered safe."""
        self.setDangerMessage(None)

    def isDangerous(self):
        """Returns if the apply operation for this component is dangerous

        :return: (bool) wheter or not the apply operation for this component is dangerous
        """
        return self._isDangerous

    def setForceDangerousOperations(self, yesno):
        """Forces/clears the dangerous operations

        :param yesno: (bool) force or not the dangerous operations"""
        self._forceDangerousOperations = yesno

    def getForceDangerousOperations(self):
        """Returns if apply dangerous operations is forced

        :return: (bool) wheter or not apply dangerous operations is forced
        """
        return self._forceDangerousOperations

    def resetForceDangerousOperations(self):
        """Clears forcing apply dangerous operations"""
        self.setForceDangerousOperations(False)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Standard Qt properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModel(self):
        """Returns the model name for this component.

        :return: (str) the model name.
        """
        return self._localModelName

    def setModel(self, model):
        """Sets/unsets the model name for this component

        :param model: (str) the new model name"""
        self.setModelCheck(model)
        self.resetFormat()
        self.updateStyle()

    def setModelCheck(self, model, check=True):
        """Sets the component taurus model. Setting the check argument to True
        (default) will check if the current model is equal to the given argument.
        If so then nothing is done. This should be the standard way to call this
        method since it will avoid recursion.

        :param model: (str) the new model name
        :param check: (bool) whether or not to check against the actual model name"""
        if model is None:
            model = ''
        model = str(model)
        if check == True and model == self._localModelName:
            return

        self._localModelName = model

        parent_widget = None
        try:
            # if this widget has a buddy, check to see if it is a valid
            # TaurusWidget
            buddy_func = getattr(self, 'buddy')
            buddy_widget = buddy_func()
            if buddy_widget and isinstance(buddy_widget, TaurusBaseComponent):
                parent_widget = buddy_widget
            elif self.getUseParentModel():
                parent_widget = self.getParentTaurusComponent()
        except:
            if self.getUseParentModel():
                parent_widget = self.getParentTaurusComponent()
        self.setModelName(model, parent_widget)
        #self.fireEvent(self.getModelObj(), taurus.core.taurusbasetypes.TaurusEventType.Change, self.getModelValueObj())

    def resetModel(self):
        """Sets the model name to the empty string"""
        self.setModel('')

    def getUseParentModel(self):
        """Returns whether this component is using the parent model

        :return: (bool) True if using parent model or False otherwise
        """
        return getattr(self, '_useParentModel', False)

    @Qt.pyqtSlot(bool)
    def setUseParentModel(self, yesno):
        """Sets/unsets using the parent model

        :param yesno: (bool) whether or not to use parent model
        """
        if yesno:
            self.deprecated(dep='setUseParentModel(True)', rel="4.3.2",
                            alt='explicit models including the parent model')
        if yesno == self._useParentModel:
            return
        self._useParentModel = yesno
        # force a recalculation of the model
        self.setModelCheck(self.getModel(), False)

    def resetUseParentModel(self):
        """Resets the usage of parent model to False"""
        self.setUseParentModel(False)
        self.updateStyle()

    @Qt.pyqtSlot(bool)
    def setShowQuality(self, showQuality):
        """Sets/unsets the show quality property

        :param showQuality: (bool) whether or not to show the quality
        """
        if showQuality == self._showQuality:
            return
        self._showQuality = showQuality
        self.updateStyle()

    def getShowQuality(self):
        """Returns if showing the quality as a background color

        :return: (bool) True if showing the quality or False otherwise
        """
        return self._showQuality

    def resetShowQuality(self):
        """Resets the show quality to self.__class__._showQuality"""
        self.setShowQuality(self.__class__._showQuality)

    @Qt.pyqtSlot(bool)
    def setShowText(self, showText):
        """Sets/unsets showing the display value of the model

        :param showText: (bool) whether or not to show the display value
        """
        if showText == self._showText:
            return
        self._showText = showText
        self.fireEvent(self.getModelObj(), TaurusEventType.Change,
                       self.getModelValueObj())
        self.updateStyle()

    def getShowText(self):
        """Returns if showing the display value

        :return: (bool) True if showing the display value or False otherwise
        """
        return self._showText

    def resetShowText(self):
        """Resets the showing of the display value to True"""
        self.setShowText(True)

    @deprecation_decorator(rel='4.5.3a')
    def setTaurusPopupMenu(self, menuData):
        """Sets/unsets the taurus popup menu

        :param menuData: (str) an xml representing the popup menu"""
        self.taurusMenuData = str(menuData)
        self.__explicitPopupMenu = True
        factory = ActionFactory()
        self.taurusMenu = factory.getNewMenu(self, self.taurusMenuData)


    @deprecation_decorator(rel='4.5.3a')
    def getTaurusPopupMenu(self):
        """Returns an xml string representing the current taurus popup menu

        :return: (str) an xml string representing the current taurus popup menu
        """
        return self.taurusMenuData

    @deprecation_decorator(rel='4.5.3a')
    def resetTaurusPopupMenu(self):
        """Resets the taurus popup menu to empty"""
        self.taurusMenuData = ''
        self.__explicitPopupMenu = False

    def isModifiableByUser(self):
        '''whether the user can change the contents of the widget

        :return: (bool) True if the user is allowed to modify the look&feel'''
        return self._modifiableByUser

    def setModifiableByUser(self, modifiable):
        '''
        sets whether the user is allowed to modify the look&feel

        :param modifiable: (bool)
        '''
        self._modifiableByUser = modifiable

    def resetModifiableByUser(self):
        '''Equivalent to setModifiableByUser(self.__class__._modifiableByUser)'''
        self.setModifiableByUser(self.__class__._modifiableByUser)

    def resetAutoProtectOperation(self):
        """Resets protecting operations"""
        self.setAutoProtectOperation(True)

    def isAutoProtectOperation(self):
        """Tells if this widget's operations are protected against exceptions

        :return: (bool) True if operations are protected against exceptions or
                 False otherwise"""
        return self._autoProtectOperation

    def setAutoProtectOperation(self, protect):
        """Sets/unsets this widget's operations are protected against exceptions

        :param protect: wheater or not to protect widget operations
        :type protect: bool"""
        self._autoProtectOperation = protect


class TaurusBaseWidget(TaurusBaseComponent):
    """The base class for all Qt Taurus widgets.

    .. note::
        Any class which inherits from TaurusBaseWidget is expected to also
        inherit from QWidget (or from a QWidget derived class)"""

    modelChanged = baseSignal('modelChanged', 'QString')
    valueChangedSignal = baseSignal('valueChanged')

    _dragEnabled = False

    def __init__(self, name='', parent=None, designMode=False, **kwargs):
        self._disconnect_on_hide = False
        self._supportedMimeTypes = None
        self._autoTooltip = True
        self.call__init__(TaurusBaseComponent, name,
                          parent=parent, designMode=designMode)
        self._setText = self._findSetTextMethod()

    @deprecation_decorator(rel="4.6.2", alt="onSetFormatter")
    def showFormatterDlg(self):
        """deprecated because it does not distinguish between a user cancelling
        the dialog and the user selecting `None` as a formatter."""
        formatter, ok = self.showFormatterDlg()
        if not ok:
            return None
        else:
            return formatter

    def __showFormatterDlg(self):
        """
        Shows a dialog to get the formatter from the user.

        :return: formatter: python format string or formatter callable
        (in string version) or None
        """
        # add formatters from plugins
        known_formatters = TaurusBaseWidget.get_registered_formatters()
        # add default formatter
        from taurus import tauruscustomsettings
        default = getattr(taurus.tauruscustomsettings,
                          'DEFAULT_FORMATTER',
                          defaultFormatter)
        known_formatters['<DEFAULT_FORMATTER>'] = default
        # add the formatter of this class
        cls = self.__class__
        known_formatters['<{}.FORMAT>'.format(cls.__name__)] = cls.FORMAT
        # add current formatter of this object
        if self.FORMAT not in known_formatters.values():
            known_formatters[str(self.FORMAT)] = self.FORMAT

        names, formatters = list(zip(*known_formatters.items()))

        url = ("http://taurus-scada.org/devel/api/taurus/qt/qtgui/base/"
               + "_TaurusBaseComponent.html")

        choice, ok = Qt.QInputDialog.getItem(
            self,
            "Set formatter",
            'Choose/Enter a formatter (<a href="{}">help</a>)'.format(url),
            names,
            current=formatters.index(self.FORMAT),
            editable=True
        )
        if not ok:
            return None, False

        if choice in names:
            return known_formatters[choice], True
        else:
            return choice, True

    def onSetFormatter(self):
        """Slot to allow interactive setting of the Formatter.

        .. seealso:: :meth:`TaurusBaseWidget.__showFormatterDlg`,
                     :meth:`TaurusBaseComponent.displayValue`,
                     :attr:`tauruscustomsettings.DEFAULT_FORMATTER`
        """
        format, ok = self.__showFormatterDlg()
        if ok:
            self.debug(
                'Default format has been changed to: {0}'.format(format))
            self.setFormat(format)
        return format

    # It makes the GUI to hang... If this needs implementing, we should
    # reimplement it using the Qt parent class, not QWidget...
    # def destroy(self):
    #    '''Reimplements the Qt.QWidget destroy method to ensure that this object
    #    stops listening its model.'''
    #    self.setUseParentModel(False)
    #    self.resetModel()
    #    Qt.QWidget.destroy(self)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Helper methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getQtClass(self, bases=None):
        """Returns the parent Qt class for this widget

        :param bases: (sequence<class> or None) the list of class objects. If None
                      is given (default) it uses the object base classes from __bases__

        :return: (QWidget class) the QWidget class object
        """
        bases = bases or self.__class__.__bases__
        for klass in bases:
            is_taurusbasewidget = issubclass(klass, TaurusBaseWidget)
            if issubclass(klass, Qt.QWidget):
                if is_taurusbasewidget:
                    return self.getQtClass(klass.__bases__)
                return klass
            elif is_taurusbasewidget:
                return self.getQtClass(klass.__bases__)
        return None

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Qt properties from TaurusBaseComponent that need to be overwritten
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    _UseParentMsg = False

    @Qt.pyqtSlot(bool)
    def setUseParentModel(self, yesno):
        """Sets/unsets using the parent model.

        .. note:: in some cases you may need to call :meth:`recheckTaurusParent`
                  after reparenting of some of this widget's ancestors

        :param yesno: (bool) whether or not to use parent model

        .. seealso:: :meth:`recheckTaurusParent`
        """
        is_same = yesno == self._useParentModel
        if not is_same:
            self._updateUseParentModel(yesno)
            if yesno and self._designMode and not TaurusBaseWidget._UseParentMsg:
                TaurusBaseWidget._UseParentMsg = True
                Qt.QMessageBox.information(self, "UseParentModel usage note",
                                           "Using the UseParentModel feature may require you to call " +
                                           "recheckTaurusParent() manually for this widget after calling " +
                                           "setupUi in your code." +
                                           "See the documentation of TaurusBaseWidget.recheckTaurusParent()")
        TaurusBaseComponent.setUseParentModel(self, yesno)

    def _updateUseParentModel(self, yesno):
        parent_widget = self.getParentTaurusComponent()
        if parent_widget:
            if yesno:
                parent_widget.modelChanged.connect(self.parentModelChanged)
            else:
                parent_widget.modelChanged.disconnect(self.parentModelChanged)

    def recheckTaurusParent(self):
        '''
        Forces the widget to recheck its Taurus parent. Taurus Widgets will in most
        situations keep track of changes in their taurus parenting, but in some
        special cases (which unfortunately tend to occur when using Qt
        Designer) they may not update it correctly.

        If this happens, you can manually call this method.

        For more information, check the :download:`issue demo example
        </devel/examples/parentmodel_issue_demo.py>`
        '''
        self._updateUseParentModel(True)

    def setModelCheck(self, model, check=True):
        """Sets the component taurus model. Setting the check argument to True
        (default) will check if the current model is equal to the given argument.
        If so then nothing is done. This should be the standard way to call this
        method since it will avoid recursion.

        :param model: (str) the new model name
        :param check: (bool) whether or not to check against the actual model name
        """
        if model is None:
            model = ''
        model = str(model)
        send_signal = (model != self._localModelName)
        TaurusBaseComponent.setModelCheck(self, model, check)

        if send_signal:
            # emit a signal informing the child widgets that the model has
            # changed
            self.modelChanged.emit(model)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Default Qt signal handlers. Overwrite them as necessary
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def changeEvent(self, evt):
        """overwrites QWidget.changeEvent(self, evt) to handle the ParentChangeEvent
        in case this widget is using the parent model. Always calls the QWidget.changeEvent
        in order not to lose events
        """
        if self.getUseParentModel():
            evt_type = evt.type()
            if evt_type == Qt.QEvent.ParentChange:
                # disconnect from old parent
                if self._parentTaurusComponent:
                    self._parentTaurusComponent.modelChanged.disconnect(
                        self.parentModelChanged)
                self._updateUseParentModel(True)
                self.setModelCheck(self.getModel(), False)
        self.getQtClass().changeEvent(self, evt)

    def parentModelChanged(self, parentmodel_name):
        """Invoked when the Taurus parent model changes

        :param parentmodel_name: (str) the new name of the parent model
        """
        self.debug("Parent model changed to '%s'" % parentmodel_name)
        parentmodel_name = str(parentmodel_name)
        if self.getUseParentModel():
            # force an update of the interpretation of the model property
            model = self.getModel()
            self.setModelCheck(model, False)
            self.modelChanged.emit(model)
        else:
            self.debug(
                "received event from parent although not using parent model")

    def handleEvent(self, evt_src, evt_type, evt_value):
        """very basic and generalistic handling of events.

        Override when necessary.

        :param evt_src: (object or None) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType or None) type of event
        :param evt_value: (object or None) event value
        """
        # Update the text shown by the widget
        if self._setText:
            text = ''
            if self.getShowText():
                if isinstance(evt_src, TaurusAttribute):
                    if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
                        text = self.displayValue(evt_value.rvalue)
                    elif evt_type == TaurusEventType.Error:
                        text = self.getNoneValue()
                    elif evt_type == TaurusEventType.Config:
                        text = self.getDisplayValue()
                else:
                    text = self.getDisplayValue()
            self._setText(text)

        # update tooltip
        if self._autoTooltip:
            self.setToolTip(self.getFormatedToolTip())

        # TODO: update whatsThis

        # update appearance
        self.updateStyle()

    def setModelInConfig(self, yesno):
        '''
        extends :meth:`TaurusBaseComponent.setModelInConfig` to include also
        the "useParentModel" property

        .. seealso:: :meth:`TaurusBaseComponent.setModelInConfig`
        '''
        if yesno == self._modelInConfig:
            return
        if yesno:
            self.registerConfigProperty(
                self.getUseParentModel, self.setUseParentModel, "useParentModel")
        else:
            self.unregisterConfigurableItem(
                "useParentModel", raiseOnError=False)

        TaurusBaseComponent.setModelInConfig(self, yesno)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory overwrite from TaurusBaseComponent
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def updateStyle(self):
        """Updates the widget style. Default implementation just calls QWidget.update()

        Override when necessary.
        """
        self.update()

    def getParentTaurusComponent(self):
        """Returns the first taurus component in the widget hierarchy or None if no
        taurus component is found

        :return: (TaurusBaseComponent or None) the parent taurus base component
        """
        p = self.parentWidget()
        while p and not isinstance(p, TaurusBaseWidget):
            p = p.parentWidget()
        if isinstance(p, TaurusBaseWidget):
            self._parentTaurusComponent = p
        else:
            self._parentTaurusComponent = p = None
        return p

    def setDisconnectOnHide(self, disconnect):
        """Sets/unsets disconnection on hide event

        :param disconnect: (bool) whether or not to disconnect on hide event
        """
        if not self.visible() and disconnect == False:
            self.info(
                "Ignoring setDisconnectOnHide to False because widget is not visible")
            return
        self._disconnect_on_hide = disconnect

    def hideEvent(self, event):
        """Override of the QWidget.hideEvent()
        """
        if self._disconnect_on_hide:
            try:
                if self.getModelName():
                    self._detach()
                event.accept()
            except Exception:
                self.warning("Exception received while trying to hide")
                self.traceback()

    def showEvent(self, event):
        """Override of the QWidget.showEvent()"""
        if self._disconnect_on_hide:
            try:
                if self.getModelName():
                    self._attach()
                event.accept()
            except Exception:
                self.warning("Exception received while trying to show")
                self.traceback()

    def closeEvent(self, event):
        """Override of the QWidget.closeEvent()"""
        try:
            self._detach()
            event.accept()
        except Exception:
            self.warning("Exception received while trying to close")
            self.traceback()

    def handleException(self, e):
        for h in self._exception_listener:
            h.exceptionReceived(e)

    def _findSetTextMethod(self):
        """Determine if this widget is able to display the text value of the taurus
        model. It searches through the possible Qt methods to display text.

        :return: (callable) a python method or None if no suitable method is found.
        """
        setMethod = None
        try:
            setMethod = getattr(self, 'setText')
        except AttributeError:
            try:
                setMethod = getattr(self, 'setTitle')
            except AttributeError:
                try:
                    setMethod = getattr(self, 'display')
                except AttributeError:
                    # it seems the widget has no way to update a value
                    pass

        return setMethod

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Drag&Drop related methods:
    #    default implementation allows setting the model by dropping it on the
    #    widget (if the widget allows modifications by the user).
    #
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setModifiableByUser(self, modifiable):
        '''Reimplemented to acept/reject drops based on whether the widget is modifiable by the user.
        See :meth:`TaurusBaseComponent.setModifiableByUser()`'''
        TaurusBaseComponent.setModifiableByUser(self, modifiable)
        self.setAcceptDrops(modifiable)

    def getSupportedMimeTypes(self):
        '''
        returns a list of supported mimeTypes that this widget support (ordered
        by priority). If none is set explicitely via :meth:`setSupportedMimeTypes`,
        a best effort will be tried based on the model class

        ..seealso: :meth:`setSupportedMimeTypes`

        This provides only a very basic implementation. Reimplement in derived classes if needed

        :return: (list<str>) list of MIME type names
        '''
        if self._supportedMimeTypes is not None:
            return self._supportedMimeTypes
        # fallback guess based on modelclass
        try:
            modelclass = self.getModelClass()
        except:
            return []
        if modelclass == TaurusDevice:
            return [TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE]
        elif modelclass == TaurusAttribute:
            return [TAURUS_ATTR_MIME_TYPE, TAURUS_MODEL_MIME_TYPE]
        else:
            return [TAURUS_MODEL_MIME_TYPE]

    def setSupportedMimeTypes(self, mimetypes):
        '''
        sets the mimeTypes that this widget support

        :param mimetypes: (list<str>) list (ordered by priority) of MIME type names
        '''
        self._supportedMimeTypes = mimetypes

    def dragEnterEvent(self, event):
        '''reimplemented to support drag&drop of models. See :class:`QWidget`'''
        if self.isModifiableByUser():
            supported = self.getSupportedMimeTypes()
            for f in event.mimeData().formats():
                if f in supported:
                    event.acceptProposedAction()
                    return

    def getDropEventCallback(self):
        '''returns the method to be called when a dropping event occurs.
        The default implementation returns `self.setModel`. Reimplement
        it subclasses to call different methods.

        :return: (callable)
        '''
        return self.setModel

    def dropEvent(self, event):
        '''reimplemented to support drag&drop of models. See :class:`QWidget`'''
        mtype = self.handleMimeData(
            event.mimeData(), self.getDropEventCallback())
        if mtype is None:
            self.info('Invalid model')
        else:
            event.acceptProposedAction()

    def handleMimeData(self, mimeData, method):
        '''Selects the most appropriate data from the given mimeData object
        (in the order returned by :meth:`getSupportedMimeTypes`) and passes
        it to the given method.

        :param mimeData: (QMimeData) the MIME data object from which the model
                         is to be extracted
        :param method: (callable<str>) a method that accepts a string as argument.
                       This method will be called with the data from the mimeData object

        :return: (str or None) returns the MimeType used if the model was
                 successfully set, or None if the model could not be set
        '''
        supported = self.getSupportedMimeTypes()
        formats = mimeData.formats()
        for mtype in supported:
            if mtype in formats:
                d = bytes(mimeData.data(mtype)).decode('utf-8')
                if d is None:
                    return None
                try:
                    method(d)
                    return mtype
                except:
                    self.debug('Invalid data (%s) for MIMETYPE=%s' %
                               (repr(d), repr(mtype)))
                    self.traceback(taurus.Debug)
                    return None

    def getModelMimeData(self):
        '''Returns a MimeData object containing the model data. The default implementation
        fills the `TAURUS_MODEL_MIME_TYPE`. If the widget's Model class is
        Attribute or Device, it also fills `TAURUS_ATTR_MIME_TYPE` or
        `TAURUS_DEV_MIME_TYPE`, respectively

        :return: (QMimeData)
        '''
        mimeData = Qt.QMimeData()
        modelname = str(self.getModelName()).encode(encoding='utf8')
        mimeData.setData(TAURUS_MODEL_MIME_TYPE, modelname)
        try:
            modelclass = self.getModelClass()
        except:
            modelclass = None
        if modelclass and issubclass(modelclass, TaurusDevice):
            mimeData.setData(TAURUS_DEV_MIME_TYPE, modelname)
        elif modelclass and issubclass(modelclass, TaurusAttribute):
            mimeData.setData(TAURUS_ATTR_MIME_TYPE, modelname)
        return mimeData

    def mousePressEvent(self, event):
        '''reimplemented to record the start position for drag events.
        See :class:`~PyQt4.QtGui.QWidget`'''
        if self._dragEnabled and event.button() == Qt.Qt.LeftButton:
            # I need to copy it explicetely to avoid a bug with PyQt4.4
            self.dragStartPosition = Qt.QPoint(event.pos())
        self.getQtClass().mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        '''reimplemented to provide drag events.
        See :class:`~PyQt4.QtGui.QWidget`'''
        if not self._dragEnabled or not event.buttons() & Qt.Qt.LeftButton:
            return self.getQtClass().mouseMoveEvent(self, event)
        if (event.pos() - self.dragStartPosition).manhattanLength() < Qt.QApplication.startDragDistance():
            return self.getQtClass().mouseMoveEvent(self, event)
        ret = self.getQtClass().mouseMoveEvent(self, event)  # call the superclass
        event.accept()  # we make sure we accept after having called the superclass so that it is not propagated (many default implementations of mouseMoveEvent call event.ignore())
        drag = Qt.QDrag(self)
        drag.setMimeData(self.getModelMimeData())
        drag.exec_(Qt.Qt.CopyAction, Qt.Qt.CopyAction)
        return ret

    def isDragEnabled(self):
        '''whether the user can drag data from this widget

        :return: (bool) True if the user can drag data'''
        return self._dragEnabled

    def setDragEnabled(self, enabled):
        '''
        sets whether the user is allowed to drag data from this widget

        :param modifiable: (bool)
        '''
        self._dragEnabled = enabled

    def resetDragEnabled(self):
        '''Equivalent to setDragEnabled(self.__class__._dragEnabled)'''
        self.setModifiableByUser(self.__class__._dragEnabled)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Pending operations related methods: default implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def updatePendingOpsStyle(self):
        """This method should be reimplemented by derived classes that want to
        change their appearance depending whether there are pending operations or not"""
        pass

    def emitValueChanged(self, *args):
        """Connect the specific XXXXChanged signals from derived classes to this
        method in order to have a unified signal which can be used by Taurus Widgets"""
        self.valueChangedSignal.emit()
        self.updatePendingOpsStyle()  # by default, update its own style

    def safeApplyOperations(self, ops=None):
        """Applies the given operations (or the pending operations if None passed)

        :param ops: (sequence<taurus.core.taurusoperation.TaurusOperation> or None) list of operations to apply.
                    If None is given (default) the component fetches the pending operations

        :return: (bool) False if the apply was aborted by the user or if the
                 widget is in design mode. True otherwise.
        """

        if ops is None:
            ops = self.getPendingOperations()

        # Check if we need to take care of dangerous operations
        if self.getForceDangerousOperations():
            dangerMsgs = []
        else:
            dangerMsgs = [op.getDangerMessage()
                          for op in ops if len(op.getDangerMessage()) > 0]
        # warn the user if need be
        if len(dangerMsgs) == 1:
            result = Qt.QMessageBox.warning(self, "Potentially dangerous action",
                                            "%s\nProceed?" % dangerMsgs[0],
                                            Qt.QMessageBox.Ok | Qt.QMessageBox.Cancel,
                                            Qt.QMessageBox.Ok)
            if result != Qt.QMessageBox.Ok:
                return False

        elif len(dangerMsgs) > 1:
            warningDlg = Qt.QMessageBox(Qt.QMessageBox.Warning, " %d potentially dangerous actions" % len(dangerMsgs),
                                        "You are about to apply %d actions that may be potentially dangerous. Proceed?" % len(
                                            dangerMsgs),
                                        Qt.QMessageBox.Ok | Qt.QMessageBox.Cancel,
                                        self)
            details = "\n".join(dangerMsgs)
            warningDlg.setDetailedText(details)
            result = warningDlg.exec_()
            if result != Qt.QMessageBox.Ok:
                return False

        if self._designMode:
            self.info('Refusing to apply operation while in design mode')
            return False

        self.applyPendingOperations(ops)
        return True

    def setAutoTooltip(self, yesno):
        """Determines if the widget should automatically generate a tooltip
        based on the current widget model.

        :param yesno: (bool) True to automatically generate tooltip or False otherwise
        """
        self._autoTooltip = yesno

    def getAutoTooltip(self):
        """Returns if the widget is automatically generating a tooltip based
        on the current widget model.

        :return: (bool)  True if automatically generating tooltip or False otherwise
        """
        return self._autoTooltip

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """Returns pertinent information in order to be able to build a valid
        QtDesigner widget plugin.

        The dictionary returned by this method should contain *at least* the
        following keys and values:

        - 'module' : a string representing the full python module name (ex.: 'taurus.qt.qtgui.base')
        - 'icon' : a string representing valid resource icon (ex.: 'designer:combobox.png')
        - 'container' : a bool telling if this widget is a container widget or not.

        This default implementation returns the following dictionary::

            { 'group'     : 'Taurus [Unclassified]',
              'icon'      : 'logos:taurus.png',
              'container' : False }

        :return: (dict) a map with pertinent designer information"""
        return {
            'group': 'Taurus [Unclassified]',
            'icon': 'logos:taurus.png',
            'container': False}


class TaurusBaseWritableWidget(TaurusBaseWidget):
    """The base class for all taurus input widgets

    it emits the applied signal when the value has been applied.
    """

    applied = baseSignal('applied')

    def __init__(self, name='', taurus_parent=None, designMode=False,
                 **kwargs):
        self.call__init__(TaurusBaseWidget, name,
                          parent=taurus_parent, designMode=designMode)

        self._lastValue = None

        # Overwrite not to show quality by default
        self._showQuality = False

        # Don't do auto-apply by default
        self._autoApply = False

        # Don't force a writing to attribute when there are not pending
        # operations
        self._forcedApply = False

        self.valueChangedSignal.connect(self.updatePendingOperations)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return TaurusAttribute

    def isReadOnly(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return False

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setAutoApply(self, auto):
        '''
        Sets autoApply mode. In autoApply mode, the widget writes the value
        automatically whenever it is changed by the user (e.g., when
        :meth:`notifyValueChanged` is called). If False, a value changed just
        flags a "pending operation" which needs to be applied manually by
        the user before the value gets written.

        :param auto: (bool) True for setting autoApply mode. False for disabling
        '''
        self._autoApply = auto

    def getAutoApply(self):
        '''whether autoApply mode is enabled or not.

        :return: (bool)
        '''
        return self._autoApply

    def resetAutoApply(self):
        '''resets the autoApply mode (i.e.: sets it to False)'''
        self.setAutoApply(False)

    def setForcedApply(self, forced):
        '''Sets the forcedApply mode. In forcedApply mode, values are written even
        if there are not pending operations (e.g. even if the displayed value is
        the same as the currently applied one).

        .. seealso: :meth:`forceApply` and :meth:`writeValue`

        :param forced: (bool) True for setting forcedApply mode. False for disabling
        '''
        self._forcedApply = forced

    def getForcedApply(self):
        '''whether forcedApply mode is enabled or not.

        :return: (bool)
        '''
        return self._forcedApply

    def resetForcedApply(self):
        '''resets the forcedApply mode (i.e.: sets it to False)'''
        self.setForcedApply(False)

    @deprecation_decorator(rel='4.0', alt='notifyValueChanged')
    def valueChanged(self, *args):
        return self.notifyValueChanged(*args)

    def notifyValueChanged(self, *args):
        '''Subclasses should connect some particular signal to this method for
        indicating that something has changed.
        e.g., a QLineEdit should connect its "textChanged" signal...
        '''
        self.emitValueChanged()
        if self._autoApply:
            self.writeValue()

    def writeValue(self, forceApply=False):
        '''Writes the value to the attribute, either by applying pending
        operations or (if the ForcedApply flag is True), it writes directly when
        no operations are pending

        It emits the applied signal if apply is not aborted.

        :param forceApply: (bool) If True, it behaves as in forceApply mode
                           (even if the forceApply mode is disabled by
                           :meth:`setForceApply`)
        '''
        if self.hasPendingOperations():
            applied = self.safeApplyOperations()
            if applied:
                self.applied.emit()
            return

        # maybe we want to force an apply even if there are no pending ops...
        kmods = Qt.QCoreApplication.instance().keyboardModifiers()
        controlpressed = bool(kmods & Qt.Qt.ControlModifier)
        if self.getForcedApply() or forceApply or controlpressed:
            self.forceApply()

    def forceApply(self):
        '''It (re)applies the value regardless of pending operations.
        WARNING: USE WITH CARE. In most cases what you need is to make sure
        that pending operations are properly created, not calling this method

        It emits the applied signal if apply is not aborted.

        .. seealso: :meth:`setForceApply` and :meth:`writeValue`

        '''
        try:
            v = self.getValue()
            op = WriteAttrOperation(self.getModelObj(), v,
                                    self.getOperationCallbacks())
            op.setDangerMessage(self.getDangerMessage())
            applied = self.safeApplyOperations([op])
            if applied:
                self.applied.emit()
            self.info('Force-Applied value = %s' % str(v))
        except:
            self.error('Unexpected exception in forceApply')
            self.traceback()

    def handleEvent(self, src, evt_type, evt_value):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
            self.emitValueChanged()

    def postAttach(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        TaurusBaseWidget.postAttach(self)
        if self.isAttached():
            try:
                v = self.getModelValueObj().wvalue
            except:
                v = None
            self.setValue(v)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Pending operations related methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def resetPendingOperations(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        if self.isAttached():
            try:
                v = self.getModelValueObj().wvalue
            except:
                v = None
            self.setValue(v)
        TaurusBaseWidget.resetPendingOperations(self)
        self.updateStyle()

    def updatePendingOperations(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        model = self.getModelObj()
        try:
            model_value = model.getValueObj().wvalue
            wigdet_value = self.getValue()
            if model.areStrValuesEqual(model_value, wigdet_value):
                self._operations = []
            else:
                operation = WriteAttrOperation(model, wigdet_value,
                                               self.getOperationCallbacks())
                operation.setDangerMessage(self.getDangerMessage())
                self._operations = [operation]
        except:
            self._operations = []
        self.updateStyle()

    def getOperationCallbacks(self):
        '''returns the operation callbacks (i.e., a sequence of methods that will be called after an operation is executed
           (this default implementation it returns an empty list).

        :return: (sequence<callable>)
        '''
        return []

    def getDisplayValue(self, cache=True, fragmentName=None):
        """Reimplemented from class:`TaurusBaseWidget`"""
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # The widgets inheriting from this class interact with
        # writable models and therefore the fragmentName should fall back to 'wvalue' 
        # instead of 'rvalue'. 
        # But changing it now is delicate due to risk of introducing API
        # incompatibilities for widgets already assuming the current default.
        # So instead of reimplementing it here, the fix was constrained to 
        # TaurusValueLineEdit.getDisplayValue()
        # TODO: Consider reimplementing this to use wvalue by default
        return TaurusBaseWidget.getDisplayValue(self, cache=cache,
                                                fragmentName=fragmentName)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getValue(self):
        '''
        This method must be implemented in derived classes to return
        the value to be written. Note that this may differ
        from the displayed value (e.g. for a numeric value being
        edited by a QLineEdit-based widget, the displayed value will
        be a string while getValue will return a number)
        '''
        raise NotImplementedError(
            "Not allowed to call TaurusBaseWritableWidget.getValue()")

    def setValue(self, v):
        '''
        This method must be implemented in derived classes to provide
        a (widget-specific) way of updating the displayed value based
        on a given attribute value

        :param v: The attribute value
        '''
        raise NotImplementedError(
            "Not allowed to call TaurusBaseWritableWidget.setValue()")

    def updateStyle(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        if self._autoTooltip:
            toolTip = self.getFormatedToolTip()
            if self.hasPendingOperations():
                v_str = str(self.getValue())
                model_v_str = getattr(
                    self.getModelValueObj(), 'wvalue', '-----')
                toolTip += '<hr/>Displayed value (%s) differs from applied value (%s)' % (
                    v_str, model_v_str)
            self.setToolTip(toolTip)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['group'] = 'Taurus Input'
        return ret

