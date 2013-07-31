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

"""This module provides a demo for the
:class:`taurus.qt.qtgui.display.TaurusLabel` widget """

__all__ = ["demo", "main"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt


def demo():
    import sys
    import taurus.qt.qtgui.application
    import taurus.qt.qtgui.display
    import taurus.qt.qtgui.resource

    getPixmap = taurus.qt.qtgui.resource.getPixmap
    Application = taurus.qt.qtgui.application.TaurusApplication
    QPixmapWidget = taurus.qt.qtgui.display.QPixmapWidget

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        app = Application()

    M = 2

    class QPixmapWidgetTestPanel(Qt.QWidget):

        def __init__(self, parent=None):
            Qt.QWidget.__init__(self, parent)
            panel_l = Qt.QVBoxLayout()
            self.setLayout(panel_l)
            panel_l.setContentsMargins(M, M, M, M)
            panel_l.setSpacing(M)

            w = QPixmapWidget()
            display_panel = Qt.QGroupBox("Pixmap Widget Display")
            display_l = Qt.QHBoxLayout()
            display_l.setContentsMargins(M, M, M, M)
            display_l.setSpacing(M)
            display_panel.setLayout(display_l)
            display_l.addWidget(w, 1)

            control_panel = Qt.QGroupBox("Control Panel")
            control_l = Qt.QFormLayout()
            control_l.setContentsMargins(M, M, M, M)
            control_l.setSpacing(M)
            control_panel.setLayout(control_l)
            pixmap_widget = Qt.QLineEdit()
            aspect_ratio_widget = Qt.QComboBox()
            transformation_widget = Qt.QComboBox()
            halign_widget = Qt.QComboBox()
            valign_widget = Qt.QComboBox()
            control_l.addRow("pixmap:", pixmap_widget)
            control_l.addRow("Aspect ratio mode:", aspect_ratio_widget)
            control_l.addRow("Transformation mode:", transformation_widget)
            control_l.addRow("Horiz. alignment:", halign_widget)
            control_l.addRow("Vert. alignment:", valign_widget)

            panel_l.addWidget(display_panel, 1)
            panel_l.addWidget(control_panel, 0)

            aspect_ratio_widget.addItems(["Ignore", "Keep", "Keep by expanding"])
            transformation_widget.addItems(["Fast", "Smooth"])
            halign_widget.addItem("Left", Qt.QVariant(Qt.Qt.AlignLeft))
            halign_widget.addItem("Center", Qt.QVariant(Qt.Qt.AlignHCenter))
            halign_widget.addItem("Right", Qt.QVariant(Qt.Qt.AlignRight))
            valign_widget.addItem("Top", Qt.QVariant(Qt.Qt.AlignTop))
            valign_widget.addItem("Center", Qt.QVariant(Qt.Qt.AlignVCenter))
            valign_widget.addItem("Bottom", Qt.QVariant(Qt.Qt.AlignBottom))

            Qt.QObject.connect(pixmap_widget, Qt.SIGNAL("textChanged(const QString &)"), self.changePixmap)
            Qt.QObject.connect(aspect_ratio_widget, Qt.SIGNAL("currentIndexChanged(int)"), self.changeAspectRatio)
            Qt.QObject.connect(transformation_widget, Qt.SIGNAL("currentIndexChanged(int)"), self.changeTransformationMode)
            Qt.QObject.connect(halign_widget, Qt.SIGNAL("currentIndexChanged(int)"), self.changeAlignment)
            Qt.QObject.connect(valign_widget, Qt.SIGNAL("currentIndexChanged(int)"), self.changeAlignment)

            self.w = w
            self.w_pixmap = pixmap_widget
            self.w_aspect_ratio = aspect_ratio_widget
            self.w_transformation = transformation_widget
            self.w_halign = halign_widget
            self.w_valign = valign_widget

            pixmap_widget.setText(":leds/images256/led_red_on.png")
            aspect_ratio_widget.setCurrentIndex(1)
            transformation_widget.setCurrentIndex(1)
            halign_widget.setCurrentIndex(0)
            valign_widget.setCurrentIndex(1)

        def changePixmap(self, name):
            self.w.pixmap = getPixmap(name)

        def changeAspectRatio(self, i):
            v = Qt.Qt.IgnoreAspectRatio
            if i == 1:
                v = Qt.Qt.KeepAspectRatio
            elif i == 2:
                v = Qt.Qt.KeepAspectRatioByExpanding
            self.w.setAspectRatioMode(v)

        def changeTransformationMode(self, i):
            v = Qt.Qt.FastTransformation
            if i == 1:
                v = Qt.Qt.SmoothTransformation
            self.w.setTransformationMode(v)

        def changeAlignment(self, i):
            halign = self.w_halign.itemData(self.w_halign.currentIndex())
            halign = Qt.from_qvariant(halign, int)
            valign = self.w_valign.itemData(self.w_valign.currentIndex())
            valign = Qt.from_qvariant(valign, int)
            self.w.alignment = halign | valign

    panel = Qt.QWidget()
    layout=Qt.QGridLayout()
    panel.setLayout(layout)
    layout.setContentsMargins(M, M, M, M)
    layout.setSpacing(M)
    p1 = QPixmapWidgetTestPanel()
    layout.addWidget(p1, 0, 0)
    panel.show()
    if owns_app:
        sys.exit(app.exec_())
    else:
        return panel

def main():
    return demo()

if __name__ == "__main__":
    main()
