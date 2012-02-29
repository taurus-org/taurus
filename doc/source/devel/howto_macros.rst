
.. currentmodule:: sardana.macroserver.macro

.. _macroserver-macros:

================
Writting macros
================

This chapter provides the necessary information to write macros in sardana.
The complete macro :term:`API` can be found :ref:`here <macroserver-macro-api>`.

What is a macro
----------------

A macro in sardana describes a specific procedure that can be executed at any
time. Macros run inside the *sardana sanbox*. This simply means that each time
you run a macro, the system makes sure the necessary environment for it to run
safely is ready.

Macros can only be written in Python_. A macro can be a **function** or a **class**.
In order for a function to be recognized as a macro, it **must** be properly
*labeled* as a macro (this is done with a special :class:`macro` *decorator*.
Details are explaind below). In the same way, for a class to be recognized as a
macro, it must inherit from a :class:`Macro` super-class. Macros are case
sensitive. This means that *helloworld* is a different macro than *HelloWorld*.

The choice between writing a macro function or a macro class depends not only
on the type of procedure you want to write, but also (and most importantly) on
the type of programming you are most confortable with.

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
background, writting classes requires a different way of thinking. It will also
require you to extend your knowledge in terms of syntax of a programming
language.

Furthermore, most tasks you will probably need to execute as macros, often
don't fit the class paradigm that object-oriented languages offer. If you are
writting a sequencial procedure to run an experiment then you are probably
better of writting a python function which does the job plain and simple.

One reason to write a macro as a class is if, for example, you want to extend
the behaviour of the :class:`~sardana.macroserver.macros.standard.mv` macro. In
this case, probably you would want to *extend* the existing macro by writting
your own macro class which *inherits* from the original macro and this way
benefit from most of the functionallity already existing in the original macro.

.. _macro_writting:

Writting a macro function
-------------------------

As metioned before, macros are just simple Python_ functions which have been
*labeled* as macros. In Python_, these labels are called *decorators*. Here is
the macro function version of *Hello, World!*::
    
    from __future__ import print_function
    
    from sardana.macroserver.macro import macro
    
    @macro()
    def hello_world():
        """This is an hello world macro"""
        print("Hello, World!")

**line 1**
    activates the new style print function. You **must** include this line if
    your macro needs to write something to the output and you use a Python_
    version < 3.0 [#f1]_

**line 3**
    imports the *macro* symbol from the sardana macro package.
    :mod:`sardana.macroserver.macro` is the package which contains most symbols
    you will require from sardana to write your macros.

**line 5**
    this line *decorates* de following function as a macro. It is **crucial**
    to use this decorator in order for your function to be recognized by
    sardana as a valid macro.

**line 6**
    this line contains the hello_world function definition

**line 7**
    Documentation for this macro. You should **always** document your macro!

**line 8**
    this line will print *Hello, World!* on your screen.
    
If you already know a little about Python_ your are probably wondering why not
use ``print "Hello, World!"``?

    Remember that your macro will be executed by a MacroServer which may be
    in a different computer than the computer you are working on. Part of the
    process of converting a function into a macro is too rewrite the original
    :class:`macro` *decorator* to print in your screen instead of the
    screen of the computer where the server is running. The :class:`macro`
    *decorator* can do this for the new :func:`print` function but
    not for the old `print` statement. Anyway, since the old `print`
    statement will disappear soon, it is good practice to always use
    :func:`print` function. [#f2]_
    
Adding parameters to your macro
--------------------------------

Standard Python_ allows you to specify parameters to a function by placing comma
separated parameter names between the ``()`` in the function definition. The
macro :term:`API`, in adition, enforces you to specify some extra parameter
information. At first, this may look like a useless complication, but you will
apreciate clear benefits soon enough. Here are some of them:

    - error prevention: a macro will not be allowed to run if the given
      parameter if of a wrong type
    - :term:`CLI`\s like Spock will be able to offer autocomplete facilities
      (press <tab> and list of allowed parameters show up)
    - :term:`GUI`\s can display list of allowed parameter values in combo boxes
      which gives increased usability and prevents errors
    - Documentation can be generated automatically

So, here is an example on how to define a macro that needs one parameter::

    from __future__ import print_function
    
    from sardana.macroserver.macro import macro
    
    @macro([["moveable", Type.Moveable, None, "moveable to get position"]])
    def where_moveable(moveable):
        """This macro prints the current moveable position"""
        print("Motor is at ", moveable.getPosition())


Here is another example on how to define a macro that needs two parameters:

    - Moveable (motor, pseudo motor)
    - Float (motor absolute position to go to)

::

    from __future__ import print_function
    
    from sardana.macroserver.macro import macro
    
    @macro([ ["moveable", Type.Moveable, None, "moveable to move"],
             ["position", Type.Float, None, "absolute position"] ])
    def move(moveable, position):
        """This macro moves a moveable to the specified position"""
        moveable.move(position)
        print("Motor ended at ", moveable.getPosition())

The parameter information is a :obj:`list` of :obj:`list`\s. Each :obj:`list`
being a composed of four elements:

    - parameter name
    - parameter type
    - parameter default value (None means no default value)
    - parameter description
    
Here is a list of allowed parameter types::

    - 

Calling other macros from inside your macro
--------------------------------------------

One of the functions of the macro decorator is to pass the *knowledge* of all
existing macros to your macro. This way, without any special imports, your macro
will *know* about all other macros on the system even if they have been written
in other files.

Lets recreate the two previous macros (*where_moveable* and *move*) to execute
two of the macros that exist in the standard macro catalog
(:class:`~sardana.macroserver.macros.standard.wm` and
:class:`~sardana.macroserver.macros.standard.mv`)

Here is the new version of *where_moveable* ::

    from __future__ import print_function
    
    from sardana.macroserver.macro import macro
    
    @macro([["moveable", Type.Moveable, None, "moveable to get position"]])
    def where_moveable(moveable):
        """This macro prints the current moveable position"""
        wm(moveable)

... and the new version of *move* ::

    from __future__ import print_function
    
    from sardana.macroserver.macro import macro
    
    @macro([ ["moveable", Type.Moveable, None, "moveable to move"],
             ["position", Type.Float, None, "absolute position"] ])
    def move(moveable, position):
        """This macro moves a moveable to the specified position"""
        mv(moveable, position)
        print("Motor ended at ", moveable.getPosition())

Macro context
--------------

One of the most powerfull features of macros is that the entire context of
sardana is at your disposal. Simply put, it means you have access to all sardana
elements by means of a variable called ``self``.

``self`` provides access to an extensive catalog of functions you can use in
your macro to do all kinds of things. The complete catalog of functions can be
found :ref:`here <macroserver-macro-api>`.

Let's say you want to write a macro that explicitly moves a known *theta* motor
to a certain position. You could write a macro which receives the motor as
parameter but that would be a little silly since you already know beforehand
which motor you will move. Instead, a better solution would be to *ask* sardana
for a motor named "theta" and use it directly. Here is how you can acomplish
that::

... and the new version of *move* ::

    from __future__ import print_function
    
    from sardana.macroserver.macro import macro
    
    @macro([["position", Type.Float, None, "absolute position"]])
    def move_theta(moveable, position):
        """This macro moves theta to the specified position"""
        mv(moveable, position)
        print("Motor ended at ", moveable.getPosition())

Writting a macro class
----------------------

This chapter describes an advanced alternative to writting macros as Python_
classes.
If words like *inheritance*, *polimorphism* sound like a lawyer's horror movie
then you probably should only read on if someone expert in sardana told you that
the task you intend to do cannot be accomplished by writting macro functions.

The simplest macro that you can write **MUST** obey the following rules:

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

.. rubric:: Footnotes

.. [#f1] To check which version of Python_ you are using type on the command
         line::
             
             $ python -c "import sys; print sys.version"
             2.7.1+ (r271:86832, Apr 11 2011, 18:05:24)
             [GCC 4.5.2]

.. [#f2] An alternative to :func:`print` is the usage of :meth:`~Macro.output`.
         Hello, World! would look like this::
         
             from sardana.macroserver.macro import macro
            
             @macro()
             def hello_world():
                 self.output("Hello, World!")
        
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