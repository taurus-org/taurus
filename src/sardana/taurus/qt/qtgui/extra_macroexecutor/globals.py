#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""
globals.py: 
"""

ORGANIZATION_NAME = "Taurus"

MACROEXECUTOR_APPLICATION_NAME = "macroexecutor"
SEQUENCER_APPLICATION_NAME = "sequencer"

SEQUENCES_DIRNAME = "Sequences"
SEQUENCE_DEFAULT_FILENAME = "Untitled.xml"

FAVOURITES_FILENAME = "favourite_macros.xml"

MACROS_HISTORY_FILENAME = ".macros_history"
MACROS_HISTORY_LENGHT = 5

TITLE_MACROSERVER_DIALOG = "Choose MacroServer"
TITLE_OUTPUT_DOCK_WIDGET = "Output"
TITLE_SPOCK_DOCK_WIDGET = "Spock"
TITLE_DEBUG_DOCK_WIDGET = "Debug"
TITLE_RESULT_DOCK_WIDGET = "Result"
TITLE_DESCRIPTION_DOCK_WIDGET = "Macro description"
TITLE_SEQUENCE_EDITOR_DOCK_WIDGET = "Sequence editor"
TITLE_MACRO_EXECUTOR_DOCK_WIDGET = "Macro executor"

MENU_FILE = "File"
MENU_FILE_CONFIGURATION = "Configuration"
MENU_FILE_NEW = "New"
MENU_FILE_OPEN = "Open..."
MENU_FILE_SAVE = "Save"
MENU_FILE_SAVEAS = "Save as..."
MENU_FILE_QUIT = "Quit"

MENU_CONTROL = "Control"
MENU_CONTROL_PLAY_SEQUENCE = "Play sequence"
MENU_CONTROL_PLAY_MACRO = "Play macro"
MENU_CONTROL_PAUSE = "Pause"
MENU_CONTROL_STOP = "Stop"

MENU_FAVOURITES = "Add to favourites"

MENU_VIEW = "View"

MENU_SETTINGS = "Settings"
MENU_SETTINGS_ONLYSCANS = "Only scan macros"

TIP_MENU_FILE_CONFIGURATION = "Configuration"
TIP_MENU_FILE_QUIT = "Quit application"
TIP_MENU_FILE_NEW = "New sequence"
TIP_MENU_FILE_OPEN = "Open sequence..."
TIP_MENU_FILE_SAVE = "Save sequence"
TIP_MENU_FILE_SAVEAS = "Save sequence as..."

TIP_MENU_CONTROL_PLAY_SEQUENCE = "Play sequence"
TIP_MENU_CONTROL_PLAY_MACRO = "Play macro"
TIP_MENU_CONTROL_PAUSE = "Pause"
TIP_MENU_CONTROL_STOP = "Stop"

TIP_MENU_FAVOURITES = "Add to favourites"


SHORTCUT_MENU_FILE_CONFIGURATION = "F2"
SHORTCUT_MENU_FILE_NEW = "Ctrl+N"
SHORTCUT_MENU_FILE_OPEN = "Ctrl+O"
SHORTCUT_MENU_FILE_SAVE = "Ctrl+S"
SHORTCUT_MENU_FILE_SAVEAS = "Ctrl+Shift+S"
SHORTCUT_MENU_FILE_QUIT = "Ctrl+Q"

SCAN_MACROS_FILTER = "scan"
ALLOWS_HOOKS_FILTER = 'allowsHooks'


PARAM_REPEAT = "ParamRepeat"

PARAM_OBJECT = "Object"
PARAM_MOTOR = "Motor"
PARAM_PSEUDOMOTOR = "PseudoMotor"
PARAM_MOVEABLE = "Moveable"
PARAM_CONTROLLER_CLASS = "ControllerClass"
PARAM_CONTROLLER = "Controller"
PARAM_MOTOR_PARAM = "MotorParam"
PARAM_MEASUREMENT_GROUP = "MeasurementGroup"
PARAM_IO_REGISTER = "IORegister"
PARAM_COMMUNICATION_CHANNEL = "ComChannel"
PARAM_EXPERIMENTAL_CHANNEL = "ExpChannel"
PARAM_MACRO_CODE = "MacroCode"
PARAM_MACRO_CLASS = "MacroClass"
PARAM_MACRO_FUNCTION = "MacroFunction"
PARAM_MACRO_LIBRARY = "MacroLibrary"


PARAM_STRING = "String"

PARAM_FILENAME = "FileName"

PARAM_FILENAME_2 = "Filename"

PARAM_INTEGER = "Integer"

PARAM_FLOAT = "Float"

PARAM_FILEDIALOG = "File"

PARAM_USERNAME = "User"

PARAM_BOOLEAN = "Boolean"

MAX_REPEATS = "max"
MIN_REPEATS = "min"

EDITOR_COMBOBOX_PARAMS = [PARAM_OBJECT,
                          PARAM_MOTOR,
                          PARAM_PSEUDOMOTOR,
                          PARAM_MOVEABLE,
                          PARAM_CONTROLLER_CLASS,
                          PARAM_CONTROLLER,
                          PARAM_MOTOR_PARAM,
                          PARAM_MEASUREMENT_GROUP,
                          PARAM_IO_REGISTER,
                          PARAM_COMMUNICATION_CHANNEL,
                          PARAM_EXPERIMENTAL_CHANNEL,
                          PARAM_MACRO_CODE,
                          PARAM_MACRO_CLASS,
                          PARAM_MACRO_FUNCTION,
                          PARAM_MACRO_LIBRARY]

EDITOR_LINEEDIT_PARAMS = [PARAM_STRING,
                          PARAM_FILENAME,
                          PARAM_FILENAME_2,
                          "Env"]

EDITOR_SPINBOX_PARAMS = [PARAM_INTEGER]

EDITOR_DOUBLESPINBOX_PARAMS = [PARAM_FLOAT]

EDITOR_FILEDIALOG_PARAMS = [PARAM_FILEDIALOG]

EDITOR_BOOLEAN_PARAMS = [PARAM_BOOLEAN]

EDITOR_NONEDITABLE_PARAMS = [PARAM_USERNAME]

TAG_MACRO = 'macro'
TAG_PARAM = 'param'
TAG_PARAMREPEAT = 'paramrepeat'
TAG_REPEAT = 'repeat'
TAG_PARAMS = 'params'
TAG_SEQUENCE = 'sequence'
TAG_ALLOWED_HOOK = 'allowedHook'
TAG_HOOK = 'hookPlaces'

ATTRIBUTE_NAME = 'name'
ATTRIBUTE_VALUE = 'value'
ATTRIBUTE_INDEX = 'nr'
ATTRIBUTE_DESCRIPTION = 'description'
ATTRIBUTE_DEFVALUE = 'defvalue'
ATTRIBUTE_TYPE = 'type'
ATTRIBUTE_ALLOWEDHOOKS = 'allowedHooks'
ATTRIBUTE_HASPARAMS = 'hasParams'
ATTRIBUTE_MIN = 'min'
ATTRIBUTE_MAX = 'max'
