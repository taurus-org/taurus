
.. currentmodule:: sardana.macroserver.macro

.. _sardana-macros-scanframework:

==============
Scan Framework
==============

In general terms, we call *scan* to a macro that moves one or more motors and
acquires data along the path of the motor(s). See the
:ref:`introduction to the concept of scan in Sardana <sardana-users-scan>`.

While a scan macro could be written from scratch, Sardana provides a higher-
level API (the *scan framework*) that greatly simplifies the development of
scan macros by taking care of the details about synchronization of motors and
of acquisitions. 

The scan framework is implemented in the :mod:`~sardana.macroserver.scan`
module, which provides the :class:`~sardana.macroserver.scan.GScan` base class
and its specialized derived classes :class:`~sardana.macroserver.scan.SScan`
and :class:`~sardana.macroserver.scan.CScan` for step  and continuous scans,
respectively.

Creating a scan macro consists in writing a generic macro (see
:ref:`the generic macro writing instructions <sardana-macros-howto>`) in
which an instance of :class:`~sardana.macroserver.scan.GScan` is created
(typically in the :meth:`~Macro.prepare` method) which is then invoked in the
:meth:`~Macro.run` method.

Central to the scan framework is the
:meth:`~sardana.macroserver.macro.scan.gscan.GScan.generator` function, which
must be passed to the GScan constructor. This generator is a function that
allows to construct the path of the scan (see
:class:`~sardana.macroserver.scan.GScan` for detailed information on the
generator). 


A basic example on writing a step scan
--------------------------------------

Step scans are built using an instance of the
:class:`~sardana.macroserver.scan.SScan` class, which requires a step generator
that defines the path for the motion. Since in a step scan the data is acquired
at each step, the generator controls both the motion and the acquisition.

Note that in general, the generator does not need to generate a determinate (or
even finite) number of steps. Also note that it is possible to write generators
that vary their current step based on the acquired values (e.g., changing step
sizes as a function of some counter reading).

The :class:`~sardana.macroserver.macros.examples.ascan_demo` macro illustrates
the most basic features of a step scan:: 

   class ascan_demo(Macro):
       """
       This is a basic reimplementation of the ascan` macro for demonstration
       purposes of the Generic Scan framework. The "real" implementation of
       :class:`sardana.macroserver.macros.ascan` derives from
       :class:`sardana.macroserver.macros.aNscan` and provides some extra features.
       """
      
       hints = { 'scan' : 'ascan_demo'} #this is used to indicate other codes that the macro is a scan
       env = ('ActiveMntGrp',) #this hints that the macro requires the ActiveMntGrp environment variable to be set
      
       param_def = [
          ['motor',      Type.Moveable, None, 'Motor to move'],
          ['start_pos',  Type.Float,    None, 'Scan start position'],
          ['final_pos',  Type.Float,    None, 'Scan final position'],
          ['nr_interv',  Type.Integer,  None, 'Number of scan intervals'],
          ['integ_time', Type.Float,    None, 'Integration time']
       ]
      
       def prepare(self, motor, start_pos, final_pos, nr_interv, integ_time, **opts):
           #parse the user parameters
           self.start = numpy.array([start_pos], dtype='d')
           self.final = numpy.array([final_pos], dtype='d')
           self.integ_time = integ_time
      
           self.nr_points = nr_interv+1
           self.interv_size = ( self.final - self.start) / nr_interv
           self.name='ascan_demo'
           env = opts.get('env',{}) #the "env" dictionary may be passed as an option
           
           #create an instance of GScan (in this case, of its child, SScan
           self._gScan=SScan(self, generator=self._generator, moveables=[motor], env=env) 
      
      
       def _generator(self):
           step = {}
           step["integ_time"] =  self.integ_time #integ_time is the same for all steps
           for point_no in xrange(self.nr_points):
               step["positions"] = self.start + point_no * self.interv_size #note that this is a numpy array
               step["point_id"] = point_no
               yield step
       
       def run(self,*args):
           for step in self._gScan.step_scan(): #just go through the steps
               yield step
           
       @property
       def data(self):
           return self._gScan.data #the GScan provides scan data


The :class:`~sardana.macroserver.macros.examples.ascan_demo` shows only basic
features of the scan framework, but it already shows that writing a step scan
macro is mostly just a matter of writing a generator function.

It also shows that the :meth:`scan.gscan.GScan.data` method can be used to
provide the needed return value of :meth:`~Macro.data`



A basic example on writing a continuous scans
---------------------------------------------

Continuous scans are built using an instance of the
:class:`~sardana.macroserver.scan.CScan` class. Since in the continuous scans
the acquisition and motion are decoupled, CScan requires two independent
generators:

* a *waypoint generator*: which defines the path for the motion in a very
  similar way as the step generator does for a continuous scan. The steps
  generated by this generator are also called "waypoints".

* a *period generator* which controls the data acquisition steps. 


Essentially, :class:`~sardana.macroserver.scan.CScan` implements the continuous
scan as an acquisition loop (controlled by the period generator) nested within
a motion loop (controlled by the waypoint generator). Note that each loop is
run on an independent thread, and only limited communication occurs between the
two (basically the acquisition starts at the beginning of each movement and
ends when a waypoint is reached).

The :class:`~sardana.macroserver.macros.examples.ascanc_demo` macro illustrates
the most basic features of a continuous scan:: ::

   class ascanc_demo(Macro):
       """
       This is a basic reimplementation of the ascanc` macro for demonstration
       purposes of the Generic Scan framework. The "real" implementation of
       :class:`sardana.macroserver.macros.ascanc` derives from
       :class:`sardana.macroserver.macros.aNscan` and provides some extra features.
       """
   
       hints = { 'scan' : 'ascanc_demo'} #this is used to indicate other codes that the macro is a scan
       env = ('ActiveMntGrp',) #this hints that the macro requires the ActiveMntGrp environment variable to be set
   
       param_def = [
          ['motor',      Type.Moveable, None, 'Motor to move'],
          ['start_pos',  Type.Float,    None, 'Scan start position'],
          ['final_pos',  Type.Float,    None, 'Scan final position'],
          ['integ_time', Type.Float,    None, 'Integration time']
       ]
   
       def prepare(self, motor, start_pos, final_pos, integ_time, **opts):
           self.name='ascanc_demo'
           #parse the user parameters
           self.start = numpy.array([start_pos], dtype='d')
           self.final = numpy.array([final_pos], dtype='d')
           self.integ_time = integ_time
           env = opts.get('env',{}) #the "env" dictionary may be passed as an option
           
           #create an instance of GScan (in this case, of its child, CScan
           self._gScan = CScan(self, 
                               waypointGenerator=self._waypoint_generator, 
                               periodGenerator=self._period_generator, 
                               moveables=[motor], 
                               env=env)
           
       def _waypoint_generator(self):
           #a very simple waypoint generator! only start and stop points!
           yield {"positions":self.start, "waypoint_id": 0}
           yield {"positions":self.final, "waypoint_id": 1}
           
   
       def _period_generator(self):
           step = {}
           step["integ_time"] =  self.integ_time
           point_no = 0
           while(True): #infinite generator. The acquisition loop is started/stopped at begin and end of each waypoint 
               point_no += 1
               step["point_id"] = point_no
               yield step
       
       def run(self,*args):
           for step in self._gScan.step_scan(): 
               yield step


.. seealso:: for another example of a continuous scan implementation 
   (with more elaborated waypoint generator), see the code of 
   :class:`~sardana.macroserver.macros.scan.meshc`



Hooks support in scans
----------------------

In general, the Hooks API provided by the
:class:`~sardana.macroserver.macro.Hookable` base class allows a macro to run
other code (the hook callable) at certain points of its execution. The hooks
use a "hints" mechanism to pass the receiving macro some extra information on
how/when they should be executed. The hints are strings, and its content is not
fixed by the API, being up to each macro to identify, use and/or ignore them.

You can find some examples of the use of hooks in the
:mod:`~sardana.macroserver.macros.examples.hooks` module.

In the case of the scan macros, the hooks can be either registered directly via
the Hooks API or passed as key:values of the "step" dictionary returned by the
scan :meth:`~sardana.macroserver.macro.scan.gscan.GScan.generator` (see
:class:`~sardana.macroserver.macro.scan.gscan.GScan` for more details).

The hints for a given hook are used by the scan framework to select the moment
of the scan execution that the given hook is run. The following is a list of
hint strings that scan macros support (other hints are ignored):

- 'pre-scan-hooks' : before starting the scan.
- 'pre-move-hooks' : for steps: before starting to move.
- 'post-move-hooks': for steps: after finishing the move.
- 'pre-acq-hooks'  : for steps: before starting to acquire.
- 'post-acq-hooks' : for steps: after finishing acquisition but before
  recording the step.
- 'post-step-hooks' : for steps: after finishing recording the step.
- 'post-scan-hooks' : after finishing the scan

See the code of :class:`~sardana.macroserver.macros.examples.hooks.hooked_scan`
for a macro that demonstrates the use of the hook points of a scan.

Other examples of the :mod:`~sardana.macroserver.macros.examples.hooks` module
can be illustrative.

Also, note that the Taurus MacroExecutor widget allows the user to dynamically
add hooks to existing macros before execution.


More examples
-------------

Other macros in the :mod:`~sardana.macroserver.macros.examples` module
illustrate more features of the scan framework.

See also the code of the standard scan macros in the
:mod:`~sardana.macroserver.macros.scan` module. 

Finally, the documentation and code of :class:`~sardana.macroserver.scan.GScan`,
:class:`~sardana.macroserver.scan.SScan` and
:class:`~sardana.macroserver.scan.CScan` may be helpful.




