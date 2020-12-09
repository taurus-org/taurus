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
###########################################################################

"""
paneldescriptionwizard.py:
"""

from __future__ import print_function

from taurus.external.qt import Qt
import sys
import weakref
from taurus.qt.qtgui.taurusgui.utils import PanelDescription
from taurus.qt.qtgui.icon import getCachedPixmap
from taurus.qt.qtgui.input import GraphicalChoiceWidget
from taurus.qt.qtgui.base import TaurusBaseComponent, TaurusBaseWidget
from taurus.qt.qtcore.communication import SharedDataManager
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE
from taurus.qt.qtgui.util import TaurusWidgetFactory
from taurus.core.util.log import Logger
import inspect
import copy


__all__ = ["PanelDescriptionWizard"]


class ExpertWidgetChooserDlg(Qt.QDialog):
    CHOOSE_TYPE_TXT = '(choose type)'

    memberSelected = Qt.pyqtSignal(dict)

    def __init__(self, parent=None):
        Qt.QDialog.__init__(self, parent)

        self.setWindowTitle('Advanced panel type selection')

        layout1 = Qt.QHBoxLayout()
        layout2 = Qt.QHBoxLayout()
        layout = Qt.QVBoxLayout()

        # subwidgets
        self.moduleNameLE = Qt.QLineEdit()
        self.moduleNameLE.setValidator(Qt.QRegExpValidator(
            Qt.QRegExp(r'[a-zA-Z0-9\.\_]*'), self.moduleNameLE))
        self.membersCB = Qt.QComboBox()
        self.dlgBox = Qt.QDialogButtonBox(
            Qt.QDialogButtonBox.Ok | Qt.QDialogButtonBox.Cancel)
        self.dlgBox.button(Qt.QDialogButtonBox.Ok).setEnabled(False)

        # layout
        layout.addWidget(
            Qt.QLabel('Select the module and widget to use in the panel:'))
        layout1.addWidget(Qt.QLabel('Module'))
        layout1.addWidget(self.moduleNameLE)
        layout2.addWidget(Qt.QLabel('Class (or widget)'))
        layout2.addWidget(self.membersCB)
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addWidget(self.dlgBox)
        self.setLayout(layout)

        # connections
        self.moduleNameLE.editingFinished.connect(self.onModuleSelected)
        self.moduleNameLE.textEdited.connect(self.onModuleEdited)
        self.membersCB.activated.connect(self.onMemberSelected)
        self.dlgBox.accepted.connect(self.accept)
        self.dlgBox.rejected.connect(self.reject)

    def onModuleEdited(self):
        self.dlgBox.button(Qt.QDialogButtonBox.Ok).setEnabled(False)
        self.module = None
        self.moduleNameLE.setStyleSheet('')
        self.membersCB.clear()

    def onModuleSelected(self):
        modulename = str(self.moduleNameLE.text())
        try:
            __import__(modulename)
            # We use this because __import__('x.y') returns x instead of y !!
            self.module = sys.modules[modulename]
            self.moduleNameLE.setStyleSheet('QLineEdit {color: green}')
        except Exception as e:
            Logger().debug(repr(e))
            self.moduleNameLE.setStyleSheet('QLineEdit {color: red}')
            return
        # inspect the module to find the members we want (classes or widgets
        # inheriting from QWidget)
        members = inspect.getmembers(self.module)
        classnames = sorted(
            [n for n, m in members if inspect.isclass(m) and issubclass(m, Qt.QWidget)])
        widgetnames = sorted(
            [n for n, m in members if isinstance(m, Qt.QWidget)])
        self.membersCB.clear()
        self.membersCB.addItem(self.CHOOSE_TYPE_TXT)
        self.membersCB.addItems(classnames)
        if classnames and widgetnames:
            self.membersCB.InsertSeparator(self.membersCB.count())
        self.membersCB.addItems(classnames)

    def onMemberSelected(self, text):
        if str(text) == self.CHOOSE_TYPE_TXT:
            return
        self.dlgBox.button(Qt.QDialogButtonBox.Ok).setEnabled(True)
        # emit a signal with a dictionary that can be used to initialize
        self.memberSelected.emit(self.getMemberDescription())

    def getMemberDescription(self):
        try:
            membername = str(self.membersCB.currentText())
            member = getattr(self.module, membername, None)
            result = {'modulename': self.module.__name__}
        except Exception as e:
            Logger().debug('Cannot get member description: %s', repr(e))
            return None
        if inspect.isclass(member):
            result['classname'] = membername
        else:
            result['widgetname'] = membername
        return result

    @staticmethod
    def getDialog():
        dlg = ExpertWidgetChooserDlg()
        dlg.exec_()
        return dlg.getMemberDescription(), (dlg.result() == dlg.Accepted)


class BlackListValidator(Qt.QValidator):

    stateChanged = Qt.pyqtSignal(int, int)

    def __init__(self, blackList=None, parent=None):
        Qt.QValidator.__init__(self, parent)
        if blackList is None:
            blackList = []
        self.blackList = blackList
        self._previousState = None
        # check the signature of the validate method (it changed from old to new versions)
        # see
        # :http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/python_v3.html#qvalidator
        dummyValidator = Qt.QDoubleValidator(None)
        self._oldMode = len(dummyValidator.validate('', 0)) < 3

    def validate(self, input, pos):
        if str(input) in self.blackList:
            state = self.Intermediate
        else:
            state = self.Acceptable
        if state != self._previousState:
            self.stateChanged.emit(state, self._previousState)
            self._previousState = state
        if self._oldMode:  # for backwards compatibility with older versions of PyQt
            return state, pos
        else:
            return state, input, pos

# class NamePage(Qt.QWizardPage):
#
#    def __init__(self, parent = None):
#        Qt.QWizardPage.__init__(self, parent)
#
#        self.setTitle('Name')
#        self.setSubTitle('Choose a name for the new panel (it must not exist already)')
#
#        #contents
#        self.nameLE = Qt.QLineEdit()
#        self.registerField("panelname*",self.nameLE)
#        self.diagnosticLabel = Qt.QLabel('')
#
#        layout = Qt.QHBoxLayout()
#        layout.addWidget(Qt.QLabel("Panel Name"))
#        layout.addWidget(self.nameLE)
#        layout.addWidget(self.diagnosticLabel)
#        self.setLayout(layout)
#
#    def initializePage(self):
#        gui = self.wizard().getGui()
#        if hasattr(gui, 'getPanelNames'):
#            pnames = gui.getPanelNames()
#            v = BlackListValidator(blackList=pnames, parent=self.nameLE)
#            self.nameLE.setValidator(v)
#            self.connect(v, Qt.SIGNAL('stateChanged'),self._onValidatorStateChanged)
#
#    def _onValidatorStateChanged(self, state, previous):
#        if state == Qt.QValidator.Acceptable:
#            self.diagnosticLabel.setText('')
#        else:
#            self.diagnosticLabel.setText('<b>(Name already exists)</b>')
#


class WidgetPage(Qt.QWizardPage, TaurusBaseWidget):
    OTHER_TXT = 'Other...'
    defaultCandidates = ['TaurusForm', 'TaurusTrend', 'TaurusPlot',
                         'TaurusImageDialog', 'TaurusTrend2DDialog', 'TaurusNeXusBrowser',
                         'TaurusDbTreeWidget', 'TaurusArrayEditor',
                         'SardanaEditor', 'TaurusJDrawSynopticsView',
                         'TaurusDevicePanel']

    def __init__(self, parent=None, designMode=False, extraWidgets=None):
        Qt.QWizardPage.__init__(self, parent)
        TaurusBaseWidget.__init__(self, 'WidgetPage')
        if extraWidgets:
            customWidgets, customWidgetScreenshots = list(zip(*extraWidgets))
            pixmaps = {}
            for k, s in extraWidgets:
                if s is None:
                    pixmaps[k] = None
                else:
                    try:
                        pixmaps[k] = getCachedPixmap(s)
                        if pixmaps[k].isNull():
                            raise Exception('Invalid Pixmap')
                    except:
                        self.warning('Could not create pixmap from %s' % s)
                        pixmaps[k] = None

        else:
            customWidgets, customWidgetScreenshots = [], []
            pixmaps = {}
        self.setFinalPage(True)
        self.setTitle('Panel type')
        self.setSubTitle('Choose a name and type for the new panel')
        self.setButtonText(Qt.QWizard.NextButton, 'Advanced settings...')

        self.widgetDescription = {'widgetname': None,
                                  'modulename': None, 'classname': None}

        # name part
        self.nameLE = Qt.QLineEdit()
        self.registerField("panelname*", self.nameLE)
        self.diagnosticLabel = Qt.QLabel('')
        nameLayout = Qt.QHBoxLayout()
        nameLayout.addWidget(Qt.QLabel("Panel Name"))
        nameLayout.addWidget(self.nameLE)
        nameLayout.addWidget(self.diagnosticLabel)

        # contents
        available = TaurusWidgetFactory().getWidgetClassNames()
        choices = []
        row = []
        for cname in self.defaultCandidates + list(customWidgets):
            if cname in available or '.' in cname:
                row.append(cname)
                if cname not in pixmaps:
                    pixmaps[cname] = getCachedPixmap('snapshot:%s.png' % cname)
                if len(row) == 3:
                    choices.append(row)
                    row = []
        row.append(self.OTHER_TXT)
        choices.append(row)

        # defaultPixmap=getPixmap('logos:taurus.png')
        self.choiceWidget = GraphicalChoiceWidget(
            choices=choices, pixmaps=pixmaps)

        self.widgetTypeLB = Qt.QLabel("<b>Widget Type:</b>")

        self.choiceWidget.choiceMade.connect(self.onChoiceMade)

        layout = Qt.QVBoxLayout()
        layout.addLayout(nameLayout)
        layout.addWidget(self.choiceWidget)
        layout.addWidget(self.widgetTypeLB)
        self.setLayout(layout)

    def initializePage(self):
        gui = self.wizard().getGui()
        if hasattr(gui, 'getPanelNames'):
            pnames = gui.getPanelNames()
            v = BlackListValidator(blackList=pnames, parent=self.nameLE)
            self.nameLE.setValidator(v)
            v.stateChanged.connect(self._onValidatorStateChanged)

    def validatePage(self):
        paneldesc = self.wizard().getPanelDescription()
        if paneldesc is None:
            Qt.QMessageBox.information(self, 'You must choose a panel type',
                                       'Choose a panel type by clicking on one of the proposed types')
            return False
        try:
            w = paneldesc.getWidget()
            if not isinstance(w, Qt.QWidget):
                raise ValueError
            # set the name now because it might have changed since the
            # PanelDescription was created
            paneldesc.name = self.field('panelname')
            # allow the wizard to proceed
            return True
        except Exception as e:
            Qt.QMessageBox.warning(
                self, 'Invalid panel', 'The requested panel cannot be created. \nReason:\n%s' % repr(e))
            return False

    def _onValidatorStateChanged(self, state, previous):
        if state == Qt.QValidator.Acceptable:
            self.diagnosticLabel.setText('')
        else:
            self.diagnosticLabel.setText('<b>(Name already exists)</b>')

    def onChoiceMade(self, choice):
        if choice == self.OTHER_TXT:
            wdesc, ok = ExpertWidgetChooserDlg.getDialog()
            if ok:
                self.widgetDescription.update(wdesc)
            else:
                return
        else:
            self.widgetDescription['classname'] = choice

        # the name will be set in self.validatePage
        self.wizard().setPanelDescription(PanelDescription('', **self.widgetDescription))
        paneltype = str(self.widgetDescription[
                        'widgetname'] or self.widgetDescription['classname'])
        self.widgetTypeLB.setText("<b>Widget Type:</b> %s" % paneltype)


class AdvSettingsPage(Qt.QWizardPage):

    def __init__(self, parent=None):
        Qt.QWizardPage.__init__(self, parent)

        self.setTitle('Advanced settings')
        self.setSubTitle('Fine-tune the behavior of the panel by assigning a Taurus model ' +
                         'and/or defining the panel interactions with other parts of the GUI')
        self.setFinalPage(True)
        self.models = []

        layout = Qt.QVBoxLayout()

        #----model---------------
        # subwidgets
        self.modelGB = Qt.QGroupBox('Model')
        self.modelGB.setToolTip(
            'Choose a Taurus model to be assigned to the panel')
        # @todo: add a regexp validator (it should return valid on TAURUS_MODEL_LIST_MIME_TYPE)
        self.modelLE = Qt.QLineEdit()
        self.modelChooserBT = Qt.QToolButton()
        self.modelChooserBT.setIcon(Qt.QIcon('designer:devs_tree.png'))
#        self.modelChooser = TaurusModelChooser()

        # connections
        self.modelChooserBT.clicked.connect(self.showModelChooser)
        self.modelLE.editingFinished.connect(self.onModelEdited)

        # layout
        layout1 = Qt.QHBoxLayout()
        layout1.addWidget(self.modelLE)
        layout1.addWidget(self.modelChooserBT)
        self.modelGB.setLayout(layout1)

        #----communications------
        # subwidgets
        self.commGB = Qt.QGroupBox('Communication')
        self.commGB.setToolTip(
            'Define how the panel communicates with other panels and the GUI')
        self.commLV = Qt.QTableView()
        self.commModel = CommTableModel()
        self.commLV.setModel(self.commModel)
        self.commLV.setEditTriggers(self.commLV.AllEditTriggers)
        self.selectedComm = self.commLV.selectionModel().currentIndex()
        self.addBT = Qt.QToolButton()
        self.addBT.setIcon(Qt.QIcon.fromTheme('list-add'))
        self.removeBT = Qt.QToolButton()
        self.removeBT.setIcon(Qt.QIcon.fromTheme('list-remove'))
        self.removeBT.setEnabled(False)

        # layout
        layout2 = Qt.QVBoxLayout()
        layout3 = Qt.QHBoxLayout()
        layout2.addWidget(self.commLV)
        layout3.addWidget(self.addBT)
        layout3.addWidget(self.removeBT)
        layout2.addLayout(layout3)
        self.commGB.setLayout(layout2)

        # connections
        self.addBT.clicked.connect(self.commModel.insertRows)
        self.removeBT.clicked.connect(self.onRemoveRows)
        self.commLV.selectionModel().currentRowChanged.connect(self.onCommRowSelectionChanged)

        layout.addWidget(self.modelGB)
        layout.addWidget(self.commGB)
        self.setLayout(layout)

    def initializePage(self):
        try:
            widget = self.wizard().getPanelDescription().getWidget()
        except Exception as e:
            Logger().debug(repr(e))
            widget = None
        # prevent the user from changing the model if it was already set
        if isinstance(widget, TaurusBaseComponent) and widget.getModelName() != '':
            self.modelLE.setText("(already set by the chosen widget)")
            self.modelGB.setEnabled(False)
        # try to get the SDM as if we were in a TaurusGui app
        try:
            if isinstance(Qt.qApp.SDM, SharedDataManager):
                sdm = Qt.qApp.SDM
        except Exception as e:
            Logger().debug(repr(e))
            sdm = None
        #@todo set selection filter in modelChooser based on the widget's modelclass
        self.itemDelegate = CommItemDelegate(widget=widget, sdm=sdm)
        self.commLV.setItemDelegate(self.itemDelegate)

    def showModelChooser(self):
        from taurus.qt.qtgui.panel import TaurusModelChooser
        models, ok = TaurusModelChooser.modelChooserDlg(
            parent=self, asMimeData=True)
        if not ok:
            return
        self.models = str(models.data(TAURUS_MODEL_LIST_MIME_TYPE))
        self.modelLE.setText(models.text())

    def onModelEdited(self):
        self.models = str(self.modelLE.text())

    def onRemoveRows(self):
        if self.selectedComm.isValid():
            self.commModel.removeRows(self.selectedComm.row())

    def onCommRowSelectionChanged(self, current, previous):
        self.selectedComm = current
        enable = (current.isValid() and 0 <= current.row()
                  < self.commModel.rowCount())
        self.removeBT.setEnabled(enable)

    def validatePage(self):
        desc = self.wizard().getPanelDescription()
        # model
        desc.model = self.models
        # communications
        for uid, slotname, signalname in self.commModel.dumpData():
            if slotname:
                desc.sharedDataRead[uid] = slotname
            if signalname:
                desc.sharedDataWrite[uid] = signalname
        self.wizard().setPanelDescription(desc)
        return True


class CommTableModel(Qt.QAbstractTableModel):
    NUMCOLS = 3
    UID, R, W = list(range(NUMCOLS))

    dataChanged = Qt.pyqtSignal(int, int)

    def __init__(self, parent=None):
        Qt.QAbstractTableModel.__init__(self, parent)
        self.__table = []

    def dumpData(self):
        return copy.deepcopy(self.__table)

    def rowCount(self, index=Qt.QModelIndex()):
        return len(self.__table)

    def columnCount(self, index=Qt.QModelIndex()):
        return self.NUMCOLS

    def headerData(self, section, orientation, role=Qt.Qt.DisplayRole):
        if role == Qt.Qt.TextAlignmentRole:
            if orientation == Qt.Qt.Horizontal:
                return int(Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter)
            return int(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter)
        if role != Qt.Qt.DisplayRole:
            return None
        # So this is DisplayRole...
        if orientation == Qt.Qt.Horizontal:
            if section == self.UID:
                return "Data UID"
            elif section == self.R:
                return "Reader (slot)"
            elif section == self.W:
                return "Writer (signal)"
            return None
        else:
            return str('%i' % (section + 1))

    def data(self, index, role=Qt.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        row = index.row()
        column = index.column()
        # Display Role
        if role == Qt.Qt.DisplayRole:
            text = self.__table[row][column]
            if text == '':
                if column == self.UID:
                    text = '(enter UID)'
                else:
                    text = '(not registered)'
            return str(text)
        return None

    def flags(self, index):
        return (Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsDragEnabled | Qt.Qt.ItemIsDropEnabled | Qt.Qt.ItemIsSelectable)

    def setData(self, index, value=None, role=Qt.Qt.EditRole):
        if index.isValid() and (0 <= index.row() < self.rowCount()):
            row = index.row()
            column = index.column()
            self.__table[row][column] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position=None, rows=1, parentindex=None):
        if position is None:
            position = self.rowCount()
        if parentindex is None:
            parentindex = Qt.QModelIndex()
        self.beginInsertRows(parentindex, position, position + rows - 1)
        slice = [self.rowModel() for i in range(rows)]
        self.__table = self.__table[:position] + \
            slice + self.__table[position:]
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, parentindex=None):
        if parentindex is None:
            parentindex = Qt.QModelIndex()
        self.beginResetModel()
        self.beginRemoveRows(parentindex, position, position + rows - 1)
        self.__table = self.__table[:position] + self.__table[position + rows:]
        self.endRemoveRows()
        self.endResetModel()
        return True

    @staticmethod
    def rowModel(uid='', slot='', signal=''):
        return [uid, slot, signal]


class CommItemDelegate(Qt.QStyledItemDelegate):
    NUMCOLS = 3
    UID, R, W = list(range(NUMCOLS))

    def __init__(self, parent=None, widget=None, sdm=None):
        super(CommItemDelegate, self).__init__(parent)
        if widget is not None:
            widget = weakref.proxy(widget)
        self._widget = widget
        if sdm is not None:
            sdm = weakref.proxy(sdm)
        self._sdm = sdm

    def createEditor(self, parent, option, index):
        column = index.column()
        combobox = Qt.QComboBox(parent)
        combobox.setEditable(True)
        if column == self.UID and self._sdm is not None:
            combobox.addItems(self._sdm.activeDataUIDs())
        elif column == self.R and self._widget is not None:
            slotnames = [n for n, o in inspect.getmembers(
                self._widget, inspect.ismethod) if not n.startswith('_')]
            combobox.addItems(slotnames)
#        elif column==self.W:
#            if self._widget is not None:
#                #@todo: if/when support for old signals style (Qt<4.6) is dropped, we can inspect the methods in search of (new style) signals
#                combobox.addItems(['(Not registered)'])
        return combobox

    def setEditorData(self, editor, index):
        editor.setEditText('')

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())


class PanelDescriptionWizard(Qt.QWizard, TaurusBaseWidget):
    '''A wizard-style dialog for configuring a new TaurusGui panel.
    Use :meth:`getDialog` for launching it
    '''

    def __init__(self, parent=None, designMode=False, gui=None, extraWidgets=None):
        Qt.QWizard.__init__(self, parent)
        name = "PanelDescriptionWizard"
        TaurusBaseWidget.__init__(self, name)
        self._panelDescription = None
        if gui is None:
            gui = parent
        if gui is not None:
            self._gui = weakref.proxy(gui)
        ###self.setOption(self.HaveFinishButtonOnEarlyPages, True)
        #self.namePG = NamePage()
        self.widgetPG = WidgetPage(extraWidgets=extraWidgets)
        self.advSettingsPG = AdvSettingsPage()

        # self.addPage(self.namePG)
        self.addPage(self.widgetPG)
        self.addPage(self.advSettingsPG)

    def getGui(self):
        '''returns a reference to the GUI to which the dialog is associated'''
        return self._gui

    def getPanelDescription(self):
        '''Returns the panel description with the choices made so far

        :return: (PanelDescription) the panel description
        '''
        return self._panelDescription

    def setPanelDescription(self, desc):
        '''Sets the Panel description

        :param desc: (PanelDescription)
        '''
        self._panelDescription = desc

    @staticmethod
    def getDialog(parent, extraWidgets=None):
        """Static method for launching a new Dialog.

        :param parent: parent widget for the new dialog

        :return: (tuple<PanelDescription,bool>) tuple of a description object
                 and a state flag. The state is True if the dialog was accepted
                 and False otherwise
        """
        dlg = PanelDescriptionWizard(parent, extraWidgets=extraWidgets)
        dlg.exec_()
        return dlg.getPanelDescription(), (dlg.result() == dlg.Accepted)


#------------------------------------------------------------------------------

def test():
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    form = PanelDescriptionWizard()

    def kk(d):
        print(d)
    Qt.qApp.SDM = SharedDataManager(form)
    Qt.qApp.SDM.connectReader('111111', kk)
    Qt.qApp.SDM.connectWriter('222222', form, 'thisisasignalname')

    form.show()
    sys.exit(app.exec_())


def test2():
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    print(ExpertWidgetChooserDlg.getDialog())
    sys.exit()


def main():
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    from taurus.qt.qtgui.container import TaurusMainWindow
    form = Qt.QMainWindow()

    def kk(d):
        print(d)
    Qt.qApp.SDM = SharedDataManager(form)
    Qt.qApp.SDM.connectReader('someUID', kk)
    Qt.qApp.SDM.connectWriter('anotherUID', form, 'thisisasignalname')

    form.show()

    paneldesc, ok = PanelDescriptionWizard.getDialog(form, extraWidgets=[('PyQt4.Qt.QLineEdit', 'logos:taurus.png'),
                                                                         ('PyQt4.Qt.QTextEdit', None)])
    if ok:
        w = paneldesc.getWidget(sdm=Qt.qApp.SDM)
        form.setCentralWidget(w)
        form.setWindowTitle(paneldesc.name)
    print(Qt.qApp.SDM.info())

    sys.exit(app.exec_())


if __name__ == "__main__":
    # test2()
    main()
