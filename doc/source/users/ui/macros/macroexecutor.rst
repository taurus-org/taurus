.. _macroexecutor_ui:

==========================================
TaurusMacroExecutorWidget User's Interface
==========================================


.. contents::


The :class:`TaurusMacroExecutorWidget` provides an user-friendly interface to macro execution.
Graphical parameter editor (standard/custom) provides a clear way to set/modify macro execution settings(parameters), 
which can be permanently stored in favourites list. Once macro is in execution phase, this widget informs 
user about its state, with Door's state led and macro progress bar. User has full control over macros, 
with action buttons: Start, Stop, Pause, Resume.
Current macro settings (parameters) are translated to spock syntax, and represented in non editable
Spock Command line edit. It is foreseen to allow macro parameters edition from this widget.

.. figure:: /_static/macros/macroexecutor01.png
  :align: center

This widget can be either embedded in others, or used as a stand-alone application.

.. _taurusmacroexecutorwidget:


TaurusMacroExecutorWidget as a stand-alone application
------------------------------------------------------

You may also use `TaurusMacroExecutor` as a stand-alone application. In this case widget will be embedded in 
`TaurusMainWindow` and some extra functionalities will be provided. 
You can launch the stand-alone `TaurusMacroExecutorWidget`
with the following command::

    macroexecutor [options] [<macro_executor_dev_name> <door_dev_name>]
	
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
	
.. _standardmacroparameterseditor:

StandardMacroParametersEditor
---------------------------------

If no custom parameter editor is assigned to macro, default tree editor is used to configure execution settings (parameters).
Parameters are represented in form of tree (with hidden root node) - every parameter is a separate branch with two columns: 
parameter name and parameter value. 

In case of macros with single parameters only, tree has a one branch level only, and then tree representation looks more like a list 
(because of hidden root node)

.. figure:: /_static/macros/macroparameterseditor01.png
  :align: center

In case of macros which contain repeat parameters, concept of tree is more visible.  
 
.. figure:: /_static/macros/macroparameterseditor02.png
  :align: center
  
- adding new parameter repetition
First select parameter node and if its maximum number of repetition is not exceeded, button with '+' sign appears enabled. 
After pressing this button child branch with new repetition appears in tree editor.   

.. figure:: /_static/macros/macroparameterseditor03.png
  :align: center
  
- modifying repetition order
First select repetition node (with #<number> text), and buttons with arrows becomes enable (if it is feasible to change order)

.. figure:: /_static/macros/macroparameterseditor04.png
  :align: center

- removing parameter repetition
First select repetition node (with #<number> text), and if it's minimum number of repetition is not reached, button with '-' sign appears enabled. 
After pressing this button child branch disappears from tree editor. (see previous picture)

Editor is populated with default values for parameters, if this in not a case 'None' values are used. (If macro execution settings 
were restored e.g. from favourites list, editor is populated with stored values). Values become editable either by double-clicking on them, 
or by pressing F2 button when value is selected. This action opens default parameter editor (combobox with predefined values, spin box etc.).  

.. _senvmacroparameterseditor:

Custom Macro Parameters Edition
-------------------------------

TODO: senv

.. _favouriteslist:

FavouritesMacrosEditor
--------------
  
Once macro parameters are configured they can be easily stored in favourites list for later reuse. 
Thanks to `FavouritesMacrosEditor` this list can be easily managed.  

- adding a favourite 
Clicking in Add to favourites button (the one with yellow star), adds a new entry in favourite list, 
with current macro and its current settings.

- restoring a favourite
To restore macro from favourites list just select it in the list and macro parameters editor will immediately populate with stored settings.

- modifying favouites' order
First select favourite macro and buttons with arrows becomes enable (if it is feasible to change order)

- removing parameter repetition
First select favourite macro, button with '-' sign appears enabled. After pressing this button, previously selected macro disappears from the list.

