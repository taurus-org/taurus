# -*- coding: utf-8 -*-

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

"""utilities to load ui files for widgets"""

from builtins import object

import os
import sys
import functools

from taurus.external.qt import Qt
from taurus.external.qt import uic


__all__ = ["loadUi",
           "UILoadable",
           ]


class __UI(object):
    pass


def loadUi(obj, filename=None, path=None, with_ui=None):
    """
    Loads a QtDesigner .ui file into the given widget.
    If no filename is given, it tries to load from a file name which is the
    widget class name plus the extension ".ui" (example: if your
    widget class is called MyWidget it tries to find a MyWidget.ui).
    If path is not given it uses the directory where the python file which
    defines the widget is located plus a *ui* directory (example: if your widget
    is defined in a file /home/homer/workspace/taurusgui/my_widget.py then it uses
    the path /home/homer/workspace/taurusgui/ui)

    :param filename: the QtDesigner .ui file name [default: None, meaning
                      calculate file name with the algorithm explained before]
    :type filename: str
    :param path: directory where the QtDesigner .ui file is located
                 [default: None, meaning calculate path with algorithm explained
                 before]
    :type path: str
    :param with_ui: if True, the objects defined in the ui file will be
                    accessible as submembers of an ui member of the widget. If
                    False, such objects will directly be members of the widget.
    :type with_ui: bool
    """
    if path is None:
        obj_file = sys.modules[obj.__module__].__file__
        path = os.path.join(os.path.dirname(obj_file), 'ui')
    if filename is None:
        filename = obj.__class__.__name__ + os.path.extsep + 'ui'
    full_name = os.path.join(path, filename)

    if with_ui is not None:
        ui_obj = __UI()
        setattr(obj, with_ui, ui_obj)
        previous_members = set(dir(obj))

        uic.loadUi(full_name, baseinstance=obj)

        post_members = set(dir(obj))
        new_members = post_members.difference(previous_members)
        for member_name in new_members:
            member = getattr(obj, member_name)
            setattr(ui_obj, member_name, member)
            delattr(obj, member_name)
    else:
        uic.loadUi(full_name, baseinstance=obj)


def UILoadable(klass=None, with_ui=None):
    """
    A class decorator intended to be used in a Qt.QWidget to make its UI
    loadable from a predefined QtDesigner UI file.
    This decorator will add a :func:`loadUi` method to the decorated class and
    optionaly a property with a name given by *with_ui* parameter.

    The folowing example assumes the existence of the ui file
    :file:`<my_widget_dir>/ui/MyWidget.ui` which is a QWidget panel with *at
    least* a QPushButton with objectName *my_button* ::

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.util.ui import UILoadable

        @UILoadable
        class MyWidget(Qt.QWidget):

            def __init__(self, parent=None):
                Qt.QWidget.__init__(self, parent)
                self.loadUi()
                self.my_button.setText("This is MY button")

    Another example using a :file:`superUI.ui` file in the same directory as
    the widget. The widget UI components can be accessed through the widget
    member *_ui* ::

        import os.path

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.util.ui import UILoadable

        @UILoadable(with_ui="_ui")
        class MyWidget(Qt.QWidget):

            def __init__(self, parent=None):
                Qt.QWidget.__init__(self, parent)
                self.loadUi(filename="superUI.ui", path=os.path.dirname(__file__))
                self._ui.my_button.setText("This is MY button")

    :param with_ui: assigns a member to the decorated class from which you
                    can access all UI components [default: None, meaning no
                    member is created]
    :type with_ui: str

    .. warning::
        the current implementation (Jul14) doesn't prevent Qt from overloading
        any members you might have defined previously by the widget object names
        from the UI file. This happens even if *with_ui* parameter is given.
        For example, if the UI contains a QPushButton with objectName
        *my_button*::

            @UILoadable(with_ui="_ui")
            class MyWidget(Qt.QWidget):

                def __init__(self, parent=None):
                    Qt.QWidget.__init__(self, parent)
                    self.my_button = "hello"
                    self.loadUi()
            widget = MyWidget()
            print widget.my_button
            <PyQt4.QtGui.QPushButton object at 0x159e2f8>

        This little problem should be solved in the next taurus version.
    """
    if klass is None:
        return functools.partial(UILoadable, with_ui=with_ui)

    klass_name = klass.__name__
    klass_file = sys.modules[klass.__module__].__file__
    klass_path = os.path.join(os.path.dirname(klass_file), 'ui')

    def _loadUi(self, filename=None, path=None):
        if filename is None:
            filename = klass_name + os.path.extsep + 'ui'
        if path is None:
            path = klass_path
        return loadUi(self, filename=filename, path=path, with_ui=with_ui)

    klass.loadUi = _loadUi
    return klass


def main():
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication([], cmd_line_parser=None)

    @UILoadable(with_ui="ui")
    class A(Qt.QWidget):

        def __init__(self, parent=None):
            Qt.QWidget.__init__(self, parent)
            import taurus.qt.qtgui.panel.ui
            path = os.path.dirname(taurus.qt.qtgui.panel.ui.__file__)
            self.loadUi(filename='TaurusMessagePanel.ui', path=path)

    gui = A()
    gui.show()
    app.exec_()

if __name__ == "__main__":
    main()
