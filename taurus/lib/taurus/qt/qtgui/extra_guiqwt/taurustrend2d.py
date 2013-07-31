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
taurustrend.py: Generic trend widget for Taurus
"""
__all__=["TaurusTrend2DDialog"]

from guiqwt.plot import ImageDialog
from taurus.qt import Qt
import taurus.core
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.extra_guiqwt.image import TaurusTrend2DItem
from taurus.qt.qtgui.extra_guiqwt.tools import TaurusModelChooserTool, TimeAxisTool, AutoScrollTool




class TaurusTrend2DDialog(ImageDialog, TaurusBaseWidget):
    '''
    This is a widget for displaying trends from 1D Taurus attributes (i.e.,
    representing the variation over time of a 1D array). Sometimes this kind of
    plots are also known as "spectrograms".
    
    The widget shows a 3D plot (Z represented with colors) where the values in
    the 1D array are plotted in the Y-Z plane and are stacked along the X axis.
    '''
    _modifiableByUser = True
    def __init__(self, parent=None, designMode=False, toolbar=True, stackMode='datetime', buffersize=512, options=None, **kwargs):
        '''see :class:`guiqwt.plot.ImageDialog` for other valid initialization parameters'''
        defaultOptions = dict(lock_aspect_ratio=False)
        if options is not None:
            defaultOptions.update(options)
        ImageDialog.__init__(self, parent=parent, toolbar=toolbar, options=defaultOptions, **kwargs)
        TaurusBaseWidget.__init__(self, "TaurusTrend2DDialog")
        self.trendItem = None  
        self.buffersize = buffersize
        self._useArchiving = False
        self._stackMode = stackMode
        self.setStackMode(stackMode)
        self.setWindowFlags(Qt.Qt.Widget)
        #add some tools
        for toolklass in (TaurusModelChooserTool,AutoScrollTool):
            self.add_tool(toolklass)
        self.setModifiableByUser(self._modifiableByUser)
    
    def keyPressEvent(self,event):
        if(event.key() == Qt.Qt.Key_Escape):
            event.ignore()
        else:
            ImageDialog.keyPressEvent(self,event)
                    
    def setStackMode(self, mode):
        '''set the type of stack to be used. This determines how X values are
        interpreted:
            
            - as timestamps ('datetime')
            - as time deltas ('timedelta')
            - as event numbers ('event')
        
        :param mode:(one of 'datetime', 'timedelta' or 'event')
        '''
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
        self._stackMode = mode
        if hasattr(self.trendItem,'stackMode'):
            self.trendItem.stackMode = mode
               
    def getStackMode(self):
        return self._stackMode
        
    def resetStackMode(self):
        self.setStackMode('datetime')
    
    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.taurusattribute.TaurusAttribute
        
    def setModel(self, model):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        plot = self.get_plot()
        if self.trendItem is not None:
            plot.del_item(self.trendItem)
        self.trendItem = TaurusTrend2DItem(stackMode=self.getStackMode(), buffersize = self.buffersize)
        self.trendItem.setModel(model)
        plot.add_item(self.trendItem)
        self.trendItem.set_readonly(not self.isModifiableByUser())
        plot.set_axis_title(plot.colormap_axis, 'value')
        plot.set_axis_unit('left', 'index')
        try:
            plot.set_axis_title('left', self.trendItem.getModelObj().getSimpleName())
        except:
            self.debug('cannot set title for left axis')
            self.traceback()
        try:
            unit = self.trendItem.getModelObj().getConfig().getUnit() or ''
            plot.set_axis_unit(plot.colormap_axis, unit)
        except:
            self.debug('cannot set units for colormap axis')
            self.traceback()
        
        self.connect(self.trendItem.getSignaller(), Qt.SIGNAL("dataChanged"), self.update_cross_sections)
        
    def getModel(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        if self.trendItem is None:
            return None
        else:
            return self.trendItem.getModel()
    
    def setUseArchiving(self, enable):
        '''enables/disables looking up in the archiver for data stored before
        the Trend was started
        
        :param enable: (bool) if True, archiving values will be used if available
        '''
        if not self._stackMode=='datetime':
            self.info('ignoring setUseArchiving. Reason: not in X time scale')
        self._useArchiving = enable
        
    def getUseArchiving(self):
        '''whether TaurusTrend is looking for data in the archiver when needed
        
        :return: (bool)
        
        .. seealso:: :meth:`setUseArchiving`
        '''
        return self._useArchiving

    def resetUseArchiving(self):
        '''Same as setUseArchiving(False)'''
        self.setUseArchiving(False)
        
    def setMaxDataBufferSize(self, maxSize):
        '''sets the maximum number of events that will be stacked
        
        :param maxSize: (int) the maximum limit
        
        .. seealso:: :class:`TaurusTrendSet`
        '''
        if self.trendItem is not None:
            self.trendItem.setBufferSize(maxSize)
    
        self.buffersize = maxSize
        
    def getMaxDataBufferSize(self):
        '''returns the maximum number of events that can be plotted in the trend
        
        :return: (int)
        '''
        return self.buffersize
            
    def resetMaxDataBufferSize(self):
        '''Same as setMaxDataBufferSize(512)  (i.e. 512 events)'''
        self.setMaxDataBufferSize(512) 
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        """reimplemented from :class:`TaurusBaseWidget`"""
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.plot'
        ret['group'] = 'Taurus Display'
        ret['icon'] =':/designer/qwtplot.png'
        return ret  
    
    def setModifiableByUser(self, modifiable):
        """reimplemented from :class:`TaurusBaseWidget`"""
        self.get_tool(TaurusModelChooserTool).action.setEnabled(modifiable)
        self.get_plot().set_items_readonly(not modifiable)
        TaurusBaseWidget.setModifiableByUser(self, modifiable)
    
    model = Qt.pyqtProperty("QString", getModel, setModel, TaurusBaseWidget.resetModel)
    useArchiving = Qt.pyqtProperty("bool", getUseArchiving, setUseArchiving, resetUseArchiving) #@todo uncomment this when archiving is supported
    maxDataBufferSize = Qt.pyqtProperty("int", getMaxDataBufferSize, setMaxDataBufferSize, resetMaxDataBufferSize)
    stackMode = Qt.pyqtProperty("QString", getStackMode, setStackMode, resetStackMode)
    modifiableByUser = Qt.pyqtProperty("bool", TaurusBaseWidget.isModifiableByUser, setModifiableByUser, TaurusBaseWidget.resetModifiableByUser) 
    

        
def taurusTrend2DMain():
    from taurus.qt.qtgui.application import TaurusApplication
    import taurus.core
    import sys
    
    #prepare options
    parser = taurus.core.util.argparse.get_taurus_parser()
    parser.set_usage("%prog [options] <model>")
    parser.set_description('a Taurus application for plotting trends of arrays (aka "spectrograms")')
    parser.add_option("-x", "--x-axis-mode", dest="x_axis_mode", default='d', metavar="t|d|e",
                  help="interpret X values as timestamps (t), time deltas (d) or event numbers (e). Accepted values: t|d|e")    
    parser.add_option("-b", "--buffer", dest="max_buffer_size", default='512', 
                      help="maximum number of values to be stacked (when reached, the oldest values will be discarded)")
    parser.add_option("-a", "--use-archiving", action="store_true", dest="use_archiving", default=False)
    parser.add_option("--demo", action="store_true", dest="demo", default=False, help="show a demo of the widget")
    parser.add_option("--window-name", dest="window_name", default="Taurus Trend 2D", help="Name of the window")
    
    app = TaurusApplication(cmd_line_parser=parser, app_name="Taurus Trend 2D", app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()
    
    #check & process options
    stackModeMap = dict(t='datetime', d='deltatime', e='event')  
    if options.x_axis_mode.lower() not in stackModeMap:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    stackMode = stackModeMap[options.x_axis_mode.lower()]
      
    if options.demo:
        args.append('eval://sin(x+t)?x=linspace(0,3,40);t=rand()')
        
    w = TaurusTrend2DDialog(stackMode=stackMode, wintitle=options.window_name, 
                            buffersize=int(options.max_buffer_size))
    
    #set archiving
    if options.use_archiving:
        raise NotImplementedError('Archiving support is not yet implemented')
        w.setUseArchiving(True)
    
    #set model
    if len(args) == 1:
        w.setModel(args[0])
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    w.show()
    sys.exit(app.exec_())      
        

if __name__ == "__main__":
    taurusTrend2DMain()    
