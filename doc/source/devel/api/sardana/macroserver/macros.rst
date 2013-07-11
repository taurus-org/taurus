.. currentmodule:: sardana.macroserver.macros

.. _macroserver-standard-macro-catalog:

:mod:`~sardana.macroserver.macros`
==================================


.. class:: scan.a2scan

    two-motor scan.
    a2scan scans two motors, as specified by motor1 and motor2.
    Each motor moves the same number of intervals with starting and ending
    positions given by start_pos1 and final_pos1, start_pos2 and final_pos2,
    respectively. The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    

.. class:: scan.a2scanc

    two-motor continuous scan
    

.. class:: scan.a3scan

    three-motor scan .
    a3scan scans three motors, as specified by motor1, motor2 and motor3.
    Each motor moves the same number of intervals with starting and ending
    positions given by start_pos1 and final_pos1, start_pos2 and final_pos2,
    start_pos3 and final_pos3, respectively.
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    

.. class:: scan.a3scanc

    three-motor continuous scan
    

.. class:: scan.a4scan

    four-motor scan .
    a4scan scans four motors, as specified by motor1, motor2, motor3 and motor4.
    Each motor moves the same number of intervals with starting and ending
    positions given by start_posN and final_posN (for N=1,2,3,4).
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    

.. class:: scan.a4scanc

    four-motor continuous scan
    

.. class:: scan.amultiscan

    Multiple motor scan.
    amultiscan scans N motors, as specified by motor1, motor2,...,motorN.
    Each motor moves the same number of intervals with starting and ending
    positions given by start_posN and final_posN (for N=1,2,...).
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    

.. class:: scan.ascan

    Do an absolute scan of the specified motor.
    ascan scans one motor, as specified by motor. The motor starts at the
    position given by start_pos and ends at the position given by final_pos.
    The step size is (start_pos-final_pos)/nr_interv. The number of data points collected
    will be nr_interv+1. Count time is given by time which if positive,
    specifies seconds and if negative, specifies monitor counts. 
    

.. class:: scan.ascanc

    Do an absolute continuous scan of the specified motor.
    ascanc scans one motor, as specified by motor.
    

.. class:: scan.ascanh

    Do an absolute scan of the specified motor.
    ascan scans one motor, as specified by motor. The motor starts at the
    position given by start_pos and ends at the position given by final_pos.
    The step size is (start_pos-final_pos)/nr_interv. The number of data points collected
    will be nr_interv+1. Count time is given by time which if positive,
    specifies seconds and if negative, specifies monitor counts. 
    
.. class:: demo.clear_sar_demo

    Undoes changes done with sar_demo

.. class:: expert.commit_ctrllib

    Puts the contents of the given data in a file inside the pool
    

.. class:: standard.ct

    Count for the specified time on the active measurement group
    

.. class:: scan.d2scan

    two-motor scan relative to the starting position.
    d2scan scans two motors, as specified by motor1 and motor2.
    Each motor moves the same number of intervals. If each motor is at a
    position X before the scan begins, it will be scanned from X+start_posN
    to X+final_posN (where N is one of 1,2).
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    

.. class:: scan.d2scanc

    continuous two-motor scan relative to the starting positions
    

.. class:: scan.d3scan

    three-motor scan .
    d3scan scans three motors, as specified by motor1, motor2 and motor3.
    Each motor moves the same number of intervals. If each motor is at a
    position X before the scan begins, it will be scanned from X+start_posN
    to X+final_posN (where N is one of 1,2,3)
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    

.. class:: scan.d3scanc

    continuous three-motor scan
    

.. class:: scan.d4scan

    four-motor scan relative to the starting positions
    a4scan scans four motors, as specified by motor1, motor2, motor3 and motor4.
    Each motor moves the same number of intervals. If each motor is at a
    position X before the scan begins, it will be scanned from X+start_posN
    to X+final_posN (where N is one of 1,2,3,4).
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    Upon termination, the motors are returned to their starting positions.
    

.. class:: scan.d4scanc

    continuous four-motor scan relative to the starting positions
    

.. class:: expert.defctrl

    Creates a new controller
    'role_prop' is a sequence of roles and/or properties.
    - A role is defined as <role name>=<role value> (only applicable to pseudo controllers)
    - A property is defined as <property name> <property value>
    
    If both roles and properties are supplied, all roles must come before properties.
    All controller properties that don't have default values must be given.
    
    Example of creating a motor controller (with a host and port properties):
    
    [1]: defctrl SuperMotorController myctrl host homer.springfield.com port 5000
    
    Example of creating a Slit pseudo motor (sl2t and sl2b motor roles, Gap and 
    Offset pseudo motor roles):
    
    [1]: defctrl Slit myslit sl2t=mot01 sl2b=mot02 Gap=gap01 Offset=offset01
    

.. class:: expert.defelem

    Creates an element on a controller with an axis
    

.. class:: expert.defm

    Creates a new motor in the active pool
    

.. class:: expert.defmeas

    Create a new measurement group. First channel in channel_list MUST
    be an internal sardana channel. At least one channel MUST be a
    Counter/Timer (by default, the first Counter/Timer in the list will
    become the master).
    

.. class:: scan.dmultiscan

    Multiple motor scan relative to the starting positions.
    dmultiscan scans N motors, as specified by motor1, motor2,...,motorN.
    Each motor moves the same number of intervals If each motor is at a
    position X before the scan begins, it will be scanned from X+start_posN
    to X+final_posN (where N is one of 1,2,...)
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    

.. class:: scan.dscan

    motor scan relative to the starting position.
    dscan scans one motor, as specified by motor. If motor motor is at a
    position X before the scan begins, it will be scanned from X+start_pos
    to X+final_pos. The step size is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1. Count time is
    given by time which if positive, specifies seconds and if negative,
    specifies monitor counts. 
    

.. class:: scan.dscanc

    continuous motor scan relative to the starting position.
    

.. class:: env.dumpenv

    Dumps the complete environment
    

.. class:: expert.edctrl

    Returns the contents of the library file which contains the given
    controller code.
    

.. class:: expert.edctrllib

    Returns the contents of the given library file
    

.. class:: scan.fscan

    N-dimensional scan along user defined paths.
    The motion path for each motor is defined through the evaluation of a
    user-supplied function that is evaluated as a function of the independent
    variables.
    -independent variables are supplied through the indepvar string.
    The syntax for indepvar is "x=expresion1,y=expresion2,..."
    -If no indep vars need to be defined, write "!" or "*" or "None"
    -motion path for motor is generated by evaluating the corresponding
    function 'func'
    -Count time is given by integ_time. If integ_time is a scalar, then
    the same integ_time is used for all points. If it evaluates as an array
    (with same length as the paths), fscan will assign a different integration
    time to each acquisition point.
    -If integ_time is positive, it specifies seconds and if negative, specifies
    monitor counts.   
    
    IMPORTANT Notes:
    -no spaces are allowed in the indepvar string.
    -all funcs must evaluate to the same number of points
    
    EXAMPLE: fscan x=[1,3,5,7,9],y=arange(5) motor1 x**2 motor2 sqrt(y*x-3) 0.1
    

.. class:: communication.get

    Reads and outputs the data from the communication channel
    

.. class:: env.load_env

    Read environment variables from config_env.xml file
    

.. class:: lists.ls0d

    Lists all 0D experiment channels
    

.. class:: lists.ls1d

    Lists all 1D experiment channels
    

.. class:: lists.ls2d

    Lists all 2D experiment channels
    

.. class:: lists.lsa

    Lists all existing objects
    

.. class:: lists.lscom

    Lists all communication channels
    

.. class:: lists.lsct

    Lists all Counter/Timers
    

.. class:: lists.lsctrl

    Lists all existing controllers
    

.. class:: lists.lsctrllib

    Lists all existing controller classes
    

.. class:: lists.lsdef

    List all macro definitions
    

.. class:: env.lsenv

    Lists the environment
    

.. class:: lists.lsexp

    Lists all experiment channels
    

.. class:: lists.lsi

    Lists all existing instruments
    

.. class:: lists.lsior

    Lists all IORegisters
    

.. class:: lists.lsm

    Lists all motors
    

.. class:: lists.lsmac

    Lists existing macros
    

.. class:: lists.lsmaclib

    Lists existing macro libraries.
    

.. class:: lists.lsmeas

    List existing measurement groups
    

.. class:: lists.lspc

    Lists all pseudo counters
    

.. class:: lists.lspm

    Lists all existing motors
    
.. class:: env.lsvo

    Lists the view options

.. class:: mca.mca_start

    Starts an mca
    

.. class:: mca.mca_stop

    Stops an mca
    

.. class:: scan.mesh

    2d grid scan  .
    The mesh scan traces out a grid using motor1 and motor2.
    The first motor scans from m1_start_pos to m1_final_pos using the specified
    number of intervals. The second motor similarly scans from m2_start_pos
    to m2_final_pos. Each point is counted for for integ_time seconds
    (or monitor counts, if integ_time is negative).
    The scan of motor1 is done at each point scanned by motor2. That is, the
    first motor scan is nested within the second motor scan.
    

.. class:: scan.meshc

    2d grid scan. scans continuous
    
.. class:: standard.mstate

    Prints the state of a motor


.. class:: standard.mv

    Move motor(s) to the specified position(s)
    

.. class:: standard.mvr

    Move motor(s) relative to the current position(s)
    

.. class:: expert.prdef

    Returns the the macro code for the given macro name.
    

.. class:: communication.put

    Sends a string to the communication channel
    

.. class:: standard.pwa

    Show all motor positions in a pretty table
    

.. class:: standard.pwm

    Show the position of the specified motors in a pretty table
    

.. class:: ioregister.read_ioreg

    Reads an output register
    

.. class:: expert.rellib

    Reloads the given python library code from the macro server filesystem.
    
    .. warning:: use with extreme care! Accidentally reloading a system
                 module or an installed python module may lead to unpredictable
                 behavior 
    
    .. note:: if python module is used by any macro, don't forget to reload
              the corresponding macros afterward so the changes take effect.
    

.. class:: expert.relmac

    Reloads the given macro code from the macro server filesystem.
    Attention: All macros inside the same file will also be reloaded.
    

.. class:: expert.relmaclib

    Reloads the given macro library code from the macro server filesystem.
    

.. class:: standard.report

    Logs a new record into the message report system (if active)
    
.. class:: demo.sar_demo

   Sets up a demo environment. It creates many elements for testing

.. class:: expert.sar_info

    Prints details about the given sardana object
    

.. class:: scan.scanhist

    Shows scan history information. Give optional parameter scan number to
    display details about a specific scan
    

.. class:: expert.send2ctrl

    Sends the given data directly to the controller
    

.. class:: env.senv

    Sets the given environment variable to the given value
    

.. class:: sequence.sequence

    This macro executes a sequence of macros. As a parameter 
    it receives a string which is a xml structure. These macros which allow
    hooks can nest another sequence (xml structure). In such a case, 
    this macro is executed recursively.
    

.. class:: standard.set_lim

    Sets the software limits on the specified motor hello
    

.. class:: standard.set_lm

    Sets the dial limits on the specified motor
    

.. class:: standard.set_pos

    Sets the position of the motor to the specified value
    

.. class:: standard.set_user_pos

    Sets the USER position of the motor to the specified value (by changing OFFSET and keeping DIAL)
    

.. class:: standard.settimer

    Defines the timer channel for the active measurement group
    

.. class:: env.setvo

    Sets the given view option to the given value
    

.. class:: standard.uct

    Count on the active measurement group and update
    

.. class:: expert.udefctrl

    Deletes an existing controller
    

.. class:: expert.udefelem

    Deletes an existing element
    

.. class:: expert.udefmeas

    Deletes an existing measurement group
    

.. class:: standard.umv

    Move motor(s) to the specified position(s) and update
    

.. class:: standard.umvr

    Move motor(s) relative to the current position(s) and update
    

.. class:: env.usenv

    Unsets the given environment variable
    

.. class:: env.usetvo

    Resets the value of the given view option
    

.. class:: standard.wa

    Show all motor positions
    

.. class:: standard.wm

    Show the position of the specified motors.
    

.. class:: ioregister.write_ioreg

    Writes a value to an input register
    

.. class:: standard.wu

    Show all user motor positions
    

.. class:: standard.wum

    Show the user position of the specified motors.
    
