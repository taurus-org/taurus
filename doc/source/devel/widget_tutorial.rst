
.. currentmodule:: taurus.qt.qtgui

.. _taurus-widget-tutorial:

======================
taurus widget tutorial
======================



.. todo::
    Update this page to Taurus. In the meanwhile, you can check the :ref:`examples`

..
    **UNDER CONSTRUCTION: OUT OF DATE**
    
    The widget package is a PyQt_ based library of widgets designed to represent 
    Tango_ data.
    The widget library provides not only basic widgets like labels, text fields and
    combo boxes, but also containers like frames, group boxes or graphics and 
    synoptics.
    
    .. _TaurusLabel-tutorial:
    
    TaurusLabel tutorial
    ----------------------
    
    The :class:`TaurusLabel` is a taurus widget designed to display the read value
    of an attribute.
    
    .. figure:: /_static/label01.png
      :align: center
      
    Simple display value
    ~~~~~~~~~~~~~~~~~~~~
    
    The simplest example of :class:`TauValueLabel`
    
    .. figure:: /_static/label01.png
      :align: center
      
    code::
    
        import sys
        from PyQt4 import Qt
        import tau.widget
    
        app = Qt.QApplication(sys.argv)
    
        w = tau.widget.TauValueLabel()
        w.setModel('sys/tautest/1/position')
    
        panel.setVisible(True)
        sys.exit(app.exec_())
    
    Hint:
        1. Try to execute the code above and place the mouse over the widget. After
           a couple of seconds an automatically generated tooltip will show up.
        2. Try to execute the code above and, without closing the tau application,
           change the format of the position attribute in the sys/tautest/1 from 6.2f 
           to 8.2f (using Jive, for example). Will will notice that the displayed value
           will change immediately (tango event system must be online in order for 
           this to work!).
    
    Using parent model
    ~~~~~~~~~~~~~~~~~~
    
    Demonstrates how to use the *showQuality* and *useParentModel* with 
    :class:`TauValueLabel` being inside another tau container: the :class:`TauWidget`
    
    .. figure:: /_static/label04.png
      :align: center
    
    code::
    
        import sys
        from PyQt4 import Qt
        import tau.widget
    
        app = Qt.QApplication(sys.argv)
        panel = tau.widget.TauWidget()
        layout = Qt.QVBoxLayout()
        panel.setLayout(layout)
        panel.setModel('sys/tautest/1')
        w1 = tau.widget.TauValueLabel()
        w2 = tau.widget.TauValueLabel()
        w3 = tau.widget.TauValueLabel()
        w1.setUseParentModel(True)
        w2.setUseParentModel(True)
        w3.setUseParentModel(True)
        w1.setModel('/state')
        w2.setModel('/position')
        w3.setModel('/simulationmode')
        w1.setShowQuality(False)
    
        layout.addWidget(w1)
        layout.addWidget(w2)
        layout.addWidget(w3)
        panel.setVisible(True)
    
        sys.exit(app.exec_())
    
    TauStateLabel tutorial
    ----------------------
    
    The :class:`TauStateLabel` is a tau widget designed to display the state of a
    device both with the background color.
    
    .. figure:: /_static/label05.png
      :align: center
    
    Because :class:`TauStateLabel` inherits from :class:`TauValueLabel`, all 
    :class:`TauValueLabel` properties are available.
    
    **model**:
        The model for the :class:`TauStateLabel` only accepts state attributes!
    
    **showQualityForeground**:
        - *Type*: bool
        - *Default value:* True
        - *Description*: When set to True, it uses the attribute quality to display
          the text foreground color
    
    Simple display state
    ~~~~~~~~~~~~~~~~~~~~
    
    The simplest example of :class:`TauStateLabel`
    
    .. figure:: /_static/label05.png
      :align: center
    
    code::
    
        import sys
        from PyQt4 import Qt
        import tau.widget
    
        app = Qt.QApplication(sys.argv)
        panel = Qt.QWidget()
        layout = Qt.QHBoxLayout()
        panel.setLayout(layout)
        w = tau.widget.TauStateLabel()
        w.setModel('sys/tautest/1/state')
        layout.addWidget(w)
        panel.setVisible(True)
    
        sys.exit(app.exec_())
    
    Array of state display
    ~~~~~~~~~~~~~~~~~~~~~~
    
    This example shows how to display multiple device states using a small area
    of the GUI.
    This example assumes there are 8 devices running with names: 'sys/tautest/<1-8>'
    
    .. figure:: /_static/label06.png
      :align: center
      
    code::
    
        import sys
        from PyQt4 import Qt
        import tau.widget
    
        app = Qt.QApplication(sys.argv)
        panel = Qt.QWidget()
        layout = Qt.QGridLayout()
        panel.setLayout(layout)
        for y in range(4):
            for x in range(2):
                w = tau.widget.TauStateLabel()
                w.setModel('sys/tautest/%d/state' % ((y+1)+4*x))
                w.setShowText(False)
                layout.addWidget(w,x,y)
        panel.setVisible(True)
    
        sys.exit(app.exec_())
    
    TauConfigLabel tutorial
    -----------------------
    
    @TODO
      
    .. _Tango: http://www.tango-controls.org/
    .. _PyTango: http://packages.python.org/PyTango/
    .. _QTango: http://www.tango-controls.org/download/index_html#qtango3
    .. _`PyTango installation steps`: http://packages.python.org/PyTango/start.html#getting-started
    .. _Qt: http://qt.nokia.com/products/
    .. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
    .. _PyQwt: http://pyqwt.sourceforge.net/
    .. _IPython: http://ipython.scipy.org/
    .. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
    .. _Qub: http://www.blissgarden.org/projects/qub/
    .. _numpy: http://numpy.scipy.org/
    .. _SPEC: http://www.certif.com/
    .. _EPICS: http://www.aps.anl.gov/epics/