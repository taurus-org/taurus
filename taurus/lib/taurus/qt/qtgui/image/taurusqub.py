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

"""taurus wrapping of Qub image visualization widget"""

import weakref

from taurus.qt import Qt

from Qub.Widget.DataDisplay.QubDataImageDisplay import QubDataImageDisplay
from Qub.Widget.QubActionSet import QubToolbarToggleButtonAction
from Qub.Widget.QubActionSet import QubOpenDialogAction

from taurus.qt.qtgui.base import TaurusBaseWidget
import taurus

try:
    import EdfFile
except ImportError:
    EdfFile = None

class _EDFFileSavePlug:
    def setData(self,data) :
        if data is not None:
            self._data = weakref.ref(data)
        else:
            self._data = None
            
class TaurusQubDataImageDisplay(QubDataImageDisplay, TaurusBaseWidget):
    
    def __init__(self, parent=None, **kwargs):
        designMode = kwargs.get('designMode', False)
        kwargs['forcePopupSubWindow'] = True
        kwargs['parent'] = parent
        self.call__init__(QubDataImageDisplay, **kwargs)
        name = self.__class__.__name__
        self._image_attr_name = ''
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self.statusBar().setSizeGripEnabled(False)
        self.setModifiableByUser(True) #to allow drop of models
        self.__addActions()
        
    def __addActions(self):
        updateAction = QubToolbarToggleButtonAction(name = 'update', iconName = 'update',
                                                    initState = True, group='image',
                                                    tooltip='Start/Stop image refresh')
        Qt.QObject.connect(updateAction, Qt.SIGNAL('StateChanged'), self.__setRefresh)
        self.addAction(updateAction)
        # a bug in Qub forces to set the state after adding the action
        updateAction.setState(True)
        self._updateAction = updateAction
        
        if EdfFile:
            saveAction = QubOpenDialogAction(name='save edf', iconName='save',
                                             label='Save data', group='admin',
                                             tooltip='Save image data in EDF format')
            
            saveDialog = Qt.QFileDialog(self, 'Save image as EDF')
            saveDialog.setAcceptMode(Qt.QFileDialog.AcceptSave)
            saveDialog.setDefaultSuffix('edf')
            nameFilters = list(saveDialog.nameFilters())
            nameFilters.insert(0, 'EDF Files (*.edf)')
            saveDialog.setNameFilters(nameFilters)
            Qt.QObject.connect(saveDialog, Qt.SIGNAL('fileSelected(const QString &)'),
                               self.__saveEDF)
            Qt.QObject.connect(saveDialog, Qt.SIGNAL('filesSelected(const QStringList &)'),
                               self.__saveEDFs)
            saveAction.setDialog(saveDialog)
            self._saveDataAction = saveAction
            
            plug = _EDFFileSavePlug()
            self.addDataAction(saveAction, plug)
            self._saveEDFPlug = plug
        
    def __saveEDF(self, fileSelected):
        if not fileSelected: return
        fileSelected = str(fileSelected)
        data = self._saveEDFPlug._data()
        edf_file = EdfFile.EdfFile(fileSelected)
        edf_file.WriteImage({}, data)

    def __saveEDFs(self, filesSelected):
        nb = len(filesSelected)
        if nb == 0: return
        fname = filesSelected[0]
        if nb > 1:
            print "WARNING: Multiple files selected. The image will be saved as:", fname
        self.__saveEDF(fname)

    def __setRefresh(self, onOff):
        self._refreshEnabled = onOff
    
    def _save_dialog_new(self,openDialogAction,aQubGraphicsView):
        QubDataImageDisplay._save_dialog_new(self,openDialogAction,aQubGraphicsView)
    
    def isReadOnly(self):
        return True
    
    def getModelClass(self):
        return taurus.core.taurusdevice.TaurusDevice
    
    def handleEvent(self, evt_src, evt_type, evt_value):
        if self._updateAction.state():
            if evt_type in (taurus.core.taurusbasetypes.TaurusEventType.Change, taurus.core.taurusbasetypes.TaurusEventType.Periodic):
                data = self.getModelObj().getImageData()
                if data:
                    data = data[self._image_attr_name][1]
                    try:
                        dim_x, dim_y = data.dim_x, data.dim_y #this is tango-centric. dim_x does not exist in TaurusConfiguration
                    except AttributeError:
                        try:
                            dim_x,dim_y = data.value.shape
                        except AttributeError:
                            dim_x,dim_y = numpy.array(data.value).shape
                    self.setData(data.value)
                    self.setInfo({
                        'name'     : data.name,
                        'width'    : dim_x, 
                        'height'   : dim_y, 
                        'quality'  : data.quality,
                        'type'     : data.type,
                        'timestamp': data.time
                    })

    def sizeHint(self):
        return Qt.QSize(640, 480)
    
    def setModel(self, model):
        dev_name, self._image_attr_name = model.rsplit('/', 1)
        obj = self.getTaurusFactory().getDevice(dev_name)
        if obj is not None:
            obj.addImageAttrName(self._image_attr_name)        
        TaurusBaseWidget.setModel(self, dev_name)
        self.setWindowTitle(self.getModel())
    
    def getModel(self):
        return '%s/%s' % (TaurusBaseWidget.getModel(self), self._image_attr_name)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.image'
        ret['group'] = 'Taurus Display'
        ret['icon'] = ":/designer/camera_photo.png"
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, setModel,
                            TaurusBaseWidget.resetModel)
    
    useParentModel = Qt.pyqtProperty("bool",
                                     TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)

def main():
    import sys
    import taurus.core.tango.img
    taurus.core.tango.img.registerExtensions()

    app = Qt.QApplication(sys.argv)
    models=sys.argv[1:]
    panel = Qt.QWidget()
    l = Qt.QHBoxLayout()
    panel.setLayout(l)
    if not models:
        from taurus.qt.qtgui.panel import TaurusModelChooser
        models, ok = TaurusModelChooser.modelChooserDlg(panel, [taurus.core.taurusbasetypes.TaurusElementType.Attribute])
        if not ok:
            models = []
    for model in models:
        w = TaurusQubDataImageDisplay()
        w.setModel(model)
        l.addWidget(w)
  
    panel.setVisible(True)
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
