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

"""This module provides a demo for the :class:`taurus.qt.qtgui.display.TaurusLabel`
widget """

__all__ = ["demo", "main"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

def demo():
    import sys
    import taurus.qt.qtgui.application
    import taurus.qt.qtgui.gauge
    import taurus.qt.qtgui.resource

    getPixmap = taurus.qt.qtgui.resource.getPixmap
    Application = taurus.qt.qtgui.application.TaurusApplication
    QManoMeter = taurus.qt.qtgui.gauge.QManoMeter
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        app = Application()

    M = 2

    class QManoMeterTestPanel(Qt.QWidget):
        
        def __init__(self, parent=None):
            Qt.QWidget.__init__(self, parent)
            panel_l = Qt.QVBoxLayout()
            self.setLayout(panel_l)
            panel_l.setContentsMargins(M, M, M, M)
            panel_l.setSpacing(M)

            w = QManoMeter()
            w.setMinimumSize(256, 256)
            display_panel = Qt.QGroupBox("QMeter Display")
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
            value_widget = Qt.QDoubleSpinBox()
            minimum_widget = Qt.QDoubleSpinBox()
            maximum_widget = Qt.QDoubleSpinBox()
            minimum_alarm_widget = Qt.QDoubleSpinBox()
            minimum_warning_widget = Qt.QDoubleSpinBox()
            maximum_alarm_widget = Qt.QDoubleSpinBox()
            maximum_warning_widget = Qt.QDoubleSpinBox()
            steps_widget = Qt.QSpinBox()
            value_offset_widget = Qt.QDoubleSpinBox()
            digit_offset_widget = Qt.QDoubleSpinBox()
            frame_width_widget = Qt.QSpinBox()
            angle_widget = Qt.QDoubleSpinBox()
            scale_color_widget = Qt.QCheckBox()
            scale_ticks_widget = Qt.QCheckBox()
            scale_text_widget = Qt.QCheckBox()
            value_text_widget = Qt.QCheckBox()
            
            control_l.addRow("Value:", value_widget)
            control_l.addRow("Minimum:", minimum_widget)
            control_l.addRow("Min. alarm:", minimum_alarm_widget)
            control_l.addRow("Min. warning:", minimum_warning_widget)
            control_l.addRow("Max. warning:", maximum_warning_widget)
            control_l.addRow("Max. alarm:", maximum_alarm_widget)
            control_l.addRow("Maximum:", maximum_widget)
            control_l.addRow("Steps:", steps_widget)
            control_l.addRow("Value offset:", value_offset_widget)
            control_l.addRow("Digit offset:", digit_offset_widget)
            control_l.addRow("Frame width:", frame_width_widget)
            control_l.addRow("Angle:", angle_widget)
            control_l.addRow("Scale color", scale_color_widget)
            control_l.addRow("Scale ticks", scale_ticks_widget)
            control_l.addRow("Scale text", scale_text_widget)
            control_l.addRow("Value text", value_text_widget)
            
            panel_l.addWidget(display_panel, 1)
            panel_l.addWidget(control_panel, 0)

            value_widget.setRange(-1000.0, 1000.0)
            minimum_widget.setRange(-1000.0, 1000.0)
            minimum_alarm_widget.setRange(-1000.0, 1000.0)
            minimum_warning_widget.setRange(-1000.0, 1000.0)
            maximum_warning_widget.setRange(-1000.0, 1000.0)
            maximum_alarm_widget.setRange(-1000.0, 1000.0)
            maximum_widget.setRange(-1000.0, 1000.0)
            steps_widget.setRange(2, 100)
            value_offset_widget.setRange(-1000.0, 1000.0)
            digit_offset_widget.setRange(-1000.0, 1000.0)
            frame_width_widget.setRange(0, 100)
            angle_widget.setRange(0.0, 360.0)
            value_widget.setValue(w.value)
            minimum_widget.setValue(w.minimum)
            minimum_alarm_widget.setValue(w.minimumAlarm)
            minimum_warning_widget.setValue(w.minimumWarning)
            maximum_warning_widget.setValue(w.maximumWarning)
            maximum_alarm_widget.setValue(w.maximumAlarm)
            maximum_widget.setValue(w.maximum)
            steps_widget.setValue(w.steps)
            value_offset_widget.setValue(w.valueOffset)
            digit_offset_widget.setValue(w.digitOffset)
            frame_width_widget.setValue(w.frameWidth)
            angle_widget.setValue(w.angle)
            scale_color_widget.setChecked(w.showScaleColor)
            scale_ticks_widget.setChecked(w.showScaleTicks)
            scale_text_widget.setChecked(w.showScaleText)
            value_text_widget.setChecked(w.showValueText)
            
            Qt.QObject.connect(value_widget, Qt.SIGNAL("valueChanged(double)"), w.setValue)
            Qt.QObject.connect(minimum_widget, Qt.SIGNAL("valueChanged(double)"), w.setMinimum)
            Qt.QObject.connect(minimum_alarm_widget, Qt.SIGNAL("valueChanged(double)"), w.setMinimumAlarm)
            Qt.QObject.connect(minimum_warning_widget, Qt.SIGNAL("valueChanged(double)"), w.setMinimumWarning)
            Qt.QObject.connect(maximum_warning_widget, Qt.SIGNAL("valueChanged(double)"), w.setMaximumWarning)
            Qt.QObject.connect(maximum_alarm_widget, Qt.SIGNAL("valueChanged(double)"), w.setMaximumAlarm)
            Qt.QObject.connect(maximum_widget, Qt.SIGNAL("valueChanged(double)"), w.setMaximum)
            Qt.QObject.connect(steps_widget, Qt.SIGNAL("valueChanged(int)"), w.setSteps)
            Qt.QObject.connect(value_offset_widget, Qt.SIGNAL("valueChanged(double)"), w.setValueOffset)
            Qt.QObject.connect(digit_offset_widget, Qt.SIGNAL("valueChanged(double)"), w.setDigitOffset)
            Qt.QObject.connect(frame_width_widget, Qt.SIGNAL("valueChanged(int)"), w.setFrameWidth)
            Qt.QObject.connect(angle_widget, Qt.SIGNAL("valueChanged(double)"), w.setAngle)
            Qt.QObject.connect(scale_color_widget, Qt.SIGNAL("toggled(bool)"), w.setShowScaleColor)
            Qt.QObject.connect(scale_ticks_widget, Qt.SIGNAL("toggled(bool)"), w.setShowScaleTicks)
            Qt.QObject.connect(scale_text_widget, Qt.SIGNAL("toggled(bool)"), w.setShowScaleText)
            Qt.QObject.connect(value_text_widget, Qt.SIGNAL("toggled(bool)"), w.setShowValueText)
            
            self.w = w
            self.w_minimum = minimum_widget
            self.w_minimum_alarm = minimum_alarm_widget
            self.w_minimum_warning = minimum_warning_widget
            self.w_maximum_warning = maximum_warning_widget
            self.w_maximum_alarm = maximum_alarm_widget
            self.w_maximum = maximum_widget
            self.w_steps = steps_widget
            self.w_value_offset = value_offset_widget
            self.w_digit_offset = digit_offset_widget
            self.w_angle = angle_widget
        
    panel = Qt.QWidget()
    layout=Qt.QGridLayout()
    panel.setLayout(layout)
    layout.setContentsMargins(M, M, M, M)
    layout.setSpacing(M)
    p1 = QManoMeterTestPanel()
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