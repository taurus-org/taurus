
.. currentmodule:: sardana.macroserver.macro

.. _macroserver-macros-scanframework:

==============
Scan Framework
==============

In general terms, we call *scan* to a macro that moves one or more motors and
adquires data along the path of the motor(s). See the
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
:ref:`the generic macro writing instructions <macroserver-macros-howto>`) in
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
provide the needed resurn value of :meth:`~Macro.data`


Hooks
-----
In order to allow calling to other macros or methods at certain points of a
scan, the scan framework can make use of the Hooks API provided by the
:class:`~sardana.macroserver.macro.Hookable` base class. See e.g. the source
code of :class:`~sardana.macroserver.macros.examples.ascanr`.

Continuous scans
----------------


.. todo:: document creation of continuous scans. For the moment, see the code of
   :class:`~sardana.macroserver.macros.scan.ascanc`


More examples
-------------

Other macros in the :mod:`~sardana.macroserver.macros.examples` module
illustrate more features of the scan framework.

See also the code of the standard scan macros in the
:mod:`~sardana.macroserver.macros.scan` module. 

Finally, the documentation and code of :class:`~sardana.macroserver.scan.GScan`,
:class:`~sardana.macroserver.scan.SScan` and
:class:`~sardana.macroserver.scan.CScan` may be helpful.




