.. _sequencer_ui:

==========================================
TaurusSequencerWidget User's Interface
==========================================


.. contents::


The :class:`TaurusSequencerWidget` provides an user-friendly interface to macro execution.
Graphical parameter editor (standard/custom) provides a clear way to set/modify macro execution settings(parameters), 
which can be permanently stored in favourites list. Once macro is in execution phase, this widget informs 
user about its state, with Door's state led and macro progress bar. User has full control over macros, 
with action buttons: Start, Stop, Pause, Resume.
Current macro settings (parameters) are translated to spock syntax, and represented in non editable
Spock Command line edit. It is foreseen to allow macro parameters edition from this widget.

.. figure:: /_static/macros/macroexecutor01.png
  :align: center

This widget can be either embedded in others, or used as a stand-alone application.

.. _sequencerwidget:


TaurusSequencerWidget as a stand-alone application
------------------------------------------------------

You may also use `TaurusMacroExecutor` as a stand-alone application. In this case widget will be embedded in 
`TaurusMainWindow` and some extra functionalities will be provided. 
You can launch the stand-alone `TaurusMacroExecutorWidget`
with the following command::

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
If not provided at the application startup, device names can be later on selected from MacroConfigurationDialog.   
   
Extra functionalities:

- MacroConfigurationDialog
	TODO
- CustomEditorsPathDialog 
	TODO
	
StandardMacroParametersEditor
---------------------------------


Custom Macro Parameters Edition
-------------------------------

