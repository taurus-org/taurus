.. _taurusqtdesigner-tutorial:

============================
Taurus Qt Designer tutorial
============================

The Taurus Qt Designer tutorial is the first tutorial in the documentation 
because it will allow you to create GUIs without writting any code at all!

You should start the designer by executing on the command line::
  
  taurusdesigner

.. tip::

  ``--help`` argument will give you the complete list of options

This script will configure the qt designer environment to be used with taurus.
After the designer is started you should see something like this (Note: the 
display may not be exactly the same depending on OS, Window manager and 
Qt designer version):

.. figure:: /_static/designer01.png
  :scale: 75

You can then design your application/widget using not only the standard Qt
widgets but also the taurus widgets. 

.. _generate-code:

Generating code
----------------  

The Qt designer will produce a .ui file that is an XML representation of the
application/widget that you designed.
To generate python code you should use the **taurusuic4** tool instead of
pyqt's pyuic4 tool. 
Suppose you created a GUI called MyGUI.ui and you want to generate python code.
All you have to do is simply execute in the command line::
    
  taurusuic4 -x -o ui_MyGUI.py MyGUI.ui

.. tip::

  ``--help`` argument will give you the complete list of options
  
This will generate an executable python file called MyGUI.py. You can test the
code by doing::

  python MyGUI.py
  
How to create custom QtDesigner enabled taurus widgets
--------------------------------------------------------

It is possible to create new taurus widgets using qt designer and make them
automatically visible in the qt designer's widget catalog the next time you start
qt designer.

The first thing you must do is create a new widget from an existing Taurus widget
containter:

.. figure:: /_static/designer02.png
    :scale: 80
    
    Qt designer widget creation dialog
    
Then give the name of the frame the widget class name (let's say you call it
MyWidget):

.. figure:: /_static/designer03.png

    Qt designer widget property editor panel 
 
After you are done designing the widget save it as a .ui file (let's say
you called it mywidget.ui):

.. figure:: /_static/designer04.png

    Sample widget created in the Qt designer

and generate python code like it was described in :ref:`generate-code`::

  taurusuic4 -x -o ui_mywidget.py mywidget.ui

.. note::
    You MUST use the '-o' option if you want to enable creation of taurus widget
    code since the generated python taurus code will import the file you supply
    in the -o parameter. This means that using the syntax::
    
        taurusuic4 -x mywidget.ui > ui_mywidget.py 
  
    will work but it will NOT trigger taurus code generation (just the uic4 code
    generation).

The taurusuic4 tool will recognize that the code being generated could be a
taurus widget and it offers to generate an additional file for it::

    $ taurusuic4 -x -o ui_mywidget.py mywidget.ui
    
    Do you whish to generate a Taurus widget (N/y) ? y
    Python file name (mywidget.py) ?
    Python package name (mywidget) ?
    Python class name (MyWidget) ?
    Python super class name (TaurusWidget) ?
    Generate Qt designer info (Y/n) ? y
    Qt group (Taurus Containers) ? My Taurus
    Qt icon (:/designer/widget.png) ?
    Qt container (N/y) ?

At this time, several questions are asked, all of them have default values:

    - Do you whish to generate a Taurus widget (N/y)
        - if you answer no then no taurus code file is generated.
        
    - Python file name (mywidget.py) ?
        - which will be the name of the taurus python file. 
          Defaults to the widget class name in lower case.
    
    - Python package name (mywidget) ?
        - full python package name. If you would be doing a standard taurus widget,
          it would be 'taurus.qt.qtgui'
          
    - Python class name (MyWidget) ?
        - which will be the name of the taurus class. Defaults to the frame object name.
          You may desire to give a different name if the final widget needs some extra logic.
          In this case you can name it MyWidgetBase and afterward manually create in your code
          a subclass called MyWidget that adds all the extra logic.
          
    - Python super class name (TaurusWidget) ?
        - the python super class. Just in case you want to override the default
          super class. Use a non different class only if you are sure of what
          you are doing.
        
    - If you choose to generate qt designer information:
        - Qt group (Taurus Containers) ?
            - in which group of widgets should your widget appear in the designer
        - Qt icon (:/designer/widget.png) ?
            - which would be the icon in the designer
        - Qt container (Y/n) ?
            - wheater or not the widget you created is a container widget.
      
You should now be able to start the designer again::

    taurusdesigner --taurus-path=/home/tcoutinho/workspace/mytauruslib
    
and you should see your new widget:

.. figure:: /_static/designer05.png

  Qt designer widget catalog panel
  
    










  
      