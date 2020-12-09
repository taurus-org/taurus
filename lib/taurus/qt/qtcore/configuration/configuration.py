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

"""This module provides the set of base classes designed to provide
configuration features to the classes that inherit from them"""
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
from future.utils import string_types

__all__ = ["configurableProperty", "BaseConfigurableClass"]

__docformat__ = 'restructuredtext'


class configurableProperty(object):
    '''A dummy class used to handle properties with the configuration API

    .. warning:: this class is intended for internal use by the configuration
                 package. Do not instantiate it directly in your code.
                 Use :meth:`BaseConfigurableClass.registerConfigProperty` instead.
    '''

    def __init__(self, name, fget, fset, obj=None):
        self.name = name
        self.fget = fget  # this may either be a method or a method name
        self.fset = fset  # this may either be a method or a method name
        self._obj = obj  # obj is only needed if fset or fget are method names

    def createConfig(self, allowUnpickable=False):
        '''returns value returned by the fget function of this property. the allowUnpickable parameter is ignored'''
        if isinstance(self.fget, string_types):  # fget is not a method but a method name...
            result = getattr(self._obj, self.fget)()
        else:
            result = self.fget()
        return result

    def applyConfig(self, value, depth=-1):
        '''calls the fset function for this property with the given value. The depth parameter is ignored'''
        if isinstance(self.fget, string_types):  # fget is not a method but a method name...
            getattr(self._obj, self.fset)(value)
        else:
            self.fset(value)

    def objectName(self):
        '''returns the name of this property'''
        return self.name


class BaseConfigurableClass(object):
    '''
    A base class defining the API for configurable objects.

    .. note:: One implicit requisite is that a configurable object must also provide a
              `meth:`objectName` method which returns the object name. This is typically
              fulfilled by inheriting from QObject.

    Using objects that inherit from :class:`BaseConfigurableClass` automates
    saving and restoring of application settings and also enables the use of
    perspectives in Taurus GUIs.

    The basic idea is that each object/widget in your application is responsible
    for providing a dictionary containing information on its properties (see
    :meth:`createConfig`). The same object/widget is also responsible for
    restoring such properties when provided with a configuration dictionary (see
    :meth:`applyConfig`).

    For a certain property to be saved/restored it is usually enough to
    *register* it using :meth:`registerConfigProperty`. When the objects are
    structured in a hierarchical way (e.g. as the widgets in a Qt application),
    the parent widget can (should) delegate the save/restore of its children to
    the children themselves. This delegation is done by registering the children
    using :meth:`registerConfigDelegate`.

    Consider the following example: I am creating a groupbox container which
    contains a :class:`TaurusForm` and I want to save/restore the state of the
    checkbox and the properties of the form::

        #The class looks like this:
        class MyBox(Qt.QGroupBox, BaseConfigurableClass):
            def __init__(self):
                ...
                self.form = TaurusForm()
                ...
                self.registerConfigProperty(self.isChecked, self.setChecked, 'checked')
                self.registerConfigDelegate(self.form)   #the TaurusForm already handles its own configuration!
                ...

        #and we can retrieve the configuration doing:
        b1 = MyBox()
        b1.setChecked(True)  #checked is a registered property of MyBox class
        b1.form.setModifiableByUser(True)  #modifiableByUser is a registered property of a TaurusForm
        cfg = b1.createConfig()  #we get the configuration as a dictionary
        ...
        b2 = MyBox()
        b2.applyConfig(cfg)  #now b2 has the same configuration as b1 when cfg was created

    :meth:`createConfig` and :meth:`applyConfig` methods use a dictionary for
    passing the configuration, but :class:`BaseConfigurableClass` also provides
    some other convenience methods for working with files
    (:meth:`saveConfigFile` and :meth:`loadConfigFile`) or as QByteArrays
    (:meth:`createQConfig` and :meth:`applyQConfig`)

    Finally, we recommend to use :class:`TaurusMainWindow` for all Taurus GUIs
    since it automates all the steps for *saving properties when closing* and
    *restoring the settings on startup*. It also provides a mechanism for
    implementing "perspectives" in your application.

    '''

    defaultConfigRecursionDepth = -1
    # the latest element of this list is considered the current version
    _supportedConfigVersions = ("__UNVERSIONED__",)

    def __init__(self, **kwargs):
        self.resetConfigurableItems()

    @staticmethod
    def isTaurusConfig(x):
        '''Checks if the given argument has the structure of a configdict

        :param x: (object) object to test

        :return: (bool) True if it is a configdict, False otherwise.
        '''
        if not isinstance(x, dict):
            return False
        for k in ('__orderedConfigNames__', '__itemConfigurations__', 'ConfigVersion', '__pickable__'):
            if k not in x:
                return False

        for k in x['__orderedConfigNames__']:
            if k not in x['__itemConfigurations__']:
                print('missing configuration for "%s" in %s' % (k, repr(x)))
        return True

    def createConfig(self, allowUnpickable=False):
        '''
        Returns a dictionary containing configuration information about the
        current state of the object.

        In most usual situations, using :meth:`registerConfigProperty` and
        :meth:`registerConfigDelegate`, should be enough to cover all needs using
        this method, although it can be reimplemented in children classes to support
        very specific configurations.

        By default, meth:`createQConfig` and meth:`saveConfigFile` call to this
        method for obtaining the data.

        Hint: The following code allows you to serialize the configuration
        dictionary as a string (which you can store as a QSetting, or as a Tango
        Attribute, provided that allowUnpickable==False)::

            import pickle
            s = pickle.dumps(widget.createConfig())  #s is a string that can be stored

        :param alllowUnpickable:  (bool) if False the returned dict is
                                  guaranteed to be a pickable object. This is
                                  the default and preferred option because it
                                  allows the serialization as a string that can
                                  be directly stored in a QSetting. If True, this
                                  limitation is not enforced, which allows to
                                  use more complex objects as values (but limits
                                  its persistence).

        :return: (dict<str,object>) configurations (which can be loaded with :meth:`applyConfig`).

        .. seealso: :meth:`applyConfig` , :meth:`registerConfigurableItem`,  meth:`createQConfig`, meth:`saveConfigFile`
        '''
        configdict = {"ConfigVersion": self._supportedConfigVersions[-1],
                      "__pickable__": True}
        # store the configurations for all registered configurable items as
        # well
        itemcfgs = {}
        for k, v in self.__configurableItems.items():
            itemcfgs[k] = v.createConfig(allowUnpickable=allowUnpickable)
        configdict["__itemConfigurations__"] = itemcfgs
        configdict["__orderedConfigNames__"] = self.__configurableItemNames
        return configdict

    def applyConfig(self, configdict, depth=None):
        """applies the settings stored in a configdict to the current object.

        In most usual situations, using :meth:`registerConfigProperty` and
        :meth:`registerConfigDelegate`, should be enough to cover all needs using
        this method, although it can be reimplemented in children classes to support
        very specific configurations.

        :param configdict: (dict)
        :param depth: (int)  If depth = 0, applyConfig will only be called
                      for this object, and not for any other object registered
                      via :meth:`registerConfigurableItem`. If depth > 0,
                      applyConfig will be called recursively as many times as
                      the depth value. If depth < 0 (default, see note), no
                      limit is imposed to recursion (i.e., it will recurse for
                      as deep as there are registered items).

        .. note:: the default recursion depth can be tweaked in derived classes
                  by changing the class property `defaultConfigRecursionDepth`

        .. seealso:: :meth:`createConfig`
        """
        if depth is None:
            depth = self.defaultConfigRecursionDepth
        if not self.checkConfigVersion(configdict):
            raise ValueError(
                'the given configuration is of unsupported version')
        # delegate restoring the configuration of any registered configurable
        # item
        if depth != 0:
            itemcfgs = configdict["__itemConfigurations__"]
            # we use the sorted item names that was stored in the configdict
            for key in configdict["__orderedConfigNames__"]:
                if key in self.__configurableItems:
                    self.__configurableItems[key].applyConfig(
                        itemcfgs[key], depth=depth - 1)

    def getConfigurableItemNames(self):
        '''returns an ordered list of the names of currently registered
        configuration items (delegates and properties)

        :return: (list<unicode>)
        '''
        return self.__configurableItemNames

    def resetConfigurableItems(self):
        ''' clears the record of configurable items depending of this object

        .. seealso:: :meth:`registerConfigurableItem`
        '''
        self.__configurableItemNames = []
        self.__configurableItems = {}

    def registerConfigurableItem(self, item, name=None):
        print("Deprecation WARNING: %s.registerConfigurableItem() has been deprecated. Use registerConfigDelegate() instead" % repr(self))
        self._registerConfigurableItem(item, name=name)

    def registerConfigDelegate(self, delegate, name=None):
        '''
        Registers the given object as a delegate for configuration.
        Delegates are typically other objects inheriting from BaseConfigurableClass
        (or at least they must provide the following methods:

          - `createConfig` (as provided by, e.g., BaseConfigurableClass)
          - `applyConfig` (as provided by, e.g., BaseConfigurableClass)
          - `objectName` (as provided by, e.g., QObject)

        :param delegate: (BaseConfigurableClass) The delegate object to be registered.
        :param name: (str) The name to be used as a key for this item in the configuration
                     dictionary. If None given, the object name is used by default.

        .. note:: the registration order will be used when restoring configurations

        .. seealso:: :meth:`unregisterConfigurableItem`, :meth:`registerConfigProperty`, :meth:`createConfig`
        '''
        return self._registerConfigurableItem(delegate, name=name)

    def registerConfigProperty(self, fget, fset, name):
        '''
        Registers a certain property to be included in the config dictionary.

        In this context a "property" is some named value that can be obtained
        via a getter method and can be set via a setter method.

        :param fget: (method or str) method (or name of a method) that gets no
                     arguments and returns the value of a property.
        :param fset: (method or str) method (or name of a method) that gets as
                     an argument the value of a property, and sets it
        :param name: (str) The name to be used as a key for this property in the configuration
                     dictionary

        .. note:: the registration order will be used when restoring configurations

        .. seealso:: :meth:`unregisterConfigurableItem`, :meth:`registerConfigDelegate`, :meth:`createConfig`
        '''
        if isinstance(fget, string_types) or isinstance(fset, string_types):
            import weakref
            obj = weakref.proxy(self)
        else:
            obj = None
        p = configurableProperty(name, fget, fset, obj=obj)
        return self._registerConfigurableItem(p, name=name)

    def _registerConfigurableItem(self, item, name=None):
        '''
        Registers the given item as a configurable item which depends of this
        Taurus widget.

        .. note:: This method is not meant to be called directly. Use
                  :meth:`registerConfigProperty`, :meth:`registerConfigDelegate`
                  instead

        Registered items are expected to implement the
        following methods:
          - `createConfig` (as provided by, e.g., BaseConfigurableClass)
          - `applyConfig` (as provided by, e.g., BaseConfigurableClass)
          - `objectName` (as provided by, e.g., QObject)

        :param item: (object) The object that should be registered.
        :param name: (str) The name to be used as a key for this item in the configuration
                     dictionary. If None given, the object name is used by default.

        .. note:: the registration order will be used when restoring configurations

        .. seealso:: :meth:`unregisterConfigurableItem`, :meth:`createConfig`
        '''
        if name is None:
            name = item.objectName()
        name = str(name)
        if name in self.__configurableItemNames:
            # abort if duplicated names
            raise ValueError(
                '_registerConfigurableItem: An object with name "%s" is already registered' % name)
        self.__configurableItemNames.append(name)
        self.__configurableItems[name] = item

    def unregisterConfigurableItem(self, item, raiseOnError=True):
        '''
        unregisters the given item (either a delegate or a property) from the
        configurable items record. It raises an exception if the item is not
        registered

        :param item: (object or str) The object that should be unregistered.
                     Alternatively, the name under which the object was registered
                     can be passed as a python string.
        :param raiseOnError: (bool) If True (default), it raises a KeyError
                             exception if item was not registered. If False, it
                             just logs a debug message

        .. seealso:: :meth:`registerConfigProperty`, :meth:`registerConfigDelegate`
        '''
        if isinstance(item, string_types):
            name = str(item)
        else:
            name = str(item.objectName())
        if name in self.__configurableItemNames and name in self.__configurableItems:
            self.__configurableItemNames.remove(name)
            self.__configurableItems.pop(name)
            return True
        elif raiseOnError:
            raise KeyError('"%s" was not registered.' % name)
        else:
            self.debug('"%s" was not registered. Skipping' % name)
            return False

    def checkConfigVersion(self, configdict, showDialog=False, supportedVersions=None):
        '''
        Check if the version of configdict is supported. By default, the
        BaseConfigurableClass objects have ["__UNVERSIONED__"] as their list of supported
        versions, so unversioned config dicts will be accepted.

        :param configdict: (dict) configuration dictionary to check
        :param showDialog: (bool) whether to show a QtWarning dialog if check
                           failed (false by default)
        :param supportedVersions: (sequence<str>, or None) supported version
                                  numbers, if None given, the versions supported
                                  by this widget will be used (i.e., those
                                  defined in self._supportedConfigVersions)

        :return: (bool) returns True if the configdict is of the right version
        '''
        if supportedVersions is None:
            supportedVersions = self._supportedConfigVersions
        version = configdict.get("ConfigVersion", "__UNVERSIONED__")
        if version not in supportedVersions:
            msg = 'Unsupported Config Version %s. (Supported: %s)' % (
                version, repr(supportedVersions))
            self.warning(msg)
            if showDialog:
                from taurus.external.qt import Qt
                Qt.QMessageBox.warning(
                    self, "Wrong Configuration Version", msg, Qt.QMessageBox.Ok)
            return False
        return True

    def createQConfig(self):
        '''
        returns the current configuration status encoded as a QByteArray. This
        state can therefore be easily stored using QSettings

        :return: (QByteArray) (in the current implementation this is just a
                 pickled configdict encoded as a QByteArray

        .. seealso:: :meth:`restoreQConfig`
        '''
        from taurus.external.qt import Qt
        import pickle
        configdict = self.createConfig(allowUnpickable=False)
        return Qt.QByteArray(pickle.dumps(configdict))

    def applyQConfig(self, qstate):
        '''
        restores the configuration from a qstate generated by :meth:`getQState`.

        :param qstate: (QByteArray)

        .. seealso:: :meth:`createQConfig`
        '''
        if qstate.isNull():
            return
        import pickle
        configdict = pickle.loads(qstate.data())
        self.applyConfig(configdict)

    def saveConfigFile(self, ofile=None):
        """Stores the current configuration on a file

        :param ofile: (file or string) file or filename to store the configuration

        :return: (str) file name used
        """
        import pickle
        if ofile is None:
            from taurus.external.qt import compat
            ofile, _ = compat.getSaveFileName(
                self, 'Save Configuration',
                '%s.pck' % self.__class__.__name__,
                'Configuration File (*.pck)'
            )
            if not ofile:
                return
        if isinstance(ofile, string_types):
            ofile = open(ofile, 'wb')
        configdict = self.createConfig(allowUnpickable=False)
        self.info("Saving current settings in '%s'" % ofile.name)
        pickle.dump(configdict, ofile)
        return ofile.name

    def loadConfigFile(self, ifile=None):
        """Reads a file stored by :meth:`saveConfig` and applies the settings

        :param ifile: (file or string) file or filename from where to read the configuration

        :return: (str) file name used
        """
        import pickle
        if ifile is None:
            from taurus.external.qt import compat
            ifile, _ = compat.getOpenFileName(
                self, 'Load Configuration', '', 'Configuration File (*.pck)')
            if not ifile:
                return
        if isinstance(ifile, string_types):
            ifile = open(ifile, 'rb')

        configdict = pickle.load(ifile)
        self.applyConfig(configdict)
        return ifile.name
