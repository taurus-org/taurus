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

"""This module provides a set of basic Taurus widgets based on QLabel"""

__all__ = ["TaurusStateLabel", "TaurusValueLabel"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

import taurus.core
from taurus.qt.qtgui.util import QT_ATTRIBUTE_QUALITY_PALETTE, QT_DEVICE_STATE_PALETTE
from taurus.qt.qtgui.base import TaurusBaseWidget

 
class TaurusValueLabel(Qt.QLabel, TaurusBaseWidget):
    """
    A widget that represents the read value of an attribute.

    .. deprecated::
        Use :class:`taurus.qt.qtgui.display.TaurusLabel` instead.

    The following features are present:
    
        * The background color changes with the attribute quality according to the :ref:`color-guide`
        * The attribute value is displayed according to the attribute format
        * Supports all data types and formats (although it is designed mainly for SCALAR format)
        * A tooltip is automatically generated displaying additional attribute information
        * If the size of the widget is too small to display the entire value, the text changes to
          a symbolic link that opens a dialog with the attribute value when clicked
    
    This widget emits the following signals (excluding signals of the super classes):
    
    **modelChanged**:
        - *Signature*: ``modelChanged(const QString &) -> None``
        - *Description*: the signal is emmited when the model for this widget 
          changes either by direct model manipulation, change of the useParentModel 
          and change of the parent model (if useParentModel is set to True)
    
    Example::
    
        import sys
        from taurus.qt import Qt
        from taurus.qt.qtgui.display import TaurusValueLabel

        app = Qt.QApplication(sys.argv)

        w = TaurusValueLabel()
        w.model = 'sys/taurustest/1/position'

        w.setVisible(True)
        sys.exit(app.exec_())

    .. image:: /_static/label01.png
        :align: center

    """
    
    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent = None, designMode = False, background = 'quality'):
        name = self.__class__.__name__

        self.call__init__wo_kw(Qt.QLabel, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Preferred)
        self.setTextInteractionFlags (Qt.Qt.TextSelectableByMouse|Qt.Qt.LinksAccessibleByMouse)
        self.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self._charWidth = self.font().pointSize()
        self._showState = False
        self._showValueStateAsBackground = False
        self.defineBackground(background)
        self.connect(self, Qt.SIGNAL("linkActivated (const QString&)"), self.showFullValueDialog)
        self._text = ''
    
    def defineBackground(self, background):
        background = str(background).lower()
        self.setShowQuality(background == 'quality')
        self.setShowState(background == 'state')
        self.setShowValueStateAsBackground(background == 'value_state')
        self.__background = background;
        
    # The minimum size of the widget (a limit for the user)
    def minimumSizeHint(self):
        return Qt.QSize(20, 20)
        
#    # The default size of the widget
#    def sizeHint(self):
#        return Qt.QSize(60, 22)
#        #return Qt.QSize(Qt.QLabel.sizeHint(self).width(), 24)
    
    def _stateListener(self, s, t, v):
        # this method exists to force state to have at least one listener
        # when showState is set to True 
        pass
    
    @Qt.pyqtSignature("setShowState(bool)")
    def setShowState(self, showState):
        '''Whether or not to show the device state as background color.
        Note: obviously, setShowState(True) forces setShowQuality(False) !'''
        if showState == self._showState:
            return
        if showState and self.getShowQuality():
            self.setShowQuality(False)
        self._showState = showState
        
        modelObj = self.getModelObj()
        if modelObj is not None:
            s = modelObj.getParent().getStateObj()
            if showState:
                s.addListener(self._stateListener)
            else:
                s.removeListener(self._stateListener)
            
        self.updateStyle()
    
    def getShowState(self):
        """either or not to show the state as a background color"""
        return self._showState

    def resetShowState(self):
        self.setShowState(False)
    
    @Qt.pyqtSignature("setShowValueStateAsBackground(bool)")
    def setShowValueStateAsBackground(self, showState):
        '''Whether or not to show the value as background color.
        The attribute value must be a state!
        Note: obviously, forces setShowState(False) and setShowQuality(False)
    '''
        if showState:
            self.setShowQuality(False)
            self.setShowState(False)
        self._showValueStateAsBackground = showState

    def getShowValueStateAsBackground(self):
        """either or not to show the state as a background color"""
        return self._showValueStateAsBackground

    def resetShowValueStateAsBackground(self):
        self.setShowValueStateAsBackground(False)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        return taurus.core.taurusattribute.TaurusAttribute

    def isReadOnly(self):
        return True
    
    def updateStyle(self, extra=''):
        if self.getShowQuality():
            quality = getattr(self.getModelValueObj(), 'quality', None)
            ss = QT_ATTRIBUTE_QUALITY_PALETTE.qtStyleSheet(quality)
        elif self.getShowState():
            try: state = self.getModelObj().getParent().getState()
            except Exception:
                state = None
            ss = QT_DEVICE_STATE_PALETTE.qtStyleSheet(state)
        elif self.getShowValueStateAsBackground():
            value = getattr(self.getModelValueObj(), 'value', None)
            ss = QT_DEVICE_STATE_PALETTE.qtStyleSheet(value)
        else:
            ss = "background-color: transparent; color:black;"
        ss = """TaurusValueLabel {
            border-style: outset;
            border-width: 2px;
            border-color: rgba(255,255,255,128);
            %s %s}""" % (ss, extra)
        self.setStyleSheet(ss)
        TaurusBaseWidget.updateStyle(self)

    def validateDisplay(self):
        '''Checks that the display fits in the widget and sets it to "..." if it does not'''
        trimmedtext = "<a href='...'>...</a>"
        self._text = self.text()
        if Qt.QLabel.sizeHint(self).width() > self.size().width():
            self.setToolTip(self.getFormatedToolTip(showValue=True) )
            self._setText(trimmedtext)
            self.updateStyle()
            return False
        return True
    
    def getFormatedToolTip(self,cache=True, showValue=False):
        ret = TaurusBaseWidget.getFormatedToolTip(self,cache=cache)
        if showValue:
            ret = u"<p><b>Value:</b> %s</p><hr>%s"%(self._text, ret)
        return Qt.QString(ret)
    
    def showFullValueDialog(self,*args):
        Qt.QMessageBox.about(self,  "Full text", self._text)
    
    def handleEvent(self, evt_src, evt_type, evt_value):
        '''reimplemented to check that the display fits the size each time that the value changes'''
        TaurusBaseWidget.handleEvent(self, evt_src, evt_type, evt_value)
        self.validateDisplay()
    
    def resizeEvent(self,event):
        #We recheck the Display every time we resize
        self.updateStyle()
        self.setText(self._text) #We set the original (untrimmed) text to force a validation from scratch.
        self.validateDisplay()
        Qt.QLabel.resizeEvent(self,event)
    
    def setModel(self, m):
        oldModelObj = self.getModelObj()

        TaurusBaseWidget.setModel(self, m)

        newModelObj = self.getModelObj()
        if self.getShowState():
            if oldModelObj is not None:
                s = oldModelObj.getParent().getStateObj()
                s.removeListener(self._stateListener)
            if newModelObj is not None:
                s = newModelObj.getParent().getStateObj()
                s.addListener(self._stateListener)
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.display'
#        ret['group'] = 'Taurus Widgets [Old]'
#        ret['icon'] = ":/designer/label.png"
#        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

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
    #:     * :meth:`TaurusValueLabel.setModel`
    #:     * :meth:`TaurusBaseWidget.resetModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel,setModel,
                            TaurusBaseWidget.resetModel)
    
    #: This property holds whether or not this widget should search in the 
    #: widget hierarchy for a model prefix in a parent widget.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getUseParentModel`
    #:     * :meth:`TaurusBaseWidget.setUseParentModel`
    #:     * :meth:`TaurusBaseWidget.resetUseParentModel`
    #:
    #: .. seealso:: :ref:`model-concept`
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel, 
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)

    #: This property holds whether or not this widget should fill the background
    #: with the attribute quality/device state according to the 
    #: :ref:`color-guide`
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getShowQuality`
    #:     * :meth:`TaurusBaseWidget.setShowQuality`
    #:     * :meth:`TaurusBaseWidget.resetShowQuality`
    #:
    #: .. seealso:: :ref:`color-guide`
    showQuality = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowQuality,
                                  TaurusBaseWidget.setShowQuality,
                                  TaurusBaseWidget.resetShowQuality)
    
    #: This property holds whether or not this widget should display the current
    #: value of the model as text. Setting this to False is useful when you just
    #: want to represent the quality/state as background color in a small space
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getShowText`
    #:     * :meth:`TaurusBaseWidget.setShowText`
    #:     * :meth:`TaurusBaseWidget.resetShowText`
    showText = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowText,
                               TaurusBaseWidget.setShowText, 
                               TaurusBaseWidget.resetShowText)
    
    #: This property holds the contents of a the popup menu as an XML string.
    #:
    #: **Access functions:**
    #:
    #:     * :meth:`TaurusBaseWidget.getTaurusPopupMenu`
    #:     * :meth:`TaurusBaseWidget.setTaurusPopupMenu`
    #:     * :meth:`TaurusBaseWidget.resetTaurusPopupMenu`
    #:
    #: .. seealso:: :ref:`popupmenu-tutorial`
    taurusPopupMenu = Qt.pyqtProperty("QString", TaurusBaseWidget.getTaurusPopupMenu,
                                   TaurusBaseWidget.setTaurusPopupMenu,
                                   TaurusBaseWidget.resetTaurusPopupMenu)


class TaurusStateLabel(TaurusValueLabel):
    '''
    .. deprecated::
        Use :class:`taurus.qt.qtgui.display.TaurusLabel` instead.
    '''
    def __init__(self, parent = None, designMode = False):
        self.call__init__(TaurusValueLabel, parent=parent, designMode=designMode, background = 'value_state')
        self.setAlignment(Qt.Qt.AlignCenter)
    
    def getFormatedToolTip(self, cache=True, **notused):
        """ The tooltip should refer to the device and not the state attribute.
            That is why this method is being rewritten
        """
        if self.modelObj is None:
            return Qt.QString.fromLatin1(self.getNoneValue())
        parent = self.modelObj.getParentObj()
        if parent is None:
            return Qt.QString.fromLatin1(self.getNoneValue())
        return Qt.QString.fromLatin1(self.toolTipObjToStr( parent.getDisplayDescrObj() ))
    
    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self,model):
        """ Added to allow setModel(device_name); assuming that State attribute
            is the desired model. To inherit the parent model but with a non
            'State' named attribute, use slash: '/TheAttribute'
        """
        try:
            if str(model).count('/')<3 and str(model)[0]!='/':
                model = str(model)+'/State'
        except Exception:
            pass
        TaurusBaseWidget.setModel(self,model)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusValueLabel.getQtDesignerPluginInfo()
#        ret['icon'] = ":/designer/state.png"
#        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, setModel,
                            TaurusBaseWidget.resetModel)

def main():
    """hello"""
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full_attribute_name(s)>"
        app = Application(sys.argv, cmd_line_parser=parser)
        
    args = app.get_command_line_args()

    if len(args) > 0:
        models = map(str.lower, args)
    else:
        models = [ 'sys/tg_test/1/%s' % a for a in ('state', 'status', 'double_scalar' ) ]

    w = Qt.QWidget()
    layout = Qt.QGridLayout()
    w.setLayout(layout)
    for model in models:
        if model.endswith('state'):
            label = TaurusStateLabel()
        else:
            label = TaurusValueLabel()
        label.model = model
        layout.addWidget(label)
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()

    