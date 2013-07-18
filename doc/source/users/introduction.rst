.. _introduction:

============
Introduction
============

taurus was originally conceived as a library for connecting client side
applications (CLIs and GUIs) to Tango_ device servers. 

.. note:: More recently, the scope of Taurus
          has been broadened and it is moving towards supporting pluggins for
          other control systems (e.g. Epics_, Spec_...). While many concepts of
          Taurus Design are heavily influenced by the Tango philosophy, the goal
          is to eventually provide a control-system agnostic API allowing
          different control systems to be used even simultaneously.
          Nevertheless, due to its Tango roots, this documentation may assume
          that you are using Tango.

Taurus is developed as a part of the Sardana_ project, which aims to provide an
integrated SCADA, but it can be used independently of the rest of Sardana.

For its Tango interface, Taurus uses PyTango_ which is a python binding
for the Tango_ library. It provides an abstraction layer that allows Tango to be
accessed in a pythonic, object oriented way. For the GUI part, taurus is built
on top of the graphical library PyQt_ which is a python binding for Qt_.

The goals of this library are:
 - provide a simple Tango (and other control systems) API to the end-user application
 - speed up development of tango (and other control systems) based applications
 - provide a standardized look-and-feel
 

For example, to display the values of four attributes (state, position, velocity, acceleration)
of a device (motor/icepap/01)::

    import sys
    from PyQt4 import Qt
    from taurus.qt.qtgui.panel import TaurusForm
    from taurus.qt.qtgui.application import TaurusApplication
    
    app = TaurusApplication(sys.argv)
    
    attrs = [ 'state', 'position', 'velocity', 'acceleration' ]
    model = [ 'motor/icepap/01/%s' % attr for attr in attrs ]
    
    w = TaurusForm()
    w.model = model
    w.show()
    sys.exit(app.exec_())

.. figure:: ../_static/taurusform_example01.png
  :scale: 50
  :align: center
  
  The generated GUI by the above code

The above example can even be achieved even without typing any code::

    % cd taurus/qt/qtgui/panel
    % python taurusform.py motor/icepap/01/state motor/icepap/01/position motor/icepap/01/velocity
  
In many aspects, taurus follows the same approach as the tango java application 
toolkit: Tango ATK_. If you know ATK_ you will find many things in taurus familiar.

Throughout the documentation we will assume that you have a basic knowledge of 
Tango_/PyTango_ and Qt_/PyQt_.

Although taurus is written primarily in pure python, it makes heavy use of 
PyTango_, numpy_, PyQt_ and PyQwt_ to provide good performance even when 
large amounts of data are involved.

taurus is designed with the philosophy that you should be able to create simple 
applications that are able to connect to tango servers with just a few lines of 
code or even with no code at all!

The concepts were not born from scratch. It is not our intention to reinvent the 
way applications are written. Many of the concepts were borrowed from the 
existing java tango library called ATK_. If you have used ATK_ before you will 
find many concepts familiar.

.. image:: /_static/taurus_layers.png
  :scale: 80
  :align: center

The taurus library provides a core module that does not depend on PyQt and which
is in charge of abstracting the lower level comunication with the control system
(:ref:`taurus-core-tutorial`). On top of the core, the qt module provides a
collection of widgets that can be used inside any PyQt_ based GUI
(:ref:`examples`). Recently, the proof-of-concept web module is being
implemented for providing web widgets.

.. _Sardana: http://www.sardana-controls.org/
.. _Tango: http://www.tango-controls.org/
.. _Epics: http://www.aps.anl.gov/epics/
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