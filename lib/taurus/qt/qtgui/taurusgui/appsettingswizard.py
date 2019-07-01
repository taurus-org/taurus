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
This Wizard provide functionality for creating from scratch a configuration
directory for a TaurusGUI based application.

The files in the configuration dir determine the default, permanent, pre-defined
contents of the GUI. While the user may add/remove more elements at run
time and those customizations will also be stored, this file defines what a
user will find when launching the GUI for the first time.
"""
from __future__ import print_function

from builtins import str

import os
import re
import sys
import shutil
import copy
import datetime
import glob
from lxml import etree

from taurus import tauruscustomsettings, warning
from taurus.external.qt import Qt, compat
import taurus.qt.qtgui.panel
import taurus.qt.qtgui.taurusgui.paneldescriptionwizard
import taurus.qt.qtgui.input
from taurus.core.util.enumeration import Enumeration
from taurus.qt.qtgui.util import ExternalAppAction


__all__ = ["AppSettingsWizard", "ExternalAppEditor"]


class BooleanWidget(Qt.QWidget):
    """
    This class represents the simple boolean widget with two RadioButtons
    true and false. The default value of the widget is true.
    It change the value by using getValue and setValue methods
    """

    valueChangedSignal = Qt.pyqtSignal(bool, bool)

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self._formLayout = Qt.QHBoxLayout(self)
        self.trueButton = Qt.QRadioButton(self)
        self._formLayout.addWidget(self.trueButton)
        self.falseButton = Qt.QRadioButton(self)
        self._formLayout.addWidget(self.falseButton)
        self.trueButton.setText("Yes")
        self.falseButton.setText("No")
        self.trueButton.clicked.connect(self.valueChanged)
        self.falseButton.clicked.connect(self.valueChanged)
        self.setValue(self.getDefaultValue())

    def valueChanged(self):
        if not (self.trueButton.isChecked() == self._actualValue):
            self.valueChangedSignal.emit(self._actualValue, not self._actualValue)
        self._actualValue = self.trueButton.isChecked()

    def setValue(self, value):
        if value is None:
            value = self.getDefaultValue()
        self.trueButton.setChecked(value)
        self.falseButton.setChecked(not value)
        self._actualValue = value

    def getValue(self):
        return self.trueButton.isChecked()

    @classmethod
    def getDefaultValue(self):
        return False


class BasePage(Qt.QWizardPage):
    """
        This class represents the base page for all of the pages in the wizard
    """

    completeChanged = Qt.pyqtSignal()

    def __init__(self, parent=None):
        Qt.QWizardPage.__init__(self, parent)
        self._item_funcs = {}
        self._layout = Qt.QGridLayout()
        self.setLayout(self._layout)
        self._setupUI()

    def initializePage(self):
        Qt.QWizardPage.initializePage(self)
        self.checkData()

    def fromXml(self, xml):
        """
        :param xml: (etree.Element) root node
        """
        pass

    def _setupUI(self):
        pass

    def checkData(self):
        self._valid = True
        self.completeChanged.emit()

    def isComplete(self):
        return self._valid

    def _markRed(self, label):
        """
            Set the color of the given label to red
        """
        palette = label.palette()
        palette.setBrush(Qt.QPalette.WindowText, Qt.Qt.red)
        label.update()

    def _markBlack(self, label):
        """
            Set the color of the given label to black
        """
        palette = label.palette()
        palette.setBrush(Qt.QPalette.WindowText, Qt.Qt.black)
        label.update()

    def setStatusLabelPalette(self, label):
        """
            Set the label look as as status label
        """
        label.setAutoFillBackground(True)
        palette = label.palette()
        gradient = Qt.QLinearGradient(0, 0, 0, 15)
        gradient.setColorAt(0.0, Qt.QColor.fromRgb(60, 150, 255))
        gradient.setColorAt(0.5, Qt.QColor.fromRgb(0, 85, 227))
        gradient.setColorAt(1.0, Qt.QColor.fromRgb(60, 150, 255))
        gradient.setSpread(Qt.QGradient.RepeatSpread)
        palette.setBrush(Qt.QPalette.Window, Qt.QBrush(gradient))
        palette.setBrush(Qt.QPalette.WindowText, Qt.Qt.white)

    def __setitem__(self, name, value):
        self._item_funcs[name] = value

    def __getitem__(self, name):
        return self._item_funcs[name]

    def setNextPageId(self, id):
        self._nextPageId = id

    def nextId(self):
        return self._nextPageId


class IntroPage(BasePage):
    """
        Introduction page
    """

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)

    def _setupUI(self):
        self.setTitle('Introduction')
        self.setPixmap(Qt.QWizard.WatermarkPixmap, Qt.QIcon.fromTheme(
            "document-properties").pixmap(120, 120))
        label = Qt.QLabel(self.getIntroText())
        label.setWordWrap(True)
        self._layout.addWidget(label, 0, 0)
        self._spacerItem1 = Qt.QSpacerItem(
            10, 200, Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Fixed)
        self._layout.addItem(self._spacerItem1, 1, 0)
        self.setLayout(self._layout)

    def getIntroText(self):
        text = 'This wizard will guide you through the process of creating a ' + \
               'GUI based on TaurusGUI.\n' + \
               'TaurusGui-based applications are very customizable. The user can ' + \
               'add/remove elements at run time and store those customizations. So ' + \
               'with this wizard you will define just the default contents of the GUI.'
        return text

    def setNextPageId(self, id):
        self._nextPageId = id


class ProjectPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)
        self.setTitle('Project')
        self.setSubTitle(
            'Choose a location for the application files (i.e., the "project directory")')
        self.__setitem__('projectDir', self._getProjectDir)

    def _setupUI(self):
        BasePage._setupUI(self)
        self._projectDirLabel = Qt.QLabel("Project Directory:")
        self._projectDirLE = Qt.QLineEdit(Qt.QDir.homePath())
        self._projectDirLE.setMinimumSize(150, 30)
        self._projectDirLE.setToolTip(
            'This directory will be used to store all files needed by the application.')
        self._projectDirBT = Qt.QPushButton(Qt.QIcon.fromTheme(
            "document-properties"), '...')
        self._layout.addWidget(self._projectDirLabel, 1, 0)
        self._layout.addWidget(self._projectDirLE, 1, 1)
        self._layout.addWidget(self._projectDirBT, 1, 2)

        self._projectDirBT.clicked.connect(self.onSelectDir)

    def onSelectDir(self):
        dirname = str(Qt.QFileDialog.getExistingDirectory(
            self, 'Choose the project directory', self._projectDirLE.text()))
        if not dirname:
            return
        self._projectDirLE.setText(dirname)

    def validatePage(self):
        dirname = str(self._projectDirLE.text())

        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except Exception as e:
                Qt.QMessageBox.warning(self, 'Error creating project directory',
                                       'Could not create the project directory.\nReason:%s' % repr(
                                           e),
                                       Qt.QMessageBox.Cancel)
                return False

        configs_found = glob.glob(os.path.join(dirname, "tgconf_*",
                                  self.wizard().getXmlConfigFileName()))
        # fname = os.path.join(dirname, self.wizard().getXmlConfigFileName())
        if len(configs_found) == 1:
            fname = configs_found[0]
            option = Qt.QMessageBox.question(self, 'Overwrite project?',
                                             'The "%s" file already exists in the project directory.\n Do you want to edit the existing project?' % (
                                                 os.path.basename(fname)),
                                             Qt.QMessageBox.Yes | Qt.QMessageBox.Cancel)
            if option == Qt.QMessageBox.Yes:
                try:
                    self.wizard().loadXml(fname)
                except Exception as e:
                    Qt.QMessageBox.warning(self, 'Error loading project configuration',
                                           'Could not load the existing configuration.\nReason:%s' % repr(
                                               e),
                                           Qt.QMessageBox.Cancel)
                    return False
            else:
                return False
        elif len(os.listdir(dirname)):
            option = Qt.QMessageBox.question(self, 'Non empty project dir',
                                             'The project directory ("%s") is not empty.\nAre you sure you want to use it?' % (
                                                 os.path.basename(dirname)),
                                             Qt.QMessageBox.Yes | Qt.QMessageBox.No)
            if option != Qt.QMessageBox.Yes:
                return False
        # if all went ok...
        return True

    def _getProjectDir(self):
        return str(self._projectDirLE.text())


class GeneralSettings(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)
        self.setTitle('General settings')

    def initializePage(self):
        BasePage.initializePage(self)
        self.wizard().__setitem__("guiName", self._getGUIName)
        self.wizard().__setitem__("organizationName", self._getOrganizationName)

    def fromXml(self, xml):
        self._guiNameLineEdit.setText(
            AppSettingsWizard.getValueFromNode(xml, "GUI_NAME", ''))
        self._organizationCombo.setEditText(
            AppSettingsWizard.getValueFromNode(xml, "ORGANIZATION", default='Taurus'))

    def _getGUIName(self):
        return str(self._guiNameLineEdit.text())

    def _getOrganizationName(self):
        if len(self._organizationCombo.currentText()) > 0:
            return str(self._organizationCombo.currentText())
        else:
            return None

    def _setupUI(self):
        BasePage._setupUI(self)
        self._guiNameLabel = Qt.QLabel("GUI name:")
        font = Qt.QFont()  # set bigger font
        font.setPointSize(14)

        self._label = Qt.QLabel()
        self._layout.addWidget(self._label, 0, 0, 1, 2, Qt.Qt.AlignRight)
        self._guiNameLineEdit = Qt.QLineEdit()
        self._guiNameLineEdit.setFont(font)
        self._guiNameLineEdit.setMinimumSize(150, 30)
        self._layout.addWidget(self._guiNameLabel, 1, 0,
                               1, 1, Qt.Qt.AlignRight)
        self._layout.addWidget(self._guiNameLineEdit, 1,
                               1, 1, 1, Qt.Qt.AlignRight)
        self._organizationNameLabel = Qt.QLabel("Organization name:")
        self._organizationCombo = Qt.QComboBox()
        self._organizationCombo.addItems(self._getOrganizationNames())
        self._organizationCombo.setMinimumSize(150, 25)
        self._organizationCombo.setEditable(True)
        self._layout.addWidget(self._organizationNameLabel,
                               2, 0, 1, 1, Qt.Qt.AlignRight)
        self._layout.addWidget(self._organizationCombo,
                               2, 1, 1, 1, Qt.Qt.AlignRight)

        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)
        self._status_label = Qt.QLabel()
        self.setStatusLabelPalette(self._status_label)
        self._layout.addWidget(self._status_label, 9, 0, 1, 3)

        self._guiNameLineEdit.textChanged.connect(self.checkData)
        self._organizationCombo.editTextChanged.connect(self.checkData)
        self._organizationCombo.currentIndexChanged.connect(self.checkData)

    def _getOrganizationNames(self):
        return ["TAURUS", "ALBA", "DESY", "Elettra", "ESRF", "MAX-lab", "SOLEIL", "XFEL"]

    def checkData(self):
        self._valid = True
        if not len(self._guiNameLineEdit.text()):
            self._valid = False
            self._markRed(self._guiNameLabel)
        else:
            self._markBlack(self._guiNameLabel)

        self.completeChanged.emit()

        if not self._valid:
            self._setStatus("Please type the name of the GUI")
        else:
            self._setStatus("Press next button to continue")

    def _setStatus(self, text):
        self._status_label.setText(text)


class CustomLogoPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)
        self._customLogoDefaultPath = getattr(tauruscustomsettings,
                                              "ORGANIZATION_LOGO",
                                              "logos:taurus.png")
        self._customLogoPath = self._customLogoDefaultPath

    def initializePage(self):
        BasePage.initializePage(self)
        self.wizard().__setitem__("customLogo", self._getCustomLogo)
        self._changeImage()

    def _setupUI(self):
        BasePage._setupUI(self)
        self.setTitle('Custom logo')
        self._label = Qt.QLabel(
            "\nIf you want to have a custom logo inside your application panel, please select the image file. \n")
        self._label.setWordWrap(True)
        self._layout.addWidget(self._label, 0, 0, 1, 4)
        self._customLogoLabel = Qt.QLabel("Custom logo:")
        self._customLogoLineEdit = Qt.QLineEdit()
        self._customLogoLineEdit.setMinimumSize(250, 25)
        self._customLogoLineEdit.setReadOnly(False)
        self._customLogoButton = Qt.QPushButton()
        self._customLogoButton.setToolTip("Browse...")
        self._customLogoButton.setIcon(Qt.QIcon.fromTheme("folder-open"))
        self._customLogoButton.setMaximumSize(80, 25)
        self._spacerItem1 = Qt.QSpacerItem(
            30, 30, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Fixed)
        self._customLogo = Qt.QLabel(self)
        self._customLogo.setAlignment(Qt.Qt.AlignCenter)
        self._customLogo.setMinimumSize(120, 120)
        self._customLogoDefaultButton = Qt.QPushButton()
        self._customLogoDefaultButton.setToolTip("Default")
        self._customLogoDefaultButton.setMaximumSize(80, 25)
        self._customLogoDefaultButton.setIcon(Qt.QIcon("actions:edit-undo.svg"))
        self._customLogoRemoveButton = Qt.QPushButton()
        self._customLogoRemoveButton.setToolTip("Remove")
        self._customLogoRemoveButton.setMaximumSize(80, 25)
        self._customLogoRemoveButton.setIcon(
            Qt.QIcon("emblems:emblem-unreadable.svg"))
        self._spacerItem2 = Qt.QSpacerItem(
            30, 30, Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)

        self._layout.addWidget(self._customLogoLabel, 2, 0, Qt.Qt.AlignRight)
        self._layout.addWidget(self._customLogoLineEdit,
                               2, 1, Qt.Qt.AlignRight)
        self._layout.addWidget(self._customLogoButton, 2, 2, Qt.Qt.AlignLeft)
        self._layout.addWidget(
            self._customLogoDefaultButton, 2, 3, Qt.Qt.AlignLeft)
        self._layout.addWidget(
            self._customLogoRemoveButton, 2, 4, Qt.Qt.AlignLeft)
        self._layout.addItem(self._spacerItem2, 2, 5)
        self._layout.addItem(self._spacerItem1, 3, 2)
        self._layout.addWidget(self._customLogo, 4, 1,
                               1, 1, Qt.Qt.AlignHCenter)

        self._customLogoButton.clicked.connect(self._selectImage)
        self._customLogoDefaultButton.clicked.connect(self._setDefaultImage)
        self._customLogoRemoveButton.clicked.connect(self._removeImage)
        self._customLogoLineEdit.textChanged.connect(self._changeImage)

        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)
        self._status_label = Qt.QLabel("Press next button to continue")
        self.setStatusLabelPalette(self._status_label)
        self._layout.addWidget(self._status_label, 9, 0, 1, 6)
        self._setNoImage()

    def fromXml(self, xml):
        customLogo = AppSettingsWizard.getValueFromNode(
            xml, "CUSTOM_LOGO", None)
        if customLogo is None:
            self._setDefaultImage()
        else:
            self._customLogoLineEdit.setText(customLogo)

    def _setDefaultImage(self):
        self._customLogoLineEdit.setText(self._customLogoDefaultPath)

    def _setNoImage(self):
        self._customLogo.setPixmap(
            Qt.QIcon.fromTheme("image-missing").pixmap(50, 50))
        self._customLogoPath = None
        self._customLogoRemoveButton.hide()

    def _removeImage(self):
        self._customLogoLineEdit.setText("")
        self._setNoImage()

    def _getCustomLogo(self):
        if (self._customLogoPath is not None):
            return str(self._customLogoPath)
        else:
            return None

    def _selectImage(self):
        fileName, _ = compat.getOpenFileName(
            self, self.tr("Open File"), Qt.QDir.homePath(),
            self.tr("Images (*.png *.xpm *.jpg *.jpeg *.svg)")
        )
        self._customLogoLineEdit.setText(fileName)
        self._changeImage()

    def _changeImage(self):
        fileName = str(self._customLogoLineEdit.text())
        if len(fileName):
            if (os.path.exists(fileName)):
                image = Qt.QImage()
                if image.load(fileName):
                    self._setImage(image)
                    self._customLogoPath = fileName
                    self._setStatus("Press next button to continue")
                    self._customLogoRemoveButton.show()
                else:
                    self._setNoImage()
                    self._setStatus("The file is invalid")
            else:
                self._setNoImage()
                self._setStatus("The file does not exist")
        else:
            self._setNoImage()
            self._setStatus("No image")

    def _setImage(self, image):
        if type(image) == Qt.QPixmap:
            self._customLogo.setPixmap(
                image.scaled(60, 200, Qt.Qt.KeepAspectRatio))
        elif type(image) == Qt.QImage:
            self._customLogo.setPixmap(Qt.QPixmap().fromImage(
                image).scaled(60, 200, Qt.Qt.KeepAspectRatio))
        else:
            self._customLogo.setPixmap(
                Qt.QPixmap("image-missing").scaled(50, 50))
            self._customLogoPath = None

    def _setStatus(self, text):
        self._status_label.setText(text)


class SynopticPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)
        self._synoptics = []

    def fromXml(self, xml):
        self._synoptics = []
        synopticNodes = AppSettingsWizard.getArrayFromNode(
            xml, "SYNOPTIC", default=[])
        for child in synopticNodes:
            if child.get("str") is not None and len(child.get("str")):
                self._synoptics.append(child.get("str"))

    def initializePage(self):
        BasePage.initializePage(self)
        self.wizard().__setitem__("synoptics", self._getSynoptics)
        self._refreshSynopticList()

    def _setupUI(self):
        BasePage._setupUI(self)
        self.setTitle('Synoptics')
        self._label = Qt.QLabel(
            "If you want to add one or more synoptic panels (graphical views of instruments) select the corresponding JDRAW files here\n")
        self._label.setWordWrap(True)
        self._layout.addWidget(self._label, 0, 0)
        self.setLayout(self._layout)
        self._synopticGroupBox = Qt.QGroupBox()
        self._synopticGroupBox.setCheckable(False)
        self._synopticGroupBox.setAlignment(Qt.Qt.AlignLeft)
        self._synopticGroupBox.setStyleSheet(
            " QGroupBox::title {  subcontrol-position: top left; padding: 5 5px; }")
        self._layout.addWidget(self._synopticGroupBox, 2, 0, 1, 1)
        self._horizontalLayout = Qt.QHBoxLayout(self._synopticGroupBox)
        self._synopticList = Qt.QListWidget(self._synopticGroupBox)
        self._horizontalLayout.addWidget(self._synopticList)
        self._verticalLayout = Qt.QVBoxLayout()
        self._addButton = Qt.QPushButton("Add Synoptic")
        self._addButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._addButton)
        self._removeButton = Qt.QPushButton("Remove Synoptic")
        self._removeButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._removeButton)
        self._upButton = Qt.QPushButton("Move Up")
        self._upButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._upButton)
        self._downButton = Qt.QPushButton("Move Down")
        self._downButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._downButton)
        self._horizontalLayout.addLayout(self._verticalLayout)
        self._addButton.setIcon(Qt.QIcon.fromTheme("list-add"))
        self._removeButton.setIcon(Qt.QIcon.fromTheme("list-remove"))
        self._upButton.setIcon(Qt.QIcon.fromTheme("go-up"))
        self._downButton.setIcon(Qt.QIcon.fromTheme("go-down"))
        self._addButton.clicked.connect(self._addSynoptic)
        self._removeButton.clicked.connect(self._removeSynoptic)
        self._upButton.clicked.connect(self._moveUp)
        self._downButton.clicked.connect(self._moveDown)
        #self._synopticList.itemDoubleClicked.connect(self._editSynoptic)
        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)
        self._status_label = Qt.QLabel("Press next button to continue")
        self.setStatusLabelPalette(self._status_label)
        self._layout.addWidget(self._status_label, 9, 0, 1, 1)

    def _addSynoptic(self):
        pdir = self.wizard().__getitem__('projectDir')
        fileNames, _ = compat.getOpenFileNames(
            self, self.tr("Open File"), pdir,
            self.tr("JDW (*.jdw );; All files (*)")
        )
        for fileName in fileNames:
            fileName = str(fileName)
            if fileName not in self._synoptics:
                self._synoptics.append(fileName)
        self._refreshSynopticList()

    def _editSynoptic(self):
        # edit
        self._refreshSynopticList()

    def _removeSynoptic(self):
        if len(self._synopticList.selectedIndexes()) > 0:
            self._synoptic_id = self._synopticList.selectedIndexes()[0].row()
            self._synoptics.remove(self._synoptics[self._synoptic_id])
            self._refreshSynopticList()

    def _moveUp(self):
        if len(self._synopticList.selectedIndexes()) > 0:
            self._synoptic_id = self._synopticList.selectedIndexes()[0].row()
            if self._synoptic_id > 0:
                tmp = self._synoptics[self._synoptic_id]
                self._synoptics[self._synoptic_id] = self._synoptics[
                    self._synoptic_id - 1]
                self._synoptics[self._synoptic_id - 1] = tmp
                self._refreshSynopticList()
                self._synopticList.setCurrentIndex(self._synopticList.indexFromItem(
                    self._synopticList.item(self._synoptic_id - 1)))

    def _moveDown(self):
        if len(self._synopticList.selectedIndexes()) > 0:
            self._synoptic_id = self._synopticList.selectedIndexes()[0].row()
            if self._synoptic_id < self._synopticList.count() - 1:
                tmp = self._synoptics[self._synoptic_id]
                self._synoptics[self._synoptic_id] = self._synoptics[
                    self._synoptic_id + 1]
                self._synoptics[self._synoptic_id + 1] = tmp
                self._refreshSynopticList()
                self._synopticList.setCurrentIndex(self._synopticList.indexFromItem(
                    self._synopticList.item(self._synoptic_id + 1)))

    def _refreshSynopticList(self):
        self._synopticList.clear()
        for name in self._synoptics:
            self._synopticList.addItem(name)

    def _getSynoptics(self):
        if len(self._synoptics) <= 0:
            return None
        else:
            return self._synoptics

    def checkData(self):
        BasePage.checkData(self)
        self._valid = True

    def _setStatus(self, text):
        self._status_label.setText(text)


class MacroServerInfoPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)

    def initializePage(self):
        BasePage.initializePage(self)
        self._label.setText("\n <b>%s</b> can communicate with a Sardana's Macro Server and Pool.\nYou can enable and configure them here:\n" %
                            self.wizard().__getitem__("guiName"))
        self.wizard().__setitem__("macroServerName", self._getMacroServerName)
        self.wizard().__setitem__("doorName", self._getDoorName)

    def _setupUI(self):
        BasePage._setupUI(self)
        self.setTitle('Macro Server Info')
        self._label = Qt.QLabel()
        self._label.setWordWrap(True)
        self._macroGroupBox = Qt.QGroupBox()
        self._macroGroupBox.setTitle("Enable Sardana communication")
        self._macroGroupBox.setCheckable(True)
        self._macroGroupBox.setChecked(False)
        self._macroGroupBox.setAlignment(Qt.Qt.AlignLeft)
        self._macroGroupBox.setStyleSheet(
            " QGroupBox::title {  subcontrol-position: top left; padding: 5 5px; }")
        self._horizontalLayout = Qt.QHBoxLayout(self._macroGroupBox)
        from sardana.taurus.qt.qtgui.extra_macroexecutor.common import \
                TaurusMacroConfigurationDialog
        self._confWidget = TaurusMacroConfigurationDialog(self)
        self._confWidget.setWindowFlags(Qt.Qt.Widget)
        self._confWidget.setModal(False)
        self._confWidget.setVisible(True)
        self._confWidget.buttonBox.setVisible(False)
        self._horizontalLayout.addWidget(self._confWidget)

        self._layout.addWidget(self._label, 0, 0, 1, 1)
        self._layout.addWidget(self._macroGroupBox, 1, 0, 1, 1)

        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)
        self._status_label = Qt.QLabel("Press next button to continue")
        self.setStatusLabelPalette(self._status_label)
        self._layout.addWidget(self._status_label, 9, 0, 1, 1)

        self._confWidget.macroServerComboBox.currentIndexChanged.connect(
            self.checkData)
        self._confWidget.doorComboBox.currentIndexChanged.connect(
            self.checkData)
        self._macroGroupBox.toggled.connect(self.checkData)

    def fromXml(self, xml):
        macroserverName = AppSettingsWizard.getValueFromNode(
            xml, "MACROSERVER_NAME", default="")
        doorName = AppSettingsWizard.getValueFromNode(
            xml, "DOOR_NAME", default="")
        macroEditorsPath = AppSettingsWizard.getValueFromNode(
            xml, "MACROEDITORS_PATH", default="")

        id = self._confWidget.macroServerComboBox.findText(
            macroserverName, Qt.Qt.MatchExactly)
        if id >= 0:
            self._confWidget.macroServerComboBox.setCurrentIndex(id)
            self._macroGroupBox.setChecked(True)
        else:
            self._macroGroupBox.setChecked(False)
            return

        id = self._confWidget.doorComboBox.findText(
            doorName, Qt.Qt.MatchExactly)
        if id >= 0:
            self._confWidget.doorComboBox.setCurrentIndex(id)

    def checkData(self):
        BasePage.checkData(self)
        if (self._macroGroupBox.isChecked()) and len(self._confWidget.macroServerComboBox.currentText()):
            self.setNextPageId(self.wizard().currentId() + 1)
        else:
            self.setNextPageId(self.wizard().currentId() + 2)

    def _getMacroServerName(self):
        if (self._macroGroupBox.isChecked()) and len(self._confWidget.macroServerComboBox.currentText()):
            try: # TODO: tango-centric
                from taurus.core.tango.tangovalidator import (
                    TangoDeviceNameValidator)
            except ImportError:
                warning('Cannot import tango (needed for sardana integration)')
                return None
            ms_name = str(self._confWidget.macroServerComboBox.currentText())
            complete_name, _, _ = TangoDeviceNameValidator().getNames(ms_name)
            return complete_name
        else:
            return None

    def _getDoorName(self):
        if (self._macroGroupBox.isChecked()) and len(self._confWidget.macroServerComboBox.currentText()):
            door_name = str(self._confWidget.doorComboBox.currentText())
            try: # TODO: tango-centric
                from taurus.core.tango.tangovalidator import (
                    TangoDeviceNameValidator)
            except ImportError:
                warning('Cannot import tango (needed for sardana integration)')
                return None
            complete_name, _, _ = TangoDeviceNameValidator().getNames(
                door_name)
            return complete_name
        else:
            return None

    def _setStatus(self, text):
        self._status_label.setText(text)


class InstrumentsPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)

    def initializePage(self):
        BasePage.initializePage(self)
        self.wizard().__setitem__("instruments", self._getInstruments)
        self._label.setText("<b>%s</b> can use instrument information stored in the Sardana's Pool to create instrument panels." %
                            self.wizard().__getitem__("guiName"))

    def _setupUI(self):
        BasePage._setupUI(self)
        self.setTitle('Instruments from Pool:')
        self._label = Qt.QLabel()
        self._label.setWordWrap(True)
        self._layout.addWidget(self._label, 0, 0, 1, 3)

        self._instrumentsLabel = Qt.QLabel("Generate panels from Pool Info?")
        self._intstrumentsBoolean = BooleanWidget()
        self._intstrumentsBoolean.setMinimumSize(150, 25)
        self._layout.addWidget(self._instrumentsLabel, 5,
                               0, 1, 1, Qt.Qt.AlignRight)
        self._layout.addWidget(self._intstrumentsBoolean,
                               5, 1, 1, 1, Qt.Qt.AlignRight)

        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)
        self._status_label = Qt.QLabel("Press next button to continue")
        self.setStatusLabelPalette(self._status_label)
        self._layout.addWidget(self._status_label, 9, 0, 1, 3)

    def fromXml(self, xml):
        instruments = AppSettingsWizard.getValueFromNode(
            xml, "INSTRUMENTS_FROM_POOL", default="False")
        if str(instruments).lower() == "true":
            self._intstrumentsBoolean.setValue(True)
        else:
            self._intstrumentsBoolean.setValue(False)

    def _getInstruments(self):
        return str(self._intstrumentsBoolean.getValue())

    def checkData(self):
        self._valid = True

    def _setStatus(self, text):
        self._status_label.setText(text)


class PanelsPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)
        self._panels = []

    def initializePage(self):
        BasePage.initializePage(self)
        self.wizard().__setitem__("panels", self._getPanels)
        self._refreshPanelList()

    def _setupUI(self):
        BasePage._setupUI(self)
        self.setTitle('Panels editor')
        self._label = Qt.QLabel(
            "If you want extra panels add them to this list\n")
        self._layout.addWidget(self._label, 0, 0)
        self.setLayout(self._layout)
        self._panelGroupBox = Qt.QGroupBox()
        self._panelGroupBox.setCheckable(False)
        self._panelGroupBox.setAlignment(Qt.Qt.AlignLeft)
        self._panelGroupBox.setStyleSheet(
            " QGroupBox::title {  subcontrol-position: top left; padding: 5 5px; }")
        self._layout.addWidget(self._panelGroupBox, 2, 0, 1, 1)
        self._horizontalLayout = Qt.QHBoxLayout(self._panelGroupBox)
        self._panelList = Qt.QListWidget(self._panelGroupBox)
        self._horizontalLayout.addWidget(self._panelList)
        self._verticalLayout = Qt.QVBoxLayout()
        self._addButton = Qt.QPushButton("Add Panel")
        self._addButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._addButton)
        self._removeButton = Qt.QPushButton("Remove Panel")
        self._removeButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._removeButton)
        self._upButton = Qt.QPushButton("Move Up")
        self._upButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._upButton)
        self._downButton = Qt.QPushButton("Move Down")
        self._downButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._downButton)
        self._horizontalLayout.addLayout(self._verticalLayout)
        self._addButton.setIcon(Qt.QIcon.fromTheme("list-add"))
        self._removeButton.setIcon(Qt.QIcon.fromTheme("list-remove"))
        self._upButton.setIcon(Qt.QIcon.fromTheme("go-up"))
        self._downButton.setIcon(Qt.QIcon.fromTheme("go-down"))
        self._addButton.clicked.connect(self._addPanel)
        self._removeButton.clicked.connect(self._removePanel)
        self._upButton.clicked.connect(self._moveUp)
        self._downButton.clicked.connect(self._moveDown)
        self._panelList.itemDoubleClicked.connect(self._editPanel)
        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)
        self._status_label = Qt.QLabel("Press next button to continue")
        self.setStatusLabelPalette(self._status_label)
        self._layout.addWidget(self._status_label, 9, 0, 1, 1)

    def fromXml(self, xml):
        self._panels = []
        panelNodes = AppSettingsWizard.getArrayFromNode(
            xml, "PanelDescriptions", default=[])
        for child in panelNodes:
            name = AppSettingsWizard.getValueFromNode(
                child, "name", default=None)
            if name:
                self._panels.append(
                    (name, etree.tostring(child, encoding='unicode')))

    def _addPanel(self):
        paneldesc, ok = taurus.qt.qtgui.taurusgui.paneldescriptionwizard.PanelDescriptionWizard.getDialog(
            self)
        if ok:
            w = paneldesc.getWidget()
            self._panels.append((paneldesc.name, paneldesc.toXml()))

        self._refreshPanelList()

    def _editPanel(self):
        # edit
        self._refreshPanelList()

    def _removePanel(self):
        if len(self._panelList.selectedIndexes()) > 0:
            self._panel_id = self._panelList.selectedIndexes()[0].row()
            self._panels.remove(self._panels[self._panel_id])
            self._refreshPanelList()

    def _moveUp(self):
        if len(self._panelList.selectedIndexes()) > 0:
            self._panel_id = self._panelList.selectedIndexes()[0].row()
            if self._panel_id > 0:
                tmp = self._panels[self._panel_id]
                self._panels[self._panel_id] = self._panels[self._panel_id - 1]
                self._panels[self._panel_id - 1] = tmp
                self._refreshPanelList()
                self._panelList.setCurrentIndex(self._panelList.indexFromItem(
                    self._panelList.item(self._panel_id - 1)))

    def _moveDown(self):
        if len(self._panelList.selectedIndexes()) > 0:
            self._panel_id = self._panelList.selectedIndexes()[0].row()
            if self._panel_id < self._panelList.count() - 1:
                tmp = self._panels[self._panel_id]
                self._panels[self._panel_id] = self._panels[self._panel_id + 1]
                self._panels[self._panel_id + 1] = tmp
                self._refreshPanelList()
                self._panelList.setCurrentIndex(self._panelList.indexFromItem(
                    self._panelList.item(self._panel_id + 1)))

    def _refreshPanelList(self):
        self._panelList.clear()
        for panel in self._panels:
            name, xml = panel
            self._panelList.addItem(name)

    def _getPanels(self):
        if len(self._panels) <= 0:
            return None
        else:
            return self._panels

    def checkData(self):
        BasePage.checkData(self)
        self._valid = True

    def _setStatus(self, text):
        self._status_label.setText(text)


class ExternalAppEditor(Qt.QDialog):
    '''
    A dialog for configuring an external appaction for a TaurusMainWindow.
    '''
    #@todo: this class should be made more generic (e.g. provide a getter for an ExternalAppAction) and then moved elsewhere

    def __init__(self, parent=None):
        Qt.QDialog.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle('External Application Editor')

        self._dlgBox = Qt.QDialogButtonBox(
            Qt.QDialogButtonBox.Ok | Qt.QDialogButtonBox.Cancel)

        self._layout = Qt.QVBoxLayout()
        self._layout1 = Qt.QGridLayout()
        self._layout2 = Qt.QHBoxLayout()
        self._layout.addLayout(self._layout1)
        self._layout.addLayout(self._layout2)
        self._layout.addWidget(self._dlgBox)
        self.setLayout(self._layout)

        self._icon = None
        self._label = Qt.QLabel(
            "\n On this page you can define an external application. \n")
        self._label.setWordWrap(True)
        self._layout1.addWidget(self._label, 0, 0, 1, 4)
        self._execFileLabel = Qt.QLabel("Command:")
        self._execFileLineEdit = Qt.QLineEdit()
        self._execFileLineEdit.setMinimumSize(150, 25)
        # self._execFileLineEdit.setReadOnly(True)
        self._execFileButton = Qt.QPushButton()
        self._execFileButton.setIcon(Qt.QIcon.fromTheme("folder-open"))
        self._execFileButton.setToolTip("Browse...")
        self._execFileButton.setMaximumSize(80, 25)
        self._layout1.addWidget(self._execFileLabel, 2, 0, Qt.Qt.AlignRight)
        self._layout1.addWidget(self._execFileLineEdit, 2, 1, Qt.Qt.AlignRight)
        self._layout1.addWidget(self._execFileButton, 2, 2, Qt.Qt.AlignLeft)
        self._paramsLabel = Qt.QLabel("Parameters:")
        self._paramsLineEdit = Qt.QLineEdit()
        self._paramsLineEdit.setMinimumSize(150, 25)
        self._layout1.addWidget(self._paramsLabel, 3, 0, Qt.Qt.AlignRight)
        self._layout1.addWidget(self._paramsLineEdit, 3, 1, Qt.Qt.AlignRight)
        self._textLabel = Qt.QLabel("Text:")
        self._textLineEdit = Qt.QLineEdit()
        self._textLineEdit.setMinimumSize(150, 25)
        self._layout1.addWidget(self._textLabel, 4, 0, Qt.Qt.AlignRight)
        self._layout1.addWidget(self._textLineEdit, 4, 1, Qt.Qt.AlignRight)

        self._iconLabel = Qt.QLabel("Icon:")
        self._iconLogo = Qt.QPushButton()
        self._iconLogo.setIcon(Qt.QIcon("status:image-missing.svg"))
        self._iconLogo.setIconSize(Qt.QSize(60, 60))
        self._layout1.addWidget(self._iconLabel, 5, 0, Qt.Qt.AlignRight)
        self._layout1.addWidget(self._iconLogo, 5, 1, Qt.Qt.AlignCenter)
        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout1.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)

        # connections
        self._execFileButton.clicked.connect(self._selectExecFile)
        self._execFileLineEdit.textChanged.connect(self._setDefaultText)
        self._iconLogo.clicked.connect(self._selectIcon)
        self._dlgBox.accepted.connect(self.accept)
        self._dlgBox.rejected.connect(self.reject)
        self.checkData()
        self._setIcon(ExternalAppAction.DEFAULT_ICON_NAME)

    def checkData(self):
        if len(self._execFileLineEdit.text()) > 0:
            self._dlgBox.button(Qt.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self._dlgBox.button(Qt.QDialogButtonBox.Ok).setEnabled(False)

    def _setDefaultText(self):
        fileName = self._execFileLineEdit.text().split('/')[-1]
        index = str(fileName).rfind(".")
        if (index > 0):
            self._textLineEdit.setText(str(fileName)[0:index])
        else:
            self._textLineEdit.setText(fileName)
        self.checkData()

    def _selectExecFile(self):
        filePath, _ = compat.getOpenFileName(
            self, self.tr("Open File"),
            Qt.QDir.homePath(), self.tr("All files (*)")
        )
        if len(filePath):
            self._execFileLineEdit.setText(filePath)
            self._setDefaultText()

    def _getExecFile(self):
        return str(self._execFileLineEdit.text())

    def _selectIcon(self):
        from taurus.qt.qtgui.icon import QIconCatalog
        catalog = QIconCatalog()
        dlg = Qt.QDialog(self)
        dlg.setLayout(Qt.QVBoxLayout())
        dlg.layout().addWidget(catalog)
        dlg.setWindowTitle('Icon Catalog')
        catalog.iconSelected.connect(self._setIcon)
        catalog.iconSelected.connect(dlg.accept)
        dlg.exec_()

    def _setIcon(self, name):
        self._iconLogo.setIcon(Qt.QIcon(name))
        self._iconLogo.setIconSize(Qt.QSize(60, 60))
        self._iconLogo.setText("")
        self._icon = name

    def _getParams(self):
        return str(self._paramsLineEdit.text())
        # return str(self._paramsLineEdit.text()).split()

    def _getText(self):
        return str(self._textLineEdit.text())

    def _getIcon(self):
        return str(self._icon)

    def _toXml(self):
        root = etree.Element("ExternalApp")
        command = etree.SubElement(root, "command")
        command.text = self._getExecFile()
        params = etree.SubElement(root, "params")
        params.text = self._getParams()
        text = etree.SubElement(root, "text")
        text.text = self._getText()
        icon = etree.SubElement(root, "icon")
        icon.text = self._getIcon()

        return etree.tostring(root, encoding='unicode')

    @staticmethod
    def getDialog():
        dlg = ExternalAppEditor()
        dlg.exec_()
        return dlg._getExecFile(), dlg._toXml(), (dlg.result() == dlg.Accepted)


class ExternalAppPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)
        self._externalApps = []

    def initializePage(self):
        BasePage.initializePage(self)
        self.wizard().__setitem__("externalApps", self._getExternalApps)
        self._refreshApplicationList()

    def _setupUI(self):
        BasePage._setupUI(self)
        self.setTitle('External Applications')
        self._label = Qt.QLabel(
            "The GUI may include shortcuts to external applications. You can add them now.\n")
        self._layout.addWidget(self._label, 0, 0)
        self.setLayout(self._layout)
        self._externalAppGroupBox = Qt.QGroupBox()
        self._externalAppGroupBox.setCheckable(False)
        self._externalAppGroupBox.setAlignment(Qt.Qt.AlignLeft)
        self._externalAppGroupBox.setStyleSheet(
            " QGroupBox::title {  subcontrol-position: top left; padding: 5 5px; }")
        self._layout.addWidget(self._externalAppGroupBox, 2, 0, 1, 1)
        self._horizontalLayout = Qt.QHBoxLayout(self._externalAppGroupBox)
        self._externalAppList = Qt.QListWidget(self._externalAppGroupBox)
        self._horizontalLayout.addWidget(self._externalAppList)
        self._verticalLayout = Qt.QVBoxLayout()
        self._addButton = Qt.QPushButton("Add Application")
        self._addButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._addButton)
        self._removeButton = Qt.QPushButton("Remove Application")
        self._removeButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._removeButton)
        self._upButton = Qt.QPushButton("Move Up")
        self._upButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._upButton)
        self._downButton = Qt.QPushButton("Move Down")
        self._downButton.setStyleSheet("text-align: left;")
        self._verticalLayout.addWidget(self._downButton)
        self._horizontalLayout.addLayout(self._verticalLayout)
        self._addButton.setIcon(Qt.QIcon.fromTheme("list-add"))
        self._removeButton.setIcon(Qt.QIcon.fromTheme("list-remove"))
        self._upButton.setIcon(Qt.QIcon.fromTheme("go-up"))
        self._downButton.setIcon(Qt.QIcon.fromTheme("go-down"))
        self._addButton.clicked.connect(self._addApplication)
        self._removeButton.clicked.connect(self._removeApplication)
        self._upButton.clicked.connect(self._moveUp)
        self._downButton.clicked.connect(self._moveDown)
        self._externalAppList.itemDoubleClicked.connect(self._editApplication)
        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)
        self._status_label = Qt.QLabel("Press next button to continue")
        self.setStatusLabelPalette(self._status_label)
        self._layout.addWidget(self._status_label, 9, 0, 1, 1)

    def fromXml(self, xml):
        self._externalApps = []
        panelNodes = AppSettingsWizard.getArrayFromNode(
            xml, "ExternalApps", default=[])
        for child in panelNodes:
            name = AppSettingsWizard.getValueFromNode(
                child, "command", default=None)
            if name:
                self._externalApps.append(
                    (name, etree.tostring(child, encoding='unicode'))
                )

    def _addApplication(self):
        name, xml, ok = ExternalAppEditor.getDialog()
        if ok:
            self._externalApps.append((name, xml))

        self._refreshApplicationList()

    def _editApplication(self):
        # edit
        self._refreshApplicationList()

    def _removeApplication(self):
        if len(self._externalAppList.selectedIndexes()) > 0:
            self._app_id = self._externalAppList.selectedIndexes()[0].row()
            self._externalApps.remove(self._externalApps[self._app_id])
            self._refreshApplicationList()

    def _moveUp(self):
        if len(self._externalAppList.selectedIndexes()) > 0:
            self._app_id = self._externalAppList.selectedIndexes()[0].row()
            if self._app_id > 0:
                tmp = self._externalApps[self._app_id]
                self._externalApps[self._app_id] = self._externalApps[
                    self._app_id - 1]
                self._externalApps[self._app_id - 1] = tmp
                self._refreshApplicationList()
                self._externalAppList.setCurrentIndex(self._externalAppList.indexFromItem(
                    self._externalAppList.item(self._app_id - 1)))

    def _moveDown(self):
        if len(self._externalAppList.selectedIndexes()) > 0:
            self._app_id = self._externalAppList.selectedIndexes()[0].row()
            if self._app_id < self._externalAppList.count() - 1:
                tmp = self._externalApps[self._app_id]
                self._externalApps[self._app_id] = self._externalApps[
                    self._app_id + 1]
                self._externalApps[self._app_id + 1] = tmp
                self._refreshApplicationList()
                self._externalAppList.setCurrentIndex(self._externalAppList.indexFromItem(
                    self._externalAppList.item(self._app_id + 1)))

    def _refreshApplicationList(self):
        self._externalAppList.clear()
        for panel in self._externalApps:
            name, xml = panel
            self._externalAppList.addItem(name)

    def _getExternalApps(self):
        if len(self._externalApps) <= 0:
            return None
        else:
            return self._externalApps

    def checkData(self):
        BasePage.checkData(self)
        self._valid = True

    def _setStatus(self, text):
        self._status_label.setText(text)


class MonitorPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)

    def initializePage(self):
        BasePage.initializePage(self)
        self.wizard().__setitem__("monitor", self._getMonitor)

    def _setupUI(self):
        BasePage._setupUI(self)
        self.setTitle('Monitor List')
        self._label = Qt.QLabel(
            "\nIf you want to monitor some attributes, add them to the monitor list. \n")
        self._label.setWordWrap(True)
        self._layout.addWidget(self._label, 0, 0, 1, 4)
        self._monitorLabel = Qt.QLabel("Monitor List:")
        self._monitorLineEdit = Qt.QLineEdit()
        self._monitorLineEdit.setToolTip(
            "Comma-separated list of attribute names")
        self._monitorLineEdit.setMinimumSize(400, 25)
        self._monitorLineEdit.setReadOnly(False)
        self._monitorButton = Qt.QPushButton()
        self._monitorButton.setToolTip("Browse...")
        # self._monitorButton.setIcon(Qt.QIcon.fromTheme("system-search"))
        self._monitorButton.setIcon(Qt.QIcon("designer:devs_tree.png"))
        self._monitorButton.setMaximumSize(80, 25)
        self._monitorClearButton = Qt.QPushButton()
        self._monitorClearButton.setToolTip("Clear")
        self._monitorClearButton.setMaximumSize(80, 25)
        self._monitorClearButton.setIcon(Qt.QIcon("actions:edit-clear.svg"))
        self._layout.addWidget(self._monitorLabel, 2, 0, Qt.Qt.AlignRight)
        self._layout.addWidget(self._monitorLineEdit, 2, 1, Qt.Qt.AlignRight)
        self._layout.addWidget(self._monitorButton, 2, 2, Qt.Qt.AlignLeft)
        self._layout.addWidget(self._monitorClearButton, 2, 3, Qt.Qt.AlignLeft)
        self._monitorButton.clicked.connect(self._selectMonitor)
        self._monitorClearButton.clicked.connect(self._clearMonitor)
        # self._synopticClear.hide()

        self._spacerItem1 = Qt.QSpacerItem(
            10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 8, 0, 1, 1, Qt.Qt.AlignCenter)
        self._status_label = Qt.QLabel("Press next button to continue")
        self.setStatusLabelPalette(self._status_label)
        self._layout.addWidget(self._status_label, 9, 0, 1, 4)

    def fromXml(self, xml):
        self._monitorLineEdit.setText(
            AppSettingsWizard.getValueFromNode(xml, "MONITOR", default=""))

    def _clearMonitor(self):
        self._monitorLineEdit.clear()
        # self._monitorClearButton.hide()

    def _getMonitor(self):
        return str(self._monitorLineEdit.text())

    def _selectMonitor(self):
        models, ok = taurus.qt.qtgui.panel.TaurusModelChooser.modelChooserDlg(
            host=None)
        if ok:
            self._monitorLineEdit.setText(",".join(models))
        self.checkData()

    def _setStatus(self, text):
        self._status_label.setText(text)


class OutroPage(BasePage):

    def __init__(self, parent=None):
        BasePage.__init__(self, parent)
        self._valid = True
        self.setTitle('Confirmation Page')
        self._label1 = Qt.QLabel("XML configuration file:")
        self._layout.addWidget(self._label1, 0, 0)
        self._xml = Qt.QTextEdit()
        self._xml.setSizePolicy(Qt.QSizePolicy(
            Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding))
        self._layout.addWidget(self._xml, 1, 0)
        self._label2 = Qt.QLabel("Files copied")
        self._layout.addWidget(self._label2, 2, 0)
        self._substTable = Qt.QTableWidget()
        self._substTable.setColumnCount(2)
        self._substTable.setEditTriggers(self._substTable.NoEditTriggers)
        self._substTable.setHorizontalHeaderLabels(
            ('Original file', 'File in Project dir'))
        self._substTable.setSizePolicy(Qt.QSizePolicy(
            Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding))
        self._layout.addWidget(self._substTable, 3, 0)

    def _getXml(self):
        return str(self._xml.toPlainText())

    def saveFile(self, fileName):
        file = Qt.QFile(fileName)

        if not file.open(Qt.QFile.WriteOnly | Qt.QFile.Text):
            Qt.QMessageBox.warning(self, self.tr("Saving XML..."),
                                   self.tr("Cannot write file %1:\n%2.")
                                   .arg(fileName)
                                   .arg(file.errorString()))
            return False

        file.write(str(self._xml.toPlainText()))
        self._valid = True
        self.checkData()
        file.close()

        return True

    def initializePage(self):
        xml, substitutions = self.wizard().generateXml()
        self._xml.setText(xml)
        self.wizard().__setitem__("xml", self._getXml)
        self._substTable.clearContents()
        self._substTable.setRowCount(len(substitutions))
        for i, (dst, src) in enumerate(substitutions.items()):
            item0, item1 = Qt.QTableWidgetItem(src), Qt.QTableWidgetItem(dst)
            self._substTable.setItem(i, 0, item0)
            self._substTable.setItem(i, 1, item1)
        self._substTable.resizeColumnsToContents()

    def validatePage(self):
        try:
            self.createProject()
        except Exception as e:
            Qt.QMessageBox.warning(self, 'Error creating project',
                                   'Could not create project files. \nReason:%s' % repr(
                                       e),
                                   Qt.QMessageBox.Cancel)
            import traceback
            traceback.print_exc()
            return False
        return True

    def createProject(self):
        # prepare a log file
        pdir = self.wizard().__getitem__('projectDir')
        gui_name = self.wizard().__getitem__("guiName")
        install_dir = os.path.join(pdir, "tgconf_{0}".format(gui_name))
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
        logfilename = os.path.join(pdir, 'wizard.log')
        logfile = open(logfilename, 'w')
        logfile.write('Project created by AppSettingsWizard on %s\n' %
                      datetime.datetime.now().isoformat())
        # copy files
        for i in range(self._substTable.rowCount()):
            src = str(self._substTable.item(i, 0).text())
            dst = os.path.join(install_dir, str(
                self._substTable.item(i, 1).text()))
            if os.path.normpath(src) != os.path.normpath(dst):
                shutil.copy(src, dst)
                logfile.write('File copied: %s --> %s\n' % (src, dst))
        # write xml config file
        xmlcfgfilename = os.path.join(install_dir,
                                      self.wizard().getXmlConfigFileName())
        f = open(xmlcfgfilename, 'w')
        f.write(str(self._xml.toPlainText()))
        f.close()
        logfile.write('XML Config file created: "%s"\n' % xmlcfgfilename)
        # write python config file
        pycfgfilename = os.path.join(install_dir,
                                '%s.py' % self.wizard().getConfigFilePrefix())
        f = open(pycfgfilename, 'w')
        f.write("XML_CONFIG = '%s'" % self.wizard().getXmlConfigFileName())
        f.close()
        logfile.write('Python config file created: "%s"\n' % pycfgfilename)
        # write __init__.py config file
        init_template = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'res', 'init.template')
        f = open(init_template, 'r')
        template = f.read()
        f.close()
        initfilename = os.path.join(install_dir, '__init__.py')
        f = open(initfilename, 'w')
        template = template.format(name=gui_name)
        f.write(template)
        f.close()
        logfile.write('python init file created: "%s"\n' % initfilename)
        # write setup file
        setup_template = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'res', 'setup.template')
        f = open(setup_template, 'r')
        template = f.read()
        f.close()
        setup = os.path.join(pdir, "setup.py")
        f = open(setup, 'w')
        template = template.format(name=gui_name)
        f.write(template)
        f.close()
        # write MANIFEST.in file
        manifest_template = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'res', 'manifest.template')
        f = open(manifest_template, 'r')
        template = f.read()
        f.close()
        manifestfile = os.path.join(pdir, "MANIFEST.in")
        f = open(manifestfile, 'w')
        template = template.format(name=gui_name)
        f.write(template)
        f.close()
        # if all went ok...
        msg = 'Application project was successfully created.' +\
              'You can find the files in: "%s"' % pdir
        msg += '\nTip: You can install it with:\n\tpip install %s' % pdir
        msg += '\nTip: And then run the application with:\n\t %s' % gui_name
        details = ''
        warnings = self.wizard().getProjectWarnings()
        if warnings:
            msg += '\n\nHowever, some fine-tuning may be needed. Please check the details:\n'
            for _short, _long in warnings:
                details += '- %s: %s\n\n' % (_short, _long)
        logfile.write(msg + details)
        logfile.close()
        dlg = Qt.QMessageBox(Qt.QMessageBox.Information,
                             'Application project created', msg, Qt.QMessageBox.Ok, self)
        dlg.setDetailedText(details)
        dlg.exec_()
        print() 
        print(msg + details)
        print()


class AppSettingsWizard(Qt.QWizard):
    """
    This Wizard provide functionality for creating from scratch a configuration
    directory for a TaurusGUI based application.

    The files in the configuration dir determine the default, permanent, pre-defined
    contents of the GUI. While the user may add/remove more elements at run
    time and those customizations will also be stored, this file defines what a
    user will find when launching the GUI for the first time.
    """
    Pages = Enumeration('Pages', ('IntroPage', 'ProjectPage', 'GeneralSettings', 'CustomLogoPage', 'SynopticPage',
                                  'MacroServerInfo', 'InstrumentsPage', 'PanelsPage', 'ExternalAppPage', 'MonitorPage', 'OutroPage'))
    SARDANA_INSTALLED = False

    def __init__(self, parent=None, jdrawCommand='jdraw', configFilePrefix='config'):
        Qt.QWizard.__init__(self, parent)
        self.installEventFilter(self)
        self._item_funcs = {}
        self._pages = {}
        self._jdrawCommand = jdrawCommand
        self._configFilePrefix = configFilePrefix
        self._loadPages()
        self._substitutions = {}
        self._projectWarnings = []

    def getProjectWarnings(self):
        return self._projectWarnings

    def getConfigFilePrefix(self):
        return self._configFilePrefix

    def getXmlConfigFileName(self):
        return "%s.xml" % self._configFilePrefix

    @staticmethod
    def getValueFromNode(rootNode, nodeName, default=None):
        '''
        returns a value from given Node
        :param rootNode: (etree.Element) root node
        :param nodeName: the name of node to find
        :param default: returned value if node is None or contains empty string
        '''
        node = rootNode.find(nodeName)
        if (node is not None) and (node.text is not None):
            return node.text
        else:
            return default

    @staticmethod
    def getArrayFromNode(rootNode, nodeName, default=None):
        '''
        returns an array contained by given Node
        :param rootNode: (etree.Element) root node
        :param nodeName: the name of node to find
        :param default: returned value if node is None or contains empty string
        '''
        array = []
        node = rootNode.find(nodeName)
        if (node is not None) and (node.text is not None):
            for child in node:
                array.append(child)
            return array
        else:
            return default

    def loadXml(self, fname):
        '''
        parses xml code and sets all pages according to its contents. It
        raises an exception if something could not be processed

        :param fname: (unicode) path to file containing xml code
        '''
        projectDir, cfgfile = os.path.split(fname)
        f = open(fname, 'r')
        xml = f.read()
        root = etree.fromstring(xml)

        # print self.Pages
        for pageNumber in range(len(self.Pages)):
            self.page(pageNumber).fromXml(root)

    def getXml(self):
        try:
            return self.__getitem__("xml")
        except Exception as e:
            return None

    def __setitem__(self, name, value):
        self._item_funcs[name] = value

    def __getitem__(self, name):
        for id in self.getPages():
            p = self.page(id)
            if isinstance(p, BasePage):
                try:
                    return p[name]()
                except Exception as e:
                    pass
        return self._item_funcs[name]()

    def addPage(self, page):
        id = Qt.QWizard.addPage(self, page)
        self._pages[id] = page

    def setPage(self, id, page):
        Qt.QWizard.setPage(self, id, page)
        self._pages[id] = page

    def getPages(self):
        return self._pages

    def _loadPages(self):
        intro = IntroPage()
        self.setPage(self.Pages.IntroPage, intro)
        intro.setNextPageId(self.Pages.ProjectPage)

        project_page = ProjectPage()
        self.setPage(self.Pages.ProjectPage, project_page)
        project_page.setNextPageId(self.Pages.GeneralSettings)

        general_settings_page = GeneralSettings()
        self.setPage(self.Pages.GeneralSettings, general_settings_page)
        general_settings_page.setNextPageId(self.Pages.CustomLogoPage)

        custom_logo_page = CustomLogoPage()
        self.setPage(self.Pages.CustomLogoPage, custom_logo_page)
        custom_logo_page.setNextPageId(self.Pages.SynopticPage)

        synoptic_page = SynopticPage()
        self.setPage(self.Pages.SynopticPage, synoptic_page)

        try:
            from sardana.taurus.qt.qtgui.extra_macroexecutor.common import \
                TaurusMacroConfigurationDialog
            # try to instantiate the dialog (e.g. this fails if using Qt5 with
            # versions of sardana which do not support it)
            _ = TaurusMacroConfigurationDialog()
            self.SARDANA_INSTALLED = True
        except:
            self.SARDANA_INSTALLED = False
        if self.SARDANA_INSTALLED:
            synoptic_page.setNextPageId(self.Pages.MacroServerInfo)

            macroserver_page = MacroServerInfoPage()
            self.setPage(self.Pages.MacroServerInfo, macroserver_page)
            macroserver_page.setNextPageId(self.Pages.InstrumentsPage)

            instruments_page = InstrumentsPage()
            self.setPage(self.Pages.InstrumentsPage, instruments_page)
            instruments_page.setNextPageId(self.Pages.PanelsPage)

        else:
            synoptic_page.setNextPageId(self.Pages.PanelsPage)

        panels_page = PanelsPage()
        self.setPage(self.Pages.PanelsPage, panels_page)
        panels_page.setNextPageId(self.Pages.ExternalAppPage)

        external_app_page = ExternalAppPage()
        self.setPage(self.Pages.ExternalAppPage, external_app_page)
        external_app_page.setNextPageId(self.Pages.MonitorPage)

        monitor_page = MonitorPage()
        self.setPage(self.Pages.MonitorPage, monitor_page)
        monitor_page.setNextPageId(self.Pages.OutroPage)

        outro_page = OutroPage()
        self.setPage(self.Pages.OutroPage, outro_page)
        outro_page.setNextPageId(-1)

        self.setOption(Qt.QWizard.CancelButtonOnLeft, True)

    def generateXml(self):
        '''returns the xml code corresponding to the options selected in the wizard
        and a dictionary representing the paths that have been substituted.

        :return: (str, dict<str,str>) The return value is a tuple whose first element
                 is the xml code and the second element is a dict where the keys are the
                 destination files and the values are the original paths.
        '''
        root = etree.Element("taurusgui_config")
        # general settings page
        guiName = etree.SubElement(root, "GUI_NAME")
        guiName.text = self.__getitem__("guiName")
        organizationName = etree.SubElement(root, "ORGANIZATION")
        organizationName.text = self.__getitem__("organizationName")
        # custom logo page
        customLogo = etree.SubElement(root, "CUSTOM_LOGO")
        src = self.__getitem__("customLogo")
        mod_dir = os.path.join(self.__getitem__('projectDir'),
                            'tgconf_' + guiName.text)
        mod_dir = os.path.abspath(mod_dir)  # make sure mod_dir is absolute
        if src is None or ":" in src:
            # using registered paths
            # TODO: what if they use windows paths such as "C:\foo" ?
            dst = src
        else:
            # if src is absolute, it stays so, and if it is relative, we assume
            # mod_dir as the root dir
            src = os.path.join(mod_dir, src)
            dst = os.path.basename(self.substitutionName(src, mod_dir))
        customLogo.text = dst
        # synoptic page
        synopticList = self.__getitem__("synoptics")
        if synopticList:
            synoptics = etree.SubElement(root, "SYNOPTIC")
            for src in synopticList:
                src = os.path.join(mod_dir, src)
                dst = self.substitutionName(src, mod_dir)
                child = etree.SubElement(synoptics, "synoptic",
                                         str=os.path.basename(dst))
                # substitute any referenced files within the jdrawfiles
                f = open(src, 'r')
                contents = f.read()
                f.close()
                for ref in re.findall(r'file_name:\"(.+?)\"', contents):
                    # this is ok for both relative and absolute references
                    refsrc = os.path.join(os.path.dirname(src), ref)
                    refdst = self.substitutionName(refsrc, mod_dir)
                    if ref != refdst:
                        _short = 'Manual editing needed in "%s"' % dst
                        _long = ('The synoptic file "%s" references a file that '
                                'has been copied to the project dir in order to make the project portable. '
                                'Please edit "%s" and replace "%s" by "%s"') % (dst, dst, ref, refdst)
                        self._projectWarnings.append((_short, _long))

        # macroserver page
        if self.SARDANA_INSTALLED and self.__getitem__("macroServerName"):
            macroServerName = etree.SubElement(root, "MACROSERVER_NAME")
            macroServerName.text = self.__getitem__("macroServerName")
            doorName = etree.SubElement(root, "DOOR_NAME")
            doorName.text = self.__getitem__("doorName")
            instruments = etree.SubElement(root, "INSTRUMENTS_FROM_POOL")
            instruments.text = str(self.__getitem__("instruments"))
        # panels page
        panelList = self.__getitem__("panels")
        if panelList:
            panels = etree.SubElement(root, "PanelDescriptions")
            for panel in panelList:
                name, xml = panel
                item = etree.fromstring(xml)
                panels.append(item)
        # external apps page
        externalAppList = self.__getitem__("externalApps")
        if externalAppList:
            externalApps = etree.SubElement(root, "ExternalApps")
            for externalApp in externalAppList:
                name, xml = externalApp
                item = etree.fromstring(xml)
                externalApps.append(item)
        # monitor page
        monitor = etree.SubElement(root, "MONITOR")
        monitor.text = self.__getitem__("monitor")

        return (etree.tostring(root, pretty_print=True, encoding='unicode'),
                copy.copy(self._substitutions))

    def substitutionName(self, src, mod_dir):
        name = os.path.basename(src)
        i = 2
        if os.path.dirname(os.path.abspath(src)) != os.path.abspath(mod_dir):
            # do not change the name if it is the same dir!
            while name in self._substitutions:
                root, ext = os.path.splitext(name)
                name = "%s_%i%s" % (root, i, ext)
                i += 1
        self._substitutions[name] = src
        return name


def main():
    app = Qt.QApplication([])
    wizard = AppSettingsWizard()
    wizard.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
