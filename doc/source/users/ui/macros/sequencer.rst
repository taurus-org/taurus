.. _sequencer_ui:

==========================================
Sequencer User's Interface
==========================================


.. contents::


`Sequencer` provides an user-friendly interface to compose and execute sequences of macros. Sequence of macros allows execution 
of ordered set of macros with just one trigger. It also allows using a concept of hooks (macros attached and executed in defined places of other macros).
It is divided into 3 main areas: `actions bar`, `sequence editor` and `parameters editor`.
`Sequence editor` allows you modifying sequences in many ways: appending new macros, changing macros locations and removing macros. 
Graphical `parameters editor` (standard/custom) provides a clear way to set/modify macro execution settings(parameters). 
Once sequence of macros is in execution phase, `Sequencer` informs user about its state with Door's state led and macros progress bars. 
User has full control over sequence, with action buttons: Start, Stop, Pause, Resume. 
If desirable, sequences can be permanently stored into a file and later on restored from there. 
This functionality is provided thanks to action buttons: Save and Open a sequence.

.. figure:: /_static/macros/sequencer01.png
  :align: center


.. _sequencer_stand-alone:

Sequencer as a stand-alone application
--------------------------------------

You may also use *Sequencer* as a stand-alone application. In this case it appears embedded
in window and some extra functionalities are provided.  
You can launch the stand-alone *Sequencer* with the following command::

    sequencer [options] [<macro_executor_dev_name> <door_dev_name>]
	
Options::
 
  --taurus-log-level=LEVEL
                        taurus log level. Allowed values are (case
                        insensitive): critical, error, warning/warn, info,
                        debug, trace
                        
  --taurus-polling-period=MILLISEC
                        taurus global polling period in milliseconds
                        
  --taurus-serialization-mode=SERIAL
                        taurus serialization mode. Allowed values are (case
                        insensitive): serial, concurrent (default)
  
  --tango-host=TANGO_HOST
                        Tango host name

    
The model list is optional and is a space-separated list of two device names: macro server and door.
If not provided at the application startup, device names can be later on selected from Macro Configuration Dialog.   
   
Extra functionalities:

- MacroConfigurationDialog

.. todo:: 
		This chapter in not ready... Sorry for inconvenience. 
		 
- CustomEditorsPathDialog
 
.. todo:: 
		This chapter in not ready... Sorry for inconvenience.
		
.. _editing_sequence:

Editing sequence
----------------

Sequence is represented as a flat list of ordered macros, in this view each macro is represented as a new line with 4 columns: 
Macro (macro name), Parameters (comma separated parameter values), Progress (macro progress bar) and Pause 
(pause point before macro execution - not implemented yet). Macros which contain hooks, expand with branched macros. 
Macro parameters values can be edited from `parameters editor`, to do so select one macro in sequence editor by clicking on it. 
Selected macro becomes highlighted, and `parameters editor` populate with its current parameters values. 

.. figure:: /_static/macros/sequenceeditor01.png
  :align: center

- adding a new macro 

First select macro from macro combo box, and when you are sure to add it to the sequence, press '+' button. 
To add macro as a hook of other macro, before adding it, please select its parent macro in the sequence, and then press '+' button.
If no macro was selected as a parent, macro will be automatically appended at the end of the list.    
   
.. figure:: /_static/macros/sequenceeditor02.png
  :align: center  
  
- reorganizing sequence

Macros which are already part of a sequence, can be freely moved around, either in execution order or in hook place (if new macro accepts hooks).
To move macro first select it in the sequence by single clicking on it (it will become highlighted). Then a set of buttons with arrows 
become enabled. Clicking on them will cause selected macro changin its position in the sequence (either vertically - execution order or horizontal
parent macro - hook macro relationship)

.. figure:: /_static/macros/sequenceeditor03.png
  :align: center
  
- remove macro

Macros which are already part of a sequence, can be freely removed from it. To do so first select macro in a sequence by 
single clicking on it (it will become highlighted). Then button with '-' becomes enabled. Clicking on it removes selected macro. 

.. figure:: /_static/macros/sequenceeditor04.png
  :align: center  

- configuring hook execution place

If macro is embedded as a hook in parent macro, please follow these instructions to configure its hook execution place. 
First select macro in a sequence by single clicking on it (it will become highlighted). 
Then using right mouse button open context menu, go to 'Hook places' sub-menu and select hook places which interest you 
(you can select more than one). 
   
.. figure:: /_static/macros/sequenceeditor05_raw.png
  :align: center 

	
Editing macro parameters
------------------------
To obtain information about editing macro parameters, please refer to the following link :ref:`Editing macro parameters <editing_macro_parameters>` 