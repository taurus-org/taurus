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
Extension of :mod:`guiqwt.plot`
"""
from builtins import next
from builtins import str

import copy

from future.utils import string_types
from guiqwt.plot import ImageDialog, CurveDialog

import taurus.core
from taurus.external.qt import Qt

from taurus.core.util.containers import CaselessList
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE
from taurus.qt.qtgui.extra_guiqwt.builder import make
from taurus.qt.qtgui.extra_guiqwt.curve import TaurusCurveItem, TaurusTrendParam, TaurusTrendItem
import taurus.cli.common


__all__ = ["TaurusCurveDialog", "TaurusTrendDialog", "TaurusImageDialog"]


class TaurusCurveDialog(CurveDialog, TaurusBaseWidget):
    '''A taurus dialog for showing 1D data.
    It behaves as a regular :class:`guiqwt.plot.CurveDialog` but it also offers
    the expected Taurus interface (e.g. setting models, save/apply configs,
    drag&drops,...)

    .. seealso:: :class:`TaurusCurveWidget`
    '''
    _modifiableByUser = True
    modelChanged = Qt.pyqtSignal([], ['QStringList'], ['QString'])

    def __init__(self, parent=None, designMode=False, toolbar=True, **kwargs):
        '''see :class:`guiqwt.plot.CurveDialog` for other valid initialization parameters'''
        CurveDialog.__init__(self, parent=parent, toolbar=toolbar, **kwargs)
        TaurusBaseWidget.__init__(self, 'TaurusCurveDialog')
        self.deprecated(rel='4.1', dep='TaurusCurveDialog', alt='TaurusPlot / taurus tpg plot launcher')
        self.setWindowFlags(Qt.Qt.Widget)
        self._designMode = designMode
        self._modelNames = CaselessList()
        from guiqwt.styles import style_generator
        self.style = style_generator()
        self.setSupportedMimeTypes(
            [TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE])
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusCurveChooserTool
        self.add_tool(TaurusCurveChooserTool)
        self.setModifiableByUser(self._modifiableByUser)
        self.setContextMenuPolicy(Qt.Qt.CustomContextMenu)

    def keyPressEvent(self, event):
        if(event.key() == Qt.Qt.Key_Escape):
            event.ignore()
        else:
            ImageDialog.keyPressEvent(self, event)

    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.taurusattribute.TaurusAttribute

    def _splitModel(self, modelNames):
        '''convert str to list if needed (commas and whitespace are considered as separators)'''
        if isinstance(modelNames, string_types):
            modelNames = str(modelNames).replace(',', ' ')
            modelNames = modelNames.split()
        return modelNames

    @Qt.pyqtSlot('QStringList')
    def setModel(self, modelNames):
        '''Removes current TaurusCurveItems and adds new ones.

        :param modelNames: (sequence<str> or str) the names of the models to be
                           plotted. For convenience, a string is also accepted
                           (instead of a sequence of strings), in which case the
                           string will be internally converted to a sequence by
                           splitting it on whitespace and commas. Each model can
                           optionally be composed of two parts, separated by "|"
                           indicating X and Y components for the curve. If only
                           one part is given, it is used for Y and X is
                           automatically generated as an index.

        .. seealso:: :meth:`addModels`
        '''

        plot = self.get_plot()
        # delete current TaurusCurveItems
        taurusCurveItems = [item for item in plot.get_public_items(
        ) if isinstance(item, TaurusCurveItem)]
        plot.del_items(taurusCurveItems)
        self._modelNames = CaselessList()
        # add new TaurusCurveItems
        self.addModels(modelNames)

    def addModels(self, modelNames):
        '''Creates TaurusCurveItems (one for each model in modelNames) and attaches
        them to the plot.

        .. note:: you can also add curves using :meth:`add_items`. :meth:`addModels`
                  is only a more Taurus-oriented interface. :meth:`add_items`
                  gives you more control.

        :param modelNames: (sequence<str> or str) the names of the models to be
                           plotted. For convenience, string is also accepted
                           (instead of a sequence of strings), in which case the
                           string will be internally converted to a sequence by
                           splitting it on whitespace and commas. Each model can
                           optionally be composed of two parts, separated by "|"
                           indicating X and Y components for the curve. If only
                           one part is given, it is used for Y and X is
                           automatically generated as an index.

        .. seealso:: :meth:`add_item`
        '''
        plot = self.get_plot()

        # pre-process the model names
        modelNames = self._splitModel(modelNames)
        self._modelNames.extend([str(n) for n in modelNames])
        if self._designMode:
            return
        # create and attach new TaurusCurveItems
        for m in modelNames:
            # split model into x and y components
            mx_my = m.split('|')
            n = len(mx_my)
            if n == 1:
                mx, my = None, mx_my[0]
            elif n == 2:
                mx, my = mx_my
            else:
                self.warning('Invalid model "%s" (Skipping)' % mx_my)
            # cycle styles
            style = next(self.style)
            color = style[0]
            linestyle = style[1:]
            # add the item
            item = make.curve(mx, my, color=color,
                              linestyle=linestyle, linewidth=2)
            item.set_readonly(not self.isModifiableByUser())
            plot.add_item(item)
        self.modelChanged.emit()

    def getModel(self):
        """reimplemented from :class:`TaurusBaseWidget`"""
        return self._modelNames

    def setModifiableByUser(self, modifiable):
        """reimplemented from :class:`TaurusBaseWidget`"""
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusCurveChooserTool
        self.get_tool(TaurusCurveChooserTool).action.setEnabled(modifiable)
        self.get_plot().set_items_readonly(not modifiable)
        TaurusBaseWidget.setModifiableByUser(self, modifiable)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """reimplemented from :class:`TaurusBaseWidget`"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.extra_guiqwt'
        ret['group'] = 'Taurus Display'
        ret['icon'] = 'designer:qwtplot.png'
        return ret

    model = Qt.pyqtProperty("QStringList", getModel,
                            setModel, TaurusBaseWidget.resetModel)
    modifiableByUser = Qt.pyqtProperty(
        "bool", TaurusBaseWidget.isModifiableByUser, setModifiableByUser, TaurusBaseWidget.resetModifiableByUser)


class TaurusTrendDialog(CurveDialog, TaurusBaseWidget):
    '''A taurus widget for showing trends of scalar data.
    It is an specialization of :class:`guiqwt.plot.CurveWidget`, for displaying
    trends and offering the expected Taurus interface (e.g. setting models,
    save/apply configs, drag&drops,...)

    .. seealso:: :class:`TaurusTrendDialog`
    '''
    _modifiableByUser = True

    modelChanged = Qt.pyqtSignal([], ['QStringList'], ['QString'])

    def __init__(self, parent=None, designMode=False, taurusparam=None, toolbar=True, **kwargs):
        '''see :class:`guiqwt.plot.CurveDialog` for other valid initialization parameters'''
        CurveDialog.__init__(self, parent=parent, toolbar=toolbar, **kwargs)
        TaurusBaseWidget.__init__(self, 'TaurusTrendDialog')
        self.deprecated(rel='4.1', dep='TaurusTrendDialog', alt='TaurusTrend / taurus tpg trend launcher')
        self.setWindowFlags(Qt.Qt.Widget)
        self._designMode = designMode
        self._modelNames = CaselessList()
        from guiqwt.styles import style_generator
        self.style = style_generator()
        self.setSupportedMimeTypes(
            [TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE])
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool, AutoScrollTool
        self.add_tool(TaurusModelChooserTool, singleModel=False)
        self.add_tool(AutoScrollTool)
        self.setModifiableByUser(self._modifiableByUser)
        if taurusparam is None:
            taurusparam = TaurusTrendParam()
        self.defaultTaurusparam = taurusparam
        self.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.registerConfigDelegate(self.get_tool(AutoScrollTool))

    def keyPressEvent(self, event):
        if(event.key() == Qt.Qt.Key_Escape):
            event.ignore()
        else:
            ImageDialog.keyPressEvent(self, event)

    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.taurusattribute.TaurusAttribute

    def getTaurusTrendItems(self):
        return [item for item in self.get_plot().get_public_items() if isinstance(item, TaurusTrendItem)]

    def _splitModel(self, modelNames):
        '''convert str to list if needed (commas and whitespace are considered as separators)'''
        if isinstance(modelNames, string_types):
            modelNames = str(modelNames).replace(',', ' ')
            modelNames = modelNames.split()
        return modelNames

    @Qt.pyqtSlot('QStringList')
    def setModel(self, modelNames):
        '''Removes current TaurusCurveItems and adds new ones.

        :param modelNames: (sequence<str> or str) the names of the models to be
                           plotted. For convenience, a string is also accepted
                           (instead of a sequence of strings), in which case the
                           string will be internally converted to a sequence by
                           splitting it on whitespace and commas.

        .. seealso:: :meth:`addModels`
        '''

        plot = self.get_plot()
        # delete current TaurusCurveItems
        taurusTrendItems = self.getTaurusTrendItems()
        plot.del_items(taurusTrendItems)
        self._modelNames = CaselessList()
        # add new TaurusCurveItems
        self.addModels(modelNames)

    def addModels(self, modelNames):
        '''Creates TaurusCurveItems (one for each model in modelNames) and attaches
        them to the plot.

        .. note:: you can also add curves using :meth:`add_items`. :meth:`addModels`
                  is only a more Taurus-oriented interface. :meth:`add_items`
                  gives you more control.

        :param modelNames: (sequence<str> or str) the names of the models to be
                           plotted. For convenience, a string is also accepted
                           (instead of a sequence of strings), in which case the
                           string will be internally converted to a sequence by
                           splitting it on whitespace and commas.

        .. seealso:: :meth:`add_item`
        '''
        plot = self.get_plot()

        # pre-process the model names
        modelNames = self._splitModel(modelNames)
        self._modelNames.extend([str(n) for n in modelNames])
        if self._designMode:
            return
        # create and attach new TaurusCurveItems
        for m in modelNames:
            # cycle styles
            style = next(self.style)
            # add the item
            item = make.ttrend(m, color=style[0], linestyle=style[
                               1:], linewidth=2, taurusparam=copy.deepcopy(self.defaultTaurusparam))
            item.set_readonly(not self.isModifiableByUser())
            plot.add_item(item)
            item.update_params()

        self.setStackMode(self.defaultTaurusparam.stackMode)
        self.modelChanged.emit()

    def getModel(self):
        """reimplemented from :class:`TaurusBaseWidget`"""
        return self._modelNames

    def setUseArchiving(self, enable):
        '''enables/disables looking up in the archiver for data stored before
        the Trend was started

        :param enable: (bool) if True, archiving values will be used if available
        '''
        if not self.defaultTaurusparam.stackMode == 'datetime':
            self.info('ignoring setUseArchiving. Reason: not in X time scale')
        self.defaultTaurusparam.useArchiving = enable

    def getUseArchiving(self):
        '''whether TaurusTrend is looking for data in the archiver when needed

        :return: (bool)

        .. seealso:: :meth:`setUseArchiving`
        '''
        return self.defaultTaurusparam.useArchiving

    def resetUseArchiving(self):
        '''Same as setUseArchiving(False)'''
        self.setUseArchiving(False)

    def setMaxDataBufferSize(self, maxSize):
        '''sets the maximum number of events that will be stacked

        :param maxSize: (int) the maximum limit

        .. seealso:: :class:`TaurusTrendSet`
        '''
        for item in self.getTaurusTrendItems():
            item.setBufferSize(maxSize)

        self.defaultTaurusparam.maxBufferSize = maxSize

    def getMaxDataBufferSize(self):
        '''returns the maximum number of events that can be plotted in the trend

        :return: (int)
        '''
        return self.defaultTaurusparam.maxBufferSize

    def resetMaxDataBufferSize(self):
        '''Same as setMaxDataBufferSize(16384)'''
        self.setMaxDataBufferSize(16384)

    def setStackMode(self, mode):
        '''set the type of stack to be used. This determines how X values are
        interpreted:

            - as timestamps ('datetime')
            - as time deltas ('timedelta')
            - as event numbers ('event')

        :param mode:(one of 'datetime', 'timedelta' or 'event')
        '''
        from taurus.qt.qtgui.extra_guiqwt.tools import TimeAxisTool
        mode = str(mode)
        if mode == 'datetime':
            timetool = self.get_tool(TimeAxisTool)
            if timetool is None:
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

        self.defaultTaurusparam.stackMode = mode

        for item in self.getTaurusTrendItems():
            item.taurusparam.stackMode = mode

    def getStackMode(self):
        return self.defaultTaurusparam.stackMode

    def resetStackMode(self):
        self.setStackMode('datetime')

    def setModifiableByUser(self, modifiable):
        """reimplemented from :class:`TaurusBaseWidget`"""
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool
        self.get_tool(TaurusModelChooserTool).action.setEnabled(modifiable)
        self.get_plot().set_items_readonly(not modifiable)
        TaurusBaseWidget.setModifiableByUser(self, modifiable)

    def getDropEventCallback(self):
        """reimplemented from :class:`TaurusBaseWidget`"""
        return self.addModels

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """reimplemented from :class:`TaurusBaseWidget`"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.extra_guiqwt'
        ret['group'] = 'Taurus Display'
        ret['icon'] = 'designer:qwtplot.png'
        return ret

    model = Qt.pyqtProperty("QStringList", getModel,
                            setModel, TaurusBaseWidget.resetModel)
    useArchiving = Qt.pyqtProperty(
        "bool", getUseArchiving, setUseArchiving, resetUseArchiving)
    maxDataBufferSize = Qt.pyqtProperty(
        "int", getMaxDataBufferSize, setMaxDataBufferSize, resetMaxDataBufferSize)
    stackMode = Qt.pyqtProperty(
        "QString", getStackMode, setStackMode, resetStackMode)
    modifiableByUser = Qt.pyqtProperty(
        "bool", TaurusBaseWidget.isModifiableByUser, setModifiableByUser, TaurusBaseWidget.resetModifiableByUser)


class TaurusImageDialog(ImageDialog, TaurusBaseWidget):
    '''A taurus dialog for showing 2D data.
    It behaves as a regular :class:`guiqwt.plot.ImageDialog` but it also offers
    the expected Taurus interface (e.g. setting models, save/apply configs,
    drag&drops,...)

    .. seealso:: :class:`TaurusImageWidget`
    '''
    _rgbmode = False

    def __init__(self, parent=None, designMode=False, toolbar=True, **kwargs):
        '''see :class:`guiqwt.plot.ImageDialog` for other valid initialization parameters'''
        ImageDialog.__init__(self, parent=parent, toolbar=toolbar, **kwargs)
        TaurusBaseWidget.__init__(self, 'TaurusImageDialog')
        self.setWindowFlags(Qt.Qt.Widget)
        self.imgItem = None
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool
        self.add_tool(TaurusModelChooserTool, singleModel=True)
        self.setModifiableByUser(True)
        self.setContextMenuPolicy(Qt.Qt.CustomContextMenu)

    def keyPressEvent(self, event):
        if(event.key() == Qt.Qt.Key_Escape):
            event.ignore()
        else:
            ImageDialog.keyPressEvent(self, event)

    def setRGBmode(self, enable):
        self._rgbmode = enable
        # enable the zaxis only when not in rgb mode
        plot = self.get_plot()
        zaxis = plot.colormap_axis
        plot.enableAxis(zaxis, not enable)

    def getRGBmode(self):
        return self._rgbmode

    def resetRGBmode(self):
        self.setRGBmode(self.__class__._rgbmode)

    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.taurusattribute.TaurusAttribute

    @Qt.pyqtSlot("QString")
    def setModel(self, model):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        if self.getUseParentModel():
            # @fixme: This assumes Tango models.
            model = "/".join((str(self.getParentModelName()), str(model)))
        plot = self.get_plot()
        if self.imgItem is not None:
            try:
                plot.del_item(self.imgItem)
            except:
                self.info("Unable to delete item from plot")
        if not model:
            self.imgItem = None
            return
        if self.rgbmode:
            self.imgItem = make.rgbimage(taurusmodel=model)
        else:
            self.imgItem = make.image(taurusmodel=model)
        plot.add_item(self.imgItem)
        self.imgItem.set_readonly(not self.isModifiableByUser())
        # IMPORTANT: connect the cross section plots to the taurusimage so that
        # they are updated when the taurus data changes
        self.imgItem.dataChanged.connect(self.update_cross_sections)

    def getModel(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        if self.imgItem is None:
            return ''
        else:
            return self.imgItem.getModel()

    def setModifiableByUser(self, modifiable):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool
        self.get_tool(TaurusModelChooserTool).action.setEnabled(modifiable)
        self.get_plot().set_items_readonly(not modifiable)
        TaurusBaseWidget.setModifiableByUser(self, modifiable)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        """reimplemented from :class:`TaurusBaseWidget`"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.extra_guiqwt'
        ret['group'] = 'Taurus Display'
        ret['icon'] = 'designer:qwtplot.png'
        return ret

    model = Qt.pyqtProperty("QString", getModel, setModel,
                            TaurusBaseWidget.resetModel)
    rgbmode = Qt.pyqtProperty("bool", getRGBmode, setRGBmode, resetRGBmode)
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)
    modifiableByUser = Qt.pyqtProperty("bool", TaurusBaseWidget.isModifiableByUser,
                                       setModifiableByUser,
                                       TaurusBaseWidget.resetModifiableByUser)


def taurusCurveDlgMain():
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.extra_guiqwt.tools import TimeAxisTool
    import taurus.core.util.argparse
    import sys

    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [<model1> [<model2>] ...]")
    parser.set_description("a taurus application for plotting 1D data sets")
    parser.add_option("--demo", action="store_true", dest="demo",
                      default=False, help="show a demo of the widget")
    parser.add_option("--window-name", dest="window_name",
                      default="Taurus Curve Dialog", help="Name of the window")
    app = TaurusApplication(
        cmd_line_parser=parser, app_name="Taurus Curve Dialog", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()

    # check & process options
    if options.demo:
        args.append('eval:rand(128)')

    w = TaurusCurveDialog(edit=False, wintitle=options.window_name)

    w.add_tool(TimeAxisTool)

    # set model
    if len(args) > 0:
        w.setModel(args)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)

    w.show()
    sys.exit(app.exec_())


def taurusTrendDlgMain():
    from taurus.qt.qtgui.application import TaurusApplication
    import taurus.core
    import sys

    # prepare options
    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] <model>")
    parser.set_description(
        'a Taurus application for plotting trends of scalars')
    parser.add_option("-x", "--x-axis-mode", dest="x_axis_mode", default='t', metavar="t|d|e",
                      help="interpret X values as timestamps (t), time deltas (d) or event numbers (e). Accepted values: t|d|e")
    parser.add_option("-b", "--buffer", dest="max_buffer_size", default='10000',
                      help="maximum number of values to be plotted (when reached, the oldest values will be discarded)")
    parser.add_option("-a", "--use-archiving",
                      action="store_true", dest="use_archiving", default=False)
    parser.add_option("--demo", action="store_true", dest="demo",
                      default=False, help="show a demo of the widget")
    parser.add_option("--window-name", dest="window_name",
                      default="Taurus Trend", help="Name of the window")
    app = TaurusApplication(
        cmd_line_parser=parser, app_name="Taurus Trend", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()

    # check & process options
    stackModeMap = dict(t='datetime', d='deltatime', e='event')
    if options.x_axis_mode.lower() not in stackModeMap:
        parser.print_help(sys.stderr)
        sys.exit(1)

    stackMode = stackModeMap[options.x_axis_mode.lower()]

    if options.use_archiving:
        raise NotImplementedError('Archiving support is not yet implemented')

    if options.demo:
        args.append('eval:rand()')

    taurusparam = TaurusTrendParam()
    taurusparam.stackMode = stackMode
    taurusparam.maxBufferSize = int(options.max_buffer_size)
    taurusparam.useArchiving = options.use_archiving

    w = TaurusTrendDialog(wintitle=options.window_name,
                          taurusparam=taurusparam)

    # set model
    if len(args) > 0:
        w.setModel(args)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)

    w.show()
    sys.exit(app.exec_())

