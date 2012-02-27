
.. currentmodule:: sardana.macroserver.macro

.. _macroserver-macros:

================
Writting macros
================

This chapter provides the necessary information to write macros in sardana.
The complete macro :term:`API` can be found :ref:`here <macroserver-macro-api>`.

Concept
----------------

A macro in sardana describes a specific procedure that can be executed at any
time. Macros run inside the *sardana sanbox*. This simply means that each time
you run a macro, the system makes sure the necessary environment for it to run
safely is ready.

Macros can only be written in Python_. A macro can be a function or a class.
In order for a function to be recognized as a macro, it **must** be *decorated*
with the specital :class:`macro` *decorator*. In the same way, for a class to be
recognized as a macro, it must inherit from a :class:`Macro` super-class.
Macros are case sensitive. This means that *helloworld* is a different macro
than *HelloWorld*.

The choice between writing a macro function or a macro class depends mostly
on your background as a programmer.

If you are a scientist, and you have a programming background on a functional
language (like fortran, matlab, SPEC_), then you might prefer to write macro
functions. Computer scientists (young ones, specially), on the other hand, often
have a background on object oriented languages (Java, C++, C#) and feel more
confortable writting macro classes.

Classes tend to scale better with the size of a program or library. By writting
a macro class you can benefit from all advantages of object-oriented
programming. This means that, in theory:

    - it would reduce the amount of code you need to write
    - reduce the complexity of your code y by dividing it into small,
      reasonably independent and re-usable components, that talk to each
      other using only well-deﬁned interfaces
    - Improvement of productivity by using easily adaptable pre-deﬁned
      software components

In practice, however, and specially if you don't come from a programming
background, writing classes requires a different way of thinking. It will also
require you to extend your knowledge in terms of syntax of a programming
language.

Furthermore, most tasks you will probably need to execute as macros, often
don't fit the class paradigm that object-oriented languages offer. If you are
writting a sequencial procedure to run an experiment then you are probably
better of writting a python function which does the job plain and simple.

One reason to write a macro as a class is if, for example, you want to extend
the behaviour of the :class:`~sardana.macroserver.macros.standard.mv` macro. In
this case, probably you would want to *extend* the existing macro by writting
your own macro class which inherits from the original macro and this way benefit
from most of the functionallity already existing in the original macro.

.. _macro_writting:

Writting a macro function
-------------------------

As metioned before, macros are just simple Python_ functions which have been
*labeled* as macros. In Python_, these labels are called *decorators*. Here is
the macro function version of *Hello, World!*::
    
    from sardana.macroserver.macro import macro
    
    @macro()
    def hello_world():
        self.output("Hello, World!")
    

:line 1:
    imports the *macro* symbol from the sardana macro package.
    :mod:`sardana.macroserver.macro` is the package which contains most symbols
    you will require from sardana to write your macros.

:line 3:
    this line *decorates* de following function as a macro. It is **crucial**
    to use this decorator in order for your function to be recognized by
    sardana as a valid macro.

:line 4:
    this line contains the hello_world function definition

:line 5:
    this line will print *Hello, World!* on your screen.
    
If you already know a little about Python_ your are probably wondering two
thing:

    - Why not use ``print "Hello, World!"``
    - By now you may be wonder

Writting a macro class
----------------------

The simplest macro that you can write **MUST** obey the following rules:

    * A Macro is a Python_ class
    * Inherit from :class:`Macro`
    * Implement the :meth:`Macro.run` method

The :meth:`Macro.run` method is the place where you write the code of your macro.
So, without further delay, here is the *Hello, World!* example::

    from sardana.macroserver.macro import *
    
    class HelloWorld(Macro):
        """Hello, World! macro"""
        
        def run(self):
            print "Hello, World!"

.. _macro_add_parameters:

Adding parameters to your macro
--------------------------------

The macro :term:`API` enforces you to properly specify the macro parameters. This way,
client applications like Spock or a graphical user interfaces can dynammicaly
adapt to your macro definition.

Let's say you want to pass an integer parameter to your macro. All you have to
do is declare the parameter by using the :attr:`Macro.param_def` Macro member::

    from sardana.macroserver.macro import *
    
    class twice(Macro):
        """Macro twice. Prints the double of the given value"""

        param_def = [ [ "value", Type.Float, None, "value to be doubled" ] ]
            
        def run(self, value):
            print 2*value

.. note::
    As soon as you add a :attr:`Macro.param_def` you also need to
    modify the :meth:`Macro.run` method to support the new paramter(s).

A set of macro parameter examples can be found :ref:`here <devel-macro-parameter-examples>`.

.. _macro_preparing:

Preparing your macro for execution
------------------------------------------------

Additionaly to the :meth:`Macro.run` method, you may write a :meth:`Macro.prepare`
method where you may put code to prepare the macro for execution (for example, checking pre-conditions for running
the macro).
By default, the prepare method is an empty method.
Here is an example on how to prepare HelloWorld to run only after year 1989::

    import datetime
    from sardana.macroserver.macro import *

    class HelloWorld(Macro):
        """Hello, World! macro"""
        
        def prepare(self):
            if datetime.datetime.now() < datetime.datetime(1990,01,01):
                raise Exception("HelloWorld can only run after year 1989")
    
        def run(self):
            print "Hello, World!"

.. _macro_documentation:

Writting macro documentation
------------------------------

.. todo:: document how to write macro documentation

.. _macro_calling:

Calling other macros from inside your macro
------------------------------------------------

The Macro :term:`API` makes it possible to call other macros from inside your macro code.
The simplest way to execute a macro from inside your macro is through the :meth:`Macro.macros`
member. This is the macro container for all existing macros.
Here is an example on how to call a macro for the *call_wa* macro::

    class call_wa(Macro):
        """call_wa macro"""
    
        def run(self):
            self.macros.wa()
            
Another example calling a macro with parameters (the wm macro which receives a list
of motors as parameters)::

    class call_wm(Macro):
        """call_wm macro"""
        
        param_def = [
            ['motors', [ ['motor', Type.Motor, None, 'a motor'] ], None, 'motors to show'],
        ]

        def run(self, *m):
            self.macros.wm(*m)

An explicit call to :meth:`Macro.execMacro` would have the same effect::

    class call_scan1(Macro):
        """call_scan1 macro"""
        
        param_def = [ [ "motor", Type.Motor, None, "a motor" ] ]
        
        def run(self, motor):
            self.execMacro('ascan', motor.getName(), '0', '100', '10', '0.2')
    
:meth:`Macro.execMacro` supports passing parameters as different *flavors*:
    
    * parameters as strings: ``execMacro('ascan', motor.getName(), '0', '100', '10', '0.2')``
    * parameters as concrete types: ``self.execMacro(['ascan', motor, 0, 100, 10, 0.2])``
    * parameters as space separated string: ``self.execMacro('ascan %s 0 100 10 0.2' % motor.getName())``

Let's say that now you need access to the data generated by the sub-macro. In this
case you need to use a lower level macro call :term:`API`::

    class call_ascan(Macro):
        """call_wm macro"""
        
        param_def = ascan.param_def

        def run(self, *args):
            my_scan = self.createMacro('ascan', *args)
            self.runMacro(my_scan)
            print len(my_scan.data)

A set of macro call examples can be found :ref:`here <devel-macro-call-examples>`.

.. _macro_logging:

Logging
----------------

The Macro :term:`API` includes a set of methods that allow you to write log messages with
different levels:

    * :meth:`Macro.debug`
    * :meth:`Macro.info`
    * :meth:`Macro.warning`
    * :meth:`Macro.error`
    * :meth:`Macro.critical`
    * :meth:`Macro.log`
    * :meth:`Macro.output`
    
The special :meth:`Macro.output` has the same effect as the print statement.

Here is an example on how to write a logging information message::

    from sardana.macroserver.macro import *

    class HelloWorld(Macro):
        """Hello, World! macro"""
        
        def run(self):
            self.info("Starting to execute %s", self.__class__.__name__)
            print "Hello, World!"
            self.info("Finished to executing %s", self.__class__.__name__)


.. _ALBA: http://www.cells.es/
.. _ANKA: http://http://ankaweb.fzk.de/
.. _ELETTRA: http://http://www.elettra.trieste.it/
.. _ESRF: http://www.esrf.eu/
.. _FRMII: http://www.frm2.tum.de/en/index.html
.. _HASYLAB: http://hasylab.desy.de/
.. _MAX-lab: http://www.maxlab.lu.se/maxlab/max4/index.html
.. _SOLEIL: http://www.synchrotron-soleil.fr/


.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://packages.python.org/PyTango/
.. _Taurus: http://packages.python.org/taurus/
.. _QTango: http://www.tango-controls.org/download/index_html#qtango3
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _Python: http://www.python.org/
.. _IPython: http://ipython.scipy.org/
.. _ATK: http://www.tango-controls.org/Documents/gui/atk/tango-application-toolkit
.. _Qub: http://www.blissgarden.org/projects/qub/
.. _numpy: http://numpy.scipy.org/
.. _SPEC: http://www.certif.com/
.. _EPICS: http://www.aps.anl.gov/epics/