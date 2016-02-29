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

"""This module contains a taurus qt style called nebula"""

__all__ = ["getStyle", "getStyleSheet"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt

_NEBULA_KEYS = {
    'border_radius': '4px',
    'titlebar_background_color': 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(200, 200, 200), stop: 1 rgb(150, 150, 150))',
    'selected_titlebar_background_color': 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(60, 150, 255), stop: 1 rgb(0, 65, 200))',
    'single_titlebar_background_color': 'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(90, 180, 255), stop: 1 rgb(30, 95, 250))',
    'titlebar_color': 'white',
    'selected_titlebar_color': 'white',
    'content_background_color': 'qlineargradient(x1: 0, y1: 0, x2: 1.0, y2: 1.0, stop: 0 rgb(224, 224, 224), stop: 1 rgb(255, 255, 255))'
}

_NEBULA_STYLESHEET = \
    """QToolBox:tab {{
    color: {titlebar_color};
    border-width: 0px;
    border-style: solid;
    border-color: rgb(0, 65, 200);
    border-top-left-radius: 0px;
    border-top-right-radius: {border_radius};
    border-bottom-left-radius: {border_radius};
    border-bottom-right-radius: {border_radius};
    background-color: {titlebar_background_color};
}}

QToolBox:tab:selected {{
    background-color: {selected_titlebar_background_color};
}}

QToolBox:tab:first {{
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}}

QToolBox:tab:last {{
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
}}

QToolBox:tab:only-one {{
    background-color: {single_titlebar_background_color};
}}

QDockWidget {{
    color: {titlebar_color};
    background-color: {content_background_color};
    titlebar-close-icon: url(:/titlebar_close_black.png);
    titlebar-normal-icon: url(:/titlebar_undock_black.png);
}}

QDockWidget::title {{
    text-align: left;
    padding-left: {border_radius};

    border-top-left-radius: {border_radius};
    border-top-right-radius: {border_radius};
    border-bottom-left-radius: {border_radius};
    border-bottom-right-radius: {border_radius};

    background-color: {selected_titlebar_background_color};
}}

 QGroupBox {{
    border: 1px solid;
    border-color: rgb(0, 65, 200);
    border-radius: {border_radius};
    margin-top: 1.5ex;
    padding-top: 8px;
    background-color: {content_background_color};
 }}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding-top: 1px;
    padding-right: 3px;
    padding-bottom: 2px;
    padding-left: 3px;
    border-width: 0px;
    border-radius: {border_radius};
    color:white;
    background-color: {selected_titlebar_background_color};
    left: 5px;
}}

 QGroupBox::indicator {{
    width: 15px;
    height: 15px;
}}

QTabWidget {{

}}

QTabWidget::tab-bar {{
    left: 6px;
}}

QTabWidget::pane {{
    border: 1px solid;
    border-color: rgb(0, 65, 200);
    border-top-left-radius: {border_radius};
    border-top-right-radius: {border_radius};
    border-bottom-left-radius: {border_radius};
    border-bottom-right-radius: {border_radius};
    background-color: {content_background_color};
}}

QTabBar::tab {{
    color:white;
    border-bottom-color: rgb(0, 65, 200);
    background-color: {titlebar_background_color};
    min-width: 8ex;
    padding: 2px;
}}

QTabBar::tab:top {{
    border-top-left-radius: {border_radius};
    border-top-right-radius: {border_radius};
}}

QTabBar::tab:bottom {{
    border-bottom-left-radius: {border_radius};
    border-bottom-right-radius: {border_radius};
}}

QTabBar::tab:selected {{
    background-color: {selected_titlebar_background_color};
}}


/*
 QMainWindow::separator {{
    background: yellow;
    width: 2px;
    height: 2px;
 }}

 QMainWindow::separator:hover {{
    background: red;
 }}

 */


"""

NEBULA_STYLESHEET = _NEBULA_STYLESHEET.format(**_NEBULA_KEYS)


def getStyle():
    return None


def getStyleSheet():
    return NEBULA_STYLESHEET
