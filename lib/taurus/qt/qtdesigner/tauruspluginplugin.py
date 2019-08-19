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
tauruspluginplugin.py:
"""
from __future__ import absolute_import

from taurus.external.qt import QtDesigner


def build_qtdesigner_widget_plugin(klass):
    from taurus.qt.qtdesigner.taurusplugin import taurusplugin

    class Plugin(taurusplugin.TaurusWidgetPlugin):
        WidgetClass = klass

    Plugin.__name__ = klass.__name__ + "QtDesignerPlugin"
    return Plugin

_SKIP = ["QLogo", "QGroupWidget", "TaurusGroupWidget"]

_plugins = {}


def main():
    from taurus.core.util.log import Logger
    from taurus.qt.qtgui.util import TaurusWidgetFactory
    Logger.setLogLevel(Logger.Debug)
    _log = Logger(__name__)

    try:
        wf = TaurusWidgetFactory()
        klasses = wf.getWidgetClasses()
        ok_nb, skipped_nb, e1_nb, e2_nb, e3_nb, e4_nb = 0, 0, 0, 0, 0, 0
        for widget_klass in klasses:
            name = widget_klass.__name__
            #_log.debug("Processing %s" % name)
            if name in _SKIP:
                #_log.debug("Skipped %s" % name)
                skipped_nb += 1
                continue
            # if getQtDesignerPluginInfo does not exist, returns None or raises
            # an exception: forget the widget
            cont = False
            try:
                qt_info = widget_klass.getQtDesignerPluginInfo()
                if qt_info is None:
                    #_log.debug("E1: Canceled %s (getQtDesignerPluginInfo)" % name)
                    e1_nb += 1
                    cont = True
            except AttributeError:
                #_log.debug("E2: Canceled %s (widget doesn't have getQtDesignerPluginInfo())" % name)
                e2_nb += 1
                cont = True
            except Exception as e:
                #_log.debug("E3: Canceled %s (%s)" % (name, str(e)))
                e3_nb += 1
                cont = True

            if cont:
                continue
            for k in ('module', ):
                if k not in qt_info:
                    #_log.debug("E4: Canceled %s (getQtDesignerPluginInfo doesn't have key %s)" % (name, k))
                    e4_nb += 1
                    cont = True
            if cont:
                continue

            plugin_klass = build_qtdesigner_widget_plugin(widget_klass)
            plugin_klass_name = plugin_klass.__name__
            globals()[plugin_klass_name] = plugin_klass
            _plugins[plugin_klass_name] = plugin_klass

            ok_nb += 1
            #_log.debug("DONE processing %s" % name)
        _log.info("Inpected %d widgets. %d (OK), %d (Skipped), %d (E1), %d (E2), %d (E3), %d(E4)" % (
            len(klasses), ok_nb, skipped_nb, e1_nb, e2_nb, e3_nb, e4_nb))
        _log.info("E1: getQtDesignerPluginInfo() returns None")
        _log.info("E2: widget doesn't implement getQtDesignerPluginInfo()")
        _log.info("E3: getQtDesignerPluginInfo() throws exception")
        _log.info(
            "E4: getQtDesignerPluginInfo() returns dictionary with missing key (probably 'module' key)")
    except Exception as e:
        import traceback
        traceback.print_exc()
        # print e


class TaurusWidgets(QtDesigner.QPyDesignerCustomWidgetCollectionPlugin):

    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetCollectionPlugin.__init__(parent)
        self._widgets = None

    def customWidgets(self):
        if self._widgets is None:
            self._widgets = [w(self) for w in _plugins.values()]
        return self._widgets

if __name__ != "__main__":
    main()
