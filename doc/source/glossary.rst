
.. _sardana-glossary:

===========
Glossary
===========

.. glossary::
    :sorted:

    ``>>>``
        The default Python prompt of the interactive shell.  Often seen for code
        examples which can be executed interactively in the interpreter.

    ``...``
        The default Python prompt of the interactive shell when entering code for
        an indented code block or within a pair of matching left and right
        delimiters (parentheses, square brackets or curly braces).

    argument
        A value passed to a function or method, assigned to a named local
        variable in the function body.  A function or method may have both
        positional arguments and keyword arguments in its definition.
        Positional and keyword arguments may be variable-length: ``*`` accepts
        or passes (if in the function definition or call) several positional
        arguments in a list, while ``**`` does the same for keyword arguments
        in a dictionary.

        Any expression may be used within the argument list, and the evaluated
        value is passed to the local variable.

    attribute
        A value associated with an object which is referenced by name using
        dotted expressions.  For example, if an object *o* has an attribute
        *a* it would be referenced as *o.a*.

        dictionary
        An associative array, where arbitrary keys are mapped to values.  The
        keys can be any object with :meth:`__hash__`  and :meth:`__eq__` methods.
        Called a hash in Perl.

    class
        A template for creating user-defined objects. Class definitions
        normally contain method definitions which operate on instances of the
        class.
      
    expression
        A piece of syntax which can be evaluated to some value.  In other words,
        an expression is an accumulation of expression elements like literals,
        names, attribute access, operators or function calls which all return a
        value.  In contrast to many other languages, not all language constructs
        are expressions.  There are also :term:`statement`\s which cannot be used
        as expressions, such as :func:`print` or :keyword:`if`.  Assignments
        are also statements, not expressions.

    function
        A series of statements which returns some value to a caller. It can also
        be passed zero or more arguments which may be used in the execution of
        the body. See also :term:`argument` and :term:`method`.

    generator
        A function which returns an iterator.  It looks like a normal function
        except that it contains :keyword:`yield` statements for producing a series
        a values usable in a for-loop or that can be retrieved one at a time with
        the :func:`next` function. Each :keyword:`yield` temporarily suspends
        processing, remembering the location execution state (including local
        variables and pending try-statements).  When the generator resumes, it
        picks-up where it left-off (in contrast to functions which start fresh on
        every invocation).

        .. index:: single: generator expression

    generator expression
        An expression that returns an iterator.  It looks like a normal expression
        followed by a :keyword:`for` expression defining a loop variable, range,
        and an optional :keyword:`if` expression.  The combined expression
        generates values for an enclosing function::

            >>> sum(i*i for i in range(10))       # sum of squares 0, 1, 4, ... 81
            285

    interactive
        Python has an interactive interpreter which means you can enter
        statements and expressions at the interpreter prompt, immediately
        execute them and see their results.  Just launch ``python`` with no
        arguments (possibly by selecting it from your computer's main
        menu). It is a very powerful way to test out new ideas or inspect
        modules and packages (remember ``help(x)``).

    interpreted
        Python is an interpreted language, as opposed to a compiled one,
        though the distinction can be blurry because of the presence of the
        bytecode compiler.  This means that source files can be run directly
        without explicitly creating an executable which is then run.
        Interpreted languages typically have a shorter development/debug cycle
        than compiled ones, though their programs generally also run more
        slowly.  See also :term:`interactive`.

    iterable
        An object capable of returning its members one at a
        time. Examples of iterables include all sequence types (such as
        :class:`list`, :class:`str`, and :class:`tuple`) and some non-sequence
        types like :class:`dict` and :class:`file` and objects of any classes you
        define with an :meth:`__iter__` or :meth:`__getitem__` method.  Iterables
        can be used in a :keyword:`for` loop and in many other places where a
        sequence is needed (:func:`zip`, :func:`map`, ...).  When an iterable
        object is passed as an argument to the built-in function :func:`iter`, it
        returns an iterator for the object.  This iterator is good for one pass
        over the set of values.  When using iterables, it is usually not necessary
        to call :func:`iter` or deal with iterator objects yourself.  The ``for``
        statement does that automatically for you, creating a temporary unnamed
        variable to hold the iterator for the duration of the loop.  See also
        :term:`iterator`, :term:`sequence`, and :term:`generator`.

    iterator
        An object representing a stream of data.  Repeated calls to the iterator's
        :meth:`next` method return successive items in the stream.  When no more
        data are available a :exc:`StopIteration` exception is raised instead.  At
        this point, the iterator object is exhausted and any further calls to its
        :meth:`next` method just raise :exc:`StopIteration` again.  Iterators are
        required to have an :meth:`__iter__` method that returns the iterator
        object itself so every iterator is also iterable and may be used in most
        places where other iterables are accepted.  One notable exception is code
        which attempts multiple iteration passes.  A container object (such as a
        :class:`list`) produces a fresh new iterator each time you pass it to the
        :func:`iter` function or use it in a :keyword:`for` loop.  Attempting this
        with an iterator will just return the same exhausted iterator object used
        in the previous iteration pass, making it appear like an empty container.

        More information can be found in :ref:`typeiter`.

    key function
        A key function or collation function is a callable that returns a value
        used for sorting or ordering.  For example, :func:`locale.strxfrm` is
        used to produce a sort key that is aware of locale specific sort
        conventions.

        A number of tools in Python accept key functions to control how elements
        are ordered or grouped.  They include :func:`min`, :func:`max`,
        :func:`sorted`, :meth:`list.sort`, :func:`heapq.nsmallest`,
        :func:`heapq.nlargest`, and :func:`itertools.groupby`.

        There are several ways to create a key function.  For example. the
        :meth:`str.lower` method can serve as a key function for case insensitive
        sorts.  Alternatively, an ad-hoc key function can be built from a
        :keyword:`lambda` expression such as ``lambda r: (r[0], r[2])``.  Also,
        the :mod:`operator` module provides three key function constructors:
        :func:`~operator.attrgetter`, :func:`~operator.itemgetter`, and
        :func:`~operator.methodcaller`.  See the :ref:`Sorting HOW TO
        <sortinghowto>` for examples of how to create and use key functions.

    keyword argument
        Arguments which are preceded with a ``variable_name=`` in the call.
        The variable name designates the local name in the function to which the
        value is assigned.  ``**`` is used to accept or pass a dictionary of
        keyword arguments.  See :term:`argument`.

    lambda
        An anonymous inline function consisting of a single :term:`expression`
        which is evaluated when the function is called.  The syntax to create
        a lambda function is ``lambda [arguments]: expression``

    list
        A built-in Python :term:`sequence`.  Despite its name it is more akin
        to an array in other languages than to a linked list since access to
        elements are O(1).

    list comprehension
        A compact way to process all or part of the elements in a sequence and
        return a list with the results.  ``result = ["0x%02x" % x for x in
        range(256) if x % 2 == 0]`` generates a list of strings containing
        even hex numbers (0x..) in the range from 0 to 255. The :keyword:`if`
        clause is optional.  If omitted, all elements in ``range(256)`` are
        processed.

    method
        A function which is defined inside a class body.  If called as an attribute
        of an instance of that class, the method will get the instance object as
        its first :term:`argument` (which is usually called ``self``).
        See :term:`function` and :term:`nested scope`.

    namespace
        The place where a variable is stored.  Namespaces are implemented as
        dictionaries.  There are the local, global and built-in namespaces as well
        as nested namespaces in objects (in methods).  Namespaces support
        modularity by preventing naming conflicts.  For instance, the functions
        :func:`__builtin__.open` and :func:`os.open` are distinguished by their
        namespaces.  Namespaces also aid readability and maintainability by making
        it clear which module implements a function.  For instance, writing
        :func:`random.seed` or :func:`itertools.izip` makes it clear that those
        functions are implemented by the :mod:`random` and :mod:`itertools`
        modules, respectively.

    nested scope
        The ability to refer to a variable in an enclosing definition.  For
        instance, a function defined inside another function can refer to
        variables in the outer function.  Note that nested scopes work only for
        reference and not for assignment which will always write to the innermost
        scope.  In contrast, local variables both read and write in the innermost
        scope.  Likewise, global variables read and write to the global namespace.

    new-style class
        Any class which inherits from :class:`object`.  This includes all built-in
        types like :class:`list` and :class:`dict`.  Only new-style classes can
        use Python's newer, versatile features like :attr:`__slots__`,
        descriptors, properties, and :meth:`__getattribute__`.

    object
        Any data with state (attributes or value) and defined behavior
        (methods).  Also the ultimate base class of any :term:`new-style
        class`.

    positional argument
        The arguments assigned to local names inside a function or method,
        determined by the order in which they were given in the call.  ``*`` is
        used to either accept multiple positional arguments (when in the
        definition), or pass several arguments as a list to a function.  See
        :term:`argument`.

    Python 3000
        Nickname for the Python 3.x release line (coined long ago when the release
        of version 3 was something in the distant future.)  This is also
        abbreviated "Py3k".

    Pythonic
        An idea or piece of code which closely follows the most common idioms
        of the Python language, rather than implementing code using concepts
        common to other languages.  For example, a common idiom in Python is
        to loop over all elements of an iterable using a :keyword:`for`
        statement.  Many other languages don't have this type of construct, so
        people unfamiliar with Python sometimes use a numerical counter instead::

            for i in range(len(food)):
                print food[i]

        As opposed to the cleaner, Pythonic method::

            for piece in food:
                print piece
             
    sequence
        An :term:`iterable` which supports efficient element access using integer
        indices via the :meth:`__getitem__` special method and defines a
        :meth:`len` method that returns the length of the sequence.
        Some built-in sequence types are :class:`list`, :class:`str`,
        :class:`tuple`, and :class:`unicode`. Note that :class:`dict` also
        supports :meth:`__getitem__` and :meth:`__len__`, but is considered a
        mapping rather than a sequence because the lookups use arbitrary
        :term:`immutable` keys rather than integers.

    slice
        An object usually containing a portion of a :term:`sequence`.  A slice is
        created using the subscript notation, ``[]`` with colons between numbers
        when several are given, such as in ``variable_name[1:3:5]``.  The bracket
        (subscript) notation uses :class:`slice` objects internally (or in older
        versions, :meth:`__getslice__` and :meth:`__setslice__`).

    statement
        A statement is part of a suite (a "block" of code).  A statement is either
        an :term:`expression` or a one of several constructs with a keyword, such
        as :keyword:`if`, :keyword:`while` or :keyword:`for`.

    triple-quoted string
        A string which is bound by three instances of either a quotation mark
        (") or an apostrophe (').  While they don't provide any functionality
        not available with single-quoted strings, they are useful for a number
        of reasons.  They allow you to include unescaped single and double
        quotes within a string and they can span multiple lines without the
        use of the continuation character, making them especially useful when
        writing docstrings.

    type
        The type of a Python object determines what kind of object it is; every
        object has a type.  An object's type is accessible as its
        :attr:`__class__` attribute or can be retrieved with ``type(obj)``.                          

    plugin
        See :term:`plug-in`.
    
    plug-in
        a plug-in (or plugin) is a set of software components that adds 
        specific abilities to a larger software application. If supported, 
        plug-ins enable customizing the functionality of an application. For
        example, plug-ins are commonly used in web browsers to play video,
        scan for viruses, and display new file types.
    
    MCA
        Multichannel Analyzer (MCA) is a device for ...

    CCD
        A charge-coupled device (CCD) is a device for the movement of electrical
        charge, usually from within the device to an area where the charge can
        be manipulated, for example conversion into a digital value. This is
        achieved by "shifting" the signals between stages within the device one
        at a time. CCDs move charge between capacitive bins in the device, with
        the shift allowing for the transfer of charge between bins.

    API
        An application programming interface (API) is a particular set of rules
        and specifications that software programs can follow to communicate with
        each other. It serves as an interface between different software
        programs and facilitates their interaction, similar to the way the user
        interface facilitates interaction between humans and computers.
        An API can be created for applications, libraries, operating systems,
        etc., as a way of defining their "vocabularies" and resources request
        conventions (e.g. function-calling conventions). It may include
        specifications for routines, data structures, object classes, and
        protocols used to communicate between the consumer program and the
        implementer program of the API.

    CLI
        A command-line interface (CLI) is a mechanism for interacting with a
        computer operating system or software by typing commands to perform
        specific tasks. This text-only interface contrasts with the use of a
        mouse pointer with a graphical user interface (:term:`GUI`) to click on
        options, or menus on a text user interface (TUI) to select options.
        This method of instructing a computer to perform a given task is
        referred to as "entering" a command: the system waits for the user
        to conclude the submitting of the text command by pressing the "Enter"
        key (a descendant of the "carriage return" key of a typewriter keyboard).
        A command-line interpreter then receives, parses, and executes the
        requested user command. The command-line interpreter may be run in a
        text terminal or in a terminal emulator window as a remote shell client
        such as PuTTY. Upon completion, the command usually returns output to
        the user in the form of text lines on the CLI. This output may be an
        answer if the command was a question, or otherwise a summary of the
        operation.

    GUI
        A graphical user interface (GUI) is a type of user interface that
        allows users to interact with electronic devices with images rather
        than text commands. GUIs can be used in computers, hand-held devices
        such as MP3 players, portable media players or gaming devices,
        household appliances and office equipment. A GUI represents the
        information and actions available to a user through graphical icons and
        visual indicators such as secondary notation, as opposed to text-based
        interfaces (:term:`CLI`), typed command labels or text navigation.
        The actions are usually performed through direct manipulation of the
        graphical elements.

    SDS
        Sardana Device server (SDS) is the sardana tango device server
        :term:`daemon`.

    OS
        An operating system (OS) is software, consisting of programs and data,
        that runs on computers, manages computer hardware resources, and
        provides common services for execution of various application software.
        Operating system is the most important type of system software in a
        computer system. Without an operating system, a user cannot run an
        application program on their computer, unless the application program
        is self booting.

    daemon
        In Unix and other computer multitasking operating systems, a daemon is a
        computer program that runs in the background, rather than under the
        direct control of a user. They are usually initiated as background
        processes. Typically daemons have names that end with the letter "d": for
        example, *syslogd*, the daemon that handles the system log, or *sshd*,
        which handles incoming SSH connections.

    SCADA
        supervisory control and data acquisition (SCADA) generally refers to
        industrial control systems: computer systems that monitor and control
        industrial, infrastructure, or facility-based processes.

    client-server model
        The client-server model of computing is a distributed application
        structure that partitions tasks or workloads between the providers of a
        resource or service, called servers, and service requesters, called
        clients. Often clients and servers communicate over a computer network
        on separate hardware, but both client and server may reside in the same
        system. A server machine is a host that is running one or more server
        programs which share their resources with clients. A client does not
        share any of its resources, but requests a server's content or service
        function. Clients therefore initiate communication sessions with servers
        which await incoming requests.

    user position
        Moveable position in user units (See also :term:`dial position`).
        Dial and user units are related by the following expressions:
            
            user = sign x dial + offset
            dial = controller_position / steps_per_unit
        
        where *sign* is -1 or 1. *offset* can be any number and *steps_per_unit*
        must be non zero.

    user
        See :term:`user position`

    dial position
        Position in controller units (See also :term:`user position`).
    
    dial
        See :term:`dial position`
        
.. _plug-in: http://en.wikipedia.org/wiki/Plug-in_(computing)
.. _CCD: http://en.wikipedia.org/wiki/Charge-coupled_device
.. _API: http://en.wikipedia.org/wiki/API
.. _CLI: http://en.wikipedia.org/wiki/Command-line_interface
.. _GUI: http://en.wikipedia.org/wiki/Graphical_user_interface
.. _OS: http://en.wikipedia.org/wiki/Operating_system
.. _daemon: http://en.wikipedia.org/wiki/Daemon_(computing)
.. _SCADA: http://en.wikipedia.org/wiki/SCADA
.. _client-server model: http://en.wikipedia.org/wiki/Client%E2%80%93server_model

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
