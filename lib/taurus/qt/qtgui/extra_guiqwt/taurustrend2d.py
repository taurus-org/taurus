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
taurustrend.py: Generic trend widget for Taurus
"""
__all__ = ["TaurusTrend2DDialog"]

from guiqwt.plot import ImageDialog
from taurus.external.qt import Qt
import taurus.core
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.extra_guiqwt.image import TaurusTrend2DItem
from taurus.qt.qtgui.extra_guiqwt.tools import (TaurusModelChooserTool,
                                                TimeAxisTool, AutoScrollTool,
                                                AutoScaleXTool, AutoScaleYTool,
                                                AutoScaleZTool)
import taurus.cli.common


class TaurusTrend2DDialog(ImageDialog, TaurusBaseWidget):
    """
    This is a widget for displaying trends from 1D Taurus attributes (i.e.,
    representing the variation over time of a 1D array). Sometimes this kind of
    plots are also known as "spectrograms".

    The widget shows a 3D plot (Z represented with colors) where the values in
    the 1D array are plotted in the Y-Z plane and are stacked along the X axis.
    """
    _modifiableByUser = True

    def __init__(self, parent=None, designMode=False, toolbar=True,
                 stackMode='deltatime', buffersize=512, options=None,
                 autoscale='xyz', **kwargs):
        """

        :param param: param to be passed to XYImageItem constructor
        :param buffersize: (int) size of the stack
        :param stackMode: (str) can be 'datetime', 'timedelta' or 'event'
        :param autoscale: (str) if autscale string contains 'x', the x axis 
                          will be autoscaled. Same with 'y' and 'z'.
                          Defaults to 'xyz'
        """
        """see :class:`guiqwt.plot.ImageDialog` for other valid initialization
        parameters"""
        defaultOptions = dict(lock_aspect_ratio=False)
        if options is not None:
            defaultOptions.update(options)
        ImageDialog.__init__(self, parent=parent, toolbar=toolbar,
                             options=defaultOptions, **kwargs)
        TaurusBaseWidget.__init__(self, "TaurusTrend2DDialog")
        # support x_axis_mode values (map them to stackMode values)
        stackMode = dict(
            t='datetime', d='deltatime', e='event', n='event'
        ).get(stackMode, stackMode)
        self.trendItem = None
        self.buffersize = buffersize
        self._useArchiving = False
        self._stackMode = stackMode
        self.setStackMode(stackMode)
        self.setWindowFlags(Qt.Qt.Widget)
        # add some tools
        for toolklass in (TaurusModelChooserTool, AutoScrollTool,
                          AutoScaleXTool, AutoScaleYTool, AutoScaleZTool
                          ):
            self.add_tool(toolklass)
        self.get_tool(TaurusModelChooserTool).singleModel = True

        if 'x' in autoscale.lower():
            self.get_tool(AutoScaleXTool).setChecked(True)
        if 'y' in autoscale.lower():
            self.get_tool(AutoScaleYTool).setChecked(True)
        if 'z' in autoscale.lower():
            self.get_tool(AutoScaleZTool).setChecked(True)

        self.setModifiableByUser(self._modifiableByUser)
        self.setContextMenuPolicy(Qt.Qt.CustomContextMenu)

        # Config properties
        self.setModelInConfig(True)
        self.registerConfigDelegate(self.trendItem or BaseConfigurableClass(),
                                    name='trendItem')
        self.registerConfigDelegate(self.get_tool(AutoScrollTool),
                                    name='AutoScrollTool')
        self.registerConfigDelegate(self.get_tool(AutoScaleXTool),
                                    name='AutoScaleXTool')
        self.registerConfigDelegate(self.get_tool(AutoScaleYTool),
                                    name='AutoScaleYTool')
        self.registerConfigDelegate(self.get_tool(AutoScaleZTool),
                                    name='AutoScaleZTool')
        self.registerConfigProperty(self.getStackMode,
                                    self.setStackMode,
                                    'stackMode'
                                    )
        self.registerConfigProperty(self._get_axes_conf,
                                    self._set_axes_conf,
                                    'axes_confs'
                                    )
        
    def _get_axes_conf(self):
        p = self.get_plot()
        conf = {}
        for a in p.AXIS_IDS:
            c = conf[a] = {}
            c['limits'] = p.get_axis_limits(a)
            c['title'] = p.get_axis_title(a)
            c['color'] = p.get_axis_color(a)
            c['scale'] = p.get_axis_scale(a)
            c['unit'] = p.get_axis_unit(a)
        return conf

    def _set_axes_conf(self, axes_conf):
        p = self.get_plot()
        for a in p.AXIS_IDS:
            c = axes_conf[a]
            if 'limits' in c:
                p.set_axis_limits(a, *c['limits'])
            if 'title' in c:
                p.set_axis_title(a, c['title'])
            if 'color' in c:
                p.set_axis_color(a, c['color'])
            if 'scale' in c:
                p.set_axis_scale(a, c['scale'], autoscale=False)
            if 'unit' in c:
                p.set_axis_unit(a, c['unit'])

    def keyPressEvent(self, event):
        if(event.key() == Qt.Qt.Key_Escape):
            event.ignore()
        else:
            ImageDialog.keyPressEvent(self, event)

    def setStackMode(self, mode):
        """set the type of stack to be used. This determines how X values are
        interpreted:

            - as timestamps ('datetime' or 't')
            - as time deltas ('deltatime' or 'd')
            - as event numbers ('event' or 'e')

        :param mode:(one of 'datetime', 'timedelta' or 'event')
        """
        mode = str(mode)
        if mode == 'datetime':
            self.add_tool(TimeAxisTool)
            timetool = self.get_tool(TimeAxisTool)
            timetool.set_scale_y_t(True)
        elif mode == 'deltatime':
            from taurus.qt.qtgui.extra_guiqwt.scales import DeltaTimeScaleEngine
            plot = self.get_plot()
            DeltaTimeScaleEngine.enableInAxis(plot, plot.xBottom, rotation=-45)
        elif mode == 'event':
            plot = self.get_plot()
            scaleEngine = plot.axisScaleEngine(plot.xBottom)
            if hasattr(scaleEngine, 'disableInAxis'):
                scaleEngine.disableInAxis(plot, plot.xBottom)
        else:
            self.error('Unknown stack mode "%s"' % repr(mode))
            return
        self._stackMode = mode
        if hasattr(self.trendItem, 'stackMode'):
            self.trendItem.stackMode = mode

    def getStackMode(self):
        return self._stackMode

    def resetStackMode(self):
        self.setStackMode('datetime')

    def getModelClass(self):
        """reimplemented from :class:`TaurusBaseWidget`"""
        return taurus.core.taurusattribute.TaurusAttribute

    def setModel(self, model):
        """reimplemented from :class:`TaurusBaseWidget`"""
        plot = self.get_plot()
        if self.trendItem is not None:
            plot.del_item(self.trendItem)
        self.trendItem = TaurusTrend2DItem(
            stackMode=self.getStackMode(), buffersize=self.buffersize)
        self.trendItem.setModel(model)
        plot.add_item(self.trendItem, autoscale=False)
        self.trendItem.set_readonly(not self.isModifiableByUser())
        plot.set_axis_title(plot.colormap_axis, 'value')
        plot.set_axis_unit('left', 'index')
        try:
            plot.set_axis_title(
                'left', self.trendItem.getModelObj().getSimpleName())
        except:
            self.debug('cannot set title for left axis')
            self.traceback()
        try:
            unit = self.trendItem.getModelObj().getConfig().getUnit() or ''
            plot.set_axis_unit(plot.colormap_axis, unit)
        except:
            self.debug('cannot set units for colormap axis')
            self.traceback()

        self.trendItem.dataChanged.connect(self.update_cross_sections)

        # unregister old trendItem and register the new one as config delegate
        self.unregisterConfigurableItem ("trendItem", raiseOnError=False)
        if self.getModelInConfig():
            self.registerConfigDelegate(self.trendItem, name='trendItem')

    def getModel(self):
        """reimplemented from :class:`TaurusBaseWidget`"""
        if self.trendItem is None:
            return None
        else:
            return self.trendItem.getModel()

    def setUseArchiving(self, enable):
        """enables/disables looking up in the archiver for data stored before
        the Trend was started

        :param enable: (bool) if True, archiving values will be used if
                       available
        """
        if not self._stackMode == 'datetime':
            self.info('ignoring setUseArchiving. Reason: not in X time scale')
        self._useArchiving = enable

    def getUseArchiving(self):
        """whether TaurusTrend is looking for data in the archiver when needed

        :return: (bool)

        .. seealso:: :meth:`setUseArchiving`
        """
        return self._useArchiving

    def resetUseArchiving(self):
        """Same as setUseArchiving(False)"""
        self.setUseArchiving(False)

    def setMaxDataBufferSize(self, maxSize):
        """sets the maximum number of events that will be stacked

        :param maxSize: (int) the maximum limit

        .. seealso:: :class:`TaurusTrendSet`
        """
        if self.trendItem is not None:
            self.trendItem.setBufferSize(maxSize)

        self.buffersize = maxSize

    def getMaxDataBufferSize(self):
        """returns the maximum number of events that can be plotted in the trend

        :return: (int)
        """
        return self.buffersize

    def resetMaxDataBufferSize(self):
        """Same as setMaxDataBufferSize(512)  (i.e. 512 events)"""
        self.setMaxDataBufferSize(512)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """reimplemented from :class:`TaurusBaseWidget`"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.extra_guiqwt'
        ret['group'] = 'Taurus Display'
        ret['icon'] = 'designer:qwtplot.png'
        return ret

    def setModifiableByUser(self, modifiable):
        """reimplemented from :class:`TaurusBaseWidget`"""
        self.get_tool(TaurusModelChooserTool).action.setEnabled(modifiable)
        self.get_plot().set_items_readonly(not modifiable)
        TaurusBaseWidget.setModifiableByUser(self, modifiable)

    model = Qt.pyqtProperty("QString", getModel, setModel,
                            TaurusBaseWidget.resetModel)
    # @todo uncomment this when archiving is supported
    useArchiving = Qt.pyqtProperty("bool", getUseArchiving, setUseArchiving,
                                   resetUseArchiving)
    maxDataBufferSize = Qt.pyqtProperty("int", getMaxDataBufferSize,
                                        setMaxDataBufferSize,
                                        resetMaxDataBufferSize)
    stackMode = Qt.pyqtProperty("QString", getStackMode, setStackMode,
                                resetStackMode)
    modifiableByUser = Qt.pyqtProperty("bool",
                                       TaurusBaseWidget.isModifiableByUser,
                                       setModifiableByUser,
                                       TaurusBaseWidget.resetModifiableByUser)
