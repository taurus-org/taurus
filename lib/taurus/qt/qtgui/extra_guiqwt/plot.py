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

"""
Extension of :mod:`guiqwt.plot`
"""
__all__=["TaurusCurveWidget", "TaurusImageDialog", "TaurusImageWidget", "TaurusImageDialog"]

from guiqwt.plot import ImageDialog, ImageWidget, CurveWidget, CurveDialog
from PyQt4 import Qt
import copy
import taurus.core
from guiqwt.curve import CurveParam
from taurus.core.util import CaselessList
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE
from taurus.qt.qtgui.extra_guiqwt.builder import make
from taurus.qt.qtgui.extra_guiqwt.curve import TaurusCurveItem, TaurusTrendParam, TaurusTrendItem


class _BaseTaurusCurveWidget(TaurusBaseWidget):
    def __init__(self, name):
        TaurusBaseWidget.__init__(self, name)
        self._modelNames = CaselessList()
        from guiqwt.styles import style_generator
        self.style = style_generator()
        #for drag&drop
        self.setSupportedMimeTypes([TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE])
    
    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.TaurusAttribute
    
    def _splitModel(self, modelNames):
        '''convert str to list if needed (commas and whitespace are considered as separators)'''
        if isinstance(modelNames,(basestring,Qt.QString)): 
            modelNames = str(modelNames).replace(',',' ')
            modelNames = modelNames.split()
        return modelNames
    
    @Qt.pyqtSignature("setModel(QStringList)")
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
        #delete current TaurusCurveItems
        taurusCurveItems = [item for item in plot.get_public_items() if isinstance(item, TaurusCurveItem)]
        plot.del_items(taurusCurveItems)
        self._modelNames = CaselessList()
        #add new TaurusCurveItems
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
         
        #pre-process the model names
        modelNames = self._splitModel(modelNames)
        self._modelNames.extend([str(n) for n in modelNames])
        if self._designMode:
            return
        #create and attach new TaurusCurveItems
        for m in modelNames:
            #split model into x and y components
            mx_my = m.split('|')
            n = len(mx_my)
            if n == 1: 
                mx, my = None, mx_my[0]
            elif n == 2:
                mx, my = mx_my
            else:
                self.warning('Invalid model "%s" (Skipping)'%mx_my)
            #cycle styles
            style = self.style.next()
            color=style[0]
            linestyle = style[1:]
            #add the item 
            item = make.curve(mx,my, color=color, linestyle=linestyle, linewidth=2)
            item.set_readonly(not self.isModifiableByUser())
            plot.add_item(item)
        self.emit(Qt.SIGNAL("modelChanged()"))

    def getModel(self):
        """reimplemented from :class:`TaurusBaseWidget`"""
        return self._modelNames
        
    def setModifiableByUser(self, modifiable):
        """reimplemented from :class:`TaurusBaseWidget`"""
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusCurveChooserTool
        self.get_tool(TaurusCurveChooserTool).action.setEnabled(modifiable)
        self.get_plot().set_items_readonly(not modifiable)
        TaurusBaseWidget.setModifiableByUser(self, modifiable)    
    

class TaurusCurveWidget(CurveWidget, _BaseTaurusCurveWidget):
    '''A taurus widget for showing 1D data.
    It behaves as a regular :class:`guiqwt.plot.CurveWidget` but it also offers
    the expected Taurus interface (e.g. setting models, save/apply configs,
    drag&drops,...)
    
    .. seealso:: :class:`TaurusCurveDialog`
    '''
    def __init__(self, parent=None, designMode=False, **kwargs):
        '''see :class:`guiqwt.plot.CurveWidget` for other valid initialization parameters'''
        CurveWidget.__init__(self, parent=parent, **kwargs)
        _BaseTaurusCurveWidget.__init__(self, 'TaurusCurveWidget')
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusCurveChooserTool
        self.register_all_curve_tools()
        self.add_tool(TaurusCurveChooserTool)
        self.setModifiableByUser(True)
        self._designMode = designMode
            
    @classmethod
    def getQtDesignerPluginInfo(cls):
        """reimplemented from :class:`TaurusBaseWidget`"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.plot'
        ret['group'] = 'Taurus Display Widgets'
        ret['icon'] =':/designer/qwtplot.png'
        return ret
    
    model = Qt.pyqtProperty("QStringList", _BaseTaurusCurveWidget.getModel, _BaseTaurusCurveWidget.setModel, TaurusBaseWidget.resetModel)


class TaurusCurveDialog(CurveDialog, _BaseTaurusCurveWidget):
    '''A taurus dialog for showing 1D data.
    It behaves as a regular :class:`guiqwt.plot.CurveDialog` but it also offers
    the expected Taurus interface (e.g. setting models, save/apply configs,
    drag&drops,...)
    
    .. seealso:: :class:`TaurusCurveWidget`
    '''
    def __init__(self, parent=None, designMode=False, **kwargs):
        '''see :class:`guiqwt.plot.CurveDialog` for other valid initialization parameters'''
        CurveDialog.__init__(self, parent=parent, **kwargs)
        _BaseTaurusCurveWidget.__init__(self, 'TaurusCurveDialog')
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusCurveChooserTool
        self.add_tool(TaurusCurveChooserTool)
        self.setModifiableByUser(True)
    
    model = Qt.pyqtProperty("QStringList", _BaseTaurusCurveWidget.getModel, _BaseTaurusCurveWidget.setModel, TaurusBaseWidget.resetModel)
    

class _BaseTaurusTrendWidget(_BaseTaurusCurveWidget):
    def __init__(self, name, taurusparam=None):
        _BaseTaurusCurveWidget.__init__(self, 'TaurusCurveWidget')
        #...
        if taurusparam is None:
            taurusparam = TaurusTrendParam()
        self.defaultTaurusparam = taurusparam
    
    def getTaurusTrendItems(self):
        return [item for item in self.get_plot().get_public_items() if isinstance(item, TaurusTrendItem)]
        
    @Qt.pyqtSignature("setModel(QStringList)")
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
        #delete current TaurusCurveItems
        taurusTrendItems = self.getTaurusTrendItems()
        plot.del_items(taurusTrendItems)
        self._modelNames = CaselessList()
        #add new TaurusCurveItems
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
         
        #pre-process the model names
        modelNames = self._splitModel(modelNames)
        self._modelNames.extend([str(n) for n in modelNames])
        if self._designMode:
            return
        #create and attach new TaurusCurveItems
        for m in modelNames:
            #cycle styles
            style = self.style.next()
            #add the item
            item = make.ttrend(m, color=style[0], linestyle=style[1:], linewidth=2, taurusparam=copy.deepcopy(self.defaultTaurusparam))
            item.set_readonly(not self.isModifiableByUser())
            plot.add_item(item)
            item.update_params()
        
        self.setStackMode(self.defaultTaurusparam.stackMode)
        self.emit(Qt.SIGNAL("modelChanged()"))

    def setUseArchiving(self, enable):
        '''enables/disables looking up in the archiver for data stored before
        the Trend was started
        
        :param enable: (bool) if True, archiving values will be used if available
        '''
        if not self.defaultTaurusparam.stackMode=='datetime':
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
        '''set the type of stack to be used. This determines how X values are interpreted:
          - as timestamps ('datetime')
          - as time deltas ('timedelta')
          - as event numbers ('event')
        
        :param mode:(one of 'datetime', 'timedelta' or 'event')
        '''
        from taurus.qt.qtgui.extra_guiqwt.tools import TimeAxisTool
        mode = str(mode)
        if mode == 'datetime':
            self.add_tool(TimeAxisTool)
            timetool = self.get_tool(TimeAxisTool)
            timetool.set_scale_y_t(True)
        elif mode == 'deltatime':
            from taurus.qt.qtgui.plot import DeltaTimeScaleEngine
            plot = self.get_plot()
            DeltaTimeScaleEngine.enableInAxis(plot, plot.xBottom, rotation=-45)
        elif mode == 'event':
            plot = self.get_plot()
            scaleEngine = plot.axisScaleEngine(plot.xBottom)
            if hasattr(scaleEngine, 'disableInAxis'):
                scaleEngine.disableInAxis(plot, plot.xBottom)
        else:
            self.error('Unknown stack mode "%s"'%repr(mode))
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
        
class TaurusTrendWidget(CurveWidget, _BaseTaurusTrendWidget):
    '''A taurus widget for showing trends of scalar data.
    It is an specialization of :class:`guiqwt.plot.CurveWidget`, for displaying
    trends and offering the expected Taurus interface (e.g. setting models,
    save/apply configs, drag&drops,...)
    
    .. seealso:: :class:`TaurusTrendDialog`
    '''
    def __init__(self, parent=None, designMode=False, taurusparam=None, **kwargs):
        '''see :class:`guiqwt.plot.CurveWidget` for other valid initialization parameters'''
        CurveWidget.__init__(self, parent=parent, **kwargs)
        _BaseTaurusTrendWidget.__init__(self, 'TaurusTrendWidget', taurusparam)
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool
        self.register_all_curve_tools()
        self.add_tool(TaurusModelChooserTool)
        self.setModifiableByUser(True)
        self._designMode = designMode
            
    @classmethod
    def getQtDesignerPluginInfo(cls):
        """reimplemented from :class:`TaurusBaseWidget`"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.plot'
        ret['group'] = 'Taurus Display Widgets'
        ret['icon'] =':/designer/qwtplot.png'
        return ret
    
    model = Qt.pyqtProperty("QStringList", _BaseTaurusTrendWidget.getModel, _BaseTaurusTrendWidget.setModel, TaurusBaseWidget.resetModel)
    useArchiving = Qt.pyqtProperty("bool", _BaseTaurusTrendWidget.getUseArchiving, _BaseTaurusTrendWidget.setUseArchiving, _BaseTaurusTrendWidget.resetUseArchiving)
    maxDataBufferSize = Qt.pyqtProperty("int", _BaseTaurusTrendWidget.getMaxDataBufferSize, _BaseTaurusTrendWidget.setMaxDataBufferSize, _BaseTaurusTrendWidget.resetMaxDataBufferSize)
    stackMode = Qt.pyqtProperty("QString", _BaseTaurusTrendWidget.getStackMode, _BaseTaurusTrendWidget.setStackMode, _BaseTaurusTrendWidget.resetStackMode)
    

class TaurusTrendDialog(CurveDialog, _BaseTaurusTrendWidget):
    '''A taurus widget for showing trends of scalar data.
    It is an specialization of :class:`guiqwt.plot.CurveWidget`, for displaying
    trends and offering the expected Taurus interface (e.g. setting models,
    save/apply configs, drag&drops,...)
    
    .. seealso:: :class:`TaurusTrendDialog`
    '''
    def __init__(self, parent=None, designMode=False, taurusparam=None, toolbar=True, **kwargs):
        '''see :class:`guiqwt.plot.CurveDialog` for other valid initialization parameters'''
        CurveDialog.__init__(self, parent=parent, toolbar=toolbar, **kwargs)
        _BaseTaurusTrendWidget.__init__(self, 'TaurusTrendDialog', taurusparam)
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool
        self.add_tool(TaurusModelChooserTool)
        self.setModifiableByUser(True)
        self._designMode = designMode
            
    model = Qt.pyqtProperty("QStringList", _BaseTaurusTrendWidget.getModel, _BaseTaurusTrendWidget.setModel, TaurusBaseWidget.resetModel)
    useArchiving = Qt.pyqtProperty("bool", _BaseTaurusTrendWidget.getUseArchiving, _BaseTaurusTrendWidget.setUseArchiving, _BaseTaurusTrendWidget.resetUseArchiving)
    maxDataBufferSize = Qt.pyqtProperty("int", _BaseTaurusTrendWidget.getMaxDataBufferSize, _BaseTaurusTrendWidget.setMaxDataBufferSize, _BaseTaurusTrendWidget.resetMaxDataBufferSize)
    stackMode = Qt.pyqtProperty("QString", _BaseTaurusTrendWidget.getStackMode, _BaseTaurusTrendWidget.setStackMode, _BaseTaurusTrendWidget.resetStackMode)
    


class _BaseTaurusImageWidget(TaurusBaseWidget):
    def __init__(self, name):
        TaurusBaseWidget.__init__(self, name)
        self.imgItem = None
    
    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.TaurusAttribute
        
    def setModel(self, model):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        plot = self.get_plot()
        if self.imgItem is not None:
            plot.del_item(self.imgItem)
        self.imgItem = make.image(taurusmodel=model)
        plot.add_item(self.imgItem)
        self.imgItem.set_readonly(not self.isModifiableByUser())
        self.connect(self.imgItem.getSignaller(), Qt.SIGNAL("dataChanged"), self.update_cross_sections) #IMPORTANT: connect the cross section plots to the taurusimage so that they are updated when the taurus data changes
        
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
   
    
class TaurusImageWidget(ImageWidget, _BaseTaurusImageWidget):
    '''A taurus widget for showing 2D data.
    It behaves as a regular :class:`guiqwt.plot.ImageWidget` but it also offers
    the expected Taurus interface (e.g. setting models, save/apply configs,
    drag&drops,...)
    
    .. seealso:: :class:`TaurusImageDialog`
    '''
    def __init__(self, parent=None, designMode=False, **kwargs):
        '''see :class:`guiqwt.plot.ImageWidget` for other valid initialization parameters'''
        ImageWidget.__init__(self, parent=parent, **kwargs)
        _BaseTaurusImageWidget.__init__(self, 'TaurusImageDialog')
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool
        self.register_all_image_tools()
        self.add_tool(TaurusModelChooserTool)
        self.setModifiableByUser(True)
        
    def get_context_menu(self, plot=None): #@todo: This is a workaround because the CrossSectionTool is not shown in the context menu by default
        ret = ImageWidget.get_context_menu(self, plot=plot)
        from guiqwt.tools import CrossSectionTool, AverageCrossSectionTool
        for toolklass in CrossSectionTool, AverageCrossSectionTool:
            tool = self.get_tool(toolklass)
            ret.addAction(tool.action)
        return ret
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        """reimplemented from :class:`TaurusBaseWidget`"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.plot'
        ret['group'] = 'Taurus Display Widgets'
        ret['icon'] =':/designer/qwtplot.png'
        return ret
    
    model = Qt.pyqtProperty("QString", _BaseTaurusImageWidget.getModel, _BaseTaurusImageWidget.setModel, TaurusBaseWidget.resetModel)
    

class TaurusImageDialog(ImageDialog, _BaseTaurusImageWidget):
    '''A taurus dialog for showing 2D data.
    It behaves as a regular :class:`guiqwt.plot.ImageDialog` but it also offers
    the expected Taurus interface (e.g. setting models, save/apply configs,
    drag&drops,...)
    
    .. seealso:: :class:`TaurusImageWidget`
    '''
    def __init__(self, parent=None, designMode=False, toolbar=True, options=None, **kwargs):
        '''see :class:`guiqwt.plot.ImageDialog` for other valid initialization parameters'''
        ImageDialog.__init__(self, parent=parent, toolbar=toolbar, options=options, **kwargs)
        _BaseTaurusImageWidget.__init__(self, 'TaurusImageDialog')
        from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool
        self.add_tool(TaurusModelChooserTool)
        self.setModifiableByUser(True)
         
    model = Qt.pyqtProperty("QString", _BaseTaurusImageWidget.getModel, _BaseTaurusImageWidget.setModel, TaurusBaseWidget.resetModel)


def test1():
    from taurus.qt.qtgui.application import TaurusApplication
    import sys
    
    #prepare options
    app = TaurusApplication()
    args = app.get_command_line_args()

    w = TaurusImageWidget()
        
    #set model
    if len(args) == 1:
        w.setModel(args[0])
    else:
        w.setModel('eval://rand(256,128)')
    
    w.show()
    sys.exit(app.exec_())      
    
    
def test2():
    from taurus.qt.qtgui.application import TaurusApplication
    import sys
    
    #prepare options
    app = TaurusApplication()
    args = app.get_command_line_args()

    w = TaurusCurveWidget()
        
    #set model
    if len(args) != 0:
        w.setModel(args)
    else:
        w.setModel('eval://rand(128)')
    
    w.show()
    sys.exit(app.exec_())    
    

def taurusCurveDlgMain():
    from taurus.qt.qtgui.extra_guiqwt.builder import make
    from taurus.qt.qtgui.application import TaurusApplication
    from guiqwt.plot import CurveDialog
    from taurus.qt.qtgui.extra_guiqwt.tools import TimeAxisTool
    import taurus.core.util.argparse
    import sys
    
    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [<model1> [<model2>] ...]")
    parser.set_description("a taurus application for plotting 1D data sets")
    parser.add_option("--demo", action="store_true", dest="demo", default=False, help="show a demo of the widget")
    app = TaurusApplication(cmd_line_parser=parser, app_name="Taurus Curve Dialog", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()
    
    #check & process options
    if options.demo:
        args.append('eval://rand(128)')
        
    w = TaurusCurveDialog(edit=False, wintitle="Taurus Curve Dialog")
    #w = TaurusCurveWidget()
    
    w.add_tool(TimeAxisTool)
     
    #set model
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
    
    #prepare options
    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] <model>")
    parser.set_description('a Taurus application for plotting trends of scalars')
    parser.add_option("-x", "--x-axis-mode", dest="x_axis_mode", default='t', metavar="t|d|e",
                  help="interpret X values as timestamps (t), time deltas (d) or event numbers (e). Accepted values: t|d|e")    
    parser.add_option("-b", "--buffer", dest="max_buffer_size", default='10000', 
                      help="maximum number of values to be plotted (when reached, the oldest values will be discarded)")
    parser.add_option("-a", "--use-archiving", action="store_true", dest="use_archiving", default=False)
    parser.add_option("--demo", action="store_true", dest="demo", default=False, help="show a demo of the widget")
    app = TaurusApplication(cmd_line_parser=parser, app_name="Taurus Trend", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()
    
    #check & process options
    stackModeMap = dict(t='datetime', d='deltatime', e='event')  
    if options.x_axis_mode.lower() not in stackModeMap:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    stackMode = stackModeMap[options.x_axis_mode.lower()]

    if options.use_archiving:
        raise NotImplementedError('Archiving support is not yet implemented')
      
    if options.demo:
        args.append('eval://rand()')
    
    taurusparam = TaurusTrendParam()
    taurusparam.stackMode = stackMode
    taurusparam.maxBufferSize = int(options.max_buffer_size)
    taurusparam.useArchiving = options.use_archiving
    
    w = TaurusTrendDialog(wintitle="Taurus Trend", taurusparam=taurusparam)
    #w = TaurusTrendWidget(taurusparam=taurusparam)
    
    #set model
    if len(args) > 0:
        w.setModel(args)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    w.show()
    sys.exit(app.exec_())      
    
def taurusImageDlgMain():
    from taurus.qt.qtgui.application import TaurusApplication
    import taurus.core
    import sys
    
    #prepare options
    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] <model>")
    parser.set_description('a Taurus application for plotting Image Attributes')
    parser.add_option("--demo", action="store_true", dest="demo", default=False, help="show a demo of the widget")
    app = TaurusApplication(cmd_line_parser=parser, app_name="Taurus Image Dialog", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()
    
    #check & process options
    if options.demo:
        args.append('eval://rand(256,128)')
        
    w = TaurusImageDialog()
    #w = TaurusImageWidget()
        
    #set model
    if len(args) == 1:
        w.setModel(args[0])
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    w.show()
    sys.exit(app.exec_())      
        

if __name__ == "__main__":
#    test2()
#    taurusCurveDlgMain()
    taurusTrendDlgMain()
#    taurusImageDlgMain()    
    